from flask import Blueprint, request, jsonify
from scanner.device_scanner import get_gateway_ip, scan_network
from router_control.router_interface import get_router_controller
import json
import os
from datetime import datetime, timedelta

api_blueprint = Blueprint('api', __name__)
BLOCKLIST_FILE = "backend/data/blocklist.json"

# Utility: Load blocklist
def load_blocklist():
    if os.path.exists(BLOCKLIST_FILE):
        with open(BLOCKLIST_FILE, "r") as f:
            return json.load(f)
    return []

# Utility: Save blocklist
def save_blocklist(data):
    with open(BLOCKLIST_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Utility: Parse "1h", "30m" into timedelta
def parse_duration(duration_str):
    if duration_str.endswith("h"):
        return timedelta(hours=int(duration_str[:-1]))
    elif duration_str.endswith("m"):
        return timedelta(minutes=int(duration_str[:-1]))
    else:
        raise ValueError("Invalid duration format. Use '1h', '30m', etc.")

# Route: GET /scan — live network scan without block history
@api_blueprint.route('/scan', methods=['GET'])
def scan():
    try:
        gateway = get_gateway_ip()
        ip_range = gateway + "/24"
        devices = scan_network(ip_range)

        # Add "status": "online" to each
        for device in devices:
            device["status"] = "online"

        return jsonify(devices), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route: GET /devices — merged list of scanned + tracked + blocked
@api_blueprint.route('/devices', methods=['GET'])
def get_devices():
    try:
        gateway = get_gateway_ip()
        ip_range = gateway + "/24"
        scanned_devices = scan_network(ip_range)
        scanned_map = {dev["mac"]: dev for dev in scanned_devices}

        blocklist = load_blocklist()
        now = datetime.now()
        updated_blocklist = []
        all_devices = []

        # Process scanned devices
        for mac, dev in scanned_map.items():
            dev["status"] = "online"
            all_devices.append(dev)

        # Handle blocked/scheduled entries
        for entry in blocklist:
            mac = entry["mac"]
            blocked_at = entry.get("blocked_at")
            expires_at = entry.get("expires_at")

            still_blocked = False

            if expires_at:
                expiry = datetime.fromisoformat(expires_at)
                if now < expiry:
                    still_blocked = True
            else:
                still_blocked = True

            if still_blocked:
                updated_blocklist.append(entry)

            if mac in scanned_map:
                if still_blocked:
                    scanned_map[mac]["status"] = "blocked"
                continue

            # Device not currently online
            device = {
                "mac": mac,
                "status": "scheduled" if still_blocked else "offline",
                "blocked_at": blocked_at,
                "expires_at": expires_at
            }
            all_devices.append(device)

        # Save updated blocklist to remove expired entries
        save_blocklist(updated_blocklist)

        return jsonify(all_devices), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route: POST /block
@api_blueprint.route('/block', methods=['POST'])
def block():
    data = request.get_json()
    mac = data.get("mac")
    duration = data.get("duration", None)

    if not mac:
        return jsonify({"error": "MAC address is required"}), 400

    try:
        router = get_router_controller()
        router.login()
        router.block_device(mac)

        blocklist = load_blocklist()
        entry = {"mac": mac, "blocked_at": datetime.now().isoformat()}

        if duration:
            try:
                delta = parse_duration(duration)
                entry["expires_at"] = (datetime.now() + delta).isoformat()
            except ValueError as ve:
                return jsonify({"error": str(ve)}), 400

        blocklist.append(entry)
        save_blocklist(blocklist)

        return jsonify({"message": f"{mac} blocked", "duration": duration or "indefinite"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route: POST /unblock
@api_blueprint.route('/unblock', methods=['POST'])
def unblock():
    data = request.get_json()
    mac = data.get("mac")

    if not mac:
        return jsonify({"error": "MAC address is required"}), 400

    try:
        router = get_router_controller()
        router.login()
        router.unblock_device(mac)

        blocklist = load_blocklist()
        blocklist = [entry for entry in blocklist if entry["mac"] != mac]
        save_blocklist(blocklist)

        return jsonify({"message": f"{mac} unblocked"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route: GET /blocklist — return raw blocklist file
@api_blueprint.route('/blocklist', methods=['GET'])
def get_blocklist():
    try:
        return jsonify(load_blocklist()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
