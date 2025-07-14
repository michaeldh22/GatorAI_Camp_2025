# Check for and install the pytmx module

import os
import sys
import subprocess
import importlib


def install(package_name):
    # Map package names to their import names
    package_import_map = {
        "opencv-python": "cv2",
        "pytorch_lightning": "pytorch_lightning",
    }

    # Get the actual import name
    import_name = package_import_map.get(package_name, package_name)

    try:
        importlib.import_module(import_name)
        print(f"{package_name} is already installed.")
    except ImportError:
        print(f"{package_name} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"{package_name} installed.")
