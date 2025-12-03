# src/ui.py
import pygame as pg
from . import settings
from .sound import sound_manager

class Button(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, text, callback):
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
        if self.hovered:
            self.image.fill(settings.GREEN)
        else:
            self.image.fill(settings.BLUE)
        surface.blit(self.image, self.rect)
        surface.blit(self.text, self.text_rect)

    def get_event(self, event):
        if event.type == pg.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                sound_manager.play_sound("click")
                self.callback()
