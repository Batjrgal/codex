from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess, os, re, threading, time

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "./downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ==== 1. Сервер асахад хуучин файлуудыг устгах ====
def clean_old_files(max_age=60):
    now = time.time()
    for file in os.listdir(DOWNLOAD_FOLDER):
        path = os.path.join(DOWNLOAD_FOLDER, file)
        if os.path.isfile(path):
            age = now - os.path.getmtime(path)
            if age > max_age:
                try:
                    os.remove(path)
                    print(f"🧹 Cleaned old file: {file}")
                except Exception as e:
                    print(f"⚠️ Could not delete old file {file}: {e}")

clean_old_files()  # сервер асах үед автоматаар цэвэрлэнэ


# ==== 2. Файлыг 1 минутын дараа устгах ====
def schedule_file_deletion(filepath, delay=60):
    """delay = секундээр (1 минут = 60 секунд)"""
    def delete_file():
        time.sleep(delay)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"🗑️ Deleted file after 1 minute: {filepath}")
            except Exception as e:
                print(f"⚠️ Could not delete {filepath}: {e}")
    threading.Thread(target=delete_file, daemon=True).start()


# ==== 3. Spotify линк татах ====
@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"success": False, "error": "No URL provided"}), 400

    try:
        result = subprocess.run(
            [
                "spotdl", url,
                "--output", DOWNLOAD_FOLDER,
                "--format", "mp3"
            ],
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

        # Сүүлд үүссэн mp3 файлыг олох
        filename = None
        for file in os.listdir(DOWNLOAD_FOLDER):
            if file.endswith(".mp3"):
                filepath = os.path.join(DOWNLOAD_FOLDER, file)
                if not filename or os.path.getmtime(filepath) > os.path.getmtime(os.path.join(DOWNLOAD_FOLDER, filename)):
                    filename = file

        if not filename:
            return jsonify({"success": True, "title": title, "file": None, "message": "File not found."})

        # 1 минутын дараа устгал төлөвлөх
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        schedule_file_deletion(filepath, delay=60)

        # Filename-г frontend-д буцаах
        return jsonify({
            "success": True,
            "title": title,
            "file": filename,
            "message": "Downloaded successfully! (auto-deletes in 1 minute)"
        })

    except subprocess.CalledProcessError as e:
        print("⚠️ spotDL error:", e.stderr)
        return jsonify({"success": False, "error": e.stderr})


# ==== 4. Файлыг татах ====
@app.route("/files/<path:filename>")
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


@app.route("/")
def home():
    return "✅ spotDL backend with 1-min auto-delete is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
