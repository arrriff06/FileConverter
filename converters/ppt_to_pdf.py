import subprocess
import os
import time

def convert_ppt_to_pdf(ppt_path, output_folder):
    try:
        ppt_path = os.path.abspath(ppt_path)
        output_folder = os.path.abspath(output_folder)

        if not os.path.exists(ppt_path):
            raise Exception("PPT file not found")

        os.makedirs(output_folder, exist_ok=True)

        # Run LibreOffice conversion
        subprocess.run([
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            ppt_path,
            "--outdir", output_folder
        ], check=True)

        # Find generated file
        base_name = os.path.splitext(os.path.basename(ppt_path))[0]
        output_file = os.path.join(output_folder, base_name + ".pdf")

        if not os.path.exists(output_file):
            raise Exception("Conversion failed: output file not found")

        return output_file

    except Exception as e:
        raise Exception(f"PPT to PDF conversion failed: {str(e)}")