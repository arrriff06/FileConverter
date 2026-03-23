import fitz
from pptx import Presentation
import os
import time

def convert_pdf_to_ppt(pdf_path, output_folder):

    doc = fitz.open(pdf_path)
    prs = Presentation()

    for page in doc:

        pix = page.get_pixmap()
        img_path = "temp_page.png"
        pix.save(img_path)

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

    return output_file