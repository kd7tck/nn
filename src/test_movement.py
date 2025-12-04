"""Unit tests for expanded movement system.

This module contains test cases to verify the functionality of the movement
system, including directional checks, blocking conditions, and aliases.
"""

import unittest
from src.game import Game
from src.control import Control

class TestExpandedMovement(unittest.TestCase):
    """Test cases for the expanded movement system."""

    def setUp(self):
        """Set up a new Game instance before each test.

        This ensures that each test starts with a fresh game state.
        """
        self.game = Game()
        self.control = Control()

    def test_move_diagonal_blocked(self):
        """Test that diagonal movement can be blocked.

        Verifies that moving to the garden is blocked if the player does
        not have the sword.
        """
        # Start location is "start"
        # "garden" is northeast, but blocked by vines if no sword
        result = self.game.move_player("northeast")
        self.assertEqual(result, "Thick vines block the path to the garden. You need something to cut them.")
        self.assertEqual(self.game.player_location, "start")

    def test_move_diagonal_allowed(self):
        """Test that diagonal movement works when conditions are met.

        Verifies that moving to the garden is allowed if the player has
        the sword.
        """
        # Give player the sword
        self.game.inventory.append({"name": "sword", "description": "A sharp, shiny sword."})

        result = self.game.move_player("northeast")
        self.assertIn("You step out into the fresh air of a vibrant garden", result)
        self.assertEqual(self.game.player_location, "garden")

    def test_move_vertical(self):
        """Test vertical movement (up/down).

        Verifies that the player can move up and down between rooms (e.g.,
        kitchen and cellar).
        """
        # Move to kitchen first
        self.game.move_player("east")
        self.assertEqual(self.game.player_location, "kitchen")

        # Move down
        result = self.game.move_player("down")
        self.assertIn("You climb down into the darkness", result)
        self.assertEqual(self.game.player_location, "cellar")

        # Move up
        result = self.game.move_player("up")
        self.assertIn("You are in a kitchen", result)
        self.assertEqual(self.game.player_location, "kitchen")

    def test_control_aliases(self):
        """Test that Control handles direction aliases.

        Verifies that short direction codes (e.g., 'n', 'u') map to the
        correct full direction names.
        """
        # We can't easily test the full loop without mocking input,
        # but we can test if the directions map is correct.
        self.assertEqual(self.control.directions["n"], "north")
        self.assertEqual(self.control.directions["ne"], "northeast")
        self.assertEqual(self.control.directions["u"], "up")
        self.assertEqual(self.control.directions["d"], "down")

    def test_invalid_move(self):
        """Test moving in an invalid direction.

        Verifies that attempting to move in a direction with no exit
        returns the appropriate message.
        """
        result = self.game.move_player("northwest") # No exit northwest from start
        self.assertEqual(result, "You can't go that way.")

if __name__ == "__main__":
    unittest.main()
