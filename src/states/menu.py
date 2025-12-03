# src/states/menu.py
import pygame as pg
from .base import BaseState
from .. import ui

class Menu(BaseState):
    def __init__(self):
        super(Menu, self).__init__()
        self.font = pg.font.Font(None, 48)
        self.title = self.font.render("Main Menu", True, pg.Color("white"))
        self.title_rect = self.title.get_rect(center=(self.screen_rect.centerx, self.screen_rect.centery - 100))
        self.buttons = pg.sprite.Group()
        self.start_button = ui.Button(
            self.screen_rect.centerx,
            self.screen_rect.centery,
            200, 50, "Start", self.start_game
        )
        self.quit_button = ui.Button(
            self.screen_rect.centerx,
            self.screen_rect.centery + 75,
            200, 50, "Quit", self.quit_game
        )
        self.buttons.add(self.start_button, self.quit_button)

    def start_game(self):
        self.done = True
        self.next_state = "GAME"

    def quit_game(self):
        self.quit = True

    def get_event(self, event):
        for button in self.buttons:
            button.get_event(event)

    def draw(self, surface, debug_mode=False):
        surface.fill(pg.Color("black"))
        surface.blit(self.title, self.title_rect)
        for button in self.buttons:
            button.draw(surface)
