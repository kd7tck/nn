"""Defines the sprite classes for the game."""

import pygame as pg
from .settings import *
from .animation import Spritesheet, Animation


class Player(pg.sprite.Sprite):
    """The player character sprite.

    This class handles the player's movement, animation, and actions.
    """

    def __init__(self):
        """Initializes the Player."""
        super().__init__()
        self.spritesheet = Spritesheet("assets/sprites/player.png")
        self.animation = Animation(
            self.spritesheet,
            [
                {'rect': (0, 0, 32, 32), 'duration': 200},
                {'rect': (32, 0, 32, 32), 'duration': 200},
            ],
        )
        self.image = self.animation.get_current_frame()
        if self.spritesheet.spritesheet is None:
            self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

    def update(self, dt):
        """Updates the player's state.

        This method is called once per frame and handles the player's movement
        and animation.

        Args:
            dt (float): The time in seconds since the last frame.
        """
        self.image = self.animation.get_current_frame()
        if self.spritesheet.spritesheet is None:
            self.image.fill(GREEN)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.rect.x -= PLAYER_SPEED * dt
        if keys[pg.K_RIGHT]:
            self.rect.x += PLAYER_SPEED * dt
        if keys[pg.K_UP]:
            self.rect.y -= PLAYER_SPEED * dt
        if keys[pg.K_DOWN]:
            self.rect.y += PLAYER_SPEED * dt

    def play_jump_sound(self):
        """Plays a jump sound.

        This is a placeholder for playing a jump sound effect.
        """
        # In a real game, you would play a sound here
        pass

    def jump(self):
        """Makes the player jump.

        This method calls the `play_jump_sound` method.
        """
        self.play_jump_sound()
