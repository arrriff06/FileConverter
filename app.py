from flask import Flask, render_template
import os
import threading
import time

from routes.convert_routes import convert_bp
<<<<<<< HEAD
from routes.room_routes import room_bp
=======
>>>>>>> 9b92c2a49887cbdad269b74e99bd8004a7d0209f
from config import UPLOAD_FOLDER, OUTPUT_FOLDER
from cleanup import cleanup  # ✅ import cleanup

app = Flask(__name__)

# ---------- CONFIG ----------
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ---------- BACKGROUND CLEANUP THREAD ----------
def run_cleanup():
    while True:
        try:
            cleanup()
        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")
        time.sleep(300)  # run every 5 minutes


# Start cleanup thread (runs in background)
cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
cleanup_thread.start()


# ---------- REGISTER BLUEPRINT ----------
app.register_blueprint(convert_bp, url_prefix="/convert")
<<<<<<< HEAD
app.register_blueprint(room_bp)
=======
>>>>>>> 9b92c2a49887cbdad269b74e99bd8004a7d0209f


# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/test")
def test():
    return "Working"


@app.route("/transfer")
def transfer_page():
    return render_template("transfer.html")


# ---------- RUN APP ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)