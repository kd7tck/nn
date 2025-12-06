"""
Time system for managing game time and scheduled events.
"""
import copy

class TimeSystem:
    def __init__(self):
        self.total_minutes = 0
        self.timers = []

    def advance_time(self, minutes):
        """Advances the game time by a given number of minutes.

        Args:
            minutes: The number of minutes to advance.

        Returns:
            list: A list of actions triggered by expired timers.
        """
        self.total_minutes += minutes
        triggered_actions = []

        # Check for expired timers
        remaining_timers = []
        # Sort timers by trigger time to ensure order, although not strictly necessary if we process all expired
        self.timers.sort(key=lambda x: x["trigger_time"])

        for timer in self.timers:
            if self.total_minutes >= timer["trigger_time"]:
                triggered_actions.extend(timer["actions"])
            else:
                remaining_timers.append(timer)

        self.timers = remaining_timers
        return triggered_actions

    def schedule_event(self, minutes, actions):
        """Schedules a list of actions to occur after a delay.

        Args:
            minutes: The delay in minutes.
            actions: A list of action dictionaries.
        """
        trigger_time = self.total_minutes + minutes
        self.timers.append({
            "trigger_time": trigger_time,
            "actions": actions
        })

    def get_date_time_string(self):
        """Returns a formatted string of the current game time.

        Returns:
            str: e.g. "Day 1, 12:00"
        """
        days = self.total_minutes // (24 * 60)
        minutes_into_day = self.total_minutes % (24 * 60)
        hours = minutes_into_day // 60
        minutes = minutes_into_day % 60

        # 0 total minutes = Day 1, 00:00
        return f"Day {days + 1}, {hours:02d}:{minutes:02d}"

    def to_dict(self):
        """Serializes the time system state.

        Returns:
            dict: The state dictionary.
        """
        return {
            "total_minutes": self.total_minutes,
            "timers": copy.deepcopy(self.timers)
        }

    def from_dict(self, data):
        """Restores the time system state.

        Args:
            data: The state dictionary.
        """
        self.total_minutes = data.get("total_minutes", 0)
        self.timers = data.get("timers", [])
