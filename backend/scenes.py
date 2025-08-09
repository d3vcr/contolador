"""
Scenes module for saving and loading DMX configurations.
"""

import json
import logging

def save_scene(dmx_data, path):
    try:
        with open(path, 'w') as f:
            json.dump(list(dmx_data), f)
        logging.info(f"Scene saved to {path}")
    except Exception as e:
        logging.error(f"Error saving scene: {e}")

def load_scene(path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        logging.info(f"Scene loaded from {path}")
        return data
    except Exception as e:
        logging.error(f"Error loading scene: {e}")
        return [0] * 512
