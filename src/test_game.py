"""Unit tests for the Game class.

This module contains test cases to verify the functionality of the Game class,
including item interaction and inspection.
"""

import unittest
from src.game import Game


class TestGame(unittest.TestCase):
    """Test cases for the Game class."""

    def setUp(self):
        """Set up a new Game instance before each test.

        This ensures that each test starts with a fresh game state.
        """
        self.game = Game()

    def test_take_item(self):
        """Test taking an item.

        Verifies that an item can be taken from the room and added to the
        player's inventory.
        """
        self.assertEqual(
            self.game.take_item("key"), "You take the key."
        )
        self.assertEqual(len(self.game.inventory), 1)
        self.assertEqual(self.game.inventory[0]["name"], "key")

    def test_drop_item(self):
        """Test dropping an item.

        Verifies that an item can be dropped from the inventory back into
        the room.
        """
        self.game.take_item("key")
        self.assertEqual(
            self.game.drop_item("key"), "You drop the key."
        )
        self.assertEqual(len(self.game.inventory), 0)

    def test_examine_item_in_room(self):
        """Test examining an item in the room.

        Verifies that an item in the current location can be examined.
        """
        self.assertEqual(
            self.game.examine_item("key"), "A small, rusty key."
        )

    def test_examine_item_in_inventory(self):
        """Test examining an item in the inventory.

        Verifies that an item in the player's inventory can be examined.
        """
        self.game.take_item("key")
        self.assertEqual(
            self.game.examine_item("key"), "A small, rusty key."
        )

    def test_inventory_output_punctuation(self):
        """Test that inventory output consistently ends with a period.

        Verifies that the get_inventory method returns a string ending with
        a period, regardless of whether the inventory is empty or contains items.
        """
        # Case 1: Empty inventory
        self.assertEqual(self.game.get_inventory(), "Your inventory is empty.")

        # Case 2: One item
        self.game.inventory.append({"name": "key"})
        self.assertEqual(self.game.get_inventory(), "You are carrying: key.")

        # Case 3: Multiple items
        self.game.inventory.append({"name": "sword"})
        self.assertEqual(self.game.get_inventory(), "You are carrying: key, sword.")


if __name__ == "__main__":
    unittest.main()
