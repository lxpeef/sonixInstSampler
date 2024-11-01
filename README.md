Here’s a comprehensive `README.md` file covering all aspects of the distributed audio recording solution.

---

# Distributed Audio Recording System (Flask-Based Solution)

This distributed audio recording system uses a Khadas device and a recording computer to orchestrate and capture high-quality audio recordings. The Khadas device hosts a Flask web application that allows centralized control of recording sessions, while the recording computer performs the actual audio recording. The solution enables efficient session management, inter-machine communication, metadata storage, and audio post-processing, such as trimming and normalization.

## Table of Contents
- [Distributed Audio Recording System (Flask-Based Solution)](#distributed-audio-recording-system-flask-based-solution)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Architecture Overview](#architecture-overview)
  - [Installation and Setup](#installation-and-setup)
  - [Configuration Files](#configuration-files)
    - [`config.json`](#configjson)
    - [`instruments.json`](#instrumentsjson)
  - [Executing the Application](#executing-the-application)
  - [Technical Details](#technical-details)
    - [Inter-machine Messaging](#inter-machine-messaging)
    - [Metadata Management](#metadata-management)
    - [Trimming and Post-processing](#trimming-and-post-processing)
      - [Example of Normalizing Audio](#example-of-normalizing-audio)
    - [Setting Up SMB File Sharing on Khadas NVMe Drive](#setting-up-smb-file-sharing-on-khadas-nvme-drive)
  - [Database Write and JSON Logging](#database-write-and-json-logging)
  - [Additional Notes](#additional-notes)

---

## Features
- **Distributed Recording**: Manages recordings across a Khadas device and a separate recording computer.
- **Web Interface**: Provides centralized control and monitoring for all recording sessions.
- **Configurable Parameters**: Easily adjustable countdown, articulation durations, and instrument metadata.
- **Post-Processing**: Optional audio normalization, trimming, and file management.
- **Metadata and Database Logging**: Detailed tracking of each session and file location for future reference.

---

## Architecture Overview

1. **Flask Application on Khadas**:
   - Hosts the primary web interface.
   - Provides a RESTful API for controlling recording sessions.
   - Central command center for initiating recordings and managing configuration.

2. **Secondary Server on Recording Computer**:
   - Receives recording requests and captures audio.
   - Responds with status updates and confirmation.
   - Stores audio files on a shared SMB NVMe drive on the Khadas.

3. **SMB File Sharing**:
   - Files are saved to a shared NVMe drive, enabling both devices to access audio recordings easily.

---

## Installation and Setup

1. **Dependencies**:
   - Both the Khadas device and recording computer need Python and Flask installed. Run:
     ```bash
     pip install flask sounddevice scipy requests librosa
     ```

2. **Config Files**:
   - Copy the provided `config.json` and `instruments.json` files to the working directory on the Khadas.

3. **Setting up SMB Share on Khadas**:
   - Install `samba` on Khadas:
     ```bash
     sudo apt update
     sudo apt install samba
     ```
   - Configure the shared directory:
     - Add the following to `/etc/samba/smb.conf`:
       ```conf
       [recordings]
       path = /path/to/nvme
       available = yes
       valid users = your_username
       read only = no
       browsable = yes
       public = yes
       writable = yes
       ```
     - Restart Samba:
       ```bash
       sudo systemctl restart smbd
       ```

4. **Configuring Network Access**:
   - Ensure both devices can access each other via DNS or IP.

---

## Configuration Files

### `config.json`
Defines global settings such as countdown duration, articulation durations, recording computer URL, file management, and logging. Example:

```json
{
    "countdown_duration": 5,
    "articulation_durations": {
        "short": 0.2,
        "medium": 0.5,
        "long": 1.0,
        "transient": 0.05
    },
    "recording_computer_url": "http://recording-computer.local:5001",
    "recording_computer_port": 5001,
    "file_naming": {
        "include_session_id": true,
        "include_user_initials": false
    },
    "storage_management": {
        "auto_cleanup": true,
        "max_age_days": 30
    },
    "post_processing": {
        "normalize_audio": true
    },
    "logging": {
        "log_directory": "logs",
        "log_to_file": true,
        "log_level": "INFO"
    },
    "session_settings": {
        "default_instrument": "guitar",
        "default_note": "A4",
        "default_frequency": 440.0,
        "default_articulation": "long"
    }
}
```

### `instruments.json`
Stores instrument metadata, including range and default articulations.

```json
{
    "instruments": [
        {
            "name": "guitar",
            "type": "string",
            "range": {
                "lowest_note": "E2",
                "highest_note": "E6"
            },
            "default_articulations": ["short", "medium", "long", "transient"]
        }
    ]
}
```

---

## Executing the Application

1. **Start Flask Application on Khadas**:
   ```bash
   python khadas_flask.py
   ```
   - Accessible at `http://khadas-ip-address:5000`.

2. **Start Recording Server on the Recording Computer**:
   ```bash
   python recording_flask.py
   ```

3. **Access the Web Interface**:
   - Use a browser to open `http://khadas-ip-address:5000`.
   - Initiate and manage recording sessions via the interface.

---

## Technical Details

### Inter-machine Messaging
- The Khadas device sends JSON commands over HTTP to the recording computer to initiate recordings.
- The recording computer responds with JSON confirmations, which the Flask application logs and displays in the UI.

### Metadata Management
- Each recording includes metadata such as note, frequency, articulation, and instrument.
- This metadata is stored in a JSON log file for each session, which can later be imported into a database for analysis.

### Trimming and Post-processing
- **Normalization**: After each recording, the file can be normalized to standardize audio levels.
- **Trimming Silence**: Silence trimming is optional but can be added in post-processing using the `librosa` library.

#### Example of Normalizing Audio
In the recording computer script:
```python
def normalize_audio(filepath):
    y, sr = librosa.load(filepath, sr=None)
    y_normalized = librosa.util.normalize(y)
    write(filepath, sr, (y_normalized * 32767).astype(np.int16))
```

### Setting Up SMB File Sharing on Khadas NVMe Drive
1. Install Samba and configure sharing permissions.
2. Ensure the shared drive is accessible from the recording computer.
3. Save recordings to this shared location, allowing centralized access.

---

## Database Write and JSON Logging

1. **JSON Logging**:
   - Each session’s events and metadata are logged in JSON files on the Khadas in the directory specified in `config.json`.
   
2. **Database Integration**:
   - JSON logs can be imported into a PostgreSQL or other relational databases for detailed analysis.
   - Example of loading JSON to PostgreSQL:
     ```sql
     CREATE TABLE recordings (
         id SERIAL PRIMARY KEY,
         session_id VARCHAR,
         filename VARCHAR,
         note VARCHAR,
         frequency FLOAT,
         articulation VARCHAR,
         instrument VARCHAR,
         timestamp TIMESTAMP
     );

     \COPY recordings FROM 'path/to/json_file.json' WITH (FORMAT json);
     ```

## Additional Notes

- **Network Resilience**: If a recording notification fails, the Khadas script retries until it receives confirmation.
- **File Management**: Old recordings are automatically deleted based on the `max_age_days` setting.
- **Error Handling**: Error handling is included for network failures and storage issues. Logs are saved in `logs` directory.
- **User Guide for Web Interface**:
  - **Initiate Session**: Fill out the session details and start a recording.
  - **Check Status**: Monitor live status and receive recording confirmations.
  - **Settings**: Adjust default values for countdown, articulation durations, and other parameters as needed.

This setup provides a reliable, centralized system for distributed audio recording with a user-friendly interface and robust backend management.