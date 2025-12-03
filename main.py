"""The main entry point for the game."""

from src.control import Control


def main():
    """Initializes and runs the game.

    This function creates a Control instance and starts the main game loop.
    """
    app = Control()
    app.main_game_loop()


if __name__ == "__main__":
    main()
