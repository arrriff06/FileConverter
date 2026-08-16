import os
import time
from pypdf import PdfReader, PdfWriter


def _timestamp_name(prefix="converted", ext="pdf"):
    return f"{prefix}_{int(time.time())}.{ext}"


def merge_pdfs(file_paths, output_folder):
    if not file_paths or len(file_paths) < 2:
        raise Exception("Please upload at least 2 PDF files to merge.")

    os.makedirs(output_folder, exist_ok=True)

    writer = PdfWriter()

    for path in file_paths:
        if not os.path.exists(path):
            raise Exception(f"File not found: {path}")
        if not path.lower().endswith(".pdf"):
            raise Exception("Only PDF files are allowed for merge.")

        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)

    output_filename = _timestamp_name(prefix="merged", ext="pdf")
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def split_pdf(input_path, start_page, end_page, output_folder):
    if not os.path.exists(input_path):
        raise Exception("PDF file not found.")
    if not input_path.lower().endswith(".pdf"):
        raise Exception("Only PDF file is allowed for split.")

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    if start_page < 1 or end_page < 1:
        raise Exception("Page numbers must be >= 1.")
    if start_page > end_page:
        raise Exception("Start page must be less than or equal to end page.")
    if end_page > total_pages:
        raise Exception(f"PDF has only {total_pages} page(s).")

    writer = PdfWriter()
    for i in range(start_page - 1, end_page):
        writer.add_page(reader.pages[i])

    os.makedirs(output_folder, exist_ok=True)
    output_filename = _timestamp_name(prefix="split", ext="pdf")
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def lock_pdf(input_path, password, output_folder):
    if not os.path.exists(input_path):
        raise Exception("PDF file not found.")
    if not password:
        raise Exception("Password is required.")
    if not input_path.lower().endswith(".pdf"):
        raise Exception("Only PDF file is allowed for lock.")

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    os.makedirs(output_folder, exist_ok=True)
    output_filename = _timestamp_name(prefix="locked", ext="pdf")
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def unlock_pdf(input_path, password, output_folder):
    if not os.path.exists(input_path):
        raise Exception("PDF file not found.")
    if not password:
        raise Exception("Password is required.")
    if not input_path.lower().endswith(".pdf"):
        raise Exception("Only PDF file is allowed for unlock.")

    reader = PdfReader(input_path)

    if not reader.is_encrypted:
        raise Exception("This PDF is not password-protected.")

    decrypt_status = reader.decrypt(password)
    if decrypt_status == 0:
        raise Exception("Wrong password. Could not unlock PDF.")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    os.makedirs(output_folder, exist_ok=True)
    output_filename = _timestamp_name(prefix="unlocked", ext="pdf")
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path