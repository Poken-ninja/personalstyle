"""Bounded engine-owned writing example persistence; no personalization behavior."""

import json
import re
import sqlite3
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from personalstyle.security import (
    SecurityError,
    prepare_private_file,
    verify_private_directory,
    verify_private_file,
)

MAX_TEXT_BYTES = 64 * 1024
APPLICATION_ID = 0x50535459
SCHEMA_V1 = {
    "store_meta": "CREATE TABLE store_meta (schema_version INTEGER NOT NULL, "
    "profile_version INTEGER NOT NULL)",
    "examples": "CREATE TABLE examples (id TEXT PRIMARY KEY, text TEXT NOT NULL, "
    "context TEXT NOT NULL, supplier TEXT NOT NULL, authorizer TEXT NOT NULL, "
    "source_kind TEXT NOT NULL, learning_eligible INTEGER NOT NULL, held_out INTEGER NOT NULL, "
    "record_version INTEGER NOT NULL, created_at TEXT NOT NULL)",
}
SCHEMA = {
    **SCHEMA_V1,
    "examples": SCHEMA_V1["examples"][:-1] +
    ", writer_schema INTEGER NOT NULL DEFAULT 2 CHECK(writer_schema=2))",
    "preferences": "CREATE TABLE preferences (id TEXT NOT NULL, version INTEGER NOT NULL, "
    "context TEXT NOT NULL, feature TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(id, version))",
    "feedback": "CREATE TABLE feedback (id TEXT PRIMARY KEY, context TEXT NOT NULL, payload TEXT NOT NULL, "
    "record_version INTEGER NOT NULL, profile_version INTEGER NOT NULL, created_at TEXT NOT NULL, "
    "run_id TEXT NOT NULL, observations TEXT NOT NULL)",
}
INDEXES = {
    "examples_eligible": "CREATE INDEX examples_eligible ON examples(context, learning_eligible, held_out, id)",
    "feedback_context": "CREATE INDEX feedback_context ON feedback(context, id)",
    "feedback_runs": "CREATE INDEX feedback_runs ON feedback(context, run_id)",
    "preferences_context": "CREATE UNIQUE INDEX preferences_context ON preferences(context, feature, version DESC)",
}
SCHEMA.update(INDEXES)



class StoreError(ValueError):
    """Fixed failure codes only; never include SQLite errors or writing."""


@dataclass(frozen=True)
class ExampleInput:
    id: str
    text: str
    context: str
    supplier: str
    authorizer: str
    source_kind: str
    authorized: bool
    learning_eligible: bool = False
    held_out: bool = False

    def payload(self) -> tuple[str | int, ...]:
        return (
            self.id, self.text, self.context, self.supplier, self.authorizer, self.source_kind,
            int(self.learning_eligible), int(self.held_out),
        )

    def validate(self) -> None:
        try:
            valid_id = str(UUID(self.id)) == self.id
            strings = (self.text, self.supplier, self.authorizer)
            valid_strings = all(type(value) is str and value.strip() for value in strings)
            sizes = [len(value.encode("utf-8")) for value in strings]
            valid = (
                valid_id and valid_strings and sizes[0] <= MAX_TEXT_BYTES
                and sizes[1] <= 256 and sizes[2] <= 256
                and type(self.context) is str
                and re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", self.context) is not None
                and self.source_kind in {"user_owned", "authorized_reference"}
                and self.authorized is True
                and type(self.learning_eligible) is bool and type(self.held_out) is bool
                and not (self.learning_eligible and self.held_out)
            )
        except (ValueError, TypeError, AttributeError, UnicodeError):
            valid = False
        if not valid:
            raise StoreError("INVALID_EXAMPLE")


class ExampleStore:
    """No connection or boundary-verification cache survives an operation."""

    def __init__(self, path: Path):
        self.path = path.absolute()

    @contextmanager
    def eligible_examples(
        self, context: str, deadline: float, *, preferences: list[dict[str, Any]] | None = None,
    ) -> Iterator[tuple[int, Iterator[tuple[str, int, str]]]]:
        """Stream one exact-context corpus from a protected, consistent read snapshot."""
        if type(context) is not str or re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", context) is None:
            raise StoreError("PROFILE_SOURCE_INVALID")
        connection = None

        def check_time() -> None:
            if time.monotonic() >= deadline:
                raise StoreError("PROFILE_RESOURCE_LIMIT")

        try:
            check_time()
            identity = self._boundary()
            connection = self._connect(readonly=True)
            connection.execute("BEGIN")
            self._schema(connection)
            self._recheck(identity)
            version = connection.execute("SELECT profile_version FROM store_meta").fetchone()[0]
            if preferences is not None:
                preferences.extend(
                    {key: p[key] for key in ("id", "version", "context", "feature",
                                            "direction", "policy_version")}
                    for p in self.active_preferences(connection, context)
                )
            cursor = connection.execute(
                "SELECT * FROM examples WHERE context=? AND learning_eligible=1 AND held_out=0 "
                "ORDER BY id COLLATE BINARY", (context,),
            )

            def rows() -> Iterator[tuple[str, int, str]]:
                for row in cursor:
                    check_time()
                    if type(row[8]) is not int or row[8] != 1:
                        raise StoreError("PROFILE_VERSION_INCOMPATIBLE")
                    if (
                        type(row[6]) is not int or row[6] != 1
                        or type(row[7]) is not int or row[7] != 0 or row[2] != context
                    ):
                        raise StoreError("PROFILE_SOURCE_INVALID")
                    try:
                        ExampleInput(
                            id=row[0], text=row[1], context=row[2], supplier=row[3],
                            authorizer=row[4], source_kind=row[5], authorized=True,
                            learning_eligible=True, held_out=False,
                        ).validate()
                    except StoreError:
                        raise StoreError("PROFILE_SOURCE_INVALID") from None
                    yield row[0], row[8], row[1]

            yield version, rows()
            self._recheck(identity)
            check_time()
        except SecurityError:
            raise StoreError("STORAGE_BOUNDARY_INVALID") from None
        except sqlite3.Error as error:
            if getattr(error, "sqlite_errorcode", None) == sqlite3.SQLITE_INTERRUPT:
                raise StoreError("PROFILE_RESOURCE_LIMIT") from None
            raise StoreError("DATABASE_UNAVAILABLE_OR_CORRUPT") from None
        except OSError:
            raise StoreError("DATABASE_UNAVAILABLE_OR_CORRUPT") from None
        finally:
            if connection is not None:
                connection.close()

    def _boundary(self, check_sidecars: bool = True) -> tuple[tuple[int, int], tuple[int, int]]:
        verify_private_directory(self.path.parent)
        verify_private_file(self.path)
        if check_sidecars and any(
            Path(str(self.path) + suffix).exists() for suffix in ("-journal", "-wal", "-shm")
        ):
            raise StoreError("DATABASE_UNAVAILABLE_OR_CORRUPT")
        directory, file = self.path.parent.stat(), self.path.stat()
        return (directory.st_dev, directory.st_ino), (file.st_dev, file.st_ino)

    def _recheck(self, identity: tuple[tuple[int, int], tuple[int, int]]) -> None:
        # An active transaction owns its rollback journal; stale sidecars were rejected
        # before opening. The verified parent ACL protects SQLite-created sidecars.
        if self._boundary(check_sidecars=False) != identity:
            raise SecurityError("Profile filesystem identity changed")

    def _connect(self, readonly: bool = False) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.path.as_uri() + ("?mode=ro" if readonly else "?mode=rw"),
            uri=True, timeout=2, isolation_level=None,
        )
        deadline = time.monotonic() + 2
        connection.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
        connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 128 * 1024)
        connection.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH, 8192)
        try:
            connection.execute("PRAGMA trusted_schema=OFF")
            connection.execute("PRAGMA cache_spill=OFF")
        except sqlite3.Error:
            connection.close()
            raise
        return connection

    @staticmethod
    def _schema(connection: sqlite3.Connection) -> None:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        if (
            connection.execute("PRAGMA application_id").fetchone() != (APPLICATION_ID,)
            or version not in (1, 2)
            or connection.execute("PRAGMA journal_mode").fetchone() != ("delete",)
        ):
            raise StoreError("DATABASE_UNAVAILABLE_OR_CORRUPT")
        objects = connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"
        ).fetchall()
        if dict(objects) != (SCHEMA_V1 if version == 1 else SCHEMA):
            raise StoreError("DATABASE_UNAVAILABLE_OR_CORRUPT")
        metadata = connection.execute("SELECT schema_version, profile_version FROM store_meta").fetchall()
        if (
            len(metadata) != 1 or metadata[0][0] != version
            or type(metadata[0][1]) is not int or metadata[0][1] < 1
        ):
            raise StoreError("DATABASE_UNAVAILABLE_OR_CORRUPT")

    def add(self, example: ExampleInput) -> dict[str, str | int]:
        example.validate()
        connection = None
        try:
            verify_private_directory(self.path.parent)
            new = not self.path.exists()
            if new:
                prepare_private_file(self.path)
            identity = self._boundary()  # Must precede opening for mutation.
            connection = self._connect()
            if not new:
                self._schema(connection)
            self._recheck(identity)
            connection.execute("BEGIN IMMEDIATE")
            if new:
                for statement in SCHEMA.values():
                    connection.execute(statement)
                connection.execute("INSERT INTO store_meta VALUES (2, 1)")
                connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
                connection.execute("PRAGMA user_version=2")
            else:
                self._schema(connection)  # Revalidate after acquiring the write lock.
                if connection.execute("PRAGMA user_version").fetchone() != (2,):
                    raise StoreError("STORAGE_MIGRATION_REQUIRED")
            row = connection.execute("SELECT * FROM examples WHERE id=?", (example.id,)).fetchone()
            if row is not None and tuple(row[:8]) != example.payload():
                raise StoreError("IDEMPOTENCY_CONFLICT")
            if row is None:
                timestamp = datetime.now(UTC).isoformat()
                connection.execute(
                    "INSERT INTO examples VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 2)",
                    (*example.payload(), timestamp),
                )
                connection.execute("UPDATE store_meta SET profile_version=profile_version+1")
            stored = connection.execute("SELECT * FROM examples WHERE id=?", (example.id,)).fetchone()
            if stored is None or tuple(stored[:8]) != example.payload():
                raise StoreError("PERSISTENCE_VERIFICATION_FAILED")
            # cache_spill=OFF retains dirty pages until guarded commit; no stale ACL grant.
            self._recheck(identity)
            connection.execute("COMMIT")
        except SecurityError:
            raise StoreError("STORAGE_BOUNDARY_INVALID") from None
        except (OSError, sqlite3.Error):
            raise StoreError("DATABASE_UNAVAILABLE_OR_CORRUPT") from None
        finally:
            if connection is not None:
                try:
                    if connection.in_transaction:
                        connection.execute("ROLLBACK")
                except sqlite3.Error:
                    raise StoreError("TRANSACTION_FAILED") from None
                finally:
                    connection.close()
        result = self.get(example.id)
        if result is None or tuple(result.values())[:8] != example.payload():
            raise StoreError("PERSISTENCE_VERIFICATION_FAILED")
        return result

    @contextmanager
    def feedback_connection(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        """Reuse the existing canonical boundary for feedback, not a second store."""
        connection = None
        try:
            identity = self._boundary()
            connection = self._connect(readonly=not write)
            connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            self._schema(connection)
            if connection.execute("PRAGMA user_version").fetchone() != (2,):
                raise StoreError("STORAGE_MIGRATION_REQUIRED")
            self._recheck(identity)
            yield connection
            self._recheck(identity)
            connection.execute("COMMIT")
        except SecurityError:
            raise StoreError("STORAGE_BOUNDARY_INVALID") from None
        except (OSError, sqlite3.Error):
            raise StoreError("DATABASE_UNAVAILABLE_OR_CORRUPT") from None
        finally:
            if connection is not None:
                try:
                    if connection.in_transaction:
                        connection.execute("ROLLBACK")
                except sqlite3.Error:
                    raise StoreError("TRANSACTION_FAILED") from None
                finally:
                    connection.close()

    def migrate_feedback_schema(self) -> None:
        """Explicit guarded 1->2 migration; no normal write migrates implicitly."""
        connection = None
        try:
            identity = self._boundary()
            connection = self._connect()
            connection.execute("BEGIN IMMEDIATE")
            self._schema(connection)
            if connection.execute("PRAGMA user_version").fetchone() == (1,):
                connection.execute(
                    "ALTER TABLE examples ADD COLUMN writer_schema INTEGER NOT NULL "
                    "DEFAULT 2 CHECK(writer_schema=2)"
                )
                connection.execute(SCHEMA["feedback"])
                connection.execute(SCHEMA["preferences"])
                for statement in INDEXES.values():
                    connection.execute(statement)
                connection.execute(
                    "UPDATE store_meta SET schema_version=2, profile_version=profile_version+1"
                )
                connection.execute("PRAGMA user_version=2")
            self._schema(connection)
            self._recheck(identity)
            connection.execute("COMMIT")
        except SecurityError:
            raise StoreError("STORAGE_BOUNDARY_INVALID") from None
        except (OSError, sqlite3.Error):
            raise StoreError("DATABASE_UNAVAILABLE_OR_CORRUPT") from None
        finally:
            if connection is not None:
                try:
                    if connection.in_transaction:
                        connection.execute("ROLLBACK")
                except sqlite3.Error:
                    raise StoreError("TRANSACTION_FAILED") from None
                finally:
                    connection.close()
        with self.feedback_connection():
            pass

    @staticmethod
    def preference_records(connection: sqlite3.Connection, context: str) -> list[dict[str, Any]]:
        """Latest version per feature; validate before either evaluation or consumption."""
        if connection.execute("PRAGMA user_version").fetchone() == (1,):
            return []
        records = []
        for row in connection.execute(
            "SELECT p.id, p.version, p.feature, p.payload FROM preferences p JOIN "
            "(SELECT feature, MAX(version) version FROM preferences WHERE context=? GROUP BY feature) latest "
            "ON p.context=? AND p.feature=latest.feature AND p.version=latest.version ORDER BY p.feature",
            (context, context),
        ):
            try:
                value = json.loads(row[3])
                units = value["supporting_units"]
                if (
                    value["id"] != row[0] or str(UUID(row[0])) != row[0]
                    or type(row[1]) is not int or row[1] < 1 or value["version"] != row[1]
                    or value["context"] != context or value["feature"] != row[2]
                    or row[2] not in {"paragraph_count", "line_count", "separator_characters"}
                    or value["policy_version"] != "context_preference_promotion.v1"
                    or value["state"] not in {"active", "contested", "unpromoted"}
                    or value["direction"] not in {None, "increase", "decrease"}
                    or type(value["source_profile_version"]) is not int
                    or value["source_profile_version"] < 1
                    or type(units) is not list or len(units) > 3
                    or any(str(UUID(u["feedback_id"])) != u["feedback_id"]
                           or str(UUID(u["run_id"])) != u["run_id"]
                           or u["direction"] not in {"increase", "decrease"} for u in units)
                    or len({u["run_id"] for u in units}) != len(units)
                    or value["supporting_feedback_ids"] != [u["feedback_id"] for u in units]
                    or value["supporting_run_ids"] != [u["run_id"] for u in units]
                    or (value["state"] == "active" and (
                        len(units) != 3 or any(u["direction"] != value["direction"] for u in units)))
                    or (value["state"] == "unpromoted" and len(units) >= 3)
                    or (value["state"] == "contested" and (
                        len(units) != 3 or len({u["direction"] for u in units}) != 2))
                ):
                    raise ValueError
            except (ValueError, KeyError, TypeError, AttributeError):
                raise StoreError("PREFERENCE_SOURCE_INVALID") from None
            records.append(value)
        if len(records) > 3 or len({p["feature"] for p in records}) != len(records):
            raise StoreError("PREFERENCE_SOURCE_INVALID")
        return records

    @classmethod
    def active_preferences(cls, connection: sqlite3.Connection, context: str) -> list[dict[str, Any]]:
        return [p for p in cls.preference_records(connection, context) if p["state"] == "active"]

    def get(self, example_id: str) -> dict[str, str | int] | None:
        try:
            if str(UUID(example_id)) != example_id:
                raise StoreError("INVALID_EXAMPLE")
        except (ValueError, TypeError, AttributeError):
            raise StoreError("INVALID_EXAMPLE") from None
        connection = None
        try:
            identity = self._boundary()
            connection = self._connect(readonly=True)
            self._schema(connection)
            self._recheck(identity)
            cursor = connection.execute("SELECT * FROM examples WHERE id=?", (example_id,))
            row = cursor.fetchone()
            return None if row is None else dict(zip((item[0] for item in cursor.description), row))
        except SecurityError:
            raise StoreError("STORAGE_BOUNDARY_INVALID") from None
        except (OSError, sqlite3.Error):
            raise StoreError("DATABASE_UNAVAILABLE_OR_CORRUPT") from None
        finally:
            if connection is not None:
                connection.close()
