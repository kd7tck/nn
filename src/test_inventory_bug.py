import unittest
from src.game import Game

class TestInventoryBug(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_inventory_output_punctuation(self):
        """Test that inventory output consistently ends with a period."""
        # Case 1: Empty inventory
        self.assertEqual(self.game.get_inventory(), "Your inventory is empty.")

        # Case 2: One item
        self.game.inventory.append({"name": "key"})
        self.assertEqual(self.game.get_inventory(), "You are carrying: key.")

        # Case 3: Multiple items
        self.game.inventory.append({"name": "sword"})
        self.assertEqual(self.game.get_inventory(), "You are carrying: key, sword.")
