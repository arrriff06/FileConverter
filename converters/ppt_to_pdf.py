import subprocess
import os
import shutil


def convert_ppt_to_pdf(ppt_path, output_folder):
    try:
        ppt_path = os.path.abspath(ppt_path)
        output_folder = os.path.abspath(output_folder)

        os.makedirs(output_folder, exist_ok=True)

        # Auto-detect LibreOffice
        soffice_path = shutil.which("soffice") or r"C:\Program Files\LibreOffice\program\soffice.exe"

        if not os.path.exists(soffice_path):
            raise Exception("LibreOffice not found")

        command = [
            soffice_path,
            "--headless",
            "--convert-to", "pdf",
            ppt_path,
            "--outdir", output_folder
        ]

        result = subprocess.run(command)

        base_name = os.path.splitext(os.path.basename(ppt_path))[0]
        output_file = os.path.join(output_folder, base_name + ".pdf")

        if result.returncode != 0 or not os.path.exists(output_file):
            raise Exception("Conversion failed")

        return output_file

    except Exception as e:
        raise Exception(f"PPT to PDF conversion failed: {str(e)}")