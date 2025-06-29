import platform
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS
import traceback

# ==============================
# Initialize the Flask app
# ==============================
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend access

# ==============================
# Before each request: log method and URL for debugging
# ==============================
@app.before_request
def log_request_info():
    print(f"[REQUEST] Method: {request.method} URL: {request.url}")

# ==============================
# /wifi route: Return current Wi-Fi SSID
# ==============================
@app.route('/wifi', methods=['GET'])
def get_wifi():
    print("[INFO] /wifi endpoint called")
    try:
        system = platform.system()
        print(f"[DEBUG] Detected OS: {system}")

        if system == 'Linux':
            result = subprocess.check_output(['iwgetid', '--raw'], stderr=subprocess.DEVNULL)
            ssid = result.decode().strip()
            print(f"[DEBUG] Linux SSID: {ssid}")

        elif system == 'Windows':
            result = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], stderr=subprocess.DEVNULL)
            lines = result.decode(errors='ignore').split('\n')
            ssid = next((line.split(':')[1].strip() for line in lines if 'SSID' in line and 'BSSID' not in line), 'Unknown')
            print(f"[DEBUG] Windows SSID: {ssid}")

        else:
            ssid = 'Unsupported OS'
            print("[WARN] Unsupported OS for Wi-Fi detection")

        return jsonify({'ssid': ssid or 'Unavailable'})

    except Exception as e:
        print(f"[ERROR] Wi-Fi detection failed: {e}")
        traceback.print_exc()
        return jsonify({'ssid': 'Unavailable'})

# ==============================
# /devices route: Return dummy device data
# Replace with live scanner data in future
# ==============================
@app.route('/devices', methods=['GET'])
def get_devices():
    print("[INFO] /devices endpoint called")
    try:
        devices = [
            {
                'hostname': 'Unknown',
                'ip': '192.168.100.1',
                'mac': '30:e9:8e:63:c5:74',
                'status': 'online',
                'online_duration': '4 days, 2:23:19.137918',
                'blocked': False
            },
            {
                'hostname': 'Unknown',
                'ip': '192.168.100.6',
                'mac': '08:40:f3:d1:8e:18',
                'status': 'online',
                'online_duration': '4 days, 2:23:19.137918',
                'blocked': False
            },
            {
                'hostname': 'Unknown',
                'ip': '192.168.100.10',
                'mac': '9e:6c:6d:b2:ee:6d',
                'status': 'online',
                'online_duration': '4 days, 2:21:43.457548',
                'blocked': False
            }
        ]
        print(f"[DEBUG] Returning {len(devices)} dummy devices")
        return jsonify(devices)

    except Exception as e:
        print(f"[ERROR] Failed to get devices: {e}")
        traceback.print_exc()
        return jsonify([])

# ==============================
# Main entry point
# ==============================
if __name__ == "__main__":
    print("[INFO] Starting Flask app on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
