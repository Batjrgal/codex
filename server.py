from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess, os, re, threading, time

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "./downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def schedule_file_deletion(filepath, delay=60):
    def delete_file():
        time.sleep(delay)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"🗑️ Deleted file: {filepath}")
            except Exception as e:
                print(f"⚠️ Could not delete {filepath}: {e}")

    threading.Thread(target=delete_file, daemon=True).start()


@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"success": False, "error": "No URL provided"}), 400

    # Spotify бүсийн линк цэвэрлэх
    url = url.replace(
        "https://open.spotify.com/intl-mn/", "https://open.spotify.com/"
    ).split("?")[0]

    try:
        result = subprocess.run(
            ["spotdl", url, "--output", DOWNLOAD_FOLDER, "--format", "mp3"],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout
        print("=== SPOTDL OUTPUT ===")
        print(output)

        title_match = re.search(r'Downloaded "(.*?)"', output)
        title = title_match.group(1) if title_match else "Unknown Track"

        filename = None
        for file in os.listdir(DOWNLOAD_FOLDER):
            if file.endswith(".mp3"):
                filepath = os.path.join(DOWNLOAD_FOLDER, file)
                if not filename or os.path.getmtime(filepath) > os.path.getmtime(
                    os.path.join(DOWNLOAD_FOLDER, filename)
                ):
                    filename = file

        if not filename:
            return jsonify({"success": False, "error": "File not found."})

        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        schedule_file_deletion(filepath, delay=60)

        return jsonify(
            {
                "success": True,
                "title": title,
                "file": filename,
                "message": "Downloaded successfully! (auto-deletes in 5 min)",
            }
        )

    except subprocess.CalledProcessError as e:
        print("❌ SPOTDL ERROR OUTPUT ===")
        print(e.stderr)
        print("===========================")
        return jsonify({"success": False, "error": e.stderr})


@app.route("/files/<path:filename>")
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


@app.route("/")
def home():
    return "✅ spotDL backend running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

