import fitz  # PyMuPDF
import os
import time

def convert_pdf_to_jpg(input_path, output_folder):

    if not os.path.exists(input_path):
        raise Exception("PDF file not found")

    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(input_path)

    output_files = []

    base_name = os.path.splitext(os.path.basename(input_path))[0]

    for i, page in enumerate(doc):

        # HIGH QUALITY (important)
        matrix = fitz.Matrix(2, 2)

        pix = page.get_pixmap(matrix=matrix)

        output_file = os.path.join(
            output_folder,
            f"{base_name}_page_{i+1}_{int(time.time())}.jpg"
        )

        pix.save(output_file)

        output_files.append(output_file)

    doc.close()

    if not output_files:
        raise Exception("PDF to JPG conversion failed")

    return output_files