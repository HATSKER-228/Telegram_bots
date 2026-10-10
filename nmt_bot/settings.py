"""
Налаштування користувачів (поки що лише перемішування кнопок).
Зберігаються у user_settings.json поруч із ботом, щоб не губитись після перезапуску.
"""
import json
from pathlib import Path

SETTINGS_PATH = Path(__file__).parent / "user_settings.json"


def _load() -> dict:
    try:
        with SETTINGS_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data: dict) -> None:
    with SETTINGS_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_shuffle(user_id: int) -> bool:
    return bool(_load().get(str(user_id), {}).get("shuffle", False))


def toggle_shuffle(user_id: int) -> bool:
    """Перемикає налаштування і повертає нове значення."""
    data = _load()
    user = data.setdefault(str(user_id), {})
    user["shuffle"] = not user.get("shuffle", False)
    _save(data)
    return user["shuffle"]
