# TextGameTemplate

TextGameTemplate is a Zork-like text-based adventure game written in Python. It provides a solid foundation for building interactive fiction, featuring a command parser, a room-based world model, and a flexible item system.

## How to Play

Once the game is running, you can interact with the world using simple text commands.

*   **Move:** Navigate between rooms using `go <direction>` or just the direction alias.
    *   Examples: `go north`, `north`, `n`, `go up`, `up`, `u`
    *   Supported directions: `north`, `south`, `east`, `west`, `northeast`, `northwest`, `southeast`, `southwest`, `up`, `down`.
*   **Look:** Type `look` to see a description of your current location and any items present.
*   **Inventory:** Type `inventory` to see what items you are carrying.
*   **Take:** Pick up an item using `take <item_name>`.
    *   Example: `take key`
*   **Drop:** Drop an item from your inventory using `drop <item_name>`.
    *   Example: `drop key`
*   **Examine:** Look closer at an item or the room using `examine <item_name>`.
    *   Examples: `examine key`, `examine room`
*   **Quit:** Type `quit` to exit the game.

## Features

*   **Command Parser:** A robust command parser that understands standard adventure game commands and abbreviations.
*   **World Model:** A graph-based world model where rooms are connected by directions.
*   **Inventory System:** Collect, drop, and examine items.
*   **Dynamic Descriptions:** Room descriptions can change based on player visits or other state.
*   **Cross-Platform Build System:** Includes a CMake build system for creating distributable packages for Windows, macOS, and Linux.

## Getting Started

To get started with the template, follow these steps:

### Prerequisites

*   Python 3.6+
*   pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/text-game-template.git
    cd text-game-template
    ```
2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Game

Run the main script to start the game:
```bash
python main.py
```

## Development

### Project Structure

```
.
├── src/
│   ├── __init__.py      # Package initialization
│   ├── control.py       # Main control loop and input handling
│   ├── game.py          # Game logic, state, and world definition
│   ├── settings.py      # Configuration constants
│   ├── test_game.py     # Unit tests for game logic
│   └── test_movement.py # Unit tests for movement system
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

### Running Tests

To run the unit tests, use the following command:
```bash
python -m unittest discover src
```

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.
