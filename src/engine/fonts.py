import pygame as pg
import pygame.freetype as ftfont
from logger import logger

class _FontManager:
    def __init__(self) -> None:
        self.fonts = {}
    
    def load_font(self, fp: str, name: str):
        self.fonts[name] = ftfont.Font(fp, 32)
    
    def get_font(self, font: str) -> ftfont.Font:
        if not self.fonts.get(font): logger.warning(f"Font not found: {font}")
        return self.fonts.get(font, ftfont.SysFont("Arial", 32))
    
    def draw_wrapped_text(self, surface: pg.Surface, text: str, font_name: str, color, rect: pg.Rect, size: int):
        font = self.get_font(font_name)
        if not font:
            logger.fatal(f"Font not found: {font_name}. Failing to render multi line text.")
            return 0
        
        # Split text into words
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            # Check width of current line + new word
            test_line = ' '.join(current_line + [word])
            text_rect = font.get_rect(test_line, size=size)
            
            if text_rect.width <= rect.width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        lines.append(' '.join(current_line)) # Add the last line

        # Render each line
        y_offset = rect.top
        for line in lines:
            if line: # Avoid rendering empty lines
                font.render_to(surface, (rect.left, y_offset), line, color, size=size)
                y_offset += font.get_sized_height(size) # Move down for the next line
        return y_offset