# src/states/game.py
import pygame as pg
import pytmx
from .. import settings
from ..sprites import Player
from .base import BaseState
from ..camera import Camera

class Game(BaseState):
    def __init__(self):
        super(Game, self).__init__()
        self.next_state = "MENU"
        self.all_sprites = pg.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.tmx_data = pytmx.util_pygame.load_pygame("assets/maps/level1.tmx")
        self.level_width = self.tmx_data.width * self.tmx_data.tilewidth
        self.level_height = self.tmx_data.height * self.tmx_data.tileheight
        self.camera = Camera(self.level_width, self.level_height)
        self.clock = None

    def startup(self, persistent):
        super().startup(persistent)
        self.clock = self.persist.get("clock")

    def get_event(self, event):
        if event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.done = True
            elif event.key == pg.K_SPACE:
                self.player.jump()

    def update(self, dt):
        self.all_sprites.update(dt)
        self.camera.update(self.player)

    def draw(self, surface, debug_mode=False):
        surface.fill(settings.BLACK)
        self.draw_tiles(surface)
        for sprite in self.all_sprites:
            surface.blit(sprite.image, self.camera.apply(sprite))
        if debug_mode and self.clock:
            self.draw_debug_info(surface)

    def draw_debug_info(self, surface):
        font = pg.font.Font(None, 24)
        fps_text = font.render(f"FPS: {self.clock.get_fps():.2f}", True, pg.Color("white"))
        player_pos_text = font.render(f"Player Pos: ({self.player.rect.x}, {self.player.rect.y})", True, pg.Color("white"))
        surface.blit(fps_text, (10, 10))
        surface.blit(player_pos_text, (10, 30))

    def draw_tiles(self, surface):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        surface.blit(tile, self.camera.apply_rect(pg.Rect(x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight, self.tmx_data.tilewidth, self.tmx_data.tileheight)))
