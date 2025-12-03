# src/states/menu.py
import pygame as pg
from .base import BaseState

class Menu(BaseState):
    def __init__(self):
        super(Menu, self).__init__()
        self.font = pg.font.Font(None, 36)
        self.title = self.font.render("Main Menu", True, pg.Color("white"))
        self.title_rect = self.title.get_rect(center=self.screen_rect.center)
        self.instructions = self.font.render("Press Enter to start", True, pg.Color("white"))
        instructions_center = (self.screen_rect.centerx, self.screen_rect.centery + 50)
        self.instructions_rect = self.instructions.get_rect(center=instructions_center)

    def get_event(self, event):
        if event.type == pg.KEYUP:
            if event.key == pg.K_RETURN:
                self.done = True
                self.next_state = "GAME"

    def draw(self, surface):
        surface.fill(pg.Color("black"))
        surface.blit(self.title, self.title_rect)
        surface.blit(self.instructions, self.instructions_rect)
