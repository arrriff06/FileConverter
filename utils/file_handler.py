import os
from werkzeug.utils import secure_filename
import uuid

def generate_file_id():
    return str(uuid.uuid4())

def save_file(file, upload_folder):
    filename = secure_filename(file.filename)

    file_id = generate_file_id()
    saved_name = f"{file_id}_{filename}"

    file_path = os.path.join(upload_folder, saved_name)
    file.save(file_path)

    # ✅ RETURN EXACTLY 2 VALUES
    return file_path, file_id