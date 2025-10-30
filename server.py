from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess, os, re, threading, time

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "./downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ==== Тусгай функц: Файлыг устгах ====
def schedule_file_deletion(filepath, delay=300):
    """delay = секундээр (5 минут = 300 секунд)"""
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

    try:
        result = subprocess.run(
            ["spotdl", url, "--output", DOWNLOAD_FOLDER, "--format", "mp3", "--bitrate", "320k"],
            capture_output=True,
            text=True,
            check=True
        )

        output = result.stdout
        print("=== SPOTDL OUTPUT ===")
        print(output)

        # "Downloaded" мөрөөс нэр гаргах
        title_match = re.search(r'Downloaded "(.*?)"', output)
        title = title_match.group(1) if title_match else "Unknown Track"

        # MP3 файл олох (хамгийн сүүлд үүссэн)
        filename = None
        for file in os.listdir(DOWNLOAD_FOLDER):
            if file.endswith(".mp3"):
                filepath = os.path.join(DOWNLOAD_FOLDER, file)
                if not filename or os.path.getmtime(filepath) > os.path.getmtime(os.path.join(DOWNLOAD_FOLDER, filename)):
                    filename = file

        if not filename:
            return jsonify({"success": True, "title": title, "file": None, "message": "File not found."})

        # Файлын бүрэн зам, устгал төлөвлөх
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        schedule_file_deletion(filepath, delay=300)  # 5 минут = 300 секунд

        # Татах линк үүсгэх
        domain = "https://laravel1-production-5b85.up.railway.app"
        file_url = f"{filename}"

        return jsonify({
            "success": True,
            "title": title,
            "file": file_url,
            "message": "Downloaded successfully! (auto-deletes in 5 min)"
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": e.stderr})


@app.route("/files/<path:filename>")
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

@app.route("/")
def home():
    return "✅ spotDL backend with 5-min auto-delete is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
