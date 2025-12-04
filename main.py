"""The main entry point for the text-based game.

This script initializes the game control and starts the main game loop.
"""

from src.control import Control


def main():
    """Initializes and runs the game.

    This function creates a Control instance and starts the main game loop.

    Returns:
        None
    """
    app = Control()
    app.main_game_loop()


if __name__ == "__main__":
    main()
