from pathlib import Path


class PdfReaderError(Exception):
    pass


def _load_reader(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader
        except ImportError as exc:
            raise PdfReaderError("Install pypdf or PyPDF2 to enable PDF reading.") from exc

    pdf_path = Path(path).expanduser()
    if not pdf_path.exists():
        raise PdfReaderError(f"PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise PdfReaderError("That file is not a PDF.")

    return pdf_path, PdfReader(str(pdf_path))


def open_pdf(path):
    pdf_path, reader = _load_reader(path)
    return {
        "current_file": str(pdf_path),
        "current_page": 1,
        "page_count": len(reader.pages),
    }


def read_page(path, page_number):
    pdf_path, reader = _load_reader(path)
    page_count = len(reader.pages)
    if page_number < 1 or page_number > page_count:
        raise PdfReaderError(f"Page must be between 1 and {page_count}.")

    text = reader.pages[page_number - 1].extract_text() or ""
    text = " ".join(text.split())
    if not text:
        return f"Page {page_number} has no extractable text. It may be scanned or image-based."
    return text


def get_current_pdf(memory):
    pdf = memory.get("pdf", {})
    current_file = pdf.get("current_file")
    if not current_file:
        raise PdfReaderError("No PDF is open. Use /pdf open <path> first.")
    return current_file
