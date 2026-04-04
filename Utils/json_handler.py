"""

# Code to use the json file

"""

"""
# Import nessicary functions/ procedures
"""
import json
import os
from typing import Any, Dict, Optional

# Loads the json file
def load_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Saves the json file
def save_json(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Gets the data stored on the json file
def get_value(path: str, key: str, protecting: Optional[object] = None, encrypted: bool = False) -> Optional[Any]:
    data = load_json(path)
    if key not in data:
        return None

    value = data[key]
    if encrypted and protecting is not None and value is not None:
        try:
            return protecting.decrypt(value)
        except Exception:
            return value
    return value

# Sets data stored on the json file
def set_value(path: str, key: str, value: Any, protecting: Optional[object] = None, encrypt: bool = False) -> None:
    data = load_json(path)

    store_value = value
    if encrypt and protecting is not None and value is not None:
        store_value = protecting.encrypt(str(value))

    data[key] = store_value

    save_json(path, data)

LOADED_USER_PATH = os.path.join("database", "loaded_user.json")

# Gets the current logged in user
def get_logged_in_user(protecting: Optional[object] = None) -> Optional[str]:
    return get_value(LOADED_USER_PATH, "logged_in_user", protecting=protecting, encrypted=True)

# Sets the current logged in user
def set_logged_in_user(username: Optional[str], protecting: Optional[object] = None, encrypt: bool = True) -> None:
    set_value(LOADED_USER_PATH, "logged_in_user", username, protecting=protecting, encrypt=encrypt)

# Gets the current stored music
def get_stored_music() -> Optional[int]:
    val = get_value(LOADED_USER_PATH, "stored_music")
    if val is None:
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None

# Sets the current stored music
def set_stored_music(track: Optional[int]) -> None:
    if track is None:
        set_value(LOADED_USER_PATH, "stored_music", None, encrypt=False)
        return

    try:
        set_value(LOADED_USER_PATH, "stored_music", int(track), encrypt=False)
    except (TypeError, ValueError):
        set_value(LOADED_USER_PATH, "stored_music", None, encrypt=False)

# Gets the current music volume
def get_music_volume() -> Optional[int]:
    val = get_value(LOADED_USER_PATH, "music_volume")
    if val is None:
        return None
    try:
        volume = int(val)
        if volume < 0:
            return 0
        if volume > 100:
            return 100
        return volume
    except (TypeError, ValueError):
        return None

# Sets the current music volume
def set_music_volume(volume: Optional[int]) -> None:
    if volume is None:
        set_value(LOADED_USER_PATH, "music_volume", None, encrypt=False)
        return
    try:
        volume_int = int(volume)
        if volume_int < 0:
            volume_int = 0
        if volume_int > 100:
            volume_int = 100
        set_value(LOADED_USER_PATH, "music_volume", volume_int, encrypt=False)
    except (TypeError, ValueError):
        set_value(LOADED_USER_PATH, "music_volume", None, encrypt=False)

# Gets the state of the music
def get_music_muted() -> Optional[bool]:
    val = get_value(LOADED_USER_PATH, "music_muted")
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        lowered = val.strip().lower()
        if lowered in ["true", "1", "yes", "y"]:
            return True
        if lowered in ["false", "0", "no", "n"]:
            return False
    if isinstance(val, (int, float)):
        return bool(val)
    return None

# Sets the state of the music
def set_music_muted(is_muted: Optional[bool]) -> None:
    if is_muted is None:
        set_value(LOADED_USER_PATH, "music_muted", None, encrypt=False)
        return
    set_value(LOADED_USER_PATH, "music_muted", bool(is_muted), encrypt=False)