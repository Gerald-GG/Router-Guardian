from flask import Blueprint, jsonify
from scanner.device_scanner import get_gateway_ip, scan_network
import os
import json

# Define a Blueprint for grouping related API routes
api_blueprint = Blueprint('api', __name__)

# Route: GET /scan
# Description: Scans the local network and returns a list of connected devices.
@api_blueprint.route('/scan', methods=['GET'])
def scan():
    try:
        # Get the gateway IP address of the local network
        gateway = get_gateway_ip()

        # Construct the IP range for scanning (e.g., 192.168.1.1/24)
        ip_range = gateway + "/24"

        # Run the device scanner to get devices currently on the network
        devices = scan_network(ip_range)

        # Return the list of devices as JSON with a 200 OK status
        return jsonify(devices), 200

    except Exception as e:
        # If an error occurs (e.g., no gateway, scanner issue), return an error message with a 500 status
        return jsonify({"error": str(e)}), 500


# Route: GET /devices
# Description: Returns all tracked devices from device_tracking.json, including offline ones.
@api_blueprint.route('/devices', methods=['GET'])
def get_tracked_devices():
    # Define the path to the tracking file
    tracking_file = os.path.join("backend", "data", "device_tracking.json")

    # Return an empty list if the file doesn't exist yet
    if not os.path.exists(tracking_file):
        return jsonify({"devices": []}), 200

    try:
        # Load device data from JSON file
        with open(tracking_file, "r") as f:
            data = json.load(f)

        # Convert from {mac: {info}} → list of {mac, ...info}
        device_list = []
        for mac, info in data.items():
            device_entry = {
                "mac": mac,
                **info
            }
            device_list.append(device_entry)

        return jsonify(device_list), 200

    except Exception as e:
        return jsonify({"error": f"Failed to load devices: {str(e)}"}), 500
