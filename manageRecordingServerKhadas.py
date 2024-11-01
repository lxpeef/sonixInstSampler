from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime
import time

app = Flask(__name__)

# Load configuration from a JSON file
with open('config.json', 'r') as f:
    config = json.load(f)

recording_computer_url = config.get("recording_computer_url", "http://recording-computer.local:5001")

# Start a recording session
@app.route('/start_recording', methods=['POST'])
def start_recording():
    data = request.json
    note = data.get("note", "A4")
    frequency = data.get("frequency", 440.0)
    articulation = data.get("articulation", "long")
    instrument = data.get("instrument", "guitar")
    countdown = data.get("countdown", config["countdown_duration"])
    
    # Prepare metadata for recording
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{note}_{articulation}_{instrument}_{timestamp}.wav"
    duration = config["articulation_durations"].get(articulation, 1.0)
    
    payload = {
        "filename": filename,
        "note": note,
        "frequency": frequency,
        "articulation": articulation,
        "instrument": instrument,
        "duration": duration,
        "timestamp": timestamp
    }

    # Trigger recording on the recording computer
    try:
        response = requests.post(f"{recording_computer_url}/initiate_recording", json=payload)
        response.raise_for_status()
        return jsonify({"status": "Recording started", "details": response.json()}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "Error", "error": str(e)}), 500

# Endpoint for recording computer to confirm recording
@app.route('/confirm_recording', methods=['POST'])
def confirm_recording():
    data = request.json
    filename = data.get("filename")
    status = data.get("status", "Unknown")
    print(f"Recording confirmed for {filename} with status: {status}")
    return jsonify({"status": "Confirmation received"}), 200

# Settings and configuration page
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Update configuration settings as per user input
        new_settings = request.json
        config.update(new_settings)
        with open('config.json', 'w') as f:
            json.dump(config, f)
        return jsonify({"status": "Settings updated"}), 200
    else:
        return jsonify(config), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
