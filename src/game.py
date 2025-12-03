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
                "items": ["key"],
            },
            "hallway": {
                "description": "You are in a long hallway. There are doors to the south and north.",
                "exits": {"south": "start", "north": "treasure_room"},
                "items": [],
            },
            "kitchen": {
                "description": "You are in a kitchen. There is a door to the west.",
                "exits": {"west": "start"},
                "items": ["sword"],
            },
            "treasure_room": {
                "description": "You have found the treasure room!",
                "exits": {"south": "hallway"},
                "items": ["treasure"],
            },
        }

    def get_location_description(self):
        """Returns the description of the player's current location."""
        description = self.world_map[self.player_location]["description"]
        items = self.world_map[self.player_location]["items"]
        if items:
            description += " You see a " + ", ".join(items) + "."
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
            if next_location == "treasure_room" and "key" not in self.inventory:
                return "The door is locked."
            self.player_location = next_location
            return self.get_location_description()
        else:
            return "You can't go that way."

    def take_item(self, item):
        """Takes an item from the current location and adds it to the player's inventory.

        Args:
            item: The item to take.

        Returns:
            A message to be printed to the console.
        """
        if item in self.world_map[self.player_location]["items"]:
            self.world_map[self.player_location]["items"].remove(item)
            self.inventory.append(item)
            return f"You take the {item}."
        else:
            return f"There is no {item} here."

    def drop_item(self, item):
        """Drops an item from the player's inventory into the current location.

        Args:
            item: The item to drop.

        Returns:
            A message to be printed to the console.
        """
        if item in self.inventory:
            self.inventory.remove(item)
            self.world_map[self.player_location]["items"].append(item)
            return f"You drop the {item}."
        else:
            return f"You don't have a {item}."

    def get_inventory(self):
        """Returns the player's inventory.

        Returns:
            A string containing the player's inventory.
        """
        if self.inventory:
            return "You are carrying: " + ", ".join(self.inventory)
        else:
            return "Your inventory is empty."
