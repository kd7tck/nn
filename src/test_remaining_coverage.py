import unittest
from unittest.mock import patch
from src.game import Game
from src.control import Control

class TestRemainingCoverage(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.control = Control()

    def test_process_events_check_condition_false(self):
        """Test process_events where condition is not met."""
        source = {
            "events": {
                "test": [
                    {
                        "condition": {"has_item": "non_existent"},
                        "actions": [{"type": "block"}]
                    }
                ]
            }
        }
        msgs, blocked = self.game.process_events(source, "test")
        self.assertFalse(blocked)
        self.assertEqual(msgs, [])

    def test_process_events_perform_action_output(self):
        """Test process_events capturing action output."""
        source = {
            "events": {
                "test": [
                    {
                        "condition": {},
                        "actions": [
                            {"type": "print", "message": "Hello World"}
                        ]
                    }
                ]
            }
        }
        msgs, blocked = self.game.process_events(source, "test")
        self.assertFalse(blocked)
        self.assertEqual(msgs, ["Hello World"])

    def test_get_location_description_transition(self):
        """Test get_location_description with transition text."""
        self.game.world_map["start"]["transition_text"] = "Entering start."
        self.game.visited_counts["start"] = 2 # Force non-first arrival
        desc = self.game.get_location_description(arrival=True)
        self.assertIn("Entering start.", desc)

    def test_format_item_list_multiple(self):
        """Test _format_item_list with various lengths."""
        items = [{"name": "a"}, {"name": "b"}, {"name": "c"}]
        self.assertEqual(self.game._format_item_list(items[:1]), "an a")
        self.assertEqual(self.game._format_item_list(items[:2]), "an a and a b")
        self.assertEqual(self.game._format_item_list(items), "an a, a b, and a c")

    def test_move_player_generic_exit_blocked(self):
        """Test move_player blocked by generic exit event."""
        self.game.world_map["start"]["events"] = {
            "exit": [
                {
                    "condition": {},
                    "actions": [{"type": "block", "message": "Generic block."}]
                }
            ]
        }
        msg = self.game.move_player("north")
        self.assertIn("Generic block.", msg)
        self.assertEqual(self.game.player_location, "start")

    def test_move_player_generic_exit_message(self):
        """Test move_player with generic exit message (non-blocking)."""
        self.game.world_map["start"]["events"] = {
            "exit": [
                {
                    "condition": {},
                    "actions": [{"type": "print", "message": "Generic msg."}]
                }
            ]
        }
        msg = self.game.move_player("north")
        self.assertIn("Generic msg.", msg)
        self.assertEqual(self.game.player_location, "hallway")

    def test_take_item_blocked(self):
        """Test take_item blocked by event."""
        self.game.world_map["start"]["items"] = [
            {
                "name": "cursed_gold",
                "description": "Gold",
                "events": {
                    "take": [
                        {
                            "condition": {},
                            "actions": [{"type": "block", "message": "It burns!"}]
                        }
                    ]
                }
            }
        ]
        msg = self.game.take_item("cursed_gold")
        self.assertEqual(msg, "It burns!")
        self.assertNotIn({"name": "cursed_gold", "description": "Gold"}, self.game.inventory)

    def test_drop_item_blocked(self):
        """Test drop_item blocked by event."""
        item = {
            "name": "sticky_ball",
            "description": "Sticky",
            "events": {
                "drop": [
                    {
                        "condition": {},
                        "actions": [{"type": "block", "message": "It's stuck!"}]
                    }
                ]
            }
        }
        self.game.inventory.append(item)
        msg = self.game.drop_item("sticky_ball")
        self.assertEqual(msg, "It's stuck!")
        self.assertIn(item, self.game.inventory)

    def test_examine_item_event(self):
        """Test examine_item triggering events."""
        self.game.world_map["start"]["items"] = [
            {
                "name": "orb",
                "description": "Glowing orb.",
                "events": {
                    "examine": [
                         {
                             "condition": {},
                             "actions": [{"type": "print", "message": "It glows brighter."}]
                         }
                    ]
                }
            }
        ]
        msg = self.game.examine_item("orb")
        self.assertIn("Glowing orb.", msg)
        self.assertIn("It glows brighter.", msg)

        # Test character examine event
        self.game.world_map["start"]["characters"] = [
            {
                "name": "sage",
                "description": "Old sage.",
                "events": {
                    "examine": [
                         {
                             "condition": {},
                             "actions": [{"type": "print", "message": "He winks."}]
                         }
                    ]
                }
            }
        ]
        msg = self.game.examine_item("sage")
        self.assertIn("Old sage.", msg)
        self.assertIn("He winks.", msg)

        # Test room examine event
        self.game.world_map["start"]["events"] = {
            "examine": [
                 {
                     "condition": {},
                     "actions": [{"type": "print", "message": "You feel cold."}]
                 }
            ]
        }
        msg = self.game.examine_item("room")
        self.assertIn("You feel cold.", msg)

    def test_talk_to_character_event_message(self):
        """Test talk_to_character triggering event messages."""
        self.game.world_map["start"]["characters"] = [
            {
                "name": "bard",
                "description": "A bard.",
                "dialogue": "La la la.",
                "events": {
                    "talk": [
                        {
                            "condition": {},
                            "actions": [{"type": "print", "message": "He tunes his lute."}]
                        }
                    ]
                }
            }
        ]
        msg = self.game.talk_to_character("bard")
        self.assertIn("He tunes his lute.", msg)
        self.assertIn("La la la.", msg)

    def test_talk_to_character_event_message_complex(self):
        """Test talk_to_character triggering event messages with complex dialogue."""
        dialogue = {
            "start_node": "start",
            "nodes": {"start": {"text": "Hello", "options": []}}
        }
        self.game.world_map["start"]["characters"] = [
            {
                "name": "bard",
                "description": "A bard.",
                "dialogue": dialogue,
                "events": {
                    "talk": [
                        {
                            "condition": {},
                            "actions": [{"type": "print", "message": "He looks up."}]
                        }
                    ]
                }
            }
        ]
        msg = self.game.talk_to_character("bard")
        self.assertIn("He looks up.", msg)
        self.assertIn("Hello", msg)

    def test_make_dialogue_choice_invalid(self):
        """Test invalid dialogue choices."""
        self.game.dialogue_active = True
        self.game.current_dialogue = {
            "start_node": "start",
            "nodes": {
                "start": {
                    "text": "Hi",
                    "options": [{"text": "Opt1", "condition": {}}]
                }
            }
        }
        self.game.current_dialogue_node_id = "start"

        self.assertEqual(self.game.make_dialogue_choice(0), "Invalid choice.")
        self.assertEqual(self.game.make_dialogue_choice(2), "Invalid choice.")

    def test_make_dialogue_choice_not_active(self):
        """Test make_dialogue_choice when not active."""
        self.game.dialogue_active = False
        self.assertEqual(self.game.make_dialogue_choice(1), "You are not in a conversation.")

    def test_perform_action_set_true_false(self):
        """Test set_true and set_false actions."""
        self.game.perform_action({"type": "set_true", "target": "flag"})
        self.assertTrue(self.game.game_state.get("flag"))

        self.game.perform_action({"type": "set_false", "target": "flag"})
        self.assertFalse(self.game.game_state.get("flag"))

    def test_control_dialogue_interaction(self):
        """Test Control loop dialogue interactions."""
        # Setup dialogue
        self.control.game.dialogue_active = True
        self.control.game.current_dialogue = {
            "start_node": "start",
            "nodes": {
                "start": {
                    "text": "Choose",
                    "options": [
                        {"text": "A", "next_node": "end", "condition": {}},
                        {"text": "B", "next_node": "end", "condition": {}}
                    ]
                },
                "end": {"text": "Done", "options": []}
            }
        }
        self.control.game.current_dialogue_node_id = "start"

        # Test numeric input
        with patch('builtins.print') as mock_print:
            # "1" makes choice. If next node has no options, it stays in dialogue active unless ended.
            # "quit" ends dialogue.
            # "quit" ends game loop.
            with patch('builtins.input', side_effect=["1", "quit", "quit"]):
                self.control.main_game_loop()
            self.assertTrue(any("Done" in str(c) for c in mock_print.mock_calls))

        # Reset
        self.control.done = False
        self.control.game.dialogue_active = True
        self.control.game.current_dialogue_node_id = "start"

        # Test invalid input
        with patch('builtins.print') as mock_print:
            # "invalid" -> error message, loop continues.
            # "quit" -> end dialogue.
            # "quit" -> end game loop.
            with patch('builtins.input', side_effect=["invalid", "quit", "quit"]):
                self.control.main_game_loop()
            self.assertTrue(any("Please enter the number" in str(c) for c in mock_print.mock_calls))

    def test_examine_inventory_and_location_item(self):
        """Test examine_item finding items in inventory and location explicitly."""
        inv_item = {"name": "inv_item", "description": "In pocket."}
        loc_item = {"name": "loc_item", "description": "On floor."}

        self.game.inventory.append(inv_item)
        self.game.world_map["start"]["items"] = [loc_item]

        self.assertIn("In pocket.", self.game.examine_item("inv_item"))
        self.assertIn("On floor.", self.game.examine_item("loc_item"))

    def test_examine_inventory_item_with_event(self):
        """Test examine_item for inventory item with event message."""
        inv_item = {
            "name": "magic_orb",
            "description": "It glows.",
            "events": {
                "examine": [
                    {
                        "condition": {},
                        "actions": [{"type": "print", "message": "You hear humming."}]
                    }
                ]
            }
        }
        self.game.inventory.append(inv_item)
        desc = self.game.examine_item("magic_orb")
        self.assertIn("It glows.", desc)
        self.assertIn("You hear humming.", desc)

    def test_examine_location_item_with_event(self):
        """Test examine_item for location item with event message."""
        loc_item = {
            "name": "ancient_rune",
            "description": "Carved in stone.",
            "events": {
                "examine": [
                    {
                        "condition": {},
                        "actions": [{"type": "print", "message": "It pulses."}]
                    }
                ]
            }
        }
        self.game.world_map["start"]["items"].append(loc_item)
        desc = self.game.examine_item("ancient_rune")
        self.assertIn("Carved in stone.", desc)
        self.assertIn("It pulses.", desc)

    def test_control_talk_variations(self):
        """Test control talk command variations."""
        with patch('builtins.print') as mock_print:
            with patch('builtins.input', side_effect=["talk", "talk to", "quit"]):
                self.control.main_game_loop()
            self.assertTrue(any("Talk to whom?" in str(c) for c in mock_print.mock_calls))
            # "talk to" falls into "talk to <char>" logic but fails if len <= 2?
            # command is "talk", user_input is ["talk", "to"].
            # if user_input[1] == "to" and len > 2: ... else ...
            # so if "talk to", it goes to else -> char_name="to".
            # It should print "There is no one named to here."
            self.assertTrue(any("no one named to" in str(c) for c in mock_print.mock_calls))

    def test_get_dialogue_text_inactive(self):
        """Test _get_dialogue_text when dialogue is not active."""
        self.game.dialogue_active = False
        self.assertEqual(self.game._get_dialogue_text(), "")

    def test_talk_to_character_simple_no_events(self):
        """Test talk_to_character with simple dialogue and no events."""
        self.game.world_map["start"]["characters"] = [
            {
                "name": "simple_npc",
                "description": "Simple.",
                "dialogue": "Hello there."
            }
        ]
        msg = self.game.talk_to_character("simple_npc")
        self.assertEqual(msg, 'simple_npc says: "Hello there."')
