"""
Layout preset manager for storing and loading privacy mask setups.
"""

import os
import json
from typing import Dict, Any, List

CONFIG_DIR = os.path.expanduser("~/.screen_cloak")
CONFIG_FILE = os.path.join(CONFIG_DIR, "presets.json")

def load_presets() -> Dict[str, List[Dict[str, Any]]]:
    if not os.path.exists(CONFIG_FILE):
        return {
            "默认预设": [
                {"x": 150, "y": 150, "w": 400, "h": 70, "label": "API_SECRET", "style": "redacted"}
            ]
        }
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_presets(presets: Dict[str, List[Dict[str, Any]]]):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(presets, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Failed to save presets: {e}")
