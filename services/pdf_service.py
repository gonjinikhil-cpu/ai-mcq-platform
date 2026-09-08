import pymupdf as fitz
import re

class PDFService:
    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes) -> dict:
        """
        Extracts text from PDF bytes with page mapping and metadata.
        Returns a dict containing total_pages, full_text, and page_chunks.
        """
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        total_pages = len(doc)
        
        page_chunks = []
        full_text = ""
        
        for i, page in enumerate(doc):
            page_num = i + 1
            text = page.get_text("text").strip()
            if text:
                # Clean up excess whitespaces
                text_clean = re.sub(r'\n+', '\n', text)
                page_chunks.append({
                    "page": page_num,
                    "text": text_clean
                })
                full_text += f"\n--- Page {page_num} ---\n" + text_clean
                
        doc.close()
        
        return {
            "total_pages": total_pages,
            "full_text": full_text.strip(),
            "page_chunks": page_chunks,
            "word_count": len(full_text.split())
        }
