"""
Document processing pipeline: PDF → chunks → FAISS vectorstore.
Uses backend2's rag/ classes. OCR fallback for scanned PDFs via RapidOCR.
"""
import fitz
from pathlib import Path
from langchain_core.documents import Document
from starlette.concurrency import run_in_threadpool

from rag import embed_instance
from rag.pdf_processor import PDFProcessor
from rag.vector_store import VectorStoreManager
import config
from features.documents.service import DocumentService


def _ocr_page(page: fitz.Page) -> str:
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    pix = page.get_pixmap(dpi=300)
    result, _ = ocr(pix.tobytes("png"))
    return "\n".join(line[1] for line in result) if result else ""


def _load_with_ocr_fallback(file_path: str) -> list[Document]:
    doc = fitz.open(file_path)
    pages: list[Document] = []
    for page_num, page in enumerate(doc):
        native_text = page.get_text().strip()
        text = native_text if len(native_text) >= 50 else _ocr_page(page)
        if text:
            pages.append(Document(page_content=text, metadata={"source": file_path, "page": page_num + 1}))
    doc.close()
    return pages


class DocumentPipeline:

    def __init__(self):
        self._processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
        self._svc = DocumentService()

    def _extract_and_index(self, file_path: str, vector_id: str) -> int:
        raw_pages = _load_with_ocr_fallback(file_path)
        if not raw_pages:
            raise ValueError("No text could be extracted from the document (even with OCR).")

        chunks = self._processor.chunk_documents(raw_pages)
        if not chunks:
            raise ValueError("Document produced 0 text chunks — may be empty or image-only.")

        store_path = str(config.VECTORSTORES_DIR / vector_id)
        store = VectorStoreManager(embedding_manager=embed_instance, store_path=store_path)
        store.create_vector_store(chunks)
        store.save_vector_store()
        return len(raw_pages)

    async def run(self, doc_id: str, user_id: str, file_path: str, vector_id: str):
        try:
            await self._svc.update_status(doc_id, "PROCESSING", "Extracting text (OCR fallback enabled)…")
            page_count = await run_in_threadpool(self._extract_and_index, file_path, vector_id)
            await self._svc.mark_completed(doc_id, page_count)
        except Exception as exc:
            await self._svc.mark_failed(doc_id, str(exc))
