import scapy.all as scapy            # For sending ARP requests to discover devices
import socket                        # For resolving hostnames
import json                          # For saving/loading device tracking info
import os                            # For file and directory operations
from datetime import datetime        # For timestamping first_seen and last_seen
import netifaces                     # To get the gateway IP of the network

# Path where tracking data will be stored
DATA_DIR = "backend/data"
TRACKING_FILE = os.path.join(DATA_DIR, "device_tracking.json")

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def get_gateway_ip():
    """
    Get the IP address of the default gateway (router).
    """
    gateways = netifaces.gateways()
    default_gateway = gateways['default'][netifaces.AF_INET][0]
    return default_gateway

def load_tracking_data():
    """
    Load existing tracking data from JSON file.
    If file doesn't exist, return empty dict.
    """
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    return {}

def save_tracking_data(data):
    """
    Save updated tracking data to JSON file.
    """
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=4)

def scan_network(ip_range):
    """
    Perform ARP scan to find devices on the network.
    Also update tracking data with timestamps and hostnames.
    """
    # Create ARP request packet
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    # Send request and collect responses
    answered = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    tracking_data = load_tracking_data()
    current_time = datetime.now().isoformat()
    devices = []

    for sent, received in answered:
        ip = received.psrc
        mac = received.hwsrc

        # Try to resolve hostname via reverse DNS
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except socket.herror:
            hostname = "Unknown"

        # Initialize or update device entry in tracking data
        if mac not in tracking_data:
            tracking_data[mac] = {
                "ip": ip,
                "hostname": hostname,
                "first_seen": current_time,
                "last_seen": current_time
            }
        else:
            tracking_data[mac]["ip"] = ip  # In case IP changes
            tracking_data[mac]["hostname"] = hostname
            tracking_data[mac]["last_seen"] = current_time

        # Calculate online duration
        first_seen = datetime.fromisoformat(tracking_data[mac]["first_seen"])
        last_seen = datetime.fromisoformat(tracking_data[mac]["last_seen"])
        online_duration = str(last_seen - first_seen)

        # Add device to response list
        devices.append({
            "ip": ip,
            "mac": mac,
            "hostname": hostname,
            "first_seen": tracking_data[mac]["first_seen"],
            "last_seen": tracking_data[mac]["last_seen"],
            "online_duration": str(datetime.fromisoformat(tracking_data[mac]["last_seen"]) - datetime.fromisoformat(tracking_data[mac]["first_seen"])),
            "status": "online"  # New field added
        })

    # Save updated tracking info
    save_tracking_data(tracking_data)
    return devices

# Run manually from CLI
if __name__ == "__main__":
    gateway_ip = get_gateway_ip()
    ip_range = gateway_ip + "/24"  # e.g., "192.168.100.1/24"

    devices = scan_network(ip_range)

    print("\nDetected Devices:\n-----------------")
    for device in devices:
        print(f"IP: {device['ip']}, MAC: {device['mac']}, Hostname: {device['hostname']}")
        print(f"   First Seen:     {device['first_seen']}")
        print(f"   Last Seen:      {device['last_seen']}")
        print(f"   Online Duration:{device['online_duration']}\n")
