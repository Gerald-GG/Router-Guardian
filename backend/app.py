import platform
import subprocess
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/wifi', methods=['GET'])
def get_wifi():
    try:
        system = platform.system()

        if system == 'Linux':
            result = subprocess.check_output(['iwgetid', '--raw'], stderr=subprocess.DEVNULL)
            ssid = result.decode().strip()

        elif system == 'Windows':
            result = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], stderr=subprocess.DEVNULL)
            lines = result.decode(errors='ignore').split('\n')
            ssid = next((line.split(':')[1].strip() for line in lines if 'SSID' in line and 'BSSID' not in line), 'Unknown')

        else:
            ssid = 'Unsupported OS'

        return jsonify({'ssid': ssid or 'Unavailable'})

    except Exception as e:
        print(f"Wi-Fi detection failed: {e}")
        return jsonify({'ssid': 'Unavailable'})


@app.route('/devices', methods=['GET'])
def get_devices():
    # Dummy device list for frontend testing
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
    return jsonify(devices)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
