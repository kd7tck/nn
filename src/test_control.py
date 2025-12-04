"""Unit tests for the Control class.

This module contains test cases to verify the functionality of the Control class,
specifically the main game loop and command parsing, by mocking user input and output.
"""

import unittest
from unittest.mock import patch, call
from src.control import Control


class TestControl(unittest.TestCase):
    """Test cases for the Control class."""

    def setUp(self):
        """Set up a new Control instance before each test.

        Args:
            None

        Returns:
            None
        """
        self.control = Control()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_quit_command(self, mock_print, mock_input):
        """Test the 'quit' command.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = ["quit"]
        self.control.main_game_loop()
        self.assertTrue(self.control.done)
        # Verify welcome message and thanks message
        self.assertIn(call("Welcome to TextGameTemplate!"), mock_print.call_args_list)
        self.assertIn(call("Thanks for playing!"), mock_print.call_args_list)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_movement_commands(self, mock_print, mock_input):
        """Test movement commands and their aliases.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        # 'n' for north, 'go east' for east
        mock_input.side_effect = ["n", "go east", "quit"]
        self.control.main_game_loop()

        # Verify calls related to movement
        # First move: n -> north (from start to hallway)
        # Second move: go east -> east (from hallway, invalid move)
        # Note: Need to check specific output messages to be sure

        # Capture print calls to verify logic
        printed_messages = [c[0][0] for c in mock_print.call_args_list]
        self.assertTrue(any("You step into the long hallway" in m for m in printed_messages))
        self.assertTrue(any("You can't go that way" in m for m in printed_messages))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_look_command(self, mock_print, mock_input):
        """Test the 'look' command.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = ["look", "quit"]
        self.control.main_game_loop()

        printed_messages = [c[0][0] for c in mock_print.call_args_list]
        # Look should print description without transition text
        self.assertTrue(any("You are in a dimly lit room" in m for m in printed_messages))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_inventory_commands(self, mock_print, mock_input):
        """Test 'take', 'drop', and 'inventory' commands.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = [
            "inventory",        # Empty
            "take key",         # Take existing item
            "inventory",        # Check it's there
            "drop key",         # Drop it
            "inventory",        # Empty again
            "take fake_item",   # Take non-existent
            "drop fake_item",   # Drop non-existent
            "quit"
        ]
        self.control.main_game_loop()

        printed_messages = [c[0][0] for c in mock_print.call_args_list]
        self.assertTrue(any("Your inventory is empty" in m for m in printed_messages))
        self.assertTrue(any("You take the key" in m for m in printed_messages))
        self.assertTrue(any("You are carrying: key" in m for m in printed_messages))
        self.assertTrue(any("You drop the key" in m for m in printed_messages))
        self.assertTrue(any("There is no fake_item here" in m for m in printed_messages))
        self.assertTrue(any("You don't have a fake_item" in m for m in printed_messages))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_examine_command(self, mock_print, mock_input):
        """Test the 'examine' command.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = [
            "examine key",      # Examine item in room
            "examine room",     # Examine room
            "examine fake",     # Examine non-existent
            "quit"
        ]
        self.control.main_game_loop()

        printed_messages = [c[0][0] for c in mock_print.call_args_list]
        self.assertTrue(any("A small, rusty key" in m for m in printed_messages))
        self.assertTrue(any("The walls are bare concrete" in m for m in printed_messages))
        self.assertTrue(any("You don't see a fake here" in m for m in printed_messages))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_incomplete_commands(self, mock_print, mock_input):
        """Test commands without required arguments.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = [
            "go",
            "take",
            "drop",
            "examine",
            "quit"
        ]
        self.control.main_game_loop()

        printed_messages = [c[0][0] for c in mock_print.call_args_list]
        self.assertTrue(any("Go where?" in m for m in printed_messages))
        self.assertTrue(any("Take what?" in m for m in printed_messages))
        self.assertTrue(any("Drop what?" in m for m in printed_messages))
        self.assertTrue(any("Examine what?" in m for m in printed_messages))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_unknown_command(self, mock_print, mock_input):
        """Test unknown command.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = ["xyzzy", "quit"]
        self.control.main_game_loop()

        printed_messages = [c[0][0] for c in mock_print.call_args_list]
        self.assertTrue(any("Unknown command" in m for m in printed_messages))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_empty_input(self, mock_print, mock_input):
        """Test empty input (just pressing enter).

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = ["", "quit"]
        self.control.main_game_loop()
        # Should just loop again without crashing
        self.assertTrue(self.control.done)

if __name__ == "__main__":
    unittest.main()
