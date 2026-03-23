from flask import Flask
import os

print("Step 1: Flask imported")

from routes.convert_routes import convert_bp
print("Step 2: Routes imported")

from config import UPLOAD_FOLDER, OUTPUT_FOLDER
print("Step 3: Config imported")

app = Flask(__name__)
print("Step 4: App created")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.register_blueprint(convert_bp)

print("Step 5: Starting server")

if __name__ == "__main__":
    app.run(debug=True)