"""The main control loop for the game.

This module contains the Control class, which manages the game's main loop.
"""


class Control:
    """Manages the game's main loop."""

    def __init__(self):
        """Initializes the Control class."""
        self.done = False

    def main_game_loop(self):
        """The main game loop.

        This loop runs until the `done` attribute is set to True. It handles
        user input and prints output to the console.
        """
        print("Welcome to the text-based game template!")
        while not self.done:
            user_input = input("> ").lower()
            if user_input == "quit":
                self.done = True
            else:
                print(f"You entered: {user_input}")
        print("Thanks for playing!")
