from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"success": False, "error": "No URL provided"}), 400

    try:
        # stdout уншдаг хувилбар
        result = subprocess.run(
            ["spotdl", url, "--output", "./downloads"],
            capture_output=True,
            text=True,
            check=True
        )

        output = result.stdout
        # "Downloaded ..." мөрөөс дууны нэр гаргах
        title = None
        for line in output.splitlines():
            if line.startswith("Downloaded"):
                title = line.split('"')[1]  # "HUNTR/X - Golden" гэх мэт
                break

        return jsonify({
            "success": True,
            "title": title if title else "Unknown Track",
            "message": "Downloaded successfully!"
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": e.stderr})

@app.route("/")
def home():
    return "✅ spotDL backend running with FFmpeg + CORS!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
