"""Unit tests for the Game class logic and edge cases.

This module targets specific methods in Game class to ensure full coverage of conditions,
actions, event processing, and description generation.
"""

import unittest
from src.game import Game


class TestGameLogic(unittest.TestCase):
    """Test cases for Game logic including conditions and actions."""

    def setUp(self):
        """Set up a new Game instance before each test."""
        self.game = Game()

    def test_check_condition_basics(self):
        """Test basic conditions."""
        # Test empty condition
        self.assertTrue(self.game.check_condition({}))
        self.assertTrue(self.game.check_condition(None))

        # Test in_location
        self.game.player_location = "start"
        self.assertTrue(self.game.check_condition({"in_location": "start"}))
        self.assertFalse(self.game.check_condition({"in_location": "kitchen"}))

    def test_check_condition_items(self):
        """Test has_item condition."""
        self.game.inventory = [{"name": "key"}]
        self.assertTrue(self.game.check_condition({"has_item": "key"}))
        self.assertFalse(self.game.check_condition({"has_item": "sword"}))

    def test_check_condition_vars(self):
        """Test variable conditions (var_true, var_false, var_eq)."""
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
        """Test the 'not' condition."""
        # Not empty (true) -> False
        self.assertFalse(self.game.check_condition({"not": {}}))

        # Not false condition -> True
        self.assertFalse(self.game.check_condition({"has_item": "sword"}))
        self.assertTrue(self.game.check_condition({"not": {"has_item": "sword"}}))

    def test_perform_action(self):
        """Test performing actions."""
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
        """Test processing events."""
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
        """Test blocking events."""
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
        """Test different variants of location descriptions."""
        room = self.game.world_map["start"]
        # Add a custom item
        room["items"].append({"name": "rock", "description": "A rock"})

        # Arrival = False
        desc = self.game.get_location_description(arrival=False)
        self.assertIn(room["description"], desc)
        self.assertIn("You see a key, rock.", desc)

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
        """Test examine item with events."""
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
        """Test examining an item in the room that has events."""
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
        """Test the legacy locked door logic (now implemented via events)."""
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
        """Test examine room with events."""
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

if __name__ == "__main__":
    unittest.main()
