# Pygame Template

This is a comprehensive template for a Pygame project. It includes a basic file structure, settings file, sprite classes, and a game loop.

## Features

*   **State Machine:** The template includes a state machine to manage different game states, such as a main menu and the game itself.
*   **Procedurally Generated Assets:** The template demonstrates how to use procedurally generated assets, such as colored surfaces for sprites and the default font.
*   **Camera System:** A camera system is included to allow for scrolling levels.
*   **Sprite Interactions:** The template includes examples of sprite interactions, such as collision detection.

## File Structure

```
.
├── src
│   ├── states
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── game.py
│   │   └── menu.py
│   ├── __init__.py
│   ├── camera.py
│   ├── control.py
│   ├── settings.py
│   └── sprites.py
└── main.py
```

## How to Use

1.  **Clone the repository.**
2.  **Install Pygame:** `pip install pygame`
3.  **Run the game:** `python main.py`

## Code

The code is split into several files to make it more organized and easier to manage.

*   `main.py`: The entry point of the game.
*   `src/control.py`: The main control loop of the game, which manages the state machine.
*   `src/settings.py`: Contains the settings for the game, such as screen dimensions and colors.
*   `src/sprites.py`: Contains the sprite classes for the game, such as the player and enemies.
*   `src/states/game.py`: The main game state.
*   `src/camera.py`: The camera class, which allows for scrolling levels.
*   `src/states/base.py`: The base class for all game states.
*   `src/states/menu.py`: The main menu state.
