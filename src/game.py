"""The main game logic for the text-based game.

This module contains the Game class, which manages the game's state,
including the player's location and the world map.
"""


class Game:
    """Manages the game's state and logic."""

    def __init__(self):
        """Initializes the Game class."""
        self.player_location = "start"
        self.inventory = []
        self.world_map = {
            "start": {
                "description": "You are in a dimly lit room. There are doors to the north and east.",
                "exits": {"north": "hallway", "east": "kitchen"},
                "items": [
                    {
                        "name": "key",
                        "description": "A small, rusty key.",
                    }
                ],
            },
            "hallway": {
                "description": "You are in a long hallway. There are doors to the south and north.",
                "exits": {"south": "start", "north": "treasure_room"},
                "items": [],
            },
            "kitchen": {
                "description": "You are in a kitchen. There is a door to the west.",
                "exits": {"west": "start"},
                "items": [
                    {
                        "name": "sword",
                        "description": "A sharp, shiny sword.",
                    }
                ],
            },
            "treasure_room": {
                "description": "You have found the treasure room!",
                "exits": {"south": "hallway"},
                "items": [
                    {
                        "name": "treasure",
                        "description": "A chest full of gold and jewels.",
                    }
                ],
            },
        }

    def get_location_description(self):
        """Returns the description of the player's current location."""
        description = self.world_map[self.player_location]["description"]
        items = self.world_map[self.player_location]["items"]
        if items:
            item_names = [item["name"] for item in items]
            description += " You see a " + ", ".join(item_names) + "."
        return description

    def move_player(self, direction):
        """Moves the player to a new location.

        Args:
            direction: The direction to move the player.

        Returns:
            A message to be printed to the console.
        """
        if direction in self.world_map[self.player_location]["exits"]:
            next_location = self.world_map[self.player_location]["exits"][direction]
            if next_location == "treasure_room" and not any(
                item["name"] == "key" for item in self.inventory
            ):
                return "The door is locked."
            self.player_location = next_location
            return self.get_location_description()
        else:
            return "You can't go that way."

    def take_item(self, item_name):
        """Takes an item from the current location and adds it to the player's inventory.

        Args:
            item_name: The name of the item to take.

        Returns:
            A message to be printed to the console.
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
            A message to be printed to the console.
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
            A string containing the player's inventory.
        """
        if self.inventory:
            item_names = [item["name"] for item in self.inventory]
            return "You are carrying: " + ", ".join(item_names)
        else:
            return "Your inventory is empty."

    def examine_item(self, item_name):
        """Examines an item in the player's inventory or the current location.

        Args:
            item_name: The name of the item to examine.

        Returns:
            The description of the item or a message if the item is not found.
        """
        # Check inventory first
        for item in self.inventory:
            if item["name"] == item_name:
                return item["description"]
        # Check current location
        for item in self.world_map[self.player_location]["items"]:
            if item["name"] == item_name:
                return item["description"]
        return f"You don't see a {item_name} here."
