# src/sound.py
import pygame as pg

class SoundManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            pg.mixer.init()
            cls._instance.sounds = {}
            cls._instance.music_path = None
        return cls._instance

    def load_sound(self, name, path):
        try:
            self.sounds[name] = pg.mixer.Sound(path)
        except pg.error:
            print(f"Warning: Could not load sound file '{path}'")

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def load_music(self, path):
        self.music_path = path

    def play_music(self, loops=-1):
        if self.music_path:
            try:
                pg.mixer.music.load(self.music_path)
                pg.mixer.music.play(loops)
            except pg.error:
                print(f"Warning: Could not load music file '{self.music_path}'")

    def stop_music(self):
        pg.mixer.music.stop()

sound_manager = SoundManager()
