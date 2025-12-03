# src/states/game.py
import pygame as pg
from .. import settings
from ..sprites import Player, Enemy
from .base import BaseState
from ..camera import Camera
import random

class Game(BaseState):
    def __init__(self):
        super(Game, self).__init__()
        self.next_state = "MENU"
        self.all_sprites = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        # Create a dummy level size for the camera
        self.level_width = 1000
        self.level_height = 1000
        self.setup_enemies()
        self.camera = Camera(self.level_width, self.level_height)

    def setup_enemies(self):
        for _ in range(5):
            x = random.randint(0, self.level_width)
            y = random.randint(0, self.level_height)
            enemy = Enemy(x, y)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

    def get_event(self, event):
        if event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.done = True
            elif event.key == pg.K_SPACE:
                self.player.jump()

    def update(self, dt):
        self.all_sprites.update(dt)
        self.camera.update(self.player)
        # Check for collisions
        hits = pg.sprite.spritecollide(self.player, self.enemies, False)
        if hits:
            # For now, just quit the game if there is a collision
            self.quit = True

    def draw(self, surface):
        surface.fill(pg.Color("black"))
        for sprite in self.all_sprites:
            surface.blit(sprite.image, self.camera.apply(sprite))
