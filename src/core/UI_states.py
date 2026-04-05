import pygame as pg

import core.configuration as c
import engine
from logger import logger
from typing import Callable

class Button():
    def __init__(self, x, y, w, h, bg_color, fg_color, text, text_color, font_size=36, border_radius = 5, frame_size = 5, callback: Callable | None = None) -> None:
        self.bg_rect = pg.Rect((0, 0), (w, h))
        self.rect = pg.Rect((0, 0), (w - frame_size, h - frame_size))
        self.rect.center = (x, y)
        self.bg_rect.center = (x, y)
        
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.text, self.text_color, self.font_size = text, text_color, font_size
        self.border_radius = border_radius
        
        self.callback: Callable | None = callback
    
    def draw(self, surf: pg.Surface) -> None:
        pg.draw.rect(surf, self.bg_color, self.bg_rect, border_radius=self.border_radius)
        pg.draw.rect(surf, self.fg_color, self.rect, border_radius=self.border_radius)
        
        font = engine.font.get_font("inter")
        if not font: return
        font_surf, font_rect = font.render(self.text, self.text_color, size = self.font_size)
        font_rect.center = self.rect.center
        surf.blit(font_surf, font_rect)

class MainMenuState(engine.GameState):
    def __init__(self):
        super().__init__()
        
        self.buttons = [
            Button(c.DISPLAY_WIDTH_CENTER, 100, 
                   200, 100, (100, 100, 100), (120, 120, 120), "Play", (255, 255, 255), callback=lambda: engine.state_manager.change_state("playing")),
        ]
    
    def draw(self, surf: pg.Surface):
        surf.fill((0, 255, 255))
        for button in self.buttons:
            button.draw(surf)
    
    def handle_event(self, event: pg.Event):
        mods = engine.input_manager.key_mods
        if event.type == pg.QUIT:
            engine.event_bus.emit("quit")
            
        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for button in self.buttons:
                if button.rect.collidepoint(mouse_pos) and button.callback:
                    button.callback()

class SettingsMenuState(engine.GameState):
    def __init__(self):
        super().__init__()

class PauseState(engine.GameState):
    def __init__(self) -> None:
        super().__init__()
        
        self.buttons = [
            Button(c.DISPLAY_WIDTH_CENTER, 100, 
                   200, 100, (100, 100, 100), (120, 120, 120), "Resume", (255, 255, 255), callback=lambda: engine.state_manager.change_state("playing")),
            Button(c.DISPLAY_WIDTH_CENTER, 250, 
                   200, 100, (100, 100, 100), (120, 120, 120), "Main Menu", (255, 255, 255), callback=lambda: engine.state_manager.change_state("main_menu"))
        ]
    
    def enter(self):
        pass
    
    def draw(self, surf: pg.Surface):
        surf.fill((0, 255, 0))
        for button in self.buttons:
            button.draw(surf)
        
    def handle_event(self, event: pg.Event):
        mods = engine.input_manager.key_mods
        if event.type == pg.QUIT:
            engine.event_bus.emit("quit")
        
        if event.type == pg.KEYUP:
            if event.key == c.CONTROLS.PAUSE_GAME[0]:
                engine.state_manager.change_state("playing")
            
        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for button in self.buttons:
                if button.rect.collidepoint(mouse_pos) and button.callback:
                    button.callback()