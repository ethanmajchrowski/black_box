import pygame as pg

import core.configuration as c
import engine
from logger import logger

class MainMenuState(engine.GameState):
    def __init__(self):
        super().__init__()

class SettingsMenuState(engine.GameState):
    def __init__(self):
        super().__init__()

class PauseState(engine.GameState):
    def __init__(self):
        super().__init__()