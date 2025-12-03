# TextGameTemplate

TextGameTemplate is a Zork-like text-based adventure game written in Python.

## How to Play

*   **Move between rooms:** Use the `go` command followed by a direction (e.g., `go north`).
*   **Look around:** Use the `look` command to see a description of your current location.
*   **Quit the game:** Use the `quit` command to exit.

## Features

*   **Command Parser:** A simple command parser that understands multi-word commands.
*   **World Model:** A basic world model with interconnected rooms.
*   **Cross-Platform Build System:** Includes a CMake build system for creating distributable packages for Windows, macOS, and Linux.

## Getting Started

To get started with the template, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/text-game-template.git
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
├── src/            # Source code
│   ├── __init__.py
│   ├── control.py    # The main control loop
│   └── game.py       # The game logic and state
├── main.py         # The main entry point of the game
├── requirements.txt # Python dependencies
└── README.md       # This file
```

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.
