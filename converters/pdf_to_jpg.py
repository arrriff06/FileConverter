import fitz  # PyMuPDF
import os
import time


def convert_pdf_to_jpg(input_path, output_folder):
    # ---------- Validate ----------
    if not os.path.exists(input_path):
        raise Exception("PDF file not found")

    os.makedirs(output_folder, exist_ok=True)

    try:
        doc = fitz.open(input_path)
    except Exception:
        raise Exception("Failed to open PDF")

    output_files = []

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    timestamp = int(time.time())

    # ---------- Convert each page ----------
    for i, page in enumerate(doc):

        # High-quality render
        matrix = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=matrix)

        output_filename = f"{base_name}_page_{i+1}_{timestamp}.jpg"
        output_path = os.path.join(output_folder, output_filename)

        pix.save(output_path)

        output_files.append(output_path)

    doc.close()

    # ---------- Final check ----------
    if not output_files:
        raise Exception("PDF to JPG conversion failed")

    return output_files