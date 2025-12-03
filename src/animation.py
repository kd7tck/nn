# src/animation.py
import pygame as pg

class Spritesheet:
    def __init__(self, filename):
        try:
            self.spritesheet = pg.image.load(filename).convert()
        except pg.error:
            print(f"Warning: Could not load spritesheet file '{filename}'")
            self.spritesheet = None

    def get_image(self, x, y, width, height):
        if not self.spritesheet:
            return pg.Surface((width, height))
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image.set_colorkey((0, 0, 0))
        return image

class Animation:
    def __init__(self, spritesheet, frame_data):
        self.spritesheet = spritesheet
        self.frame_data = frame_data
        self.current_frame = 0
        self.last_update = pg.time.get_ticks()

    def get_current_frame(self):
        now = pg.time.get_ticks()
        frame_info = self.frame_data[self.current_frame]
        if now - self.last_update > frame_info['duration']:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frame_data)
        frame_rect = frame_info['rect']
        return self.spritesheet.get_image(frame_rect[0], frame_rect[1], frame_rect[2], frame_rect[3])
