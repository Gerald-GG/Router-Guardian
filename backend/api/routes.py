from flask import Blueprint, jsonify
from scanner.device_scanner import get_gateway_ip, scan_network

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
