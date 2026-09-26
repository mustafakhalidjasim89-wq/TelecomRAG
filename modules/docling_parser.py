import re
import tempfile
import os
from docling.document_converter import DocumentConverter

converter = DocumentConverter()

def extract_pdf_data(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        result = converter.convert(tmp_path)
        markdown_text = result.document.export_to_markdown()
        
        # Regex pattern for typical Telecom Site IDs (e.g., BAG2972, KHR0012)
        site_id_match = re.search(r'\b[A-Z]{3}\d{4}\b', markdown_text)
        site_id = site_id_match.group(0) if site_id_match else "UNKNOWN_SITE"
        
        return site_id, markdown_text
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
