from flask import Flask, render_template
import os

# Import routes
from routes.convert_routes import convert_bp

# Import config
from config import UPLOAD_FOLDER, OUTPUT_FOLDER

# Initialize app
app = Flask(__name__)

# Configure folders
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Register blueprint
app.register_blueprint(convert_bp)

# ✅ Homepage route (THIS WAS MISSING)
@app.route("/")
def home():
    return render_template("index.html")

# ✅ Optional test route (for debugging)
@app.route("/test")
def test():
    return "App is working"

# Run locally
if __name__ == "__main__":
    app.run(debug=True)
