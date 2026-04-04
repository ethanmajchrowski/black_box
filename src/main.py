import pygame as pg

import core.configuration as c
from game import Game
from logger import logger

def main():
    pg.init()
    pg.mixer.init(buffer=2048, channels=8)
    pg.font.init()
    display_surface = pg.display.set_mode(c.DISPLAY_SIZE)
    pg.display.set_caption(c.WINDOW_TITLE)
    logger.info("Pygame initialized")

    game = Game(display_surface)
    logger.info("Game object created")
    logger.info("Starting game")
    game.run()
    
if __name__ == "__main__":
    main()
    