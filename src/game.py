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
        if direction in self.world_map[self.player_location]["exits"]:
            next_location = self.world_map[self.player_location]["exits"][direction]
            if next_location == "treasure_room" and not any(
                item["name"] == "key" for item in self.inventory
            ):
                return "The door is locked."

            # Demonstrate blocked path for "garden" if user doesn't have the sword (just as an example)
            if next_location == "garden" and not any(
                item["name"] == "sword" for item in self.inventory
            ):
                return "Thick vines block the path to the garden. You need something to cut them."

            self.player_location = next_location
            self.visited_counts[next_location] += 1
            return self.get_location_description(arrival=True)
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
                location_items.remove(item)
                self.inventory.append(item)
                return f"You take the {item_name}."
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
                self.inventory.remove(item)
                self.world_map[self.player_location]["items"].append(item)
                return f"You drop the {item_name}."
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
            return room.get("examination_text", room["description"])

        # Check inventory first
        for item in self.inventory:
            if item["name"] == item_name:
                return item["description"]
        # Check current location
        for item in self.world_map[self.player_location]["items"]:
            if item["name"] == item_name:
                return item["description"]
        return f"You don't see a {item_name} here."
