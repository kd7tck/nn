# src/control.py
import pygame as pg
from .states import menu
from .states import game as gameplay
from . import settings

class Control:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.done = False
        self.fps = settings.FPS
        self.state_dict = {
            "MENU": menu.Menu(),
            "GAME": gameplay.Game()
        }
        self.state_name = "MENU"
        self.state = self.state_dict[self.state_name]
        self.state.startup({})

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            self.state.get_event(event)

    def main_game_loop(self):
        while not self.done:
            delta_time = self.clock.tick(self.fps) / 1000.0
            self.event_loop()
            self.update(delta_time)
            self.draw()
            pg.display.update()

    def update(self, dt):
        if self.state.quit:
            self.done = True
            return
        self.state.update(dt)
        if self.state.done:
            self.flip_state()

    def draw(self):
        self.state.draw(self.screen)

    def flip_state(self):
        previous, self.state_name = self.state_name, self.state.next_state
        persist = self.state.persist
        self.state = self.state_dict[self.state_name]
        self.state.startup(persist)
