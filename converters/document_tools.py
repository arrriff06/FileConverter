import os
import time
import tempfile
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def _output_name(prefix: str, ext: str = "pdf") -> str:
    return f"{prefix}_{int(time.time())}.{ext}"


def _create_number_overlay(page_width, page_height, page_num):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp.name, pagesize=(float(page_width), float(page_height)))
    c.setFont("Helvetica", 10)
    c.drawCentredString(float(page_width) / 2, 18, str(page_num))
    c.save()
    return temp.name


def add_page_numbers(pdf_path, output_folder):
    if not os.path.exists(pdf_path):
        raise Exception("PDF file not found.")

    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    os.makedirs(output_folder, exist_ok=True)

    temp_files = []
    try:
        for i, page in enumerate(reader.pages, start=1):
            width = page.mediabox.width
            height = page.mediabox.height

            overlay_path = _create_number_overlay(width, height, i)
            temp_files.append(overlay_path)

            overlay_pdf = PdfReader(overlay_path)
            page.merge_page(overlay_pdf.pages[0])
            writer.add_page(page)

        output_path = os.path.join(output_folder, _output_name("numbered"))
        with open(output_path, "wb") as f:
            writer.write(f)

        return output_path
    finally:
        for t in temp_files:
            try:
                os.remove(t)
            except Exception:
                pass


def rotate_pdf(pdf_path, angle, output_folder):
    if not os.path.exists(pdf_path):
        raise Exception("PDF file not found.")
    if angle not in [90, 180, 270]:
        raise Exception("Angle must be 90, 180, or 270.")

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)

    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, _output_name(f"rotated_{angle}"))
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def reorder_pdf(pdf_path, page_order, output_folder):
    """
    page_order example: [3,1,2,4]
    """
    if not os.path.exists(pdf_path):
        raise Exception("PDF file not found.")

    reader = PdfReader(pdf_path)
    total = len(reader.pages)

    if not page_order:
        raise Exception("Page order is required.")

    # validate page numbers
    for p in page_order:
        if p < 1 or p > total:
            raise Exception(f"Invalid page number {p}. PDF has {total} pages.")

    writer = PdfWriter()
    for p in page_order:
        writer.add_page(reader.pages[p - 1])

    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, _output_name("reordered"))
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path