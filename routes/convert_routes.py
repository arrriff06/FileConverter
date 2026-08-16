# convert_routes.py

from flask import (
    Blueprint,
    render_template,
    request,
    send_from_directory,
    send_file,
    current_app,
    jsonify
)

import os
import time
import zipfile
import random
import string
import qrcode

from werkzeug.utils import secure_filename

from utils.file_handler import save_file

from converters.ppt_to_pdf import convert_ppt_to_pdf
from converters.jpg_to_pdf import convert_jpg_to_pdf
from converters.pdf_to_jpg import convert_pdf_to_jpg
from converters.pdf_to_ppt import convert_pdf_to_ppt
from converters.word_to_pdf import convert_word_to_pdf

from converters.study_tools import (
    extract_pdf_text,
    generate_summary,
    extract_key_points,
    generate_important_questions
)


# =========================================================
# BLUEPRINT
# =========================================================

convert_bp = Blueprint("convert_bp", __name__)


# =========================================================
# GLOBAL STORAGE
# =========================================================

# Generated conversion files and their expiry time
file_expiry = {}

# Temporary file-transfer records
files_db = {}

# Temporary text/code rooms
rooms_db = {}


# =========================================================
# CONFIGURATION
# =========================================================

ROOM_EXPIRY = 60 * 60          # 1 hour
TRANSFER_EXPIRY = 10 * 60       # 10 minutes
DOWNLOAD_EXPIRY = 10 * 60       # 10 minutes

MAX_CONTENT_LENGTH = 500_000    # 500 KB


# =========================================================
# ALLOWED FILE TYPES
# =========================================================

ALLOWED_CONVERSION_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "pdf",
    "ppt",
    "pptx",
    "doc",
    "docx"
}


ALLOWED_TRANSFER_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp",
    "pdf",
    "ppt",
    "pptx",
    "doc",
    "docx",
    "mp4",
    "mov",
    "avi",
    "mkv",
    "webm"
}


def allowed_file(filename):
    """
    Check whether a filename is allowed for the main converter.
    """

    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_CONVERSION_EXTENSIONS


def allowed_transfer_file(filename):
    """
    Check whether a filename is allowed for file transfer.
    """

    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_TRANSFER_EXTENSIONS


# =========================================================
# HELPER: RANDOM CODE
# =========================================================

def generate_code(length=6):
    """
    Generate a random uppercase alphanumeric code.
    """

    return "".join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=length
        )
    )


# =========================================================
# TEXT & CODE ROOM SYSTEM
# =========================================================

ROOM_EXPIRY = 60 * 60          # 1 hour
MAX_CONTENT_LENGTH = 500_000   # 500 KB

rooms_db = {}


def generate_room_code():
    """Generate a unique 6-character room code."""

    while True:
        code = "".join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )

        if code not in rooms_db:
            return code


def cleanup_rooms():
    """Remove rooms older than 1 hour."""

    current_time = time.time()

    expired_rooms = [
        code
        for code, room in rooms_db.items()
        if current_time - room["created_at"] > ROOM_EXPIRY
    ]

    for code in expired_rooms:
        rooms_db.pop(code, None)


# =========================================================
# CREATE ROOM WITH CONTENT
# =========================================================

@convert_bp.route("/room/create", methods=["POST"])
def create_room():

    cleanup_rooms()

    data = request.get_json(silent=True) or {}

    content = data.get("content", "")
    content_type = data.get("type", "text")

    # Validate content
    if not isinstance(content, str):
        return jsonify({
            "success": False,
            "error": "Invalid content."
        }), 400

    content = content.strip()

    # Content cannot be empty
    if not content:
        return jsonify({
            "success": False,
            "error": "Please paste some text or code first."
        }), 400

    # Maximum size
    if len(content) > MAX_CONTENT_LENGTH:
        return jsonify({
            "success": False,
            "error": "Content is too large. Maximum size is 500 KB."
        }), 413

    # Validate type
    if content_type not in ("text", "code"):
        content_type = "text"

    code = generate_room_code()

    rooms_db[code] = {
        "content": content,
        "type": content_type,
        "created_at": time.time()
    }

    return jsonify({
        "success": True,
        "code": code,
        "content": content,
        "type": content_type
    })


# =========================================================
# GET ROOM
# =========================================================

@convert_bp.route("/room/<code>", methods=["GET"])
def get_room(code):

    cleanup_rooms()

    code = code.upper().strip()

    room = rooms_db.get(code)

    if not room:
        return jsonify({
            "success": False,
            "error": "Room not found or expired."
        }), 404

    return jsonify({
        "success": True,
        "code": code,
        "content": room["content"],
        "type": room["type"]
    })


# =========================================================
# UPDATE ROOM
# =========================================================

@convert_bp.route("/room/<code>/update", methods=["POST"])
def update_room(code):

    cleanup_rooms()

    code = code.upper().strip()

    room = rooms_db.get(code)

    if not room:
        return jsonify({
            "success": False,
            "error": "Room not found or expired."
        }), 404

    data = request.get_json(silent=True) or {}

    content = data.get("content", "")
    content_type = data.get("type", "text")

    if not isinstance(content, str):
        return jsonify({
            "success": False,
            "error": "Invalid content."
        }), 400

    if len(content) > MAX_CONTENT_LENGTH:
        return jsonify({
            "success": False,
            "error": "Content is too large. Maximum size is 500 KB."
        }), 413

    if content_type not in ("text", "code"):
        content_type = "text"

    room["content"] = content
    room["type"] = content_type

    return jsonify({
        "success": True
    })


# =========================================================
# DELETE ROOM
# =========================================================

@convert_bp.route("/room/<code>", methods=["DELETE"])
def delete_room(code):

    code = code.upper().strip()

    rooms_db.pop(code, None)

    return jsonify({
        "success": True
    })

# =========================================================
# QR CODE GENERATOR
# =========================================================

def generate_qr(filename):
    """
    Generate a QR code for a converted file.
    """

    base_url = request.host_url.rstrip("/")

    download_link = (
        f"{base_url}/convert/download/{filename}"
    )

    qr_folder = os.path.join(
        current_app.root_path,
        "static",
        "qr"
    )

    os.makedirs(
        qr_folder,
        exist_ok=True
    )

    safe_filename = secure_filename(filename)

    qr_filename = f"{safe_filename}.png"

    qr_path = os.path.join(
        qr_folder,
        qr_filename
    )

    qrcode.make(download_link).save(qr_path)

    file_expiry[filename] = time.time()

    return (
        f"qr/{qr_filename}",
        download_link
    )


# =========================================================
# FILE TRANSFER
# =========================================================

@convert_bp.route("/transfer/send", methods=["POST"])
def send_file_transfer():

    files = request.files.getlist("files")

    if not files or all(
        not file or file.filename == ""
        for file in files
    ):

        return jsonify({
            "error": "No files provided"
        }), 400

    code = generate_code()

    saved_paths = []

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    for file in files:

        if not file or not file.filename:
            continue

        original_filename = secure_filename(
            file.filename
        )

        if not allowed_transfer_file(
            original_filename
        ):
            continue

        filename = (
            f"{code}_{original_filename}"
        )

        filepath = os.path.join(
            upload_folder,
            filename
        )

        file.save(filepath)

        saved_paths.append(filepath)

    if not saved_paths:

        return jsonify({
            "error": "No valid files provided."
        }), 400

    files_db[code] = {
        "paths": saved_paths,
        "time": time.time(),
        "count": len(saved_paths)
    }

    return jsonify({
        "code": code,
        "count": len(saved_paths)
    })


# =========================================================
# CHECK TRANSFER CODE
# =========================================================

@convert_bp.route("/transfer/check/<code>", methods=["GET"])
def check_code(code):

    code = code.upper().strip()

    data = files_db.get(code)

    if not data:

        return jsonify({
            "valid": False
        })

    if time.time() - data["time"] > TRANSFER_EXPIRY:

        files_db.pop(code, None)

        return jsonify({
            "valid": False
        })

    return jsonify({
        "valid": True,
        "count": data["count"]
    })


# =========================================================
# RECEIVE TRANSFER FILE
# =========================================================

@convert_bp.route("/transfer/receive/<code>", methods=["GET"])
def receive_file_transfer(code):

    code = code.upper().strip()

    data = files_db.get(code)

    if not data:

        return "Invalid or expired code.", 404

    if time.time() - data["time"] > TRANSFER_EXPIRY:

        files_db.pop(code, None)

        return "Transfer code expired.", 404

    paths = data["paths"]

    # Single file
    if len(paths) == 1:

        path = paths[0]

        if not os.path.exists(path):
            return "File no longer exists.", 404

        return send_file(
            path,
            as_attachment=True
        )

    # Multiple files
    upload_folder = current_app.config[
        "UPLOAD_FOLDER"
    ]

    zip_name = f"files_{code}.zip"

    zip_path = os.path.join(
        upload_folder,
        zip_name
    )

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for path in paths:

            if not os.path.exists(path):
                continue

            original_name = os.path.basename(
                path
            )

            prefix = f"{code}_"

            if original_name.startswith(prefix):
                original_name = original_name[
                    len(prefix):
                ]

            zipf.write(
                path,
                original_name
            )

    return send_file(
        zip_path,
        as_attachment=True,
        download_name=zip_name
    )


# =========================================================
# HOME / MAIN CONVERTER PAGE
# =========================================================

@convert_bp.route("/", methods=["GET"])
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# MAIN FILE CONVERTER
# =========================================================

@convert_bp.route("/", methods=["POST"])
def convert_file():

    conversion = request.form.get(
        "conversion",
        ""
    ).strip()

    upload_folder = current_app.config[
        "UPLOAD_FOLDER"
    ]

    output_folder = current_app.config[
        "OUTPUT_FOLDER"
    ]

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Validate conversion type
    # -----------------------------------------------------

    supported_conversions = {
        "jpg_to_pdf",
        "pdf_to_jpg",
        "pdf_to_ppt",
        "ppt_to_pdf",
        "word_to_pdf"
    }

    if conversion not in supported_conversions:

        return (
            "Please select a valid conversion type.",
            400
        )

    # -----------------------------------------------------
    # Get uploaded files
    # -----------------------------------------------------

    files = request.files.getlist(
        "file"
    )

    if not files:

        return (
            "No file uploaded.",
            400
        )

    saved_paths = []

    # -----------------------------------------------------
    # Save valid files
    # -----------------------------------------------------

    for file in files:

        if not file:
            continue

        if not file.filename:
            continue

        if not allowed_file(
            file.filename
        ):
            continue

        result = save_file(
            file,
            upload_folder
        )

        if isinstance(result, tuple):
            path = result[0]
        else:
            path = result

        if path:
            saved_paths.append(path)

    if not saved_paths:

        return (
            "No valid file uploaded.",
            400
        )

    # -----------------------------------------------------
    # Perform conversion
    # -----------------------------------------------------

    try:

        # =================================================
        # JPG → PDF
        # =================================================

        if conversion == "jpg_to_pdf":

            output_path = convert_jpg_to_pdf(
                saved_paths,
                output_folder
            )

            filename = os.path.basename(
                output_path
            )

        # =================================================
        # PDF → JPG
        # =================================================

        elif conversion == "pdf_to_jpg":

            output_files = convert_pdf_to_jpg(
                saved_paths[0],
                output_folder
            )

            if not output_files:

                return (
                    "No JPG files were generated.",
                    500
                )

            zip_name = (
                f"converted_{int(time.time())}.zip"
            )

            zip_path = os.path.join(
                output_folder,
                zip_name
            )

            with zipfile.ZipFile(
                zip_path,
                "w",
                zipfile.ZIP_DEFLATED
            ) as zipf:

                for output_file in output_files:

                    if os.path.exists(
                        output_file
                    ):

                        zipf.write(
                            output_file,
                            os.path.basename(
                                output_file
                            )
                        )

            filename = zip_name

        # =================================================
        # PDF → PPT
        # =================================================

        elif conversion == "pdf_to_ppt":

            output_path = convert_pdf_to_ppt(
                saved_paths[0],
                output_folder
            )

            filename = os.path.basename(
                output_path
            )

        # =================================================
        # PPT → PDF
        # =================================================

        elif conversion == "ppt_to_pdf":

            output_path = convert_ppt_to_pdf(
                saved_paths[0],
                output_folder
            )

            filename = os.path.basename(
                output_path
            )

        # =================================================
        # WORD → PDF
        # =================================================

        elif conversion == "word_to_pdf":

            output_path = convert_word_to_pdf(
                saved_paths[0],
                output_folder
            )

            filename = os.path.basename(
                output_path
            )

        else:

            return (
                "Conversion not supported.",
                400
            )

        # -------------------------------------------------
        # Generate QR code
        # -------------------------------------------------

        qr_image, download_link = generate_qr(
            filename
        )

        # -------------------------------------------------
        # Result page
        # -------------------------------------------------

        if conversion == "pdf_to_jpg":

            return render_template(
                "result.html",
                files=[
                    os.path.basename(file)
                    for file in output_files
                ],
                filename=filename,
                qr_image=qr_image,
                download_link=download_link
            )

        return render_template(
            "result.html",
            filename=filename,
            qr_image=qr_image,
            download_link=download_link
        )

    except Exception as e:

        print(
            "CONVERSION ERROR:",
            repr(e)
        )

        return (
            f"Conversion failed: {str(e)}",
            500
        )


# =========================================================
# DOWNLOAD CONVERTED FILE
# =========================================================

@convert_bp.route(
    "/download/<path:filename>",
    methods=["GET"]
)
def download_file(filename):

    output_folder = current_app.config[
        "OUTPUT_FOLDER"
    ]

    # Prevent unsafe path traversal
    safe_filename = os.path.basename(
        filename
    )

    # Check expiry
    if safe_filename in file_expiry:

        if (
            time.time()
            - file_expiry[safe_filename]
            > DOWNLOAD_EXPIRY
        ):

            file_expiry.pop(
                safe_filename,
                None
            )

            return (
                "Download link expired.",
                403
            )

    file_path = os.path.join(
        output_folder,
        safe_filename
    )

    if not os.path.isfile(file_path):

        return (
            "File not found.",
            404
        )

    return send_from_directory(
        output_folder,
        safe_filename,
        as_attachment=True
    )


# =========================================================
# VIEW CONVERTED FILE
# =========================================================

@convert_bp.route(
    "/view/<path:filename>",
    methods=["GET"]
)
def view_file(filename):

    output_folder = current_app.config[
        "OUTPUT_FOLDER"
    ]

    safe_filename = os.path.basename(
        filename
    )

    file_path = os.path.join(
        output_folder,
        safe_filename
    )

    if not os.path.isfile(file_path):

        return (
            "File not found.",
            404
        )

    return send_from_directory(
        output_folder,
        safe_filename
    )


# =========================================================
# CONTACT
# =========================================================

@convert_bp.route(
    "/contact",
    methods=["GET"]
)
def contact():

    return render_template(
        "contact.html"
    )


# =========================================================
# NOTES / STUDY - ANALYZE PDF
# =========================================================

@convert_bp.route(
    "/study/analyze-pdf",
    methods=["POST"]
)
def study_analyze_pdf_route():

    file = request.files.get(
        "file"
    )

    length = request.form.get(
        "summary_length",
        "medium"
    ).strip().lower()

    if not file or not file.filename:

        return (
            "Please upload a PDF file.",
            400
        )

    # -----------------------------------------------------
    # Make sure it is a PDF
    # -----------------------------------------------------

    if not file.filename.lower().endswith(
        ".pdf"
    ):

        return (
            "Please upload a PDF file only.",
            400
        )

    length_map = {
        "short": 5,
        "medium": 8,
        "long": 12
    }

    max_sentences = length_map.get(
        length,
        8
    )

    try:

        upload_folder = current_app.config[
            "UPLOAD_FOLDER"
        ]

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        saved_path = save_file(
            file,
            upload_folder
        )

        if isinstance(saved_path, tuple):
            saved_path = saved_path[0]

        # -------------------------------------------------
        # Extract PDF text
        # -------------------------------------------------

        text = extract_pdf_text(
            saved_path
        )

        if not text or not text.strip():

            return (
                "Could not extract text from this PDF.",
                400
            )

        # -------------------------------------------------
        # Generate study material
        # -------------------------------------------------

        summary = generate_summary(
            text,
            max_sentences=max_sentences
        )

        key_points = extract_key_points(
            text,
            n=10
        )

        questions = generate_important_questions(
            text,
            n=8
        )

        # -------------------------------------------------
        # Render study result
        # -------------------------------------------------

        return render_template(
            "study_result.html",
            summary=summary,
            key_points=key_points,
            questions=questions
        )

    except Exception as e:

        print(
            "STUDY ANALYSIS ERROR:",
            repr(e)
        )

        return (
            f"Study analysis failed: {str(e)}",
            500
        )