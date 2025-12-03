"""A camera for scrolling the map.

This module defines the Camera class, which is used to create a scrolling
view of the game world.
"""
import pygame as pg
from .settings import *


class Camera:
    """A camera that follows a target sprite.

    The camera's position is updated to keep the target sprite centered on the
    screen. The camera also ensures that the view does not go beyond the
    boundaries of the game world.
    """

    def __init__(self, width, height):
        """Initializes the Camera.

        Args:
            width (int): The width of the game world in pixels.
            height (int): The height of the game world in pixels.
        """
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        """Applies the camera's offset to a sprite.

        Args:
            entity (pygame.sprite.Sprite): The sprite to apply the offset to.

        Returns:
            pygame.Rect: The new rect of the sprite, with the offset applied.
        """
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        """Updates the camera's position to follow the target.

        Args:
            target (pygame.sprite.Sprite): The sprite for the camera to
                follow.
        """
        x = -target.rect.x + int(WIDTH / 2)
        y = -target.rect.y + int(HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom
        self.camera = pg.Rect(x, y, self.width, self.height)
