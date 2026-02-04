"""
JSON handler utilities that integrate with the project's EncryptionService.
Provides safe read/update functions which preserve other keys and optionally
encrypt/decrypt specific fields using an EncryptionService instance.
"""
import json
import os
from typing import Any, Dict, Optional


def load_json(path: str) -> Dict[str, Any]:
    """Load JSON from `path`. Returns empty dict if file not found or invalid."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json(path: str, data: Dict[str, Any]) -> None:
    """Write `data` to `path` atomically (simple overwrite)."""
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_value(path: str, key: str, protecting: Optional[object] = None, encrypted: bool = False) -> Optional[Any]:
    """Get `key` from JSON file at `path`.

    If `encrypted` is True and `protecting` is provided, attempt to decrypt the value.
    Returns None if key is not present.
    """
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
    return get_value(LOADED_USER_PATH, "logged_in_user", protecting=protecting, encrypted=True)


def set_logged_in_user(username: str, protecting: Optional[object] = None, encrypt: bool = True) -> None:
    set_value(LOADED_USER_PATH, "logged_in_user", username, protecting=protecting, encrypt=encrypt)


def get_stored_music() -> Optional[int]:
    val = get_value(LOADED_USER_PATH, "stored_music")
    if val is None:
        return None
    try:
        # Accept numeric or numeric-string values; otherwise return None
        return int(val)
    except (TypeError, ValueError):
        return None


def set_stored_music(track: Optional[int]) -> None:
    # Allow None to clear or skip stored music
    if track is None:
        set_value(LOADED_USER_PATH, "stored_music", None, encrypt=False)
        return

    try:
        set_value(LOADED_USER_PATH, "stored_music", int(track), encrypt=False)
    except (TypeError, ValueError):
        # If track cannot be converted to int, store None instead
        set_value(LOADED_USER_PATH, "stored_music", None, encrypt=False)
