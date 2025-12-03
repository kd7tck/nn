"""Manages the game's sound and music.

This module provides a singleton SoundManager class for loading and playing
sounds and music.
"""
import pygame as pg


class SoundManager:
    """A singleton class for managing sound and music."""

    _instance = None

    def __new__(cls):
        """Creates a new SoundManager instance if one doesn't already exist."""
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            try:
                pg.mixer.init()
                cls._instance.sounds = {}
                cls._instance.music_path = None
                cls._instance.sound_enabled = True
            except pg.error:
                print("Warning: Could not initialize sound mixer.")
                cls._instance.sound_enabled = False
        return cls._instance

    def load_sound(self, name, path):
        """Loads a sound from a file.

        Args:
            name (str): The name to assign to the sound.
            path (str): The path to the sound file.
        """
        if not self.sound_enabled:
            return
        try:
            self.sounds[name] = pg.mixer.Sound(path)
        except pg.error:
            print(f"Warning: Could not load sound file '{path}'")

    def play_sound(self, name):
        """Plays a loaded sound.

        Args:
            name (str): The name of the sound to play.
        """
        if self.sound_enabled and name in self.sounds:
            self.sounds[name].play()

    def load_music(self, path):
        """Loads music from a file.

        Args:
            path (str): The path to the music file.
        """
        if not self.sound_enabled:
            return
        self.music_path = path

    def play_music(self, loops=-1):
        """Plays the loaded music.

        Args:
            loops (int): The number of times to repeat the music. -1 means
                the music will loop indefinitely.
        """
        if self.sound_enabled and self.music_path:
            try:
                pg.mixer.music.load(self.music_path)
                pg.mixer.music.play(loops)
            except pg.error:
                print(f"Warning: Could not load music file '{self.music_path}'")

    def stop_music(self):
        """Stops the music that is currently playing."""
        if self.sound_enabled:
            pg.mixer.music.stop()


sound_manager = SoundManager()
