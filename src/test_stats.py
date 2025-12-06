import unittest
import os
import json
from src.game import Game
from src.loader import load_characters, load_templates

class TestStats(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_character_stats_loading(self):
        """Test that character stats are loaded correctly from templates and overrides."""
        # The 'guard' character uses 'base_npc' template.
        # base_npc: hp=100, str=10
        # guard override: hp=120, str=15

        # Find the guard in the world map
        guard = None
        for room_id, room in self.game.world_map.items():
            if "characters" in room:
                for char in room["characters"]:
                    if char["name"] == "guard":
                        guard = char
                        break
            if guard:
                break

        self.assertIsNotNone(guard, "Guard character not found in world map")
        self.assertIn("stats", guard, "Guard should have stats")

        stats = guard["stats"]
        self.assertEqual(stats["hp"], 120, "Guard HP should be overridden to 120")
        self.assertEqual(stats["str"], 15, "Guard STR should be overridden to 15")
        self.assertEqual(stats["def"], 10, "Guard DEF should remain default 10")
        self.assertEqual(stats["spd"], 10, "Guard SPD should remain default 10")

    def test_stats_persistence(self):
        """Test that modified stats are saved and loaded correctly."""
        # Find the guard
        guard = None
        for room_id, room in self.game.world_map.items():
            if "characters" in room:
                for char in room["characters"]:
                    if char["name"] == "guard":
                        guard = char
                        break
            if guard:
                break

        self.assertIsNotNone(guard)

        # Modify stats
        guard["stats"]["hp"] = 50
        guard["stats"]["new_stat"] = 999

        # Save game
        save_file = "test_save_stats.json"
        self.game.save_game(save_file)

        # Create new game and load
        new_game = Game()
        new_game.load_game(save_file)

        # Find guard in new game
        new_guard = None
        for room_id, room in new_game.world_map.items():
            if "characters" in room:
                for char in room["characters"]:
                    if char["name"] == "guard":
                        new_guard = char
                        break
            if new_guard:
                break

        self.assertIsNotNone(new_guard)
        self.assertEqual(new_guard["stats"]["hp"], 50, "Modified HP should be loaded")
        self.assertEqual(new_guard["stats"]["new_stat"], 999, "New stat should be loaded")

        # Cleanup
        if os.path.exists(save_file):
            os.remove(save_file)

if __name__ == '__main__':
    unittest.main()
