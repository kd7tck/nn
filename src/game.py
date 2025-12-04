"""The main game logic for the text-based game.

This module contains the Game class, which manages the game's state,
including the player's location, inventory, and the world map.
"""
from collections import defaultdict


class Game:
    """Manages the game's state and logic.

    This class handles the core mechanics of the game, including player movement,
    interaction with items, and tracking the state of the world.
    """

    def __init__(self):
        """Initializes the Game class.

        Sets up the initial player location, inventory, visited counts, and the world map.
        """
        self.player_location = "start"
        self.inventory = []
        self.visited_counts = defaultdict(int)
        self.visited_counts["start"] = 1
        self.game_state = {}

        self.world_map = {
            "start": {
                "description": "You are in a dimly lit room. There are doors to the north, east, and northeast.",
                "first_arrival_text": "You wake up in a strange, dimly lit room. Your head hurts.",
                "transition_text": "You enter the dimly lit room.",
                "examination_text": "The walls are bare concrete. The air smells musty.",
                "exits": {
                    "north": "hallway",
                    "east": "kitchen",
                    "northeast": "garden",
                },
                "items": [
                    {
                        "name": "key",
                        "description": "A small, rusty key.",
                    }
                ],
                "events": {
                    "exit_northeast": [
                        {
                            "condition": {
                                "not": {"has_item": "sword"}
                            },
                            "actions": [
                                {
                                    "type": "block",
                                    "message": "Thick vines block the path to the garden. You need something to cut them."
                                }
                            ]
                        }
                    ]
                }
            },
            "hallway": {
                "description": "You are in a long hallway. There are doors to the south and north.",
                "transition_text": "You step into the long hallway.",
                "examination_text": "The hallway seems to stretch on forever.",
                "nth_arrival_text": {
                    2: "You find yourself back in the long hallway."
                },
                "exits": {"south": "start", "north": "treasure_room"},
                "items": [],
                "events": {
                    "exit_north": [
                        {
                            "condition": {
                                "not": {"has_item": "key"}
                            },
                            "actions": [
                                {
                                    "type": "block",
                                    "message": "The door is locked."
                                }
                            ]
                        }
                    ]
                }
            },
            "kitchen": {
                "description": "You are in a kitchen. There is a door to the west and a hatch to the cellar down below.",
                "first_arrival_text": "You push open the door and reveal a messy kitchen.",
                "examination_text": "Dirty dishes are piled high in the sink.",
                "exits": {"west": "start", "down": "cellar"},
                "items": [
                    {
                        "name": "sword",
                        "description": "A sharp, shiny sword.",
                        "events": {
                            "take": [
                                {
                                    "condition": {},
                                    "actions": [
                                        {
                                            "type": "print",
                                            "message": "As you grasp the hilt, you feel a surge of power.",
                                        }
                                    ],
                                }
                            ]
                        },
                    }
                ],
            },
            "garden": {
                "description": "You are in a beautiful garden. There is a path leading southwest.",
                "first_arrival_text": "You step out into the fresh air of a vibrant garden.",
                "examination_text": "Flowers bloom in every color imaginable.",
                "exits": {"southwest": "start"},
                "items": [],
            },
            "cellar": {
                "description": "You are in a dark, damp cellar. There is a ladder leading up.",
                "first_arrival_text": "You climb down into the darkness.",
                "examination_text": "It's too dark to see much.",
                "exits": {"up": "kitchen"},
                "items": [],
            },
            "treasure_room": {
                "description": "You have found the treasure room!",
                "first_arrival_text": "At last! You have discovered the legendary treasure room.",
                "examination_text": "Gold glitters from every corner.",
                "exits": {"south": "hallway"},
                "items": [
                    {
                        "name": "treasure",
                        "description": "A chest full of gold and jewels.",
                    }
                ],
            },
        }

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
            if not any(item["name"] == item_name for item in self.inventory):
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

        return True

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
            item_names = [item["name"] for item in items]
            description_parts.append("You see a " + ", ".join(item_names) + ".")

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

            # Process enter events
            enter_msgs, _ = self.process_events(self.world_map[next_location], "enter")

            desc = self.get_location_description(arrival=True)

            # Combine all messages
            all_parts = exit_msgs + [desc] + enter_msgs
            return "\n".join(all_parts)
        else:
            return "You can't go that way."

    def take_item(self, item_name):
        """Takes an item from the current location and adds it to the player's inventory.

        Args:
            item_name: The name of the item to take.

        Returns:
            str: A message indicating whether the item was successfully taken or not.
        """
        location_items = self.world_map[self.player_location]["items"]
        for item in location_items:
            if item["name"] == item_name:
                msgs, blocked = self.process_events(item, "take")

                if blocked:
                     return "\n".join(msgs)

                location_items.remove(item)
                self.inventory.append(item)

                output_msgs = [f"You take the {item_name}."]
                output_msgs.extend(msgs)

                return "\n".join(output_msgs)
        return f"There is no {item_name} here."

    def drop_item(self, item_name):
        """Drops an item from the player's inventory into the current location.

        Args:
            item_name: The name of the item to drop.

        Returns:
            str: A message indicating whether the item was successfully dropped or not.
        """
        for item in self.inventory:
            if item["name"] == item_name:
                msgs, blocked = self.process_events(item, "drop")

                if blocked:
                    return "\n".join(msgs)

                self.inventory.remove(item)
                self.world_map[self.player_location]["items"].append(item)

                output_msgs = [f"You drop the {item_name}."]
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
            return "You are carrying: " + ", ".join(item_names)
        else:
            return "Your inventory is empty."

    def examine_item(self, item_name):
        """Examines an item in the player's inventory or the current location.

        Also allows examining the room itself.

        Args:
            item_name: The name of the item to examine, or 'room'/'here' to examine the room.

        Returns:
            str: The description of the item or room, or a message if the item is not found.
        """
        if item_name in ["room", "here"]:
            room = self.world_map[self.player_location]
            # Process examine events for room
            msgs, _ = self.process_events(room, "examine")
            desc = room.get("examination_text", room["description"])
            if msgs:
                return desc + "\n" + "\n".join(msgs)
            return desc

        # Check inventory first
        for item in self.inventory:
            if item["name"] == item_name:
                msgs, _ = self.process_events(item, "examine")
                desc = item["description"]
                if msgs:
                    return desc + "\n" + "\n".join(msgs)
                return desc

        # Check current location
        for item in self.world_map[self.player_location]["items"]:
            if item["name"] == item_name:
                msgs, _ = self.process_events(item, "examine")
                desc = item["description"]
                if msgs:
                    return desc + "\n" + "\n".join(msgs)
                return desc
        return f"You don't see a {item_name} here."
