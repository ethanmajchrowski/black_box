import pygame as pg

import core.configuration as c
import engine
from core.game_states import PlayingState
from core.UI_states import SettingsMenuState, MainMenuState, PauseState
from core.llm import ai_manager
from logger import logger

class Game:
    def __init__(self, display_surface: pg.Surface) -> None:
        engine.state_manager.register_state(PlayingState(), "playing", True)
        engine.state_manager.register_state(SettingsMenuState(), "settings")
        engine.state_manager.register_state(MainMenuState(), "main_menu")
        engine.state_manager.register_state(PauseState(), "pause")
        engine.state_manager.change_state("playing")
        
        engine.setup(c)
        # variables
        self.running = True
        
        # pygame stuff
        self.display_surface = display_surface
        self.clock = pg.time.Clock()
        
        # hookup input events
        engine.event_bus.connect("quit", lambda: setattr(self, "running", False))
        
        # load things
        engine.sound.register_sound("assets/sound/type.wav", "typing")
        engine.font.load_font("assets/font/inter24.ttf", "inter")
        engine.font.load_font("assets/font/space_mono.ttf", "mono")
        
        # fps time for debug
        self.fps_update_time = 0.0
        self.game_time = 0.0
        self.fps_history = []

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000 # clock.tick returns milliseconds as integer so we convert to seconds since last frame by / 1000
            self.game_time += dt
            self.display_surface.fill((0, 0, 0))

            for event in pg.event.get():
                engine.state_manager.current_state.handle_event(event)
            
            # Backend systems updates
            engine.state_manager.current_state.draw(self.display_surface)
            engine.update(dt)
                        
            pg.display.update()

            if c.DEBUG_MODE:
                # FPS avg & window display
                self.fps_history.append(self.clock.get_fps())
                if len(self.fps_history) > 1000: # 1000 frames stored
                    self.fps_history.pop(0)

                avg_fps = sum(self.fps_history) / len(self.fps_history)

                if self.fps_update_time < 0.25:
                    self.fps_update_time += dt
                else:
                    pg.display.set_caption(
                        f"{c.WINDOW_TITLE} | {engine.state_manager.current_state} | FPS: {avg_fps:.1f}"
                    )
                    self.fps_update_time = 0.0

        pg.quit()
        exit()