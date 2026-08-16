from flask import Flask, render_template
import os
import threading
import time

from routes.convert_routes import convert_bp

from config import UPLOAD_FOLDER, OUTPUT_FOLDER
from cleanup import cleanup


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# CONFIGURATION
# =========================================================

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# =========================================================
# BACKGROUND CLEANUP
# =========================================================

def run_cleanup():

    while True:

        try:
            cleanup()

        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")

        time.sleep(300)


cleanup_thread = threading.Thread(
    target=run_cleanup,
    daemon=True
)

cleanup_thread.start()


# =========================================================
# BLUEPRINTS
# =========================================================

app.register_blueprint(
    convert_bp,
    url_prefix="/convert"
)



# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# TEST
# =========================================================

@app.route("/test")
def test():

    return "Working"


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )