"""Local text-document format and atomic output boundaries."""

import os
from pathlib import Path

import pytest

from personalstyle import documents
from personalstyle.documents import DocumentError, export_document, import_document
from personalstyle.storage import MAX_TEXT_BYTES


@pytest.mark.parametrize("suffix", ["txt", "md"])
def test_import_preserves_utf8_paragraphs_and_unicode(tmp_path, suffix):
    source = tmp_path / f"source.{suffix}"
    source.write_bytes("\ufeffHeading — Καλημέρα\r\n\r\nSecond paragraph.\n".encode("utf-8"))

    result = import_document(str(source), suffix)

    assert result == {
        "document_id": str(documents.uuid5(
            documents._DOCUMENT_NAMESPACE, str(source.resolve()).casefold(),
        )),
        "format": suffix,
        "text": "Heading — Καλημέρα\r\n\r\nSecond paragraph.\n",
        "bytes": source.stat().st_size,
    }


@pytest.mark.parametrize(
    ("name", "data", "format_name", "code"),
    [
        ("empty.txt", b"", "txt", "DOCUMENT_EMPTY"),
        ("binary.md", b"hello\0world", "md", "DOCUMENT_MALFORMED"),
        ("invalid.txt", b"\xff", "txt", "DOCUMENT_MALFORMED"),
        ("wrong.txt", b"text", "md", "DOCUMENT_EXTENSION_MISMATCH"),
        ("large.txt", None, "txt", "DOCUMENT_RESOURCE_LIMIT"),
        ("unsupported.pdf", b"%PDF", "pdf", "DOCUMENT_FORMAT_UNSUPPORTED"),
    ],
)
def test_import_rejects_invalid_or_unsupported_files(tmp_path, name, data, format_name, code):
    source = tmp_path / name
    source.write_bytes(b"x" * (MAX_TEXT_BYTES + 1) if data is None else data)

    with pytest.raises(DocumentError, match=f"^{code}$"):
        import_document(str(source), format_name)


def test_import_rejects_traversal_path_before_open(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("text", encoding="utf-8")
    traversal = str(source.parent / ".." / source.name)

    with pytest.raises(DocumentError, match="^DOCUMENT_PATH_INVALID$"):
        import_document(traversal, "txt")


def test_export_preserves_text_and_atomically_replaces_target(tmp_path):
    target = tmp_path / "result.md"
    target.write_text("old result", encoding="utf-8")

    result = export_document(str(target), "md", "# Title\n\nπ paragraph\n")

    assert result == {"format": "md", "bytes": len("# Title\n\nπ paragraph\n".encode())}
    assert target.read_bytes().decode("utf-8") == "# Title\n\nπ paragraph\n"
    assert list(tmp_path.glob(".personalstyle-*.tmp")) == []


def test_export_failure_preserves_existing_file_and_cleans_temp(tmp_path, monkeypatch):
    target = tmp_path / "result.txt"
    target.write_text("prior", encoding="utf-8")

    def fail_replace(source: os.PathLike[str] | str, destination: os.PathLike[str] | str) -> None:
        raise OSError("synthetic replacement failure")

    monkeypatch.setattr(documents.os, "replace", fail_replace)
    with pytest.raises(DocumentError, match="^DOCUMENT_EXPORT_FAILED$"):
        export_document(str(target), "txt", "new output")

    assert target.read_text(encoding="utf-8") == "prior"
    assert list(tmp_path.glob(".personalstyle-*.tmp")) == []


@pytest.mark.parametrize(
    ("name", "format_name", "text", "code"),
    [
        ("result.txt", "md", "text", "DOCUMENT_EXTENSION_MISMATCH"),
        ("result.exe", "exe", "text", "DOCUMENT_FORMAT_UNSUPPORTED"),
        ("result.txt", "txt", None, "DOCUMENT_RESOURCE_LIMIT"),
        ("result.txt", "txt", "contains\0nul", "DOCUMENT_MALFORMED"),
    ],
)
def test_export_rejects_invalid_values_before_creating_output(tmp_path, name, format_name, text, code):
    target = tmp_path / name
    value = "x" * (MAX_TEXT_BYTES + 1) if text is None else text

    with pytest.raises(DocumentError, match=f"^{code}$"):
        export_document(str(target), format_name, value)

    assert not target.exists()
    assert list(tmp_path.glob(".personalstyle-*.tmp")) == []


def test_import_rejects_reparse_target(tmp_path, monkeypatch):
    source = tmp_path / "source.txt"
    source.write_text("text", encoding="utf-8")
    original = Path.lstat

    def reparse_target(path: Path):
        metadata = original(path)
        if path == source:
            return type("Metadata", (), {
                "st_mode": metadata.st_mode,
                "st_size": metadata.st_size,
                "st_dev": metadata.st_dev,
                "st_ino": metadata.st_ino,
                "st_file_attributes": documents._REPARSE_POINT,
            })()
        return metadata

    monkeypatch.setattr(Path, "lstat", reparse_target)
    with pytest.raises(DocumentError, match="^DOCUMENT_PATH_INVALID$"):
        import_document(str(source), "txt")
