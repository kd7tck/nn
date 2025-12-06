import unittest
import os
import shutil
from src.game import Game
from src.loader import load_characters

class TestDialogueStats(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        # Manually load the mentor into the world map for testing
        # Assuming the mentor file is created in src/data/characters/mentor.json
        # We need to inject him into a room.

        # Load character data manually to bypass full reload if needed,
        # but Game() init calls load_world_data which loads all characters.
        # We just need to find the mentor or inject him.
        # Since mentor isn't in any room by default, we'll put him in 'start'.

        characters = load_characters()
        if "mentor" in characters:
            mentor = characters["mentor"]
            self.game.world_map["start"]["characters"].append(mentor)
        else:
            self.fail("Mentor character not found. Did you create src/data/characters/mentor.json?")

        self.game.player_location = "start"

    def test_default_stats_dialogue(self):
        """Test dialogue options with default stats."""
        # Default stats: STR 10, INT 10
        # Mentor options:
        # - "What do you mean?" (Always)
        # - "[STR >= 15]..." (Requires STR 15) -> Should NOT be visible
        # - "[INT >= 15]..." (Requires INT 15) -> Should NOT be visible
        # - "[NPC STR < 10]..." (Requires NPC STR < 10) -> Mentor STR is 5 -> Should BE visible
        # - "Goodbye." (Always)

        dialogue_text = self.game.talk_to_character("mentor")

        self.assertIn("Greetings, traveler", dialogue_text)
        self.assertIn("What do you mean?", dialogue_text)
        self.assertNotIn("I don't need your riddles", dialogue_text)
        self.assertNotIn("You are referring to the magical aura", dialogue_text)
        self.assertIn("You look weak, old man", dialogue_text)

    def test_high_str_dialogue(self):
        """Test dialogue options with high strength."""
        self.game.player_stats["str"] = 15

        dialogue_text = self.game.talk_to_character("mentor")

        self.assertIn("I don't need your riddles", dialogue_text)

    def test_high_int_dialogue(self):
        """Test dialogue options with high intelligence."""
        self.game.player_stats["int"] = 15

        dialogue_text = self.game.talk_to_character("mentor")

        self.assertIn("You are referring to the magical aura", dialogue_text)

    def test_stat_modification(self):
        """Test that dialogue actions can modify stats."""
        self.game.player_stats["str"] = 15

        # Start dialogue
        self.game.talk_to_character("mentor")

        # We need to find the option index for "I don't need your riddles"
        # Since options are filtered, the index might change.
        # Options:
        # 1. What do you mean?
        # 2. [STR >= 15] ...
        # 3. [NPC STR < 10] ...
        # 4. Goodbye.

        # So we choose option 2.

        # Verify current STR
        self.assertEqual(self.game.player_stats["str"], 15)

        res = self.game.make_dialogue_choice(2)
        self.assertIn("Ho ho! You have spirit", res) # Moved to fight_challenge node

        # Next node "fight_challenge" options:
        # 1. I will show you! (Adds 1 STR)

        res = self.game.make_dialogue_choice(1)
        self.assertIn("You feel your muscles grow", res)

        # Verify STR increased
        self.assertEqual(self.game.player_stats["str"], 16)

if __name__ == '__main__':
    unittest.main()
