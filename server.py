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

    try:
        result = subprocess.run(
            ["spotdl", url, "--output", DOWNLOAD_FOLDER],
            capture_output=True,
            text=True,
            check=True
        )

        output = result.stdout
        title = None
        for line in output.splitlines():
            if line.startswith("Downloaded"):
                title = line.split('"')[1]
                break

        # татсан файлыг олох
        filename = None
        for file in os.listdir(DOWNLOAD_FOLDER):
            if title and title.lower().replace(" ", "_") in file.lower().replace(" ", "_") and file.endswith(".mp3"):
                filename = file
                break

        if not filename:
            return jsonify({"success": True, "title": title, "message": "Downloaded, but file not found."})

        file_url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'laravel1-production-5b85.up.railway.app')}/files/{filename}"

        return jsonify({
            "success": True,
            "title": title,
            "file": file_url,
            "message": "Downloaded successfully!"
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": e.stderr})


@app.route("/files/<path:filename>")
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)


@app.route("/")
def home():
    return "✅ spotDL backend with working MP3 download links!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
