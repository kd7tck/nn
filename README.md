# Pygame Template

This repository contains a feature-rich template for creating games with Pygame. It provides a solid foundation for game development, including a state machine, sprite animation, a camera system, and more.

## Features

*   **State Machine:** The game is built around a state machine that manages different game states, such as the main menu and gameplay. This makes it easy to add new states and manage the flow of the game.
*   **Sprite Animation:** The template includes a sprite animation system that can be used to create animated characters and objects.
*   **Scrolling Camera:** A camera system is included that allows the view to scroll and follow the player.
*   **Sound Manager:** A singleton sound manager is provided for easy loading and playing of sound effects and music.
*   **UI Elements:** The template includes a simple UI system with a button class.
*   **Tiled Map Loading:** The game state demonstrates how to load and render tile maps created with the Tiled Map Editor.

## Getting Started

To get started with the template, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/pygame-template.git
    ```
2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the game:**
    ```bash
    python main.py
    ```

## Project Structure

The project is organized into the following directories and files:

```
.
├── assets/         # Game assets such as sprites, sounds, and maps
├── src/            # Source code
│   ├── states/     # Game states
│   │   ├── __init__.py
│   │   ├── base.py   # Base class for all game states
│   │   ├── game.py   # The main gameplay state
│   │   └── menu.py   # The main menu state
│   ├── __init__.py
│   ├── animation.py  # Sprite animation classes
│   ├── camera.py     # The camera class
│   ├── control.py    # The main control loop and state machine
│   ├── settings.py   # Game settings
│   ├── sound.py      # The sound manager
│   ├── sprites.py    # Sprite classes
│   └── ui.py         # UI classes
├── main.py         # The main entry point of the game
├── requirements.txt # Python dependencies
└── README.md       # This file
```

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.
