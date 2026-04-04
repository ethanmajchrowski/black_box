import pygame as pg

class _SoundManager:
    def __init__(self) -> None:
        self.sounds: dict[str, pg.mixer.Sound] = {}
    
    def register_sound(self, sound_fp: str, sound_name: str):
        self.sounds[sound_name] = pg.mixer.Sound(sound_fp)