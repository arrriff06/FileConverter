import fitz
import os

def convert_pdf_to_jpg(input_path, output_folder):

    doc = fitz.open(input_path)

    filename = os.path.splitext(os.path.basename(input_path))[0]

    output_file = os.path.join(output_folder, filename + ".jpg")

    page = doc.load_page(0)

    pix = page.get_pixmap()

    pix.save(output_file)

    doc.close()

    return output_file