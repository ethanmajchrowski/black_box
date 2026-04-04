import pygame as pg

import core.configuration as c
import engine
from logger import logger
from math import sin
from typing import Literal
from random import uniform

class Message:
    def __init__(self, str: str, source: Literal["AI", "Player", "Hint"]) -> None:
        self.str = str
        self.source: Literal["AI", "Player", "Hint"] = source
        self.start_time = 0.05 * len(str)
        self.current_time = self.start_time
        self.last_visible = 0

class PlayingState(engine.GameState):
    def __init__(self) -> None:
        super().__init__()
        self.ai_token_queue = None
        self.current_ai_line = ""
        
        self.conversation: list[Message] = []
        self.add_message("Welcome to the terminal!", "AI")
        self.add_message("This is the same time as the first message. :(", "Hint")
        self.add_message("This is the player talking!", "Player")
        self.user_input = ""
        
        engine.event_bus.connect("ai_start", lambda queue: setattr(self, "ai_token_queue", queue))
    
    def add_message(self, str: str, source: Literal["AI", "Player", "Hint"]):
        if not str:
            logger.warning("Empty string tried to add to message log")
            return
        self.conversation.append(Message(str, source))
    
    def enter(self):
        pass
    
    def draw(self, surf: pg.Surface):
        surf.fill((0, 0, 0))
        
        bottom = 0
        text_rect = pg.Rect(10, 10, c.DISPLAY_WIDTH - 20, c.DISPLAY_HEIGHT - 60)
        text_rect.centerx = c.DISPLAY_WIDTH_CENTER
        text_rect.top = 10
        for line in self.conversation:
            if line.source == "Player":
                visible_chars = len(line.str)
                color = (100, 100, 255)
            else:
                if line.source == "Hint":
                    color = (240, 208, 103)
                else:
                    color = (255, 255, 255)
                # cap chars in line based on line time value
                progress = 1 - line.current_time / line.start_time
                visible_chars = int(len(line.str) * progress)
                if visible_chars > line.last_visible:
                    line.last_visible = visible_chars
                    engine.sound.sounds["typing"].set_volume(uniform(0.1, 0.15))
                    engine.sound.sounds["typing"].play()

            bottom = engine.font.draw_wrapped_text(surf, f"> {line.str[:visible_chars]}", "inter", color, text_rect, 18)
            text_rect.top = bottom
        
        # draw type box
        font = engine.font.get_font("inter")
        _, align_rect = font.render("|", (0, 0, 0), (0, 0, 0), size=18)
        align_rect.bottomleft = (10, c.DISPLAY_HEIGHT - 10)
        type_surf, _ = font.render(self.user_input, (255, 255, 255), (0, 0, 0), size=18)
        
        type_surf_rect = pg.Rect(0, 0, c.DISPLAY_WIDTH - 20, 18)
        type_surf_rect.topleft = (10, c.DISPLAY_HEIGHT - 40)
        surf.blit(type_surf, align_rect)
        
        # cursor icon
        color = (255, 255, 255)
        if sin(engine.time_manager.global_time * 4) < -0.5: color = (0, 0, 0)
        cursor_rect = pg.Rect(type_surf.width + 15, align_rect.top, 2, align_rect.height)
        cursor_rect.centery = align_rect.centery
        pg.draw.rect(surf, color, cursor_rect)
    
    def update(self, dt: float):
        for line in self.conversation:
            if line.source == "Player":
                continue
            if line.current_time > 0: 
                line.current_time -= dt
        
        # update AI content
        if not self.ai_token_queue: return
        while not self.ai_token_queue.empty():
            token = self.ai_token_queue.get()
            if token is None:
                print("ai DONE")
                self.add_message(self.current_ai_line, source="AI")
                engine.event_bus.emit("ai_done", response=self.current_ai_line)
                self.current_ai_line = ""
            else:
                self.current_ai_line += token
        
    def handle_event(self, event: pg.Event):
        mods = engine.input_manager.key_mods
        if event.type == pg.QUIT:
            engine.event_bus.emit("quit")
        
        if event.type == pg.KEYUP:
            if event.key == c.CONTROLS.PAUSE_GAME[0]:
                engine.state_manager.change_state("pause")
            
        if event.type == pg.KEYDOWN:
            char = event.unicode
            if event.key == c.CONTROLS.DEL_WORD_LEFT[0] and event.mod & c.CONTROLS.DEL_WORD_LEFT[1]:
                if not self.user_input: return
                
                i = len(self.user_input)-1
                if self.user_input[i] in [" ", "_", ",", "."]:
                    self.user_input= self.user_input[:-1]
                    if not self.user_input: return
                    i-= 1
                while self.user_input[i] not in [" ", "_", ",", "."]:
                    self.user_input= self.user_input[:-1]
                    if not self.user_input: break
                    i -= 1
                return
            if event.key == c.CONTROLS.DELETE_CHAR_LEFT[0]:
                self.user_input = self.user_input[:-1]
                return
            
            
            elif char.isalnum() or char == ' ':
                self.user_input += char
            elif not event.unicode.isspace() and not event.unicode.isalnum() and event.unicode != "":
                self.user_input += char
            
            if event.key == c.CONTROLS.SEND_MESSAGE[0] and self.user_input:
                engine.event_bus.emit("player_message", user_prompt=self.user_input)
                self.add_message(self.user_input, "Player")
                self.user_input = ""