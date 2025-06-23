# backend/router_control/router_interface.py

import importlib
import json
import os

# Load router profiles to identify brand and credentials
PROFILE_PATH = "config/router_profiles.json"

class RouterInterface:
    """
    Base class defining interface for router control.
    Brand-specific classes must override login(), block_device(), and unblock_device().
    """
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password

    def login(self):
        raise NotImplementedError("Router login not implemented")

    def block_device(self, mac_address):
        raise NotImplementedError("Blocking not implemented")

    def unblock_device(self, mac_address):
        raise NotImplementedError("Unblocking not implemented")

def get_router_controller():
    """Load the appropriate brand controller based on router_profiles.json"""
    if not os.path.exists(PROFILE_PATH):
        raise FileNotFoundError("Router profile config not found")

    with open(PROFILE_PATH) as f:
        profile = json.load(f)

    brand = profile.get("brand")
    ip = profile.get("ip")
    username = profile.get("username")
    password = profile.get("password")

    if not brand:
        raise ValueError("Router brand not specified in profile")

    try:
        # Dynamically import the brand-specific module
        module = importlib.import_module(f"router_control.brand_scripts.{brand.lower()}")
        controller_class = getattr(module, "RouterController")
        return controller_class(ip, username, password)
    except (ModuleNotFoundError, AttributeError):
        raise ImportError(f"No controller found for router brand '{brand}'")
