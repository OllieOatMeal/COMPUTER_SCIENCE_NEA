"""
Reads and writes JSON files for storing settings and user data
Can optionally encrypt/decrypt values using the EncryptionService
"""
import json
import os
from typing import Any, Dict, Optional


def load_json(path: str) -> Dict[str, Any]:
    """Load a JSON file and return the data as a dict"""
    # Read JSON safely and just return {} on errors
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json(path: str, data: Dict[str, Any]) -> None:
    """Save a dict to a JSON file"""
    # Make folders if needed then write JSON
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_value(path: str, key: str, protecting: Optional[object] = None, encrypted: bool = False) -> Optional[Any]:
    """Get a value from a JSON file and optionally decrypt it"""
    # Pull one key and decrypt if needed
    data = load_json(path)
    if key not in data:
        return None

    value = data[key]
    if encrypted and protecting is not None and value is not None:
        try:
            return protecting.decrypt(value)
        except Exception:
            # Fallback: return raw stored value if decryption fails (backwards compat)
            return value
    return value


def set_value(path: str, key: str, value: Any, protecting: Optional[object] = None, encrypt: bool = False) -> None:
    """Set `key` to `value` inside JSON file at `path`.

    Reads existing file, updates the single key, and writes file back preserving other keys.
    If `encrypt` is True and `protecting` is provided, the `value` will be encrypted before saving.
    """
    # Update one key while keeping everything else intact
    data = load_json(path)

    store_value = value
    if encrypt and protecting is not None and value is not None:
        # Ensure we operate on strings for encryption
        store_value = protecting.encrypt(str(value))

    data[key] = store_value

    save_json(path, data)


# Convenience helpers for database/loaded_user.json
LOADED_USER_PATH = os.path.join("database", "loaded_user.json")


def get_logged_in_user(protecting: Optional[object] = None) -> Optional[str]:
    # Grab stored username if there is one
    return get_value(LOADED_USER_PATH, "logged_in_user", protecting=protecting, encrypted=True)


def set_logged_in_user(username: Optional[str], protecting: Optional[object] = None, encrypt: bool = True) -> None:
    # Save or clear the current user
    set_value(LOADED_USER_PATH, "logged_in_user", username, protecting=protecting, encrypt=encrypt)


def get_stored_music() -> Optional[int]:
    # Read the saved track number and coerce it to int
    val = get_value(LOADED_USER_PATH, "stored_music")
    if val is None:
        return None
    try:
        # Accept numeric or numeric-string values; otherwise return None
        return int(val)
    except (TypeError, ValueError):
        return None


def set_stored_music(track: Optional[int]) -> None:
    # Store track number or clear it when None
    # Allow None to clear or skip stored music
    if track is None:
        set_value(LOADED_USER_PATH, "stored_music", None, encrypt=False)
        return

    try:
        set_value(LOADED_USER_PATH, "stored_music", int(track), encrypt=False)
    except (TypeError, ValueError):
        # If track cannot be converted to int, store None instead
        set_value(LOADED_USER_PATH, "stored_music", None, encrypt=False)


def get_music_volume() -> Optional[int]:
    """Return stored music volume (0-100) or None if not set."""
    # Read volume and clamp to 0-100
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


def set_music_volume(volume: Optional[int]) -> None:
    """Store music volume (0-100). Use None to clear."""
    # Write a clamped volume or clear it
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


def get_music_muted() -> Optional[bool]:
    """Return stored mute state or None if not set."""
    # Accept a few types for backwards compat
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


def set_music_muted(is_muted: Optional[bool]) -> None:
    """Store music muted state. Use None to clear."""
    # Store boolean muted state or clear it
    if is_muted is None:
        set_value(LOADED_USER_PATH, "music_muted", None, encrypt=False)
        return
    set_value(LOADED_USER_PATH, "music_muted", bool(is_muted), encrypt=False)
