import json
import os

# Settings management
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')

def load_settings():
    """Load application settings from file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_settings(settings):
    """Save application settings to file"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving settings: {e}")