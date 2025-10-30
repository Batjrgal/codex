from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"success": False, "error": "No URL provided"}), 400

    try:
        subprocess.run(["spotdl", url, "--output", "./downloads"], check=True)
        return jsonify({"success": True, "message": "Downloaded successfully!"})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/")
def home():
    return "✅ spotDL Python backend is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
