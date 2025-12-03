"""The main control loop for the game.

This module contains the Control class, which manages the game's state machine,
event loop, and main game loop.
"""
import pygame as pg
from .states import menu
from .states import game as gameplay
from . import settings
from .sound import sound_manager


class Control:
    """Manages the game's state machine and main loop."""

    def __init__(self):
        """Initializes the Control class.

        This method sets up the Pygame window, clock, and state machine.
        """
        pg.init()
        self.screen = pg.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.done = False
        self.fps = settings.FPS
        self.debug_mode = False
        sound_manager.load_sound("click", "assets/sounds/click.wav")
        sound_manager.load_music("assets/music/menu.ogg")
        sound_manager.play_music()
        self.state_dict = {
            "MENU": menu.Menu(),
            "GAME": gameplay.Game()
        }
        self.state_name = "MENU"
        self.state = self.state_dict[self.state_name]
        self.state.startup({})

    def event_loop(self):
        """Handles all events from the Pygame event queue."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYUP:
                if event.key == pg.K_F3:
                    self.debug_mode = not self.debug_mode
            self.state.get_event(event)

    def main_game_loop(self):
        """The main game loop.

        This loop runs until the `done` attribute is set to True. It handles
        updating the game state, drawing to the screen, and managing the
        frame rate.
        """
        while not self.done:
            delta_time = self.clock.tick(self.fps) / 1000.0
            self.event_loop()
            self.update(delta_time)
            self.draw()
            pg.display.update()

    def update(self, dt):
        """Updates the current game state.

        Args:
            dt (float): The time in seconds since the last frame.
        """
        if self.state.quit:
            self.done = True
            return
        self.state.update(dt)
        if self.state.done:
            self.flip_state()

    def draw(self):
        """Draws the current game state to the screen."""
        self.state.draw(self.screen, self.debug_mode)

    def flip_state(self):
        """Switches to the next game state."""
        previous, self.state_name = self.state_name, self.state.next_state
        persist = self.state.persist
        if self.state_name == "GAME":
            persist["clock"] = self.clock
        self.state = self.state_dict[self.state_name]
        self.state.startup(persist)
