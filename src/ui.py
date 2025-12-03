"""Defines the UI elements for the game."""

import pygame as pg
from . import settings
from .sound import sound_manager


class Button(pg.sprite.Sprite):
    """A clickable button sprite.

    This class creates a button with a text label that can be clicked to
    trigger a callback function.
    """

    def __init__(self, x, y, width, height, text, callback):
        """Initializes the Button.

        Args:
            x (int): The x-coordinate of the center of the button.
            y (int): The y-coordinate of the center of the button.
            width (int): The width of the button in pixels.
            height (int): The height of the button in pixels.
            text (str): The text to display on the button.
            callback (function): The function to call when the button is
                clicked.
        """
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill(settings.BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.font = pg.font.Font(None, 32)
        self.text = self.font.render(text, True, settings.WHITE)
        self.text_rect = self.text.get_rect(center=self.rect.center)
        self.callback = callback
        self.hovered = False

    def draw(self, surface):
        """Draws the button on the screen.

        The button changes color when the mouse hovers over it.

        Args:
            surface (pygame.Surface): The surface to draw the button on.
        """
        if self.hovered:
            self.image.fill(settings.GREEN)
        else:
            self.image.fill(settings.BLUE)
        surface.blit(self.image, self.rect)
        surface.blit(self.text, self.text_rect)

    def get_event(self, event):
        """Handles events for the button.

        This method checks for mouse motion and clicks on the button.

        Args:
            event (pygame.event.Event): The event to handle.
        """
        if event.type == pg.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                sound_manager.play_sound("click")
                self.callback()
