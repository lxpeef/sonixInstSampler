from flask import Flask, request, jsonify
import sounddevice as sd
from scipy.io.wavfile import write
import json
import os

app = Flask(__name__)

# Directory for saving recordings
recordings_dir = "/path/to/shared/nvme"

@app.route('/initiate_recording', methods=['POST'])
def initiate_recording():
    data = request.json
    filename = data["filename"]
    duration = data["duration"]
    fs = 44100

    # Start recording audio
    try:
        filepath = os.path.join(recordings_dir, filename)
        print(f"Starting recording for {filename} with duration {duration}s...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float64')
        sd.wait()
        write(filepath, fs, recording)
        
        # Notify Khadas of completion
        confirmation = {"filename": filename, "status": "Completed"}
        requests.post("http://khadas-ip-address:5000/confirm_recording", json=confirmation)
        return jsonify({"status": "Recording completed", "file": filepath}), 200
    except Exception as e:
        return jsonify({"status": "Error", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
