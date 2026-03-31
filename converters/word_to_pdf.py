import subprocess
import os
import shutil


def convert_word_to_pdf(doc_path, output_folder):
    try:
        doc_path = os.path.abspath(doc_path)
        output_folder = os.path.abspath(output_folder)

        if not os.path.exists(doc_path):
            raise Exception("File not found")

        os.makedirs(output_folder, exist_ok=True)

        # Auto-detect LibreOffice
        soffice_path = shutil.which("soffice") or r"C:\Program Files\LibreOffice\program\soffice.exe"

        if not os.path.exists(soffice_path):
            raise Exception("LibreOffice not installed")

        command = [
            soffice_path,
            "--headless",
            "--convert-to", "pdf",
            doc_path,
            "--outdir", output_folder
        ]

        result = subprocess.run(command)

        base_name = os.path.splitext(os.path.basename(doc_path))[0]
        output_file = os.path.join(output_folder, base_name + ".pdf")

        if result.returncode != 0 or not os.path.exists(output_file):
            raise Exception("Conversion failed")

        return output_file

    except Exception as e:
        raise Exception(f"Word to PDF conversion failed: {str(e)}")