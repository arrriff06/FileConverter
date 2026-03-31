from flask import Blueprint, render_template, request, send_from_directory, current_app
import os
import qrcode
import time
import zipfile

from utils.file_handler import save_file
from converters.jpg_to_pdf import convert_jpg_to_pdf
from converters.pdf_to_jpg import convert_pdf_to_jpg
from converters.pdf_to_ppt import convert_pdf_to_ppt
from converters.ppt_to_pdf import convert_ppt_to_pdf
from converters.word_to_pdf import convert_word_to_pdf

# ---------- CREATE BLUEPRINT ----------
convert_bp = Blueprint("convert_bp", __name__)

# ---------- FILE EXPIRY TRACK ----------
file_expiry = {}

# ---------- Allowed File Types ----------
def allowed_file(filename):
    allowed_extensions = {
        "jpg", "jpeg", "png",
        "pdf",
        "ppt", "pptx",
        "doc", "docx"
    }
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

# ---------- QR GENERATOR ----------
def generate_qr(filename):
    base_url = request.host_url.rstrip("/")
    download_link = f"{base_url}/convert/download/{filename}"

    qr_folder = os.path.join("static", "qr")
    os.makedirs(qr_folder, exist_ok=True)

    qr_path = os.path.join(qr_folder, f"{filename}.png")
    qrcode.make(download_link).save(qr_path)

    file_expiry[filename] = time.time()

    return f"qr/{filename}.png", download_link

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

    # ---------- Save Files ----------
    for file in files:
        if file and file.filename != "" and allowed_file(file.filename):
            result = save_file(file, upload_folder)

            # ✅ HANDLE tuple or string (SAFE)
            if isinstance(result, tuple):
                path = result[0]
            else:
                path = result

            saved_paths.append(path)

    if not saved_paths:
        return "No valid file uploaded"

    try:

        # ---------- JPG → PDF ----------
        if conversion == "jpg_to_pdf":
            output_path = convert_jpg_to_pdf(saved_paths, output_folder)
            filename = os.path.basename(output_path)

        # ---------- PDF → JPG ----------
        elif conversion == "pdf_to_jpg":
            output_files = convert_pdf_to_jpg(saved_paths[0], output_folder)

            zip_name = f"converted_{int(time.time())}.zip"
            zip_path = os.path.join(output_folder, zip_name)

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in output_files:
                    zipf.write(file, os.path.basename(file))

            filename = zip_name

            return render_template(
                "result.html",
                files=[os.path.basename(f) for f in output_files],
                filename=filename,
                qr_image=generate_qr(filename)[0],
                download_link=generate_qr(filename)[1]
            )

        # ---------- PDF → PPT ----------
        elif conversion == "pdf_to_ppt":
            output_path = convert_pdf_to_ppt(saved_paths[0], output_folder)
            filename = os.path.basename(output_path)

        # ---------- PPT → PDF ----------
        elif conversion == "ppt_to_pdf":
            output_path = convert_ppt_to_pdf(saved_paths[0], output_folder)
            filename = os.path.basename(output_path)

        # ---------- WORD → PDF ----------
        elif conversion == "word_to_pdf":
            output_path = convert_word_to_pdf(saved_paths[0], output_folder)
            filename = os.path.basename(output_path)

        else:
            return "Conversion not supported"

        # ---------- COMMON RESULT ----------
        qr_image, download_link = generate_qr(filename)

        return render_template(
            "result.html",
            filename=filename,
            qr_image=qr_image,
            download_link=download_link
        )

    except Exception as e:
        print("ERROR:", e)
        return f"Conversion failed: {str(e)}"

# ---------- Download ----------
@convert_bp.route("/download/<filename>")
def download_file(filename):
    output_folder = current_app.config["OUTPUT_FOLDER"]

    # Expiry check
    if filename in file_expiry:
        if time.time() - file_expiry[filename] > 600:
            return "Link expired", 403

    return send_from_directory(output_folder, filename, as_attachment=True)

# ---------- View ----------
@convert_bp.route("/view/<filename>")
def view_file(filename):
    output_folder = current_app.config["OUTPUT_FOLDER"]
    return send_from_directory(output_folder, filename)

# ---------- Contact ----------
@convert_bp.route("/contact")
def contact():
    return render_template("contact.html")