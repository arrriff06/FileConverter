import subprocess
import os

def convert_word_to_pdf(doc_path, output_folder):
    try:
        doc_path = os.path.abspath(doc_path)
        output_folder = os.path.abspath(output_folder)

        if not os.path.exists(doc_path):
            raise Exception("File not found")

        os.makedirs(output_folder, exist_ok=True)

        # ✅ FIX: use full path for LibreOffice
        subprocess.run([
            "/usr/bin/soffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_folder,
            doc_path
        ], check=True)

        base_name = os.path.splitext(os.path.basename(doc_path))[0]
        output_file = os.path.join(output_folder, base_name + ".pdf")

        if not os.path.exists(output_file):
            raise Exception("Conversion failed: output file not found")

        return output_file

    except Exception as e:
        raise Exception(f"Word to PDF conversion failed: {str(e)}")