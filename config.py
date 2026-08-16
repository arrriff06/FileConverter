import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
 
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "ppt", "pptx"}