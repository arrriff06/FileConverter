import fitz
from pptx import Presentation
import os
import time

def convert_pdf_to_ppt(pdf_path, output_folder):

    if not os.path.exists(pdf_path):
        raise Exception("PDF file not found")

    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)
    prs = Presentation()

    temp_images = []

    for i, page in enumerate(doc):

        pix = page.get_pixmap()
        img_path = os.path.join(output_folder, f"temp_{i}_{int(time.time())}.png")

        pix.save(img_path)
        temp_images.append(img_path)

        slide = prs.slides.add_slide(prs.slide_layouts[6])

        slide.shapes.add_picture(
            img_path,
            0,
            0,
            width=prs.slide_width
        )

    output_file = os.path.join(
        output_folder,
        f"converted_{int(time.time())}.pptx"
    )

    prs.save(output_file)

    doc.close()

    return output_file