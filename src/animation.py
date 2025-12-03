"""Handles sprite animations.

This module provides classes for loading spritesheets and managing frame-based
animations.
"""
import pygame as pg


class Spritesheet:
    """A class for loading and parsing spritesheets."""

    def __init__(self, filename):
        """Initializes the Spritesheet.

        Args:
            filename (str): The path to the spritesheet image file.
        """
        try:
            self.spritesheet = pg.image.load(filename).convert()
        except pg.error:
            print(f"Warning: Could not load spritesheet file '{filename}'")
            self.spritesheet = None

    def get_image(self, x, y, width, height):
        """Extracts an image from the spritesheet.

        Args:
            x (int): The x-coordinate of the top-left corner of the image.
            y (int): The y-coordinate of the top-left corner of the image.
            width (int): The width of the image.
            height (int): The height of the image.

        Returns:
            pygame.Surface: The extracted image. Returns a blank surface if the
                spritesheet failed to load.
        """
        if not self.spritesheet:
            return pg.Surface((width, height))
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image.set_colorkey((0, 0, 0))
        return image


class Animation:
    """Manages an animation sequence from a spritesheet."""

    def __init__(self, spritesheet, frame_data):
        """Initializes the Animation.

        Args:
            spritesheet (Spritesheet): The spritesheet to use for the animation.
            frame_data (list): A list of dictionaries, where each dictionary
                describes a frame. Each dictionary should have the keys 'rect'
                (a tuple of x, y, width, height) and 'duration' (in
                milliseconds).
        """
        self.spritesheet = spritesheet
        self.frame_data = frame_data
        self.current_frame = 0
        self.last_update = pg.time.get_ticks()

    def get_current_frame(self):
        """Gets the current frame of the animation.

        This method checks if it's time to advance to the next frame and
        returns the current frame's image.

        Returns:
            pygame.Surface: The image of the current frame.
        """
        now = pg.time.get_ticks()
        frame_info = self.frame_data[self.current_frame]
        if now - self.last_update > frame_info['duration']:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frame_data)
        frame_rect = frame_info['rect']
        return self.spritesheet.get_image(
            frame_rect[0], frame_rect[1], frame_rect[2], frame_rect[3]
        )
