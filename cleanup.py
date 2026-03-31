import os
import time

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
QR_FOLDER = "static/qr"

EXPIRY_TIME = 600  # 10 minutes


def delete_old_files(folder):
    if not os.path.exists(folder):
        return

    now = time.time()

    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)

        if os.path.isfile(path):
            file_age = now - os.path.getmtime(path)

            if file_age > EXPIRY_TIME:
                try:
                    os.remove(path)
                    print(f"Deleted: {path}")
                except Exception as e:
                    print(f"Error deleting {path}: {e}")


def cleanup():
    delete_old_files(UPLOAD_FOLDER)
    delete_old_files(OUTPUT_FOLDER)
    delete_old_files(QR_FOLDER)


if __name__ == "__main__":
    cleanup()