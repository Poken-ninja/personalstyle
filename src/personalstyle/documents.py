"""Bounded local document import/export primitives owned by the engine."""

from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path, PureWindowsPath
from typing import NoReturn
from uuid import UUID, uuid5

from personalstyle.storage import MAX_TEXT_BYTES

TEXT_FORMATS = frozenset({"txt", "md"})
MAX_FILE_BYTES = MAX_TEXT_BYTES
MAX_DOCUMENT_BODY_BYTES = MAX_TEXT_BYTES * 6 + 128 * 1024
_REPARSE_POINT = 0x400
_DOCUMENT_NAMESPACE = UUID("b30b1e02-1d0c-5f7d-87c8-67b34e3bd9ad")


class DocumentError(ValueError):
    """A fixed, safe-to-return document operation failure."""


def _fail(code: str) -> NoReturn:
    raise DocumentError(code)


def _path(value: object) -> Path:
    if (type(value) is not str or not value or len(value) > 32767 or "\0" in value
            or ".." in Path(value).parts or ".." in PureWindowsPath(value).parts):
        return _fail("DOCUMENT_PATH_INVALID")
    native = Path(value)
    windows = PureWindowsPath(value)
    if not native.is_absolute() or windows.drive.startswith("\\\\"):
        return _fail("DOCUMENT_PATH_INVALID")
    return native


def _safe_ancestors(path: Path) -> None:
    """Reject symlink/reparse traversal for every existing component."""
    for component in (path, *path.parents):
        try:
            metadata = component.lstat()
        except FileNotFoundError:
            continue
        except OSError:
            _fail("DOCUMENT_PATH_INVALID")
        if (stat.S_ISLNK(metadata.st_mode)
                or getattr(metadata, "st_file_attributes", 0) & _REPARSE_POINT):
            _fail("DOCUMENT_PATH_INVALID")


def _supported_path(value: object, format_name: object) -> tuple[Path, str]:
    if type(format_name) is not str or format_name not in TEXT_FORMATS:
        return _fail("DOCUMENT_FORMAT_UNSUPPORTED")
    path = _path(value)
    if path.suffix.lower() != f".{format_name}":
        return _fail("DOCUMENT_EXTENSION_MISMATCH")
    return path, format_name


def import_document(path_value: object, format_name: object) -> dict[str, object]:
    """Read one selected UTF-8 text file without following links or reading past the cap."""
    path, selected_format = _supported_path(path_value, format_name)
    _safe_ancestors(path)
    try:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_FILE_BYTES:
            return _fail("DOCUMENT_RESOURCE_LIMIT" if before.st_size > MAX_FILE_BYTES
                         else "DOCUMENT_PATH_INVALID")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if (not stat.S_ISREG(opened.st_mode)
                    or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)):
                return _fail("DOCUMENT_PATH_INVALID")
            with os.fdopen(descriptor, "rb", closefd=False) as source:
                raw = source.read(MAX_FILE_BYTES + 1)
            after = path.lstat()
            if ((after.st_dev, after.st_ino, after.st_size)
                    != (before.st_dev, before.st_ino, before.st_size)):
                return _fail("DOCUMENT_IMPORT_FAILED")
        finally:
            os.close(descriptor)
    except DocumentError:
        raise
    except OSError:
        return _fail("DOCUMENT_IMPORT_FAILED")
    if len(raw) > MAX_FILE_BYTES:
        return _fail("DOCUMENT_RESOURCE_LIMIT")
    if not raw:
        return _fail("DOCUMENT_EMPTY")
    try:
        text = raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        return _fail("DOCUMENT_MALFORMED")
    if "\0" in text:
        return _fail("DOCUMENT_MALFORMED")
    if len(text.encode("utf-8")) > MAX_TEXT_BYTES:
        return _fail("DOCUMENT_RESOURCE_LIMIT")
    if not text.strip():
        return _fail("DOCUMENT_EMPTY")
    stable_source = str(path.resolve(strict=True)).casefold()
    document_id = str(uuid5(_DOCUMENT_NAMESPACE, stable_source))
    return {"document_id": document_id, "format": selected_format,
            "text": text, "bytes": len(raw)}


def export_document(path_value: object, format_name: object, text: object) -> dict[str, object]:
    """Write UTF-8 through a same-directory temporary and atomically replace the target."""
    path, selected_format = _supported_path(path_value, format_name)
    if type(text) is not str or "\0" in text:
        return _fail("DOCUMENT_MALFORMED")
    try:
        encoded = text.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        return _fail("DOCUMENT_MALFORMED")
    if len(encoded) > MAX_TEXT_BYTES:
        return _fail("DOCUMENT_RESOURCE_LIMIT")
    parent = path.parent
    _safe_ancestors(parent)
    try:
        parent_before = parent.stat()
        if not stat.S_ISDIR(parent_before.st_mode):
            return _fail("DOCUMENT_PATH_INVALID")
        try:
            target_before = path.lstat()
        except FileNotFoundError:
            target_before = None
        if target_before is not None and (
            not stat.S_ISREG(target_before.st_mode)
            or stat.S_ISLNK(target_before.st_mode)
            or getattr(target_before, "st_file_attributes", 0) & _REPARSE_POINT
        ):
            return _fail("DOCUMENT_PATH_INVALID")
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".personalstyle-", suffix=".tmp", dir=parent,
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as output:
                output.write(encoded)
                output.flush()
                os.fsync(output.fileno())
            _safe_ancestors(parent)
            parent_now = parent.stat()
            if (parent_now.st_dev, parent_now.st_ino) != (parent_before.st_dev, parent_before.st_ino):
                return _fail("DOCUMENT_PATH_INVALID")
            try:
                target_now = path.lstat()
            except FileNotFoundError:
                target_now = None
            if ((target_before is None) != (target_now is None)
                    or (target_before is not None and target_now is not None
                        and (target_before.st_dev, target_before.st_ino)
                        != (target_now.st_dev, target_now.st_ino))):
                return _fail("DOCUMENT_EXPORT_FAILED")
            os.replace(temporary, path)
        finally:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
    except DocumentError:
        raise
    except OSError:
        return _fail("DOCUMENT_EXPORT_FAILED")
    return {"format": selected_format, "bytes": len(encoded)}
