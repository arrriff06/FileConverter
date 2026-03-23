from flask import Flask, render_template
import os

from routes.convert_routes import convert_bp
from config import UPLOAD_FOLDER, OUTPUT_FOLDER

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ✅ FIXED (IMPORTANT)
app.register_blueprint(convert_bp, url_prefix="/convert")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/test")
def test():
    return "Working"

if __name__ == "__main__":
    app.run(debug=True)
