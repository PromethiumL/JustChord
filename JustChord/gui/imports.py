import os
import sys


def resource_path(path):
    """Convert relative path to absolute, handling PyInstaller bundles."""
    path = path.replace("/", os.sep)
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath("."), path)
