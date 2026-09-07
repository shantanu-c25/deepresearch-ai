from io import BytesIO

import pytest
from docx import Document as DocxDocument
from openpyxl import Workbook

from backend.rag.uploaded_loader import DocumentLoadError, UploadedDocumentLoader


def make_pdf() -> bytes:
    objects = [
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>endobj\n",
        b"4 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n",
        b"5 0 obj<< /Length 47 >>stream\nBT /F1 12 Tf 20 100 Td (Uploaded PDF evidence) Tj ET\nendstream\nendobj\n",
    ]
    header = b"%PDF-1.4\n"
    body = header + b"".join(objects)
    offsets = [0]
    position = len(header)
    for obj in objects:
        offsets.append(position)
        position += len(obj)
    xref = position
    trailer = (
        b"xref\n0 6\n0000000000 65535 f \n"
        + b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:])
        + b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
        + str(xref).encode()
        + b"\n%%EOF"
    )
    return body + trailer


def make_docx() -> bytes:
    document = DocxDocument()
    document.add_paragraph("Uploaded DOCX evidence")
    table = document.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Topic"
    table.cell(0, 1).text = "Value"
    table.cell(1, 0).text = "Status"
    table.cell(1, 1).text = "Ready"
    output = BytesIO()
    document.save(output)
    return output.getvalue()


def make_xlsx() -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Research"
    sheet.append(["Company", "Year"])
    sheet.append(["OpenAI", 2026])
    second_sheet = workbook.create_sheet("Empty")
    second_sheet["A1"] = ""
    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


@pytest.mark.parametrize(
    ("filename", "data", "expected"),
    [
        ("notes.txt", b"Plain text evidence", "Plain text evidence"),
        ("notes.md", b"# Markdown\n\nMarkdown evidence", "# Markdown\n\nMarkdown evidence"),
        ("notes.markdown", b"Markdown extension evidence", "Markdown extension evidence"),
        ("rows.csv", b"Company,Revenue\nOpenAI,100", "Company: OpenAI | Revenue: 100"),
        ("sheet.xlsx", make_xlsx(), "Company: OpenAI | Year: 2026"),
        ("report.docx", make_docx(), "Uploaded DOCX evidence"),
        ("report.pdf", make_pdf(), "Uploaded PDF evidence"),
    ],
    ids=["txt", "md", "markdown", "csv", "xlsx", "docx", "pdf"],
)
def test_supported_files_are_loaded_with_readable_content(filename, data, expected):
    uploaded = UploadedDocumentLoader().load(data, filename, "application/octet-stream")

    assert expected in uploaded.document.content
    assert uploaded.document.metadata["source_type"] == "uploaded_document"
    assert uploaded.document.metadata["filename"] == filename
    assert uploaded.document.source_url.startswith("uploaded://")
    assert uploaded.section_count >= 1


def test_loader_rejects_empty_unsupported_and_invalid_text_files():
    loader = UploadedDocumentLoader()

    with pytest.raises(DocumentLoadError, match="empty"):
        loader.load(b"", "empty.txt")
    with pytest.raises(DocumentLoadError, match="unsupported"):
        loader.load(b"content", "script.exe")
    with pytest.raises(DocumentLoadError, match="UTF-8"):
        loader.load(b"\xff\xfe", "invalid.txt")


def test_loader_rejects_corrupt_structured_files():
    loader = UploadedDocumentLoader()

    with pytest.raises(DocumentLoadError, match="could not read"):
        loader.load(b"not a pdf", "broken.pdf")
    with pytest.raises(DocumentLoadError, match="could not read"):
        loader.load(b"not a workbook", "broken.xlsx")