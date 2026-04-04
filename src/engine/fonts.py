import pygame as pg
import pygame.freetype as ftfont

class _FontManager:
    def __init__(self) -> None:
        self.fonts = {}
    
    def load_font(self, fp: str, name: str):
        self.fonts[name] = ftfont.Font(fp, 32)
    
    def get_font(self, font: str) -> None | ftfont.Font:
        return self.fonts.get(font)