@convert_bp.route("/convert", methods=["POST"])
def convert_file():

    conversion = request.form.get("conversion")

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    output_folder = current_app.config["OUTPUT_FOLDER"]

    saved_paths = []
    files = request.files.getlist("file")

    # Save uploaded files
    for file in files:
        if file and file.filename != "" and allowed_file(file.filename):
            path = save_file(file, upload_folder)
            saved_paths.append(path)

    if not saved_paths:
        return "No valid file uploaded"

    try:

        # ---------- JPG → PDF ----------
        if conversion == "jpg_to_pdf":
            output_path = convert_jpg_to_pdf(saved_paths, output_folder)
            filename = os.path.basename(output_path)

        # ---------- PDF → JPG (MULTIPLE FILES) ----------
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
            from converters.word_to_pdf import convert_word_to_pdf
            output_path = convert_word_to_pdf(saved_paths[0], output_folder)
            filename = os.path.basename(output_path)

        else:
            return "Conversion not supported"

    except Exception as e:
        print("ERROR:", e)
        return f"Conversion failed: {str(e)}"

    return render_template("result.html", filename=filename)