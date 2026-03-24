import subprocess
import os

def convert_ppt_to_pdf(ppt_path, output_folder):
    try:
        ppt_path = os.path.abspath(ppt_path)
        output_folder = os.path.abspath(output_folder)

        os.makedirs(output_folder, exist_ok=True)

        # ✅ Correct path for Windows LibreOffice
        soffice_path = r"C:\Program Files\LibreOffice\program\soffice.exe"

        if not os.path.exists(soffice_path):
            raise Exception("LibreOffice not found. Please install it.")

        subprocess.run([
            soffice_path,
            "--headless",
            "--convert-to", "pdf",
            ppt_path,
            "--outdir", output_folder
        ], check=True)

        base_name = os.path.splitext(os.path.basename(ppt_path))[0]
        output_file = os.path.join(output_folder, base_name + ".pdf")

        if not os.path.exists(output_file):
            raise Exception("Output file not created")

        return output_file

    except Exception as e:
        raise Exception(f"PPT to PDF conversion failed: {str(e)}")