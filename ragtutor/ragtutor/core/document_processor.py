from io import BytesIO
from typing import Dict, List
from uuid import uuid4

from pypdf import PdfReader

from ..config.settings import settings
from ..exceptions.rag_exceptions import RAGDocumentError


def _split_text_with_overlap(text: str, chunk_size: int, overlap: int) -> List[str]:
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start = max(end - overlap, 0)
    return chunks


def process_pdf_document(filename: str, content: bytes) -> Dict[str, object]:
    """Extract text from PDF, split into chunks, and attach metadata."""
    try:
        reader = PdfReader(BytesIO(content))
        document_id = str(uuid4())
        all_chunks: List[Dict[str, object]] = []

        print(f"DEBUG: PDF {filename} has {len(reader.pages)} pages")

        for page_index, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""
                print(f"DEBUG: Failed to extract text from page {page_index}: {e}")

            if not page_text.strip():
                print(f"DEBUG: Page {page_index} has no extractable text")
                continue

            chunks = _split_text_with_overlap(
                page_text, settings.chunk_size, settings.chunk_overlap
            )

            if not chunks:
                print(f"DEBUG: Page {page_index} produced 0 chunks with "
                      f"chunk_size={settings.chunk_size}, overlap={settings.chunk_overlap}")

            for chunk_text in chunks:
                chunk_id = str(uuid4())
                all_chunks.append(
                    {
                        "id": chunk_id,
                        "text": chunk_text,
                        "metadata": {
                            "document_id": document_id,
                            "filename": filename,
                            "page": page_index,
                        },
                    }
                )

        print(f"DEBUG: Total chunks created from {filename}: {len(all_chunks)}")
        return {"document_id": document_id, "chunks": all_chunks}
    except Exception as exc:
        raise RAGDocumentError("Failed to process PDF document", {"filename": filename}) from exc
