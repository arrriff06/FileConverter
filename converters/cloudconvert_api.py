import requests
import os
import time
from config import CLOUDCONVERT_API_KEY

def convert_to_pdf(input_path, output_folder):

    url = "https://api.cloudconvert.com/v2/jobs"

    filename = os.path.basename(input_path)

    payload = {
        "tasks": {
            "import-file": {
                "operation": "import/upload"
            },
            "convert-file": {
                "operation": "convert",
                "input": "import-file",
                "output_format": "pdf"
            },
            "export-file": {
                "operation": "export/url",
                "input": "convert-file"
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {CLOUDCONVERT_API_KEY}"
    }

    # Create job
    response = requests.post(url, json=payload, headers=headers)
    job = response.json()["data"]

    # Upload file
    upload_task = next(t for t in job["tasks"] if t["name"] == "import-file")
    upload_url = upload_task["result"]["form"]["url"]
    upload_params = upload_task["result"]["form"]["parameters"]

    with open(input_path, "rb") as f:
        files = {"file": f}
        requests.post(upload_url, data=upload_params, files=files)

    # Wait for conversion
    job_id = job["id"]

    while True:
        time.sleep(2)
        status_res = requests.get(f"{url}/{job_id}", headers=headers)
        status_data = status_res.json()["data"]

        if status_data["status"] == "finished":
            break
        elif status_data["status"] == "error":
            raise Exception("CloudConvert failed")

    # Get download URL
    export_task = next(t for t in status_data["tasks"] if t["name"] == "export-file")
    file_url = export_task["result"]["files"][0]["url"]

    # Download file
    output_filename = f"converted_{int(time.time())}.pdf"
    output_path = os.path.join(output_folder, output_filename)

    r = requests.get(file_url)
    with open(output_path, "wb") as f:
        f.write(r.content)

    return output_path