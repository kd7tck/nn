import json
import os
import copy
from typing import Dict, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_json_file(filepath: str) -> Dict[str, Any]:
    """Loads a JSON file and returns its content as a dictionary."""
    with open(filepath, 'r') as f:
        return json.load(f)

def recursive_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merges two dictionaries.

    Args:
        base: The base dictionary (e.g., template).
        override: The overriding dictionary (e.g., character data).

    Returns:
        The merged dictionary.
    """
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = recursive_merge(merged[key], value)
        else:
            merged[key] = value
    return merged

def load_items() -> Dict[str, Dict[str, Any]]:
    """Loads all item definitions from the data/items directory."""
    items = {}
    items_dir = os.path.join(DATA_DIR, "items")
    if os.path.exists(items_dir):
        for filename in os.listdir(items_dir):
            if filename.endswith(".json"):
                item_id = filename[:-5]
                items[item_id] = load_json_file(os.path.join(items_dir, filename))
    return items


def load_templates() -> Dict[str, Dict[str, Any]]:
    """Loads all character templates from the data/templates directory."""
    templates = {}
    templates_dir = os.path.join(DATA_DIR, "templates")
    if os.path.exists(templates_dir):
        for filename in os.listdir(templates_dir):
            if filename.endswith(".json"):
                template_id = filename[:-5]
                templates[template_id] = load_json_file(os.path.join(templates_dir, filename))
    return templates


def load_characters() -> Dict[str, Dict[str, Any]]:
    """Loads all character definitions from the data/characters directory.

    Supports character templates by merging template data with character data.
    """
    templates = load_templates()
    characters = {}
    chars_dir = os.path.join(DATA_DIR, "characters")
    if os.path.exists(chars_dir):
        for filename in os.listdir(chars_dir):
            if filename.endswith(".json"):
                char_id = filename[:-5]
                char_data = load_json_file(os.path.join(chars_dir, filename))

                if "template" in char_data:
                    template_id = char_data["template"]
                    if template_id in templates:
                        # Recursively merge character data over the template
                        char_data = recursive_merge(templates[template_id], char_data)
                    else:
                        print(f"Warning: Template '{template_id}' not found for character '{char_id}'")

                characters[char_id] = char_data
    return characters

def load_global_data() -> Dict[str, Any]:
    """Loads global game data from data/global.json."""
    global_path = os.path.join(DATA_DIR, "global.json")
    if os.path.exists(global_path):
        return load_json_file(global_path)
    return {}

def load_world_data() -> Dict[str, Dict[str, Any]]:
    """Loads the entire world data including rooms, items, and characters.

    Combines data from separate files into the structure expected by the Game class.
    """
    items_data = load_items()
    chars_data = load_characters()
    rooms_data = {}

    rooms_dir = os.path.join(DATA_DIR, "rooms")
    if os.path.exists(rooms_dir):
        for filename in os.listdir(rooms_dir):
            if filename.endswith(".json"):
                room = load_json_file(os.path.join(rooms_dir, filename))
                room_id = room.get("id", filename[:-5])

                # Process items
                room_items = []
                for item_ref in room.get("items", []):
                    if isinstance(item_ref, str):
                        if item_ref in items_data:
                            # Create a deep copy to ensure independence
                            room_items.append(copy.deepcopy(items_data[item_ref]))
                        else:
                            print(f"Warning: Item '{item_ref}' not found for room '{room_id}'")
                    else:
                        room_items.append(item_ref)
                room["items"] = room_items

                # Process characters
                room_chars = []
                for char_ref in room.get("characters", []):
                    if isinstance(char_ref, str):
                        if char_ref in chars_data:
                            room_chars.append(copy.deepcopy(chars_data[char_ref]))
                        else:
                            print(f"Warning: Character '{char_ref}' not found for room '{room_id}'")
                    else:
                        room_chars.append(char_ref)
                room["characters"] = room_chars

                # Process nth_arrival_text keys (convert string keys to int)
                if "nth_arrival_text" in room:
                    new_nth = {}
                    for k, v in room["nth_arrival_text"].items():
                        try:
                            new_nth[int(k)] = v
                        except ValueError:
                            new_nth[k] = v
                    room["nth_arrival_text"] = new_nth

                rooms_data[room_id] = room

    return rooms_data
