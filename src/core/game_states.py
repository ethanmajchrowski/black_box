import pygame as pg

import core.configuration as c
import engine
from logger import logger

class PlayingState(engine.GameState):
    def __init__(self) -> None:
        super().__init__()
        self.bg_brightness: float = 1.0
    
    def enter(self):
        print('started scene')
        self.bg_brightness = 1.0
        engine.time_manager.create_tween(5.0, self, "bg_brightness", 0.0)
    
    def draw(self, surf: pg.Surface):
        surf.fill(engine.modulate_color((255, 0, 0), self.bg_brightness))
        
    def handle_event(self, event: pg.Event):
        if event.type == pg.QUIT:
            engine.event_bus.emit("quit")
