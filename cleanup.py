import os
import time

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
QR_FOLDER = os.path.join("static", "qr")

EXPIRY_TIME = 600  # 10 minutes


def delete_old_files(folder):
    if not os.path.exists(folder):
        print(f"[SKIP] Folder not found: {folder}")
        return

    now = time.time()

    for root, dirs, files in os.walk(folder):
        for name in files:
            path = os.path.join(root, name)

            try:
                file_age = now - os.path.getmtime(path)

                if file_age > EXPIRY_TIME:
                    os.remove(path)
                    print(f"[DELETED] {path}")

            except Exception as e:
                print(f"[ERROR] Could not delete {path}: {e}")

        # Optional: remove empty folders
        for d in dirs:
            dir_path = os.path.join(root, d)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"[REMOVED EMPTY FOLDER] {dir_path}")
            except Exception:
                pass


def cleanup():
    print("\n--- CLEANUP STARTED ---")

    delete_old_files(UPLOAD_FOLDER)
    delete_old_files(OUTPUT_FOLDER)
    delete_old_files(QR_FOLDER)

    print("--- CLEANUP FINISHED ---\n")


if __name__ == "__main__":
    cleanup()