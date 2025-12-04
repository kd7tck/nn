"""The main control loop for the game.

This module contains the Control class, which manages the game's main loop,
processing user input and interacting with the Game instance.
"""
from src.game import Game


class Control:
    """Manages the game's main loop.

    This class interprets user commands, calls the appropriate methods on the
    Game object, and displays the results to the user.
    """

    def __init__(self):
        """Initializes the Control class.

        Sets up the game instance, the 'done' flag, and the direction mappings.
        """
        self.done = False
        self.game = Game()
        self.directions = {
            "n": "north",
            "north": "north",
            "s": "south",
            "south": "south",
            "e": "east",
            "east": "east",
            "w": "west",
            "west": "west",
            "ne": "northeast",
            "northeast": "northeast",
            "nw": "northwest",
            "northwest": "northwest",
            "se": "southeast",
            "southeast": "southeast",
            "sw": "southwest",
            "southwest": "southwest",
            "u": "up",
            "up": "up",
            "d": "down",
            "down": "down",
        }

    def main_game_loop(self):
        """The main game loop.

        This loop runs until the `done` attribute is set to True. It handles
        user input and prints output to the console.

        Returns:
            None
        """
        print("Welcome to TextGameTemplate!")
        print(self.game.get_location_description(arrival=True))
        while not self.done:
            user_input = input("> ").lower().split()
            if not user_input:
                continue
            command = user_input[0]
            if command == "quit":
                self.done = True
            elif command in self.directions:
                direction = self.directions[command]
                print(self.game.move_player(direction))
            elif command == "go":
                if len(user_input) > 1:
                    direction = user_input[1]
                    if direction in self.directions:
                        direction = self.directions[direction]
                    print(self.game.move_player(direction))
                else:
                    print("Go where?")
            elif command == "look":
                print(self.game.get_location_description())
            elif command == "take":
                if len(user_input) > 1:
                    item = " ".join(user_input[1:])
                    print(self.game.take_item(item))
                else:
                    print("Take what?")
            elif command == "drop":
                if len(user_input) > 1:
                    item = " ".join(user_input[1:])
                    print(self.game.drop_item(item))
                else:
                    print("Drop what?")
            elif command == "inventory":
                print(self.game.get_inventory())
            elif command == "examine":
                if len(user_input) > 1:
                    item_name = " ".join(user_input[1:])
                    print(self.game.examine_item(item_name))
                else:
                    print("Examine what?")
            else:
                print("Unknown command.")
        print("Thanks for playing!")
