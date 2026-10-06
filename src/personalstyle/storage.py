"""Bounded engine-owned writing example persistence; no personalization behavior."""

import re
import sqlite3
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from personalstyle.security import (
    SecurityError,
    prepare_private_file,
    verify_private_directory,
    verify_private_file,
)

MAX_TEXT_BYTES = 64 * 1024
MAX_EXAMPLES = 1000
MAX_DATABASE_BYTES = 128 * 1024 * 1024
APPLICATION_ID = 0x50535459
SCHEMA = {
    "store_meta": "CREATE TABLE store_meta (schema_version INTEGER NOT NULL, "
    "profile_version INTEGER NOT NULL)",
    "examples": "CREATE TABLE examples (id TEXT PRIMARY KEY, text TEXT NOT NULL, "
    "context TEXT NOT NULL, supplier TEXT NOT NULL, authorizer TEXT NOT NULL, "
    "source_kind TEXT NOT NULL, learning_eligible INTEGER NOT NULL, held_out INTEGER NOT NULL, "
    "record_version INTEGER NOT NULL, created_at TEXT NOT NULL)",
}


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

    def _boundary(self, check_sidecars: bool = True) -> tuple[tuple[int, int], tuple[int, int]]:
        verify_private_directory(self.path.parent)
        verify_private_file(self.path)
        if self.path.stat().st_size > MAX_DATABASE_BYTES:
            raise StoreError("DATABASE_UNAVAILABLE_OR_CORRUPT")
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
        if (
            connection.execute("PRAGMA application_id").fetchone() != (APPLICATION_ID,)
            or connection.execute("PRAGMA user_version").fetchone() != (1,)
            or connection.execute("PRAGMA journal_mode").fetchone() != ("delete",)
        ):
            raise StoreError("DATABASE_UNAVAILABLE_OR_CORRUPT")
        objects = connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"
        ).fetchall()
        if dict(objects) != SCHEMA:
            raise StoreError("DATABASE_UNAVAILABLE_OR_CORRUPT")
        metadata = connection.execute("SELECT schema_version, profile_version FROM store_meta").fetchall()
        if (
            len(metadata) != 1 or metadata[0][0] != 1
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
                connection.execute("INSERT INTO store_meta VALUES (1, 1)")
                connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
                connection.execute("PRAGMA user_version=1")
            row = connection.execute("SELECT * FROM examples WHERE id=?", (example.id,)).fetchone()
            if row is not None and tuple(row[:8]) != example.payload():
                raise StoreError("IDEMPOTENCY_CONFLICT")
            if row is None:
                if connection.execute("SELECT count(*) FROM examples").fetchone()[0] >= MAX_EXAMPLES:
                    raise StoreError("INVALID_EXAMPLE")
                timestamp = datetime.now(UTC).isoformat()
                connection.execute(
                    "INSERT INTO examples VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)",
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
