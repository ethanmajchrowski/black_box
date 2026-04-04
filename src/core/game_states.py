import pygame as pg

import core.configuration as c
import engine
from logger import logger

class PlayingState(engine.GameState):
    def __init__(self) -> None:
        super().__init__()
    
    def enter(self):
        pass
    
    def draw(self, surf: pg.Surface):
        surf.fill((255, 0, 0))
    
    def handle_event(self, event: pg.Event):
        mods = engine.input_manager.key_mods
        if event.type == pg.QUIT:
            engine.event_bus.emit("quit")
        
        if event.type == pg.KEYUP:
            if event.key == c.CONTROLS.PAUSE_GAME[0]:
                engine.state_manager.change_state("pause")