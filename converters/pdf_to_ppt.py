import subprocess
import os
import shutil
import fitz
from pptx import Presentation
import time


def convert_pdf_to_ppt(pdf_path, output_folder):
    try:
        pdf_path = os.path.abspath(pdf_path)
        output_folder = os.path.abspath(output_folder)

        os.makedirs(output_folder, exist_ok=True)

        # ===== Try LibreOffice =====
        soffice_path = shutil.which("soffice") or r"C:\Program Files\LibreOffice\program\soffice.exe"

        if os.path.exists(soffice_path):
            command = [
                soffice_path,
                "--headless",
                "--convert-to", "pptx",
                pdf_path,
                "--outdir", output_folder
            ]

            result = subprocess.run(command)

            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_file = os.path.join(output_folder, base_name + ".pptx")

            if result.returncode == 0 and os.path.exists(output_file):
                return output_file

        print("LibreOffice failed → using fallback")

        # ===== Fallback: Image-based PPT =====
        doc = fitz.open(pdf_path)
        prs = Presentation()

        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            img_path = os.path.join(output_folder, f"temp_{i}_{int(time.time())}.png")
            pix.save(img_path)

            slide = prs.slides.add_slide(prs.slide_layouts[6])
            slide.shapes.add_picture(img_path, 0, 0, width=prs.slide_width)

        output_file = os.path.join(output_folder, f"converted_{int(time.time())}.pptx")
        prs.save(output_file)

        doc.close()

        return output_file

    except Exception as e:
        raise Exception(f"PDF to PPT conversion failed: {str(e)}")