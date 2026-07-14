import json
from pathlib import Path


DEFAULT_MEMORY = {
    "profile": "default",
    "facts": [],
    "accessibility": {
        "profiles": {
            "adhd": False,
            "autism": False,
            "dyslexia": False,
            "mobility": False,
            "simple": False,
            "low_vision": False,
        }
    },
    "settings": {
        "tts": False,
        "voice": False,
        "model": "gemma2:2b",
    },
    "pdf": {
        "current_file": None,
        "current_page": 1,
        "page_count": 0,
    },
}


def deep_merge(defaults, current):
    if not isinstance(defaults, dict):
        return current

    merged = dict(defaults)
    if not isinstance(current, dict):
        return merged

    for key, value in current.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def migrate_legacy_flags(memory):
    accessibility = memory.setdefault("accessibility", {})
    profiles = accessibility.setdefault("profiles", {})

    if accessibility.pop("dyslexia_mode", False):
        profiles["dyslexia"] = True
    if accessibility.pop("simple_language", False):
        profiles["simple"] = True

    legacy_profile = memory.get("profile")
    if legacy_profile in profiles:
        profiles[legacy_profile] = True

    settings = memory.setdefault("settings", {})
    settings.setdefault("tts", False)
    settings.setdefault("voice", False)

    return memory


def load_memory(path):
    memory_path = Path(path)
    if not memory_path.exists():
        memory = DEFAULT_MEMORY
        save_memory(memory_path, memory)
        return memory

    with memory_path.open("r", encoding="utf-8") as file:
        loaded = json.load(file)

    memory = deep_merge(DEFAULT_MEMORY, loaded)
    memory = migrate_legacy_flags(memory)
    save_memory(memory_path, memory)
    return memory


def save_memory(path, memory):
    memory_path = Path(path)
    with memory_path.open("w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4)
        file.write("\n")
