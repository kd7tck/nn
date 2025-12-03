"""Unit tests for the Game class."""

import unittest
from src.game import Game


class TestGame(unittest.TestCase):
    """Test cases for the Game class."""

    def setUp(self):
        """Set up a new Game instance before each test."""
        self.game = Game()

    def test_take_item(self):
        """Test taking an item."""
        self.assertEqual(
            self.game.take_item("key"), "You take the key."
        )
        self.assertEqual(len(self.game.inventory), 1)
        self.assertEqual(self.game.inventory[0]["name"], "key")

    def test_drop_item(self):
        """Test dropping an item."""
        self.game.take_item("key")
        self.assertEqual(
            self.game.drop_item("key"), "You drop the key."
        )
        self.assertEqual(len(self.game.inventory), 0)

    def test_examine_item_in_room(self):
        """Test examining an item in the room."""
        self.assertEqual(
            self.game.examine_item("key"), "A small, rusty key."
        )

    def test_examine_item_in_inventory(self):
        """Test examining an item in the inventory."""
        self.game.take_item("key")
        self.assertEqual(
            self.game.examine_item("key"), "A small, rusty key."
        )


if __name__ == "__main__":
    unittest.main()
