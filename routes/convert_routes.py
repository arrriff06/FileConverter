# convert_routes.py
from flask import Blueprint, render_template, request, send_from_directory, send_file, current_app, jsonify
import os
import qrcode
import time
import zipfile
import random
import string

from converters.ppt_to_pdf import convert_ppt_to_pdf
from utils.file_handler import save_file
from converters.jpg_to_pdf import convert_jpg_to_pdf
from converters.pdf_to_jpg import convert_pdf_to_jpg
from converters.pdf_to_ppt import convert_pdf_to_ppt
from converters.word_to_pdf import convert_word_to_pdf
from converters.pdf_tools import merge_pdfs, split_pdf, lock_pdf, unlock_pdf
from converters.document_tools import add_page_numbers, rotate_pdf, reorder_pdf
from converters.image_tools import (
    resize_image, compress_image, crop_image,
    watermark_image, convert_image_format
)
from converters.study_tools import (
    extract_pdf_text, generate_summary, extract_key_points, generate_important_questions
)

# ---------- CREATE BLUEPRINT ----------
convert_bp = Blueprint("convert_bp", __name__)

# ---------- FILE EXPIRY TRACK ----------
file_expiry = {}

# ---------- TRANSFER FILES DB ----------
files_db = {}

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

# ---------- TRANSFER HELPERS ----------
def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ---------- TRANSFER ROUTES ----------
@convert_bp.route('/transfer/send', methods=['POST'])
def send_file_transfer():
    files = request.files.getlist('files')

    if not files or all(f.filename == '' for f in files):
        return jsonify({"error": "No files provided"}), 400

    code = generate_code()
    saved_paths = []

    for file in files:
        if file and file.filename != '':
            filename = code + "_" + file.filename
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            saved_paths.append(filepath)

    files_db[code] = {
        "paths": saved_paths,
        "time": time.time(),
        "count": len(saved_paths)
    }

    return jsonify({"code": code, "count": len(saved_paths)})


@convert_bp.route('/transfer/check/<code>', methods=['GET'])
def check_code(code):
    data = files_db.get(code.upper())
    if not data:
        return jsonify({"valid": False}), 200

    if time.time() - data["time"] > 600:
        del files_db[code.upper()]
        return jsonify({"valid": False}), 200

    return jsonify({"valid": True, "count": data["count"]}), 200


@convert_bp.route('/transfer/receive/<code>', methods=['GET'])
def receive_file_transfer(code):
    data = files_db.get(code.upper())
    if not data:
        return "Invalid or expired code", 404

    paths = data["paths"]

    if len(paths) == 1:
        return send_file(paths[0], as_attachment=True)

    zip_name = f"transfer_{code}.zip"
    zip_path = os.path.join(current_app.config["UPLOAD_FOLDER"], zip_name)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for path in paths:
            original_name = os.path.basename(path).replace(code + "_", "", 1)
            zipf.write(path, original_name)

    return send_file(zip_path, as_attachment=True, download_name=f"files_{code}.zip")

# ---------- HOME ----------
@convert_bp.route("/convert")
def home():
    return render_template("index.html")

# ---------- CONVERT ----------
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

# ---------- DOWNLOAD ----------
@convert_bp.route("/download/<filename>")
def download_file(filename):
    output_folder = current_app.config["OUTPUT_FOLDER"]
    if filename in file_expiry:
        if time.time() - file_expiry[filename] > 600:
            return "Link expired", 403
    return send_from_directory(output_folder, filename, as_attachment=True)

# ---------- VIEW ----------
@convert_bp.route("/view/<filename>")
def view_file(filename):
    output_folder = current_app.config["OUTPUT_FOLDER"]
    return send_from_directory(output_folder, filename)

# ---------- CONTACT ----------
@convert_bp.route("/contact")
def contact():
    return render_template("contact.html")


# ---------- PDF TOOLS: MERGE ----------
@convert_bp.route("/tools/merge-pdf", methods=["POST"])
def merge_pdf_route():
    output_folder = current_app.config["OUTPUT_FOLDER"]
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    files = request.files.getlist("files")
    if not files or len(files) < 2:
        return "Please upload at least 2 PDF files."

    saved_paths = []
    for file in files:
        if file and file.filename.lower().endswith(".pdf"):
            saved_paths.append(save_file(file, upload_folder))

    if len(saved_paths) < 2:
        return "Please upload valid PDF files only."

    try:
        output_path = merge_pdfs(saved_paths, output_folder)
        filename = os.path.basename(output_path)
        qr_image, download_link = generate_qr(filename)
        return render_template(
            "result.html",
            filename=filename,
            qr_image=qr_image,
            download_link=download_link
        )
    except Exception as e:
        return f"Merge failed: {str(e)}"


# ---------- PDF TOOLS: SPLIT ----------
@convert_bp.route("/tools/split-pdf", methods=["POST"])
def split_pdf_route():
    output_folder = current_app.config["OUTPUT_FOLDER"]
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    file = request.files.get("file")
    start_page = request.form.get("start_page", type=int)
    end_page = request.form.get("end_page", type=int)

    if not file or file.filename == "":
        return "Please upload a PDF file."
    if start_page is None or end_page is None:
        return "Please enter valid start and end pages."

    try:
        saved_path = save_file(file, upload_folder)
        output_path = split_pdf(saved_path, start_page, end_page, output_folder)
        filename = os.path.basename(output_path)
        qr_image, download_link = generate_qr(filename)
        return render_template(
            "result.html",
            filename=filename,
            qr_image=qr_image,
            download_link=download_link
        )
    except Exception as e:
        return f"Split failed: {str(e)}"


# ---------- PDF TOOLS: LOCK ----------
@convert_bp.route("/tools/lock-pdf", methods=["POST"])
def lock_pdf_route():
    output_folder = current_app.config["OUTPUT_FOLDER"]
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    file = request.files.get("file")
    password = request.form.get("password", "").strip()

    if not file or file.filename == "":
        return "Please upload a PDF file."
    if not password:
        return "Please enter a password."

    try:
        saved_path = save_file(file, upload_folder)
        output_path = lock_pdf(saved_path, password, output_folder)
        filename = os.path.basename(output_path)
        qr_image, download_link = generate_qr(filename)
        return render_template(
            "result.html",
            filename=filename,
            qr_image=qr_image,
            download_link=download_link
        )
    except Exception as e:
        return f"Lock failed: {str(e)}"


# ---------- PDF TOOLS: UNLOCK ----------
@convert_bp.route("/tools/unlock-pdf", methods=["POST"])
def unlock_pdf_route():
    output_folder = current_app.config["OUTPUT_FOLDER"]
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    file = request.files.get("file")
    password = request.form.get("password", "").strip()

    if not file or file.filename == "":
        return "Please upload a locked PDF file."
    if not password:
        return "Please enter password."

    try:
        saved_path = save_file(file, upload_folder)
        output_path = unlock_pdf(saved_path, password, output_folder)
        filename = os.path.basename(output_path)
        qr_image, download_link = generate_qr(filename)
        return render_template(
            "result.html",
            filename=filename,
            qr_image=qr_image,
            download_link=download_link
        )
    except Exception as e:
        return f"Unlock failed: {str(e)}"
    
    # ---------- DOCUMENT UTILITIES ----------
@convert_bp.route("/tools/add-page-numbers", methods=["POST"])
def add_page_numbers_route():
    file = request.files.get("file")
    if not file:
        return "Please upload a PDF file."

    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        output_folder = current_app.config["OUTPUT_FOLDER"]
        saved_path = save_file(file, upload_folder)

        output_path = add_page_numbers(saved_path, output_folder)
        filename = os.path.basename(output_path)
        qr_image, download_link = generate_qr(filename)

        return render_template("result.html", filename=filename, qr_image=qr_image, download_link=download_link)
    except Exception as e:
        return f"Add page numbers failed: {str(e)}"


@convert_bp.route("/tools/rotate-pdf", methods=["POST"])
def rotate_pdf_route():
    file = request.files.get("file")
    angle = request.form.get("angle", type=int)

    if not file:
        return "Please upload a PDF file."

    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        output_folder = current_app.config["OUTPUT_FOLDER"]
        saved_path = save_file(file, upload_folder)

        output_path = rotate_pdf(saved_path, angle, output_folder)
        filename = os.path.basename(output_path)
        qr_image, download_link = generate_qr(filename)

        return render_template("result.html", filename=filename, qr_image=qr_image, download_link=download_link)
    except Exception as e:
        return f"Rotate failed: {str(e)}"


@convert_bp.route("/tools/reorder-pdf", methods=["POST"])
def reorder_pdf_route():
    file = request.files.get("file")
    order_str = request.form.get("page_order", "").strip()

    if not file:
        return "Please upload a PDF file."
    if not order_str:
        return "Please enter page order like 3,1,2,4"

    try:
        page_order = [int(x.strip()) for x in order_str.split(",") if x.strip()]

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        output_folder = current_app.config["OUTPUT_FOLDER"]
        saved_path = save_file(file, upload_folder)

        output_path = reorder_pdf(saved_path, page_order, output_folder)
        filename = os.path.basename(output_path)
        qr_image, download_link = generate_qr(filename)

        return render_template("result.html", filename=filename, qr_image=qr_image, download_link=download_link)
    except Exception as e:
        return f"Reorder failed: {str(e)}"


# ---------- IMAGE TOOLS ----------
@convert_bp.route("/tools/image-resize", methods=["POST"])
def image_resize_route():
    file = request.files.get("file")
    width = request.form.get("width", type=int)
    height = request.form.get("height", type=int)

    if not file:
        return "Please upload an image."

    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        output_folder = current_app.config["OUTPUT_FOLDER"]
        saved_path = save_file(file, upload_folder)

        output_path = resize_image(saved_path, width, height, output_folder)
        filename = os.path.basename(output_path)
        qr_image, download_link = generate_qr(filename)

        return render_template("result.html", filename=filename, qr_image=qr_image, download_link=download_link)
    except Exception as e:
        return f"Resize failed: {str(e)}"


@convert_bp.route("/tools/image-compress", methods=["POST"])
def image_compress_route():
    file = request.files.get("file")
    quality = request.form.get("quality", type=int)

    if not file:
        return "Please upload an image."

    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        output_folder = current_app.config["OUTPUT_FOLDER"]
        saved_path = save_file(file, upload_folder)

        output_path = compress_image(saved_path, quality, output_folder)
        filename = os.path.basename(output_path)
        qr_image, download_link = generate_qr(filename)

        return render_template("result.html", filename=filename, qr_image=qr_image, download_link=download_link)
    except Exception as e:
        return f"Compress failed: {str(e)}"


@convert_bp.route("/tools/image-crop", methods=["POST"])
def image_crop_route():
    file = request.files.get("file")
    x = request.form.get("x", type=int)
    y = request.form.get("y", type=int)
    w = request.form.get("w", type=int)
    h = request.form.get("h", type=int)

    if not file:
        return "Please upload an image."

    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        output_folder = current_app.config["OUTPUT_FOLDER"]
        saved_path = save_file(file, upload_folder)

        output_path = crop_image(saved_path, x, y, w, h, output_folder)
        filename = os.path.basename(output_path)
        qr_image, download_link = generate_qr(filename)

        return render_template("result.html", filename=filename, qr_image=qr_image, download_link=download_link)
    except Exception as e:
        return f"Crop failed: {str(e)}"


@convert_bp.route("/tools/image-watermark", methods=["POST"])
def image_watermark_route():
    file = request.files.get("file")
    text = request.form.get("text", "").strip()

    if not file:
        return "Please upload an image."

    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        output_folder = current_app.config["OUTPUT_FOLDER"]
        saved_path = save_file(file, upload_folder)

        output_path = watermark_image(saved_path, text, output_folder)
        filename = os.path.basename(output_path)
        qr_image, download_link = generate_qr(filename)

        return render_template("result.html", filename=filename, qr_image=qr_image, download_link=download_link)
    except Exception as e:
        return f"Watermark failed: {str(e)}"


@convert_bp.route("/tools/image-convert", methods=["POST"])
def image_convert_route():
    file = request.files.get("file")
    target_format = request.form.get("target_format", "").strip()

    if not file:
        return "Please upload an image."

    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        output_folder = current_app.config["OUTPUT_FOLDER"]
        saved_path = save_file(file, upload_folder)

        output_path = convert_image_format(saved_path, target_format, output_folder)
        filename = os.path.basename(output_path)
        qr_image, download_link = generate_qr(filename)

        return render_template("result.html", filename=filename, qr_image=qr_image, download_link=download_link)
    except Exception as e:
        return f"Image convert failed: {str(e)}"


# ---------- NOTES / STUDY ----------
@convert_bp.route("/study/analyze-pdf", methods=["POST"])
def study_analyze_pdf_route():
    file = request.files.get("file")
    length = request.form.get("summary_length", "medium").strip().lower()

    if not file:
        return "Please upload a PDF file."

    length_map = {
        "short": 5,
        "medium": 8,
        "long": 12
    }
    max_sentences = length_map.get(length, 8)

    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        saved_path = save_file(file, upload_folder)

        text = extract_pdf_text(saved_path)
        summary = generate_summary(text, max_sentences=max_sentences)
        key_points = extract_key_points(text, n=10)
        questions = generate_important_questions(text, n=8)

        return render_template(
            "study_result.html",
            summary=summary,
            key_points=key_points,
            questions=questions
        )
    except Exception as e:
        return f"Study analysis failed: {str(e)}"