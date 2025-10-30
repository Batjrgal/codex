from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess, os

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "./downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"success": False, "error": "No URL provided"}), 400

    result = subprocess.run(
        ["spotdl", url, "--output", DOWNLOAD_FOLDER],
        capture_output=True,
        text=True
    )
    output = result.stdout

    title = None
    for line in output.splitlines():
        if line.startswith("Downloaded"):
            title = line.split('"')[1]
            break

    filename = None
    for file in os.listdir(DOWNLOAD_FOLDER):
        if title and title.lower().replace(" ", "_") in file.lower().replace(" ", "_"):
            filename = file
            break

    if filename:
        file_url = f"https://laravel1-production-5b85.up.railway.app/files/{filename}"
    else:
        file_url = None

    return jsonify({
        "success": True,
        "title": title,
        "file": file_url,
        "message": "Downloaded successfully!"
    })


@app.route("/files/<path:filename>")
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

