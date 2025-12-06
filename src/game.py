"""The main game logic for the text-based game.

This module contains the Game class, which manages the game's state,
including the player's location, inventory, and the world map.
"""
import json
from collections import defaultdict
from src.loader import load_world_data, load_global_data
from src.time_system import TimeSystem


class Game:
    """Manages the game's state and logic.

    This class handles the core mechanics of the game, including player movement,
    interaction with items, and tracking the state of the world.
    """

    def __init__(self):
        """Initializes the Game class.

        Sets up the initial player location, inventory, visited counts, and the world map.

        Args:
            None

        Returns:
            None
        """
        self.player_location = "start"
        self.inventory = []
        self.visited_counts = defaultdict(int)
        self.visited_counts["start"] = 1
        self.game_state = {}
        self.player_stats = {
            "hp": 100,
            "max_hp": 100,
            "str": 10,
            "def": 10,
            "spd": 10
        }

        self.dialogue_active = False
        self.current_dialogue = None
        self.current_dialogue_node_id = None
        self.current_character_name = None
        self.processing_global_events = False

        self.time_system = TimeSystem()

        self._init_world_map()
        self._init_global_data()

    def save_game(self, filename):
        """Saves the current game state to a file.

        Args:
            filename: The name of the file to save to.

        Returns:
            str: A message indicating the result of the save operation.
        """
        try:
            data = {
                "player_location": self.player_location,
                "inventory": self.inventory,
                "visited_counts": dict(self.visited_counts),
                "game_state": self.game_state,
                "world_map": self.world_map,
                "player_stats": self.player_stats,
                "time_system": self.time_system.to_dict(),
                "global_events": self.global_events
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            return f"Game saved to {filename}."
        except Exception as e:
            return f"Error saving game: {e}"

    def load_game(self, filename):
        """Loads a game state from a file.

        Args:
            filename: The name of the file to load from.

        Returns:
            str: A message indicating the result of the load operation.
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            self.player_location = data["player_location"]
            self.inventory = data["inventory"]
            self.visited_counts = defaultdict(int, data["visited_counts"])
            self.game_state = data["game_state"]
            self.world_map = data["world_map"]
            self.player_stats = data.get("player_stats", {
                "hp": 100,
                "max_hp": 100,
                "str": 10,
                "def": 10,
                "spd": 10
            })
            self.global_events = data.get("global_events", [])

            if "time_system" in data:
                self.time_system.from_dict(data["time_system"])
            else:
                self.time_system = TimeSystem()

            return f"Game loaded from {filename}."
        except FileNotFoundError:
            return f"Save file {filename} not found."
        except Exception as e:
            return f"Error loading game: {e}"

    def _name_matches(self, item_name, input_name):
        """Checks if the user input matches the item name, allowing for articles.

        Args:
            item_name: The actual name of the item.
            input_name: The name provided by the user.

        Returns:
            bool: True if it matches, False otherwise.
        """
        if item_name == input_name:
            return True
        if input_name == f"the {item_name}":
            return True
        if input_name == f"a {item_name}":
            return True
        if input_name == f"an {item_name}":
            return True
        return False

    def _init_world_map(self):
        self.world_map = load_world_data()

    def _init_global_data(self):
        data = load_global_data()
        self.global_events = data.get("events", [])

    def check_condition(self, condition):
        """Checks if a condition is met.

        Args:
            condition: A dictionary defining the condition.

        Returns:
            bool: True if the condition is met, False otherwise.
        """
        if not condition:
            return True

        if "not" in condition:
            if self.check_condition(condition["not"]):
                return False

        if "has_item" in condition:
            item_name = condition["has_item"]
            found, _, _ = self._find_item_recursive(self.inventory, item_name)
            if not found:
                return False

        if "in_location" in condition:
            if self.player_location != condition["in_location"]:
                return False

        if "var_true" in condition:
            var_name = condition["var_true"]
            if not self.game_state.get(var_name, False):
                return False

        if "var_false" in condition:
            var_name = condition["var_false"]
            if self.game_state.get(var_name, False):
                return False

        if "var_eq" in condition:
            for var_name, value in condition["var_eq"].items():
                if self.game_state.get(var_name) != value:
                    return False

        if "player_stat_ge" in condition:
            for stat, val in condition["player_stat_ge"].items():
                if self.player_stats.get(stat, 0) < val:
                    return False

        if "player_stat_le" in condition:
            for stat, val in condition["player_stat_le"].items():
                if self.player_stats.get(stat, 0) > val:
                    return False

        # Time conditions
        if "time_ge" in condition:
            if self.time_system.total_minutes < condition["time_ge"]:
                return False
        if "time_le" in condition:
            if self.time_system.total_minutes > condition["time_le"]:
                return False
        if "time_eq" in condition:
            if self.time_system.total_minutes != condition["time_eq"]:
                return False

        # Visited condition
        if "visited" in condition:
            room_id = condition["visited"].get("room")
            count = condition["visited"].get("count", 1)
            op = condition["visited"].get("op", "ge") # ge, le, eq
            visited_count = self.visited_counts.get(room_id, 0)

            if op == "ge" and visited_count < count:
                return False
            elif op == "le" and visited_count > count:
                return False
            elif op == "eq" and visited_count != count:
                return False

        # Item state condition
        if "item_state" in condition:
            item_name = condition["item_state"].get("item")
            prop = condition["item_state"].get("property")
            value = condition["item_state"].get("value")

            # Find item
            target_item = None
            # Check inventory
            found, _, _ = self._find_item_recursive(self.inventory, item_name)
            if found:
                target_item = found
            else:
                # Check room
                found, _, _ = self._find_item_recursive(self.world_map[self.player_location]["items"], item_name)
                if found:
                    target_item = found
                else:
                     # Check all rooms? Expensive but maybe needed.
                     # For now let's assume item must be near.
                     # Actually, users might want to check state of item anywhere.
                     # Let's search all rooms.
                     for room in self.world_map.values():
                         found, _, _ = self._find_item_recursive(room["items"], item_name)
                         if found:
                             target_item = found
                             break

            if not target_item:
                return False # Item not found, condition fails

            if target_item.get(prop) != value:
                return False

        # Check NPC stats (only valid if we are in a dialogue with a character)
        if ("npc_stat_ge" in condition or "npc_stat_le" in condition) and self.current_character_name:
            current_npc = None
            room = self.world_map[self.player_location]
            if "characters" in room:
                for char in room["characters"]:
                    if char["name"] == self.current_character_name:
                        current_npc = char
                        break

            if current_npc:
                npc_stats = current_npc.get("stats", {})

                if "npc_stat_ge" in condition:
                    for stat, val in condition["npc_stat_ge"].items():
                        if npc_stats.get(stat, 0) < val:
                            return False

                if "npc_stat_le" in condition:
                    for stat, val in condition["npc_stat_le"].items():
                        if npc_stats.get(stat, 0) > val:
                            return False
            else:
                # If checking NPC stats but NPC not found, fail safely?
                # Or assume false? Assuming false seems safer.
                return False

        return True

    def check_global_events(self):
        """Checks and processes global events.

        Returns:
             list: List of messages from triggered events.
        """
        if self.processing_global_events:
            return []

        self.processing_global_events = True
        messages = []

        try:
            if not hasattr(self, 'global_events'):
                return messages

            for event in self.global_events:
                # Skip if not repeatable and already triggered
                if not event.get("repeatable", False) and event.get("triggered", False):
                    continue

                if self.check_condition(event.get("condition")):
                    # Mark as triggered
                    event["triggered"] = True

                    for action in event.get("actions", []):
                        msg = self.perform_action(action)
                        if msg:
                            messages.append(msg)
        finally:
            self.processing_global_events = False

        return messages

    def pass_time(self, minutes):
        """Advances time and processes triggered events.

        Args:
            minutes: Number of minutes to advance.

        Returns:
            list: List of messages from triggered events.
        """
        triggered_actions = self.time_system.advance_time(minutes)
        messages = []
        for action in triggered_actions:
            msg = self.perform_action(action)
            if msg:
                messages.append(msg)

        # Check global events after time passes
        global_msgs = self.check_global_events()
        messages.extend(global_msgs)

        return messages

    def perform_action(self, action):
        """Performs an action.

        Args:
            action: A dictionary defining the action.

        Returns:
            str: A message if the action produces output, None otherwise.
        """
        action_type = action.get("type")

        if action_type == "print":
            return action.get("message")

        elif action_type == "start_timer":
            minutes = action.get("minutes", 0)
            timer_actions = action.get("actions", [])
            self.time_system.schedule_event(minutes, timer_actions)

        elif action_type == "set_true":
            self.game_state[action["target"]] = True

        elif action_type == "set_false":
            self.game_state[action["target"]] = False

        elif action_type == "set_val":
            self.game_state[action["target"]] = action["value"]

        elif action_type == "modify_room":
            room_id = action.get("room_id")
            if room_id in self.world_map:
                self.world_map[room_id][action["property"]] = action["value"]

        elif action_type == "add_item":
            item = action.get("item")
            if item:
                self.inventory.append(item)

        elif action_type == "remove_item":
            item_name = action.get("item_name")
            for item in self.inventory:
                 if item["name"] == item_name:
                      self.inventory.remove(item)
                      break

        elif action_type == "modify_player_stat":
            stat = action["stat"]
            value = action["value"]
            op = action.get("operation", "set")
            if op == "add":
                 self.player_stats[stat] = self.player_stats.get(stat, 0) + value
            elif op == "sub":
                 self.player_stats[stat] = self.player_stats.get(stat, 0) - value
            else: # set
                 self.player_stats[stat] = value

            # Check global events immediately after stat change
            # But we can't easily return messages here if perform_action only returns one string.
            # However, perform_action returns ONE message. If check_global_events returns multiple,
            # we might lose some if we don't handle it.
            # For now, let's just print them or append to a queue?
            # Or better, let's make perform_action capable of returning list or we handle it in caller.
            # But caller expects single string or None.
            # Let's concatenate with newline.
            msgs = self.check_global_events()
            if msgs:
                return "\n".join(msgs)

        elif action_type == "modify_item":
            item_name = action.get("item_name")
            prop = action.get("property")
            value = action.get("value")

            target_item = None
            found, _, _ = self._find_item_recursive(self.inventory, item_name)
            if found:
                target_item = found
            else:
                 for room in self.world_map.values():
                     found, _, _ = self._find_item_recursive(room["items"], item_name)
                     if found:
                         target_item = found
                         break

            if target_item:
                target_item[prop] = value

                # Check global events immediately after item change
                msgs = self.check_global_events()
                if msgs:
                    return "\n".join(msgs)

        elif action_type == "move_player":
            location = action.get("location")
            if location in self.world_map:
                self.player_location = location
                # Should we trigger enter/exit events?
                # The existing move_player does heavy lifting.
                # But this is a "teleport".
                # Let's just update visited counts and maybe look?
                self.visited_counts[location] += 1
                return self.get_location_description(arrival=True)

        elif action_type == "end_game":
             # Simple flag for now, control loop handles it if it checks game_active
             # But Game class doesn't have game_active flag explicitly shown in init?
             # It has game_state.
             self.game_state["game_over"] = True
             return "GAME OVER"

        return None

    def process_events(self, source, trigger):
        """Processes events for a given source and trigger.

        Args:
            source: The dictionary containing the events (room or item).
            trigger: The trigger string (e.g., 'enter', 'take').

        Returns:
            tuple: A tuple (messages, blocked).
                messages (list): A list of messages produced by the events.
                blocked (bool): True if an action blocked the operation, False otherwise.
        """
        messages = []
        blocked = False
        if "events" in source and trigger in source["events"]:
            for event in source["events"][trigger]:
                if self.check_condition(event.get("condition")):
                    for action in event.get("actions", []):
                        if action.get("type") == "block":
                            blocked = True
                            if "message" in action:
                                messages.append(action["message"])
                            # If blocked, we usually stop processing further events for this trigger
                            # or at least signal blocking.
                            return messages, blocked

                        msg = self.perform_action(action)
                        if msg:
                            messages.append(msg)
        return messages, blocked

    def _get_article(self, word):
        """Determines the appropriate indefinite article ('a' or 'an') for a word.

        Args:
            word: The word to determine the article for.

        Returns:
            str: 'a' or 'an'.
        """
        if not word:
            return ""
        if word[0].lower() in "aeiou":
            return "an"
        return "a"

    def _format_item_list(self, items):
        """Formats a list of item names into a grammatically correct string.

        Args:
            items: A list of item dictionaries.

        Returns:
            str: A formatted string listing the items (e.g., "a sword and an apple").
        """
        if not items:
            return ""

        formatted_items = []
        for item in items:
            name = item["name"]
            article = self._get_article(name)
            formatted_items.append(f"{article} {name}")

        if len(formatted_items) == 1:
            return formatted_items[0]
        elif len(formatted_items) == 2:
            return f"{formatted_items[0]} and {formatted_items[1]}"
        else:
            return f"{', '.join(formatted_items[:-1])}, and {formatted_items[-1]}"

    def get_location_description(self, arrival=False):
        """Returns the description of the player's current location.

        Args:
            arrival: Boolean indicating if the player just arrived at this location.
                Defaults to False.

        Returns:
            str: A string containing the description of the current location,
            including any dynamic text based on visit counts and items present.
        """
        room = self.world_map[self.player_location]
        description_parts = []

        if arrival:
            # Add transition text if present
            if "transition_text" in room:
                description_parts.append(room["transition_text"])

            count = self.visited_counts[self.player_location]

            # Check for first arrival text
            if count == 1 and "first_arrival_text" in room:
                description_parts.append(room["first_arrival_text"])
            # Check for nth arrival text
            elif "nth_arrival_text" in room and count in room["nth_arrival_text"]:
                description_parts.append(room["nth_arrival_text"][count])
            else:
                description_parts.append(room["description"])
        else:
            # Just looking around
            description_parts.append(room["description"])

        items = room["items"]
        if items:
            description_parts.append(f"You see {self._format_item_list(items)}.")

        characters = room.get("characters", [])
        if characters:
            char_names = [char["name"] for char in characters]
            description_parts.append("You see " + ", ".join(char_names) + ".")

        return " ".join(description_parts)

    def move_player(self, direction):
        """Moves the player to a new location.

        Args:
            direction: The direction to move the player (e.g., 'north', 'south').

        Returns:
            str: A message describing the result of the movement attempt,
            such as the new room description or an error message if blocked.
        """
        current_room = self.world_map[self.player_location]
        if direction in current_room["exits"]:
            next_location = current_room["exits"][direction]

            # Check specific directional exit events first (for blocks)
            exit_trigger = f"exit_{direction}"
            msgs, blocked = self.process_events(current_room, exit_trigger)
            if blocked:
                return "\n".join(msgs)

            # Process generic exit events
            generic_exit_msgs, blocked = self.process_events(current_room, "exit")

            if blocked:
                return "\n".join(msgs + generic_exit_msgs)

            # Combine generic exit messages with any non-blocking specific exit messages
            exit_msgs = msgs + generic_exit_msgs

            self.player_location = next_location
            self.visited_counts[next_location] += 1

            # Pass time for movement (1 minute)
            time_msgs = self.pass_time(1)

            # Process enter events
            enter_msgs, _ = self.process_events(self.world_map[next_location], "enter")

            desc = self.get_location_description(arrival=True)

            # Combine all messages
            all_parts = exit_msgs + time_msgs + [desc] + enter_msgs
            return "\n".join(all_parts)
        else:
            return "You can't go that way."

    def _find_item_recursive(self, items_list, item_name, container_name=None):
        """Recursively finds an item in a list of items (and their open containers).

        Args:
            items_list: The list of items to search.
            item_name: The name of the item to find.
            container_name: The name of the container these items are in (for message context).

        Returns:
            tuple: (item, parent_list, source_name)
                   item: The found item dictionary.
                   parent_list: The list containing the item (to allow removal).
                   source_name: Name of the container or None if top-level.
        """
        for item in items_list:
            if self._name_matches(item["name"], item_name):
                return item, items_list, container_name

            if item.get("is_container") and item.get("is_open"):
                found, parent, source = self._find_item_recursive(
                    item.get("contents", []),
                    item_name,
                    item["name"]
                )
                if found:
                    return found, parent, source

        return None, None, None

    def take_item(self, item_name):
        """Takes an item from the current location or a container and adds it to the player's inventory.

        Args:
            item_name: The name of the item to take.

        Returns:
            str: A message indicating whether the item was successfully taken or not.
        """
        # 1. Check current location items (recursive)
        location_items = self.world_map[self.player_location]["items"]
        item, parent, source = self._find_item_recursive(location_items, item_name)

        if item:
            msgs, blocked = self.process_events(item, "take")
            if blocked:
                return "\n".join(msgs)

            parent.remove(item)
            self.inventory.append(item)

            if source:
                msg = f"You take the {item['name']} from the {source}."
            else:
                msg = f"You take the {item['name']}."

            output_msgs = [msg]
            output_msgs.extend(msgs)
            return "\n".join(output_msgs)

        # 2. Check inside open containers in inventory (recursive)
        # We must ignore items that are directly in inventory (not in a container),
        # as the user already has them.
        for inv_item in self.inventory:
            if inv_item.get("is_container") and inv_item.get("is_open"):
                item, parent, source = self._find_item_recursive(
                    inv_item.get("contents", []),
                    item_name,
                    inv_item["name"]
                )
                if item:
                    msgs, blocked = self.process_events(item, "take")
                    if blocked:
                        return "\n".join(msgs)

                    parent.remove(item)
                    self.inventory.append(item)

                    msg = f"You take the {item['name']} from the {source}."
                    output_msgs = [msg]
                    output_msgs.extend(msgs)
                    return "\n".join(output_msgs)

        return f"There is no {item_name} here."

    def put_item(self, item_name, container_name):
        """Puts an item from inventory into a container (in inventory or room).

        Args:
            item_name: The name of the item to put.
            container_name: The name of the container.

        Returns:
            str: Result message.
        """
        # Find item in inventory
        item_to_put = None
        for item in self.inventory:
            if self._name_matches(item["name"], item_name):
                item_to_put = item
                break

        if not item_to_put:
            return f"You don't have a {item_name}."

        # Find container
        target_container = None

        # Check inventory for container
        for item in self.inventory:
            if self._name_matches(item["name"], container_name):
                target_container = item
                break

        # Check room for container
        if not target_container:
            for item in self.world_map[self.player_location]["items"]:
                if self._name_matches(item["name"], container_name):
                    target_container = item
                    break

        if not target_container:
            return f"You don't see a {container_name} here."

        if not target_container.get("is_container"):
            return f"The {container_name} is not a container."

        if not target_container.get("is_open"):
            return f"The {container_name} is closed."

        if item_to_put is target_container:
            return "You can't put an item inside itself."

        # Move item
        self.inventory.remove(item_to_put)
        if "contents" not in target_container:
            target_container["contents"] = []
        target_container["contents"].append(item_to_put)

        return f"You put the {item_name} in the {container_name}."

    def open_item(self, item_name):
        """Opens a container.

        Args:
            item_name: Name of the item to open.

        Returns:
            str: Result message.
        """
        target = None
        # Check inventory
        for item in self.inventory:
            if self._name_matches(item["name"], item_name):
                target = item
                break
        # Check room
        if not target:
            for item in self.world_map[self.player_location]["items"]:
                if self._name_matches(item["name"], item_name):
                    target = item
                    break

        if not target:
            return f"You don't see a {item_name} here."

        if not target.get("is_container"):
            return f"You can't open that."

        if target.get("is_locked"):
             return f"The {item['name']} is locked."

        if target.get("is_open"):
            return f"The {item['name']} is already open."

        target["is_open"] = True
        return f"You open the {item['name']}."

    def close_item(self, item_name):
        """Closes a container.

        Args:
            item_name: Name of the item to close.

        Returns:
            str: Result message.
        """
        target = None
        # Check inventory
        for item in self.inventory:
            if self._name_matches(item["name"], item_name):
                target = item
                break
        # Check room
        if not target:
            for item in self.world_map[self.player_location]["items"]:
                if self._name_matches(item["name"], item_name):
                    target = item
                    break

        if not target:
            return f"You don't see a {item_name} here."

        if not target.get("is_container"):
            return f"You can't close that."

        if not target.get("is_open"):
            return f"The {item['name']} is already closed."

        target["is_open"] = False
        return f"You close the {item['name']}."

    def drop_item(self, item_name):
        """Drops an item from the player's inventory into the current location.

        Args:
            item_name: The name of the item to drop.

        Returns:
            str: A message indicating whether the item was successfully dropped or not.
        """
        for item in self.inventory:
            if self._name_matches(item["name"], item_name):
                msgs, blocked = self.process_events(item, "drop")

                if blocked:
                    return "\n".join(msgs)

                self.inventory.remove(item)
                self.world_map[self.player_location]["items"].append(item)

                output_msgs = [f"You drop the {item['name']}."]
                output_msgs.extend(msgs)

                return "\n".join(output_msgs)
        return f"You don't have a {item_name}."

    def get_inventory(self):
        """Returns the player's inventory.

        Returns:
            str: A string listing the items currently in the player's inventory.
        """
        if self.inventory:
            item_names = [item["name"] for item in self.inventory]
            return "You are carrying: " + ", ".join(item_names) + "."
        else:
            return "Your inventory is empty."

    def _get_examination_desc(self, item):
        """Helper to get the examination description of an item.

        Args:
            item: The item dictionary.

        Returns:
            str: The full examination description including contents and events.
        """
        msgs, _ = self.process_events(item, "examine")
        desc = item["description"]
        if item.get("is_container") and item.get("is_open"):
            contents = item.get("contents", [])
            if contents:
                desc += f" It contains: {self._format_item_list(contents)}."
            else:
                desc += " It is empty."
        elif item.get("is_container") and not item.get("is_open"):
            desc += " It is closed."

        if msgs:
            return desc + "\n" + "\n".join(msgs)
        return desc

    def examine_item(self, item_name):
        """Examines an item in the player's inventory or the current location.

        Also allows examining the room itself.

        Args:
            item_name: The name of the item to examine, or 'room'/'here' to examine the room.

        Returns:
            str: The description of the item or room, or a message if the item is not found.
        """
        if item_name in ["room", "here"] or self._name_matches("room", item_name):
            room = self.world_map[self.player_location]
            # Process examine events for room
            msgs, _ = self.process_events(room, "examine")
            desc = room.get("examination_text", room["description"])
            if msgs:
                return desc + "\n" + "\n".join(msgs)
            return desc

        # Check inventory (including nested)
        item, _, _ = self._find_item_recursive(self.inventory, item_name)
        if item:
            return self._get_examination_desc(item)

        # Check current location items (including nested)
        item, _, _ = self._find_item_recursive(self.world_map[self.player_location]["items"], item_name)
        if item:
            return self._get_examination_desc(item)

        # Check current location characters
        room = self.world_map[self.player_location]
        if "characters" in room:
            for char in room["characters"]:
                if self._name_matches(char["name"], item_name):
                    msgs, _ = self.process_events(char, "examine")
                    desc = char["description"]
                    if msgs:
                        return desc + "\n" + "\n".join(msgs)
                    return desc

        return f"You don't see a {item_name} here."

    def talk_to_character(self, character_name):
        """Talks to a character in the current location.

        Args:
            character_name: The name of the character to talk to.

        Returns:
            str: The character's dialogue, or a message if the character is not found.
        """
        room = self.world_map[self.player_location]
        if "characters" in room:
            for char in room["characters"]:
                if self._name_matches(char["name"], character_name):
                    msgs, blocked = self.process_events(char, "talk")
                    if blocked:
                        return "\n".join(msgs)

                    dialogue = char.get("dialogue", "They have nothing to say.")

                    if isinstance(dialogue, dict):
                        # Start complex dialogue
                        self.dialogue_active = True
                        self.current_dialogue = dialogue
                        self.current_dialogue_node_id = dialogue.get("start_node")
                        self.current_character_name = char["name"]
                        return self._get_dialogue_text(msgs)

                    if msgs:
                         return dialogue + "\n" + "\n".join(msgs)
                    return f'{char["name"]} says: "{dialogue}"'

        return f"There is no one named {character_name} here."

    def _get_dialogue_text(self, initial_msgs=None):
        """Helper to format the current dialogue text and options.

        Args:
            initial_msgs: A list of messages to prepend to the dialogue text.

        Returns:
            str: The formatted dialogue text and options.
        """
        if not self.dialogue_active or not self.current_dialogue:
            return ""

        node = self.current_dialogue["nodes"][self.current_dialogue_node_id]
        text = node.get("text", "")
        if initial_msgs:
            text = "\n".join(initial_msgs) + "\n" + text

        options_text = []
        valid_options = []
        for opt in node.get("options", []):
            if self.check_condition(opt.get("condition")):
                valid_options.append(opt)

        for i, opt in enumerate(valid_options):
            options_text.append(f"{i + 1}. {opt.get('text')}")

        if options_text:
            return text + "\n" + "\n".join(options_text)
        return text

    def make_dialogue_choice(self, choice_index):
        """Processes the player's choice in a dialogue.

        Args:
            choice_index: The 1-based index of the choice.

        Returns:
            str: The result of the choice (next node text or end message).
        """
        if not self.dialogue_active:
             return "You are not in a conversation."

        node = self.current_dialogue["nodes"][self.current_dialogue_node_id]
        valid_options = []
        for opt in node.get("options", []):
            if self.check_condition(opt.get("condition")):
                valid_options.append(opt)

        if choice_index < 1 or choice_index > len(valid_options):
            return "Invalid choice."

        choice = valid_options[choice_index - 1]

        # Execute actions
        for action in choice.get("actions", []):
            self.perform_action(action)

        next_node_id = choice.get("next_node")

        if next_node_id:
            self.current_dialogue_node_id = next_node_id
            # Execute enter actions for the new node?
            # The spec didn't strictly say so but it's good practice.
            # Current design doesn't support 'actions' on nodes yet, just options.
            # But the user might want node actions later.
            return self._get_dialogue_text()
        else:
            char_name = self.current_character_name
            self.end_dialogue()
            return f"You stop talking to the {char_name}."

    def end_dialogue(self):
        """Ends the current dialogue session.

        Resets the dialogue state.

        Args:
            None

        Returns:
            None
        """
        self.dialogue_active = False
        self.current_dialogue = None
        self.current_dialogue_node_id = None
        self.current_character_name = None
