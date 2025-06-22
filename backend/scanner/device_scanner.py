import scapy.all as scapy
import socket
import json
import os
from datetime import datetime

TRACKING_FILE = "device_tracking.json"

def load_tracking_data():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    return {}

def save_tracking_data(data):
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=4)

def scan_network(ip_range):
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    tracking_data = load_tracking_data()
    current_time = datetime.now().isoformat()

    devices = []

    for sent, received in answered:
        ip = received.psrc
        mac = received.hwsrc

        # Try to resolve hostname
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except socket.herror:
            hostname = "Unknown"

        # Update or create tracking entry
        if mac not in tracking_data:
            tracking_data[mac] = {
                "ip": ip,
                "hostname": hostname,
                "first_seen": current_time,
                "last_seen": current_time
            }
        else:
            tracking_data[mac]["ip"] = ip  # Update IP in case it's changed
            tracking_data[mac]["hostname"] = hostname
            tracking_data[mac]["last_seen"] = current_time

        devices.append({
            "ip": ip,
            "mac": mac,
            "hostname": hostname,
            "first_seen": tracking_data[mac]["first_seen"],
            "last_seen": tracking_data[mac]["last_seen"]
        })

    save_tracking_data(tracking_data)
    return devices

# Example usage
if __name__ == "__main__":
    ip_range = "192.168.100.1/24"  # Modify this to match your network
    devices = scan_network(ip_range)

    print("\nDetected Devices:\n-----------------")
    for device in devices:
        print(f"IP: {device['ip']}, MAC: {device['mac']}, Hostname: {device['hostname']}")
        print(f"   First Seen: {device['first_seen']}")
        print(f"   Last Seen:  {device['last_seen']}\n")
