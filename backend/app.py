from flask import Flask, render_template, jsonify, send_from_directory
import os
import json
import sys
import subprocess


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

BACKEND_DIR = os.path.join(BASE_DIR, "backend")
VIDEO_FOLDER = os.path.join(BASE_DIR, "videos")
VIDEO_FILE = "v1.mov"
INCIDENTS_FILE = os.path.join(BACKEND_DIR, "incidents.json")
DETECTOR_FILE = os.path.join(
    BACKEND_DIR,
    "ai",
    "accident_detector.py"
)


# ============================================================
# FLASK
# ============================================================

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static")
)


# ============================================================
# AI PROCESS
# ============================================================

detector_process = None


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# INCIDENT API
# ============================================================

@app.route("/api/incidents")
def get_incidents():
    try:
        if not os.path.exists(INCIDENTS_FILE):
            return jsonify([])

        with open(INCIDENTS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return jsonify(data)

        if isinstance(data, dict):
            return jsonify(data.get("incidents", []))

        return jsonify([])

    except Exception as error:
        print("❌ Error reading incidents:", error)
        return jsonify([])


# ============================================================
# VIDEO
# ============================================================

@app.route("/video")
def video():
    video_path = os.path.join(VIDEO_FOLDER, VIDEO_FILE)

    if not os.path.exists(video_path):
        return f"Video not found: {video_path}", 404

    return send_from_directory(VIDEO_FOLDER, VIDEO_FILE)


# ============================================================
# START AI DETECTION
# ============================================================

@app.route("/api/start-detection", methods=["POST"])
def start_detection():
    global detector_process

    if detector_process is not None and detector_process.poll() is None:
        return jsonify({
            "success": True,
            "message": "AI detection is already running.",
            "running": True
        })

    if not os.path.exists(DETECTOR_FILE):
        return jsonify({
            "success": False,
            "message": "accident_detector.py not found.",
            "running": False
        }), 404

    video_path = os.path.join(VIDEO_FOLDER, VIDEO_FILE)
    if not os.path.exists(video_path):
        return jsonify({
            "success": False,
            "message": "v1.mov not found.",
            "running": False
        }), 404

    try:
        print("=" * 60)
        print("🤖 STARTING AI ACCIDENT DETECTOR")
        print("=" * 60)
        print("📁 Detector:", DETECTOR_FILE)
        print("🎥 Video:", video_path)
        print("=" * 60)

        # Use the same Python interpreter running Flask/Gunicorn.
        detector_process = subprocess.Popen(
            [sys.executable, DETECTOR_FILE],
            cwd=BACKEND_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )

        return jsonify({
            "success": True,
            "message": "AI detection started.",
            "running": True
        })

    except Exception as error:
        detector_process = None
        print("❌ Could not start detector:", error)

        return jsonify({
            "success": False,
            "message": str(error),
            "running": False
        }), 500


# ============================================================
# STOP AI DETECTION
# ============================================================

@app.route("/api/stop-detection", methods=["POST"])
def stop_detection():
    global detector_process

    try:
        if detector_process is not None and detector_process.poll() is None:
            print("🛑 Stopping AI detector...")
            detector_process.terminate()

            try:
                detector_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                detector_process.kill()

        detector_process = None

        return jsonify({
            "success": True,
            "message": "AI detection stopped.",
            "running": False
        })

    except Exception as error:
        print("❌ Error stopping detector:", error)

        return jsonify({
            "success": False,
            "message": str(error),
            "running": False
        }), 500


# ============================================================
# AI STATUS
# ============================================================

@app.route("/api/detection-status")
def detection_status():
    global detector_process

    running = (
        detector_process is not None
        and detector_process.poll() is None
    )

    return jsonify({"running": running})


# ============================================================
# SYSTEM STATUS
# ============================================================

@app.route("/api/status")
def system_status():
    global detector_process

    running = (
        detector_process is not None
        and detector_process.poll() is None
    )

    return jsonify({
        "status": "running" if running else "ready",
        "system": "AI Accident Detection System",
        "camera_count": 12,
        "ai_detection": running
    })


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🚗 AI ACCIDENT DETECTION DASHBOARD")
    print("=" * 60)
    print("📁 Project:", BASE_DIR)
    print("🎥 Video:", os.path.join(VIDEO_FOLDER, VIDEO_FILE))
    print("🤖 Detector:", DETECTOR_FILE)
    print("📋 Incidents:", INCIDENTS_FILE)
    print("=" * 60)

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
        use_reloader=False
    )
