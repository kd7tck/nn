"""The main control loop for the game.

This module contains the Control class, which manages the game's main loop.
"""
from src.game import Game


class Control:
    """Manages the game's main loop."""

    def __init__(self):
        """Initializes the Control class."""
        self.done = False
        self.game = Game()

    def main_game_loop(self):
        """The main game loop.

        This loop runs until the `done` attribute is set to True. It handles
        user input and prints output to the console.
        """
        print("Welcome to TextGameTemplate!")
        print(self.game.get_location_description())
        while not self.done:
            user_input = input("> ").lower().split()
            if not user_input:
                continue
            command = user_input[0]
            if command == "quit":
                self.done = True
            elif command == "go":
                if len(user_input) > 1:
                    direction = user_input[1]
                    print(self.game.move_player(direction))
                else:
                    print("Go where?")
            elif command == "look":
                print(self.game.get_location_description())
            else:
                print("Unknown command.")
        print("Thanks for playing!")
