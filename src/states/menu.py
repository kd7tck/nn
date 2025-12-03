"""The main menu state of the game."""

import pygame as pg
from .base import BaseState
from .. import ui


class Menu(BaseState):
    """The main menu state."""

    def __init__(self):
        """Initializes the Menu state."""
        super(Menu, self).__init__()
        self.font = pg.font.Font(None, 48)
        self.title = self.font.render("Main Menu", True, pg.Color("white"))
        self.title_rect = self.title.get_rect(
            center=(self.screen_rect.centerx, self.screen_rect.centery - 100)
        )
        self.buttons = pg.sprite.Group()
        self.start_button = ui.Button(
            self.screen_rect.centerx,
            self.screen_rect.centery,
            200,
            50,
            "Start",
            self.start_game,
        )
        self.quit_button = ui.Button(
            self.screen_rect.centerx,
            self.screen_rect.centery + 75,
            200,
            50,
            "Quit",
            self.quit_game,
        )
        self.buttons.add(self.start_button, self.quit_button)

    def start_game(self):
        """Starts the game by transitioning to the GAME state."""
        self.done = True
        self.next_state = "GAME"

    def quit_game(self):
        """Quits the game."""
        self.quit = True

    def get_event(self, event):
        """Handles events for the menu.

        Args:
            event (pygame.event.Event): The event to handle.
        """
        for button in self.buttons:
            button.get_event(event)

    def draw(self, surface, debug_mode=False):
        """Draws the menu to the screen.

        Args:
            surface (pygame.Surface): The surface to draw the menu on.
            debug_mode (bool): Whether to draw debug information.
        """
        surface.fill(pg.Color("black"))
        surface.blit(self.title, self.title_rect)
        for button in self.buttons:
            button.draw(surface)
