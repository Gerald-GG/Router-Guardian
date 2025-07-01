import platform
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS
import traceback
import os
from dotenv import load_dotenv

# ==============================
# Import scanner functions
# ==============================
from scanner.device_scanner import scan_network, get_gateway_ip as original_get_gateway_ip
import netifaces

# ==============================
# Load environment variables from .env in project root
# ==============================
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
API_URL = os.getenv("API_URL", "http://localhost:5000")

# ==============================
# Initialize the Flask app
# ==============================
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend access

# ==============================
# Improved get_gateway_ip with safe fallback
# ==============================
def get_gateway_ip():
    try:
        gateways = netifaces.gateways()
        if 'default' in gateways and netifaces.AF_INET in gateways['default']:
            default_gateway = gateways['default'][netifaces.AF_INET][0]
            print(f"[DEBUG] Detected gateway IP: {default_gateway}")
            return default_gateway
        else:
            raise Exception("No IPv4 default gateway found. Ensure you're connected to a network.")
    except Exception as e:
        print(f"[ERROR] get_gateway_ip failed: {e}")
        raise

# ==============================
# Before each request: log method and URL for debugging
# ==============================
@app.before_request
def log_request_info():
    print(f"[REQUEST] Method: {request.method} URL: {request.url}")

# ==============================
# Root route for health check
# ==============================
@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Router Guardian API is running.'})

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
# /devices route: Return real scanned device data
# ==============================
@app.route('/devices', methods=['GET'])
def get_devices():
    print("[INFO] /devices endpoint called")
    try:
        gateway_ip = get_gateway_ip()
        ip_range = gateway_ip + "/24"
        devices = scan_network(ip_range)
        print(f"[DEBUG] Returning {len(devices)} scanned devices")
        return jsonify(devices)

    except Exception as e:
        print(f"[ERROR] Failed to scan devices: {e}")
        traceback.print_exc()
        return jsonify([])

# ==============================
# Main entry point
# ==============================
if __name__ == "__main__":
    print("[INFO] Starting Flask app on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
