"""Defines the base class for all game states."""

import pygame as pg


class BaseState:
    """The base class for all game states.

    This class provides the basic structure for a game state, including methods
    for handling events, updating the state, and drawing to the screen.
    """

    def __init__(self):
        """Initializes the BaseState."""
        self.done = False
        self.quit = False
        self.next_state = None
        self.screen_rect = pg.display.get_surface().get_rect()
        self.persist = {}
        self.font = pg.font.Font(None, 24)

    def startup(self, persistent):
        """Called when the state is first started.

        Args:
            persistent (dict): A dictionary of data that persists between
                states.
        """
        self.persist = persistent

    def get_event(self, event):
        """Handles events for the state.

        Args:
            event (pygame.event.Event): The event to handle.
        """
        pass

    def update(self, dt):
        """Updates the state.

        Args:
            dt (float): The time in seconds since the last frame.
        """
        pass

    def draw(self, surface, debug_mode=False):
        """Draws the state to the screen.

        Args:
            surface (pygame.Surface): The surface to draw the state on.
            debug_mode (bool): Whether or not to draw debug information.
        """
        pass
