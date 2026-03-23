from flask import Blueprint, render_template, request, send_from_directory, current_app
import os

from utils.file_handler import save_file
from converters.jpg_to_pdf import convert_jpg_to_pdf
from converters.pdf_to_jpg import convert_pdf_to_jpg
from converters.pdf_to_ppt import convert_pdf_to_ppt
from converters.ppt_to_pdf import convert_ppt_to_pdf
from converters.word_to_pdf import convert_word_to_pdf

# ✅ CREATE FIRST
convert_bp = Blueprint("convert_bp", __name__)


# ---------- Allowed File Types ----------
def allowed_file(filename):
    allowed_extensions = {
        "jpg", "jpeg", "png",
        "pdf",
        "ppt", "pptx",
        "doc", "docx"
    }
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


# ---------- Home ----------
@convert_bp.route("/convert")
def home():
    return render_template("index.html")


# ---------- Convert ----------
@convert_bp.route("/", methods=["POST"])
def convert_file():

    conversion = request.form.get("conversion")

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    output_folder = current_app.config["OUTPUT_FOLDER"]

    saved_paths = []
    files = request.files.getlist("file")

    for file in files:
        if file and file.filename != "" and allowed_file(file.filename):
            path = save_file(file, upload_folder)
            saved_paths.append(path)

    if not saved_paths:
        return "No valid file uploaded"

    try:

        if conversion == "jpg_to_pdf":
            output_path = convert_jpg_to_pdf(saved_paths, output_folder)
            filename = os.path.basename(output_path)

        elif conversion == "pdf_to_jpg":
            output_files = convert_pdf_to_jpg(saved_paths[0], output_folder)

            import zipfile
            import time

            zip_name = f"converted_{int(time.time())}.zip"
            zip_path = os.path.join(output_folder, zip_name)

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in output_files:
                    zipf.write(file, os.path.basename(file))

            filename = zip_name

        elif conversion == "pdf_to_ppt":
            output_path = convert_pdf_to_ppt(saved_paths[0], output_folder)
            filename = os.path.basename(output_path)

        elif conversion == "ppt_to_pdf":
            output_path = convert_ppt_to_pdf(saved_paths[0], output_folder)
            filename = os.path.basename(output_path)

        elif conversion == "word_to_pdf":
            output_path = convert_word_to_pdf(saved_paths[0], output_folder)
            filename = os.path.basename(output_path)

        else:
            return "Conversion not supported"

    except Exception as e:
        print("ERROR:", e)
        return f"Conversion failed: {str(e)}"

    return render_template("result.html", filename=filename)


# ---------- Download ----------
@convert_bp.route("/download/<filename>")
def download_file(filename):
    output_folder = current_app.config["OUTPUT_FOLDER"]
    return send_from_directory(output_folder, filename, as_attachment=True)


# ---------- View ----------
@convert_bp.route("/view/<filename>")
def view_file(filename):
    output_folder = current_app.config["OUTPUT_FOLDER"]
    return send_from_directory(output_folder, filename)
