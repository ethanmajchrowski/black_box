import pygame as pg

import core.configuration as c
import engine
from logger import logger
from typing import Callable
from core.game_states import PlayingState

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
            Button(c.DISPLAY_WIDTH_CENTER, c.DISPLAY_HEIGHT_CENTER, 
                   200, 100, (20, 20, 20), (0, 0, 0), "PLAY", (255, 255, 255), callback=lambda: engine.state_manager.change_state("playing"), border_radius=0, font_size=24),
            Button(c.DISPLAY_WIDTH_CENTER, c.DISPLAY_HEIGHT_CENTER+200, 
                   100, 50, (20, 20, 20), (80, 0, 0), "RESET", (255, 255, 255), callback=self.reset_playing_state, border_radius=0, font_size=24),
            Button(c.DISPLAY_WIDTH_CENTER, c.DISPLAY_HEIGHT_CENTER+260, 
                   100, 50, (20, 20, 20), (0, 0, 0), "QUIT", (255, 255, 255), callback=lambda:engine.event_bus.emit("quit"), border_radius=0, font_size=24)
        ]
        
        self.pygame_surf = pg.image.load("assets/graphics/pygame_tiny.png").convert_alpha()
    
    def reset_playing_state(self):
        engine.state_manager.states["playing"] = PlayingState()
    
    def draw(self, surf: pg.Surface):
        surf.fill((0, 0, 0))
        font = engine.font.get_font("inter")
        font.render_to(surf, (10, 10, 10, 10), "BLACK BOX", (80, 80, 80), (0, 0, 0), size=64)
        
        surf.blit(self.pygame_surf, (c.DISPLAY_WIDTH - self.pygame_surf.width - 5, c.DISPLAY_HEIGHT - self.pygame_surf.height - 5))
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
            Button(110, 110, 
                   200, 100, (20, 20, 20), (0, 0, 0), "RESUME", (255, 255, 255), callback=lambda: engine.state_manager.change_state("playing"), border_radius=0, font_size=24),
            Button(110, 210, 
                   200, 100, (20, 20, 20), (0, 0, 0), "MAIN MENU", (255, 255, 255), callback=lambda: engine.state_manager.change_state("main_menu"), border_radius=0, font_size=24)
        ]
    
    def enter(self):
        pass
    
    def draw(self, surf: pg.Surface):
        surf.fill((0, 0, 0))
        font = engine.font.get_font('inter')
        font.render_to(surf, (10, 10, 10, 10), "PAUSED", (80, 80, 80), (20, 20, 20), size=48)
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