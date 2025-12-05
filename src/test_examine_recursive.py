import unittest
from src.game import Game

class TestExamineRecursive(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.player_location = "start"

        # Setup a container with an item inside
        self.container = {
            "name": "bag",
            "description": "A small leather bag.",
            "is_container": True,
            "is_open": True,
            "contents": [
                {
                    "name": "scroll",
                    "description": "An ancient scroll with magic text."
                }
            ]
        }
        self.game.inventory.append(self.container)

    def test_examine_item_in_inventory_container(self):
        # Examining the scroll should work if it's in an open container in inventory
        description = self.game.examine_item("scroll")
        self.assertEqual(description, "An ancient scroll with magic text.")

    def test_examine_item_in_room_container(self):
        # Move container to room
        self.game.inventory.remove(self.container)
        self.game.world_map["start"]["items"].append(self.container)

        description = self.game.examine_item("scroll")
        self.assertEqual(description, "An ancient scroll with magic text.")

    def test_examine_item_in_closed_container(self):
        # Close the container
        self.container["is_open"] = False

        description = self.game.examine_item("scroll")
        self.assertEqual(description, "You don't see a scroll here.")

if __name__ == '__main__':
    unittest.main()
