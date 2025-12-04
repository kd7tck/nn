import unittest
from unittest.mock import patch
from src.game import Game
from src.control import Control

class TestCoverageImprovements(unittest.TestCase):
    def setUp(self):
        """Set up for tests.

        Args:
            None

        Returns:
            None
        """
        self.game = Game()
        self.control = Control()

    def test_get_article_empty(self):
        """Test _get_article with empty string.

        Args:
            None

        Returns:
            None
        """
        self.assertEqual(self.game._get_article(""), "")
        self.assertEqual(self.game._get_article(None), "")

    def test_format_item_list_empty(self):
        """Test _format_item_list with empty list.

        Args:
            None

        Returns:
            None
        """
        self.assertEqual(self.game._format_item_list([]), "")
        self.assertEqual(self.game._format_item_list(None), "")

    def test_perform_action_modify_room(self):
        """Test modify_room action.

        Args:
            None

        Returns:
            None
        """
        # Setup a dummy room in world map
        self.game.world_map["test_room"] = {"description": "Old description"}

        action = {
            "type": "modify_room",
            "room_id": "test_room",
            "property": "description",
            "value": "New description"
        }
        self.game.perform_action(action)
        self.assertEqual(self.game.world_map["test_room"]["description"], "New description")

    def test_perform_action_add_remove_item(self):
        """Test add_item and remove_item actions.

        Args:
            None

        Returns:
            None
        """
        item = {"name": "test_item", "description": "desc"}

        # Test add_item
        action_add = {"type": "add_item", "item": item}
        self.game.perform_action(action_add)
        self.assertIn(item, self.game.inventory)

        # Test remove_item
        action_remove = {"type": "remove_item", "item_name": "test_item"}
        self.game.perform_action(action_remove)
        self.assertNotIn(item, self.game.inventory)

    def test_perform_action_set_val(self):
        """Test set_val action.

        Args:
            None

        Returns:
            None
        """
        action = {"type": "set_val", "target": "test_var", "value": 123}
        self.game.perform_action(action)
        self.assertEqual(self.game.game_state.get("test_var"), 123)

    def test_process_events_blocked(self):
        """Test process_events returning blocked state.

        Args:
            None

        Returns:
            None
        """
        source = {
            "events": {
                "test_trigger": [
                    {
                        "condition": {},
                        "actions": [
                            {"type": "block", "message": "Blocked!"}
                        ]
                    }
                ]
            }
        }
        msgs, blocked = self.game.process_events(source, "test_trigger")
        self.assertTrue(blocked)
        self.assertEqual(msgs, ["Blocked!"])

    def test_process_events_blocked_no_message(self):
        """Test process_events blocked without message.

        Args:
            None

        Returns:
            None
        """
        source = {
            "events": {
                "test_trigger": [
                    {
                        "condition": {},
                        "actions": [{"type": "block"}]
                    }
                ]
            }
        }
        msgs, blocked = self.game.process_events(source, "test_trigger")
        self.assertTrue(blocked)
        self.assertEqual(msgs, [])

    def test_get_location_description_variations(self):
        """Test get_location_description with various text keys.

        Args:
            None

        Returns:
            None
        """
        # Mock world map
        self.game.player_location = "test_loc"
        self.game.visited_counts["test_loc"] = 1
        self.game.world_map["test_loc"] = {
            "description": "Default desc",
            "first_arrival_text": "First time here",
            "transition_text": "Moving in",
            "items": [],
            "exits": {}
        }

        # Test first arrival
        desc = self.game.get_location_description(arrival=True)
        self.assertIn("Moving in", desc)
        self.assertIn("First time here", desc)

        # Test second arrival (nth not set, default fallback)
        self.game.visited_counts["test_loc"] = 2
        desc = self.game.get_location_description(arrival=True)
        self.assertIn("Moving in", desc)
        self.assertIn("Default desc", desc)

        # Test nth arrival
        self.game.world_map["test_loc"]["nth_arrival_text"] = {2: "Back again"}
        desc = self.game.get_location_description(arrival=True)
        self.assertIn("Moving in", desc)
        self.assertIn("Back again", desc)

    def test_move_player_blocked_by_exit_event(self):
        """Test move_player being blocked by exit_{direction} event.

        Args:
            None

        Returns:
            None
        """
        self.game.player_location = "start"
        self.game.world_map["start"]["exits"]["north"] = "hallway"
        self.game.world_map["start"]["events"] = {
            "exit_north": [
                {
                    "condition": {},
                    "actions": [{"type": "block", "message": "You shall not pass!"}]
                }
            ]
        }

        msg = self.game.move_player("north")
        self.assertEqual(msg, "You shall not pass!")
        self.assertEqual(self.game.player_location, "start")

    def test_examine_room_and_items(self):
        """Test examine command for room and items.

        Args:
            None

        Returns:
            None
        """
        self.game.player_location = "start"
        self.game.world_map["start"]["items"] = [{"name": "rock", "description": "Just a rock"}]
        self.game.world_map["start"]["characters"] = [{"name": "bob", "description": "It's Bob"}]
        self.game.world_map["start"]["examination_text"] = "Room detail"

        # Examine room
        self.assertIn("Room detail", self.game.examine_item("room"))
        self.assertIn("Room detail", self.game.examine_item("here"))

        # Examine item in room
        self.assertEqual(self.game.examine_item("rock"), "Just a rock")

        # Examine character
        self.assertEqual(self.game.examine_item("bob"), "It's Bob")

        # Examine non-existent
        self.assertIn("don't see a ghost", self.game.examine_item("ghost"))

    def test_talk_to_character_blocked(self):
        """Test talking to a character blocked by event.

        Args:
            None

        Returns:
            None
        """
        self.game.player_location = "start"
        self.game.world_map["start"]["characters"] = [
            {
                "name": "shy_guy",
                "description": "Shy",
                "dialogue": "Hi",
                "events": {
                    "talk": [
                        {
                            "condition": {},
                            "actions": [{"type": "block", "message": "He runs away."}]
                        }
                    ]
                }
            }
        ]

        msg = self.game.talk_to_character("shy_guy")
        self.assertEqual(msg, "He runs away.")
        self.assertFalse(self.game.dialogue_active)

    def test_complex_dialogue_flow(self):
        """Test complex dialogue interactions.

        Args:
            None

        Returns:
            None
        """
        dialogue_tree = {
            "start_node": "node1",
            "nodes": {
                "node1": {
                    "text": "Hello",
                    "options": [
                        {
                            "text": "Option 1",
                            "next_node": "node2",
                            "condition": {}
                        },
                        {
                            "text": "Option 2 (Hidden)",
                            "condition": {"var_true": "impossible"}
                        }
                    ]
                },
                "node2": {
                    "text": "Bye",
                    "options": [
                         {
                             "text": "End",
                             "actions": [{"type": "set_true", "target": "talked_node2"}]
                         }
                    ]
                }
            }
        }

        self.game.player_location = "start"
        self.game.world_map["start"]["characters"] = [
            {"name": "npc", "description": "npc", "dialogue": dialogue_tree}
        ]

        # Initiate dialogue
        msg = self.game.talk_to_character("npc")
        self.assertIn("Hello", msg)
        self.assertIn("1. Option 1", msg)
        self.assertNotIn("Option 2", msg)
        self.assertTrue(self.game.dialogue_active)

        # Make choice
        msg = self.game.make_dialogue_choice(1)
        self.assertIn("Bye", msg)
        self.assertEqual(self.game.current_dialogue_node_id, "node2")

        # End dialogue via choice
        msg = self.game.make_dialogue_choice(1)
        self.assertIn("stop talking", msg)
        self.assertFalse(self.game.dialogue_active)
        self.assertTrue(self.game.game_state.get("talked_node2"))

    def test_control_input_handling(self):
        """Test Control class input handling for various commands.

        Args:
            None

        Returns:
            None
        """
        # Mock print
        with patch('builtins.print') as mock_print:
            # Quit
            with patch('builtins.input', side_effect=["quit"]):
                self.control.main_game_loop()
            self.assertTrue(self.control.done)

            # Reset
            self.control.done = False

            # Go where?
            with patch('builtins.input', side_effect=["go", "quit"]):
                self.control.main_game_loop()
                # Verify "Go where?" was printed
                # Access calls on mock_print
                # We expect "Go where?" to be in one of the calls
                self.assertTrue(any("Go where?" in str(c) for c in mock_print.mock_calls))

            # Reset
            self.control.done = False

            # Talk to logic
            with patch('builtins.input', side_effect=["talk to guard", "quit"]):
                with patch.object(self.control.game, 'talk_to_character') as mock_talk:
                    mock_talk.return_value = "Talking..."
                    self.control.main_game_loop()
                    mock_talk.assert_called_with("guard")
