"""Combined unit tests for the TextGameTemplate project.

This module contains all test cases merged from separate test files to verify
the functionality of the Game and Control classes, covering logic, movement,
interactions, stats, dialogue, and edge cases.
"""

import unittest
from unittest.mock import patch, call
import os
import json
import shutil
from src.control import Control
from src.game import Game
from src.loader import load_characters, load_templates


class TestControl(unittest.TestCase):
    """Test cases for the Control class."""

    def setUp(self):
        """Set up a new Control instance before each test.

        Args:
            None

        Returns:
            None
        """
        self.control = Control()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_quit_command(self, mock_print, mock_input):
        """Test the 'quit' command.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = ["quit"]
        self.control.main_game_loop()
        self.assertTrue(self.control.done)
        # Verify welcome message and thanks message
        self.assertIn(call("Welcome to TextGameTemplate!"), mock_print.call_args_list)
        self.assertIn(call("Thanks for playing!"), mock_print.call_args_list)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_movement_commands(self, mock_print, mock_input):
        """Test movement commands and their aliases.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        # 'n' for north, 'go east' for east
        mock_input.side_effect = ["n", "go east", "quit"]
        self.control.main_game_loop()

        # Verify calls related to movement
        # First move: n -> north (from start to hallway)
        # Second move: go east -> east (from hallway, invalid move)
        # Note: Need to check specific output messages to be sure

        # Capture print calls to verify logic
        printed_messages = [c[0][0] for c in mock_print.call_args_list]
        self.assertTrue(any("You step into the long hallway" in m for m in printed_messages))
        self.assertTrue(any("You can't go that way" in m for m in printed_messages))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_look_command(self, mock_print, mock_input):
        """Test the 'look' command.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = ["look", "quit"]
        self.control.main_game_loop()

        printed_messages = [c[0][0] for c in mock_print.call_args_list]
        # Look should print description without transition text
        self.assertTrue(any("You are in a dimly lit room" in m for m in printed_messages))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_inventory_commands(self, mock_print, mock_input):
        """Test 'take', 'drop', and 'inventory' commands.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = [
            "inventory",        # Empty
            "take key",         # Take existing item
            "inventory",        # Check it's there
            "drop key",         # Drop it
            "inventory",        # Empty again
            "take fake_item",   # Take non-existent
            "drop fake_item",   # Drop non-existent
            "quit"
        ]
        self.control.main_game_loop()

        printed_messages = [c[0][0] for c in mock_print.call_args_list]
        self.assertTrue(any("Your inventory is empty" in m for m in printed_messages))
        self.assertTrue(any("You take the key" in m for m in printed_messages))
        self.assertTrue(any("You are carrying: key" in m for m in printed_messages))
        self.assertTrue(any("You drop the key" in m for m in printed_messages))
        self.assertTrue(any("There is no fake_item here" in m for m in printed_messages))
        self.assertTrue(any("You don't have a fake_item" in m for m in printed_messages))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_examine_command(self, mock_print, mock_input):
        """Test the 'examine' command.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = [
            "examine key",      # Examine item in room
            "examine room",     # Examine room
            "examine fake",     # Examine non-existent
            "quit"
        ]
        self.control.main_game_loop()

        printed_messages = [c[0][0] for c in mock_print.call_args_list]
        self.assertTrue(any("A small, rusty key" in m for m in printed_messages))
        self.assertTrue(any("The walls are bare concrete" in m for m in printed_messages))
        self.assertTrue(any("You don't see a fake here" in m for m in printed_messages))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_incomplete_commands(self, mock_print, mock_input):
        """Test commands without required arguments.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = [
            "go",
            "take",
            "drop",
            "examine",
            "quit"
        ]
        self.control.main_game_loop()

        printed_messages = [c[0][0] for c in mock_print.call_args_list]
        self.assertTrue(any("Go where?" in m for m in printed_messages))
        self.assertTrue(any("Take what?" in m for m in printed_messages))
        self.assertTrue(any("Drop what?" in m for m in printed_messages))
        self.assertTrue(any("Examine what?" in m for m in printed_messages))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_unknown_command(self, mock_print, mock_input):
        """Test unknown command.

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = ["xyzzy", "quit"]
        self.control.main_game_loop()

        printed_messages = [c[0][0] for c in mock_print.call_args_list]
        self.assertTrue(any("Unknown command" in m for m in printed_messages))

    @patch("builtins.input")
    @patch("builtins.print")
    def test_empty_input(self, mock_print, mock_input):
        """Test empty input (just pressing enter).

        Args:
            mock_print: Mock for print function.
            mock_input: Mock for input function.

        Returns:
            None
        """
        mock_input.side_effect = ["", "quit"]
        self.control.main_game_loop()
        # Should just loop again without crashing
        self.assertTrue(self.control.done)


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


class TestGame(unittest.TestCase):
    """Test cases for the Game class."""

    def setUp(self):
        """Set up a new Game instance before each test.

        This ensures that each test starts with a fresh game state.

        Args:
            None

        Returns:
            None
        """
        self.game = Game()

    def test_take_item(self):
        """Test taking an item.

        Verifies that an item can be taken from the room and added to the
        player's inventory.

        Args:
            None

        Returns:
            None
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

        Args:
            None

        Returns:
            None
        """
        self.game.take_item("key")
        self.assertEqual(
            self.game.drop_item("key"), "You drop the key."
        )
        self.assertEqual(len(self.game.inventory), 0)

    def test_examine_item_in_room(self):
        """Test examining an item in the room.

        Verifies that an item in the current location can be examined.

        Args:
            None

        Returns:
            None
        """
        self.assertEqual(
            self.game.examine_item("key"), "A small, rusty key."
        )

    def test_examine_item_in_inventory(self):
        """Test examining an item in the inventory.

        Verifies that an item in the player's inventory can be examined.

        Args:
            None

        Returns:
            None
        """
        self.game.take_item("key")
        self.assertEqual(
            self.game.examine_item("key"), "A small, rusty key."
        )

    def test_inventory_output_punctuation(self):
        """Test that inventory output consistently ends with a period.

        Verifies that the get_inventory method returns a string ending with
        a period, regardless of whether the inventory is empty or contains items.

        Args:
            None

        Returns:
            None
        """
        # Case 1: Empty inventory
        self.assertEqual(self.game.get_inventory(), "Your inventory is empty.")

        # Case 2: One item
        self.game.inventory.append({"name": "key"})
        self.assertEqual(self.game.get_inventory(), "You are carrying: key.")

        # Case 3: Multiple items
        self.game.inventory.append({"name": "sword"})
        self.assertEqual(self.game.get_inventory(), "You are carrying: key, sword.")


class TestGameLogic(unittest.TestCase):
    """Test cases for Game logic including conditions and actions."""

    def setUp(self):
        """Set up a new Game instance before each test.

        Args:
            None

        Returns:
            None
        """
        self.game = Game()

    def test_check_condition_basics(self):
        """Test basic conditions.

        Args:
            None

        Returns:
            None
        """
        # Test empty condition
        self.assertTrue(self.game.check_condition({}))
        self.assertTrue(self.game.check_condition(None))

        # Test in_location
        self.game.player_location = "start"
        self.assertTrue(self.game.check_condition({"in_location": "start"}))
        self.assertFalse(self.game.check_condition({"in_location": "kitchen"}))

    def test_check_condition_items(self):
        """Test has_item condition.

        Args:
            None

        Returns:
            None
        """
        self.game.inventory = [{"name": "key"}]
        self.assertTrue(self.game.check_condition({"has_item": "key"}))
        self.assertFalse(self.game.check_condition({"has_item": "sword"}))

    def test_check_condition_vars(self):
        """Test variable conditions (var_true, var_false, var_eq).

        Args:
            None

        Returns:
            None
        """
        self.game.game_state = {"door_open": True, "counter": 5}

        # var_true
        self.assertTrue(self.game.check_condition({"var_true": "door_open"}))
        self.assertFalse(self.game.check_condition({"var_true": "missing_var"}))

        # var_false
        self.assertTrue(self.game.check_condition({"var_false": "missing_var"}))
        self.assertFalse(self.game.check_condition({"var_false": "door_open"}))

        # var_eq
        self.assertTrue(self.game.check_condition({"var_eq": {"counter": 5}}))
        self.assertFalse(self.game.check_condition({"var_eq": {"counter": 3}}))
        self.assertFalse(self.game.check_condition({"var_eq": {"missing_var": 1}}))

    def test_check_condition_not(self):
        """Test the 'not' condition.

        Args:
            None

        Returns:
            None
        """
        # Not empty (true) -> False
        self.assertFalse(self.game.check_condition({"not": {}}))

        # Not false condition -> True
        self.assertFalse(self.game.check_condition({"has_item": "sword"}))
        self.assertTrue(self.game.check_condition({"not": {"has_item": "sword"}}))

    def test_perform_action(self):
        """Test performing actions.

        Args:
            None

        Returns:
            None
        """
        # Print action
        msg = self.game.perform_action({"type": "print", "message": "Hello"})
        self.assertEqual(msg, "Hello")

        # set_true
        self.game.perform_action({"type": "set_true", "target": "flag"})
        self.assertTrue(self.game.game_state["flag"])

        # set_false
        self.game.perform_action({"type": "set_false", "target": "flag"})
        self.assertFalse(self.game.game_state["flag"])

        # set_val
        self.game.perform_action({"type": "set_val", "target": "count", "value": 10})
        self.assertEqual(self.game.game_state["count"], 10)

        # modify_room
        self.game.perform_action({
            "type": "modify_room",
            "room_id": "start",
            "property": "description",
            "value": "New Desc"
        })
        self.assertEqual(self.game.world_map["start"]["description"], "New Desc")

        # modify_room (invalid room)
        self.game.perform_action({
            "type": "modify_room",
            "room_id": "invalid_room",
            "property": "description",
            "value": "New Desc"
        })
        # Should not raise error

    def test_process_events(self):
        """Test processing events.

        Args:
            None

        Returns:
            None
        """
        # Setup a custom object with events
        obj = {
            "events": {
                "touch": [
                    {
                        "condition": {"var_true": "active"},
                        "actions": [
                            {"type": "print", "message": "Touched!"},
                            {"type": "set_true", "target": "touched"}
                        ]
                    }
                ]
            }
        }

        # Condition not met
        self.game.game_state["active"] = False
        msgs, blocked = self.game.process_events(obj, "touch")
        self.assertEqual(msgs, [])
        self.assertFalse(blocked)
        self.assertFalse(self.game.game_state.get("touched"))

        # Condition met
        self.game.game_state["active"] = True
        msgs, blocked = self.game.process_events(obj, "touch")
        self.assertEqual(msgs, ["Touched!"])
        self.assertFalse(blocked)
        self.assertTrue(self.game.game_state["touched"])

        # Trigger not found
        msgs, blocked = self.game.process_events(obj, "look")
        self.assertEqual(msgs, [])
        self.assertFalse(blocked)

        # No events key
        msgs, blocked = self.game.process_events({}, "look")
        self.assertEqual(msgs, [])
        self.assertFalse(blocked)

    def test_process_events_block(self):
        """Test blocking events.

        Args:
            None

        Returns:
            None
        """
        obj = {
            "events": {
                "go_north": [
                    {
                        "condition": {},
                        "actions": [
                            {"type": "block", "message": "Blocked!"}
                        ]
                    }
                ]
            }
        }
        msgs, blocked = self.game.process_events(obj, "go_north")
        self.assertEqual(msgs, ["Blocked!"])
        self.assertTrue(blocked)

    def test_location_description_variants(self):
        """Test different variants of location descriptions.

        Args:
            None

        Returns:
            None
        """
        room = self.game.world_map["start"]
        # Add a custom item
        room["items"].append({"name": "rock", "description": "A rock"})

        # Arrival = False
        desc = self.game.get_location_description(arrival=False)
        self.assertIn(room["description"], desc)
        self.assertIn("You see a key and a rock.", desc)

        # Arrival = True, First visit (count=1)
        self.game.visited_counts["start"] = 1
        desc = self.game.get_location_description(arrival=True)
        self.assertIn(room["transition_text"], desc)
        self.assertIn(room["first_arrival_text"], desc)

        # Arrival = True, Second visit
        self.game.visited_counts["start"] = 2
        # Start doesn't have nth_arrival_text for 2, so it falls back to description
        desc = self.game.get_location_description(arrival=True)
        self.assertIn(room["description"], desc)

        # Test nth_arrival_text (hallway has one for visit 2)
        self.game.player_location = "hallway"
        self.game.visited_counts["hallway"] = 2
        desc = self.game.get_location_description(arrival=True)
        self.assertIn("You find yourself back in the long hallway.", desc)

    def test_examine_item_complex(self):
        """Test examine item with events.

        Args:
            None

        Returns:
            None
        """
        # Mock an item with examine event
        item = {
            "name": "magic_orb",
            "description": "A glowing orb.",
            "events": {
                "examine": [
                    {
                        "condition": {},
                        "actions": [{"type": "print", "message": "It hums with power."}]
                    }
                ]
            }
        }
        self.game.inventory.append(item)
        desc = self.game.examine_item("magic_orb")
        self.assertIn("A glowing orb.", desc)
        self.assertIn("It hums with power.", desc)

    def test_examine_item_in_room_with_event(self):
        """Test examining an item in the room that has events.

        Args:
            None

        Returns:
            None
        """
        item = {
            "name": "statue",
            "description": "A stone statue.",
            "events": {
                "examine": [
                    {
                        "condition": {},
                        "actions": [{"type": "print", "message": "It seems to be watching you."}]
                    }
                ]
            }
        }
        self.game.world_map[self.game.player_location]["items"].append(item)
        desc = self.game.examine_item("statue")
        self.assertIn("A stone statue.", desc)
        self.assertIn("It seems to be watching you.", desc)

    def test_locked_door(self):
        """Test the legacy locked door logic (now implemented via events).

        Args:
            None

        Returns:
            None
        """
        # Move to hallway
        self.game.move_player("north")
        self.assertEqual(self.game.player_location, "hallway")

        # Try to move to treasure room without key
        # Ensure key is not in inventory
        self.game.inventory = []
        msg = self.game.move_player("north")
        self.assertEqual(msg, "The door is locked.")
        self.assertEqual(self.game.player_location, "hallway")

        # Now get the key and try again
        self.game.inventory.append({"name": "key"})
        msg = self.game.move_player("north")
        self.assertIn("At last! You have discovered the legendary treasure room.", msg)
        self.assertEqual(self.game.player_location, "treasure_room")

    def test_examine_room_event(self):
        """Test examine room with events.

        Args:
            None

        Returns:
            None
        """
        room = self.game.world_map["start"]
        room["events"] = {
            "examine": [
                {
                    "condition": {},
                    "actions": [{"type": "print", "message": "You notice a crack in the wall."}]
                }
            ]
        }
        desc = self.game.examine_item("room")
        self.assertIn(room["examination_text"], desc)
        self.assertIn("You notice a crack in the wall.", desc)


class TestExpandedMovement(unittest.TestCase):
    """Test cases for the expanded movement system."""

    def setUp(self):
        """Set up a new Game instance before each test.

        This ensures that each test starts with a fresh game state.

        Args:
            None

        Returns:
            None
        """
        self.game = Game()
        self.control = Control()

    def test_move_diagonal_blocked(self):
        """Test that diagonal movement can be blocked.

        Verifies that moving to the garden is blocked if the player does
        not have the sword.

        Args:
            None

        Returns:
            None
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

        Args:
            None

        Returns:
            None
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

        Args:
            None

        Returns:
            None
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

        Args:
            None

        Returns:
            None
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

        Args:
            None

        Returns:
            None
        """
        result = self.game.move_player("northwest") # No exit northwest from start
        self.assertEqual(result, "You can't go that way.")


class TestRemainingCoverage(unittest.TestCase):
    def setUp(self):
        """Set up for tests.

        Args:
            None

        Returns:
            None
        """
        self.game = Game()
        self.control = Control()

    def test_process_events_check_condition_false(self):
        """Test process_events where condition is not met.

        Args:
            None

        Returns:
            None
        """
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
        """Test process_events capturing action output.

        Args:
            None

        Returns:
            None
        """
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
        """Test get_location_description with transition text.

        Args:
            None

        Returns:
            None
        """
        self.game.world_map["start"]["transition_text"] = "Entering start."
        self.game.visited_counts["start"] = 2 # Force non-first arrival
        desc = self.game.get_location_description(arrival=True)
        self.assertIn("Entering start.", desc)

    def test_format_item_list_multiple(self):
        """Test _format_item_list with various lengths.

        Args:
            None

        Returns:
            None
        """
        items = [{"name": "a"}, {"name": "b"}, {"name": "c"}]
        self.assertEqual(self.game._format_item_list(items[:1]), "an a")
        self.assertEqual(self.game._format_item_list(items[:2]), "an a and a b")
        self.assertEqual(self.game._format_item_list(items), "an a, a b, and a c")

    def test_move_player_generic_exit_blocked(self):
        """Test move_player blocked by generic exit event.

        Args:
            None

        Returns:
            None
        """
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
        """Test move_player with generic exit message (non-blocking).

        Args:
            None

        Returns:
            None
        """
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
        """Test take_item blocked by event.

        Args:
            None

        Returns:
            None
        """
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
        """Test drop_item blocked by event.

        Args:
            None

        Returns:
            None
        """
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
        """Test examine_item triggering events.

        Args:
            None

        Returns:
            None
        """
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
        """Test talk_to_character triggering event messages.

        Args:
            None

        Returns:
            None
        """
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
        """Test talk_to_character triggering event messages with complex dialogue.

        Args:
            None

        Returns:
            None
        """
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
        """Test invalid dialogue choices.

        Args:
            None

        Returns:
            None
        """
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
        """Test make_dialogue_choice when not active.

        Args:
            None

        Returns:
            None
        """
        self.game.dialogue_active = False
        self.assertEqual(self.game.make_dialogue_choice(1), "You are not in a conversation.")

    def test_perform_action_set_true_false(self):
        """Test set_true and set_false actions.

        Args:
            None

        Returns:
            None
        """
        self.game.perform_action({"type": "set_true", "target": "flag"})
        self.assertTrue(self.game.game_state.get("flag"))

        self.game.perform_action({"type": "set_false", "target": "flag"})
        self.assertFalse(self.game.game_state.get("flag"))

    def test_control_dialogue_interaction(self):
        """Test Control loop dialogue interactions.

        Args:
            None

        Returns:
            None
        """
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
        """Test examine_item finding items in inventory and location explicitly.

        Args:
            None

        Returns:
            None
        """
        inv_item = {"name": "inv_item", "description": "In pocket."}
        loc_item = {"name": "loc_item", "description": "On floor."}

        self.game.inventory.append(inv_item)
        self.game.world_map["start"]["items"] = [loc_item]

        self.assertIn("In pocket.", self.game.examine_item("inv_item"))
        self.assertIn("On floor.", self.game.examine_item("loc_item"))

    def test_examine_inventory_item_with_event(self):
        """Test examine_item for inventory item with event message.

        Args:
            None

        Returns:
            None
        """
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
        """Test examine_item for location item with event message.

        Args:
            None

        Returns:
            None
        """
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
        """Test control talk command variations.

        Args:
            None

        Returns:
            None
        """
        with patch('builtins.print') as mock_print:
            with patch('builtins.input', side_effect=["talk", "talk to", "quit"]):
                self.control.main_game_loop()
            self.assertTrue(any("Talk to whom?" in str(c) for c in mock_print.mock_calls))
            # command "talk to" should now prompt "Talk to whom?" instead of "There is no one named to here."
            # We verified "Talk to whom?" above.
            self.assertFalse(any("no one named to" in str(c) for c in mock_print.mock_calls))

    def test_get_dialogue_text_inactive(self):
        """Test _get_dialogue_text when dialogue is not active.

        Args:
            None

        Returns:
            None
        """
        self.game.dialogue_active = False
        self.assertEqual(self.game._get_dialogue_text(), "")

    def test_talk_to_character_simple_no_events(self):
        """Test talk_to_character with simple dialogue and no events.

        Args:
            None

        Returns:
            None
        """
        self.game.world_map["start"]["characters"] = [
            {
                "name": "simple_npc",
                "description": "Simple.",
                "dialogue": "Hello there."
            }
        ]
        msg = self.game.talk_to_character("simple_npc")
        self.assertEqual(msg, 'simple_npc says: "Hello there."')


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

if __name__ == "__main__":
    unittest.main()
