"""Unit tests for expanded movement system."""

import unittest
from src.game import Game
from src.control import Control

class TestExpandedMovement(unittest.TestCase):
    """Test cases for the expanded movement system."""

    def setUp(self):
        """Set up a new Game instance before each test."""
        self.game = Game()
        self.control = Control()

    def test_move_diagonal_blocked(self):
        """Test that diagonal movement can be blocked."""
        # Start location is "start"
        # "garden" is northeast, but blocked by vines if no sword
        result = self.game.move_player("northeast")
        self.assertEqual(result, "Thick vines block the path to the garden. You need something to cut them.")
        self.assertEqual(self.game.player_location, "start")

    def test_move_diagonal_allowed(self):
        """Test that diagonal movement works when conditions are met."""
        # Give player the sword
        self.game.inventory.append({"name": "sword", "description": "A sharp, shiny sword."})

        result = self.game.move_player("northeast")
        self.assertIn("You step out into the fresh air of a vibrant garden", result)
        self.assertEqual(self.game.player_location, "garden")

    def test_move_vertical(self):
        """Test vertical movement (up/down)."""
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
        """Test that Control handles direction aliases."""
        # We can't easily test the full loop without mocking input,
        # but we can test if the directions map is correct.
        self.assertEqual(self.control.directions["n"], "north")
        self.assertEqual(self.control.directions["ne"], "northeast")
        self.assertEqual(self.control.directions["u"], "up")
        self.assertEqual(self.control.directions["d"], "down")

    def test_invalid_move(self):
        """Test moving in an invalid direction."""
        result = self.game.move_player("northwest") # No exit northwest from start
        self.assertEqual(result, "You can't go that way.")

if __name__ == "__main__":
    unittest.main()
