# services/document_service.py

import os
from services.pdf_service import extract_text_from_pdf
from services.excel_service import extract_text_from_excel


def extract_text(file_path):
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    elif extension in [".xlsx", ".xls"]:
        return extract_text_from_excel(file_path)

    else:
        raise ValueError(f"Unsupported file type: {extension}")