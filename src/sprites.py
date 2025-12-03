# sprites.py
# This file contains the sprite classes for the game.

import pygame as pg
from .settings import *

class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((50, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

    def update(self, dt):
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
        # In a real game, you would play a sound here
        pass

    def jump(self):
        self.play_jump_sound()

class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        pass
