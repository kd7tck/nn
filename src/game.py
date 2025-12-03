"""The main game logic for the text-based game.

This module contains the Game class, which manages the game's state,
including the player's location and the world map.
"""


class Game:
    """Manages the game's state and logic."""

    def __init__(self):
        """Initializes the Game class."""
        self.player_location = "start"
        self.world_map = {
            "start": {
                "description": "You are in a dimly lit room. There are doors to the north and east.",
                "exits": {"north": "hallway", "east": "kitchen"},
            },
            "hallway": {
                "description": "You are in a long hallway. There is a door to the south.",
                "exits": {"south": "start"},
            },
            "kitchen": {
                "description": "You are in a kitchen. There is a door to the west.",
                "exits": {"west": "start"},
            },
        }

    def get_location_description(self):
        """Returns the description of the player's current location."""
        return self.world_map[self.player_location]["description"]

    def move_player(self, direction):
        """Moves the player to a new location.

        Args:
            direction: The direction to move the player.

        Returns:
            A message to be printed to the console.
        """
        if direction in self.world_map[self.player_location]["exits"]:
            self.player_location = self.world_map[self.player_location]["exits"][direction]
            return self.get_location_description()
        else:
            return "You can't go that way."
