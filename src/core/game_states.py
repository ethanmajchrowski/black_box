import pygame as pg

import core.configuration as c
import engine
from logger import logger
from math import sin, floor
from typing import Literal, Callable
from random import uniform

class Message:
    def __init__(self, message: str, source: Literal["AI", "Player", "Hint", "Misc", "Fake_AI"], already_revealed: int = 0, start_pause_time: float = 0.0, callback: Callable | None = None) -> None:
        self.str = message
        self.source: Literal["AI", "Player", "Hint", "Misc", "Fake_AI"] = source
        self.total_time = 0.03 * len(message)
        self.start_pause_time = start_pause_time
        
        self.current_time = self.total_time * (1 - (already_revealed / len(message)))
        self.callback = callback
        
        self.last_visible = already_revealed

class PlayingState(engine.GameState):
    def __init__(self) -> None:
        super().__init__()
        self.allow_player_typing: bool = False
        self.first_enter: bool = True
        
        self.ai_token_queue = None
        self.current_ai_line = ""
        self.ai_displayed_line = ""  # what has actually been drawn so far
        self.ai_char_timer = 0.03     # accumulates time for letter reveal
        self.ai_char_delay = 0.03    # time between letters revealed
        
        self.scroll_offset = 0
        self.max_scroll = 0
        
        self.conversation: list[Message] = []
        self.current_message = 0
        self.user_input = ""
        self.endgame_triggered = False
        # self.add_message("\nhi"*50, "Hint")
        
        engine.event_bus.connect("ai_start", lambda queue: setattr(self, "ai_token_queue", queue))
        engine.event_bus.connect("endgame", self.endgame)
        # engine.event_bus.connect("unlock_science_logs", 
        #                          lambda: self.add_message("Our team just noticed that a new block of memory opened up in the connection. Try asking about any 'science logs'?", "Hint", 
        #                                                   start_pause_time=0.5, callback=lambda:setattr(self, "allow_player_typing", True)))
    
    def endgame(self):
        self.endgame_triggered = True
        self.allow_player_typing = False
        def final_messages():
            self.add_message("Jesus.", "Hint", start_pause_time=2.0)
            self.add_message("Good..work... We'll get this sent off to the labs for thorough analysis.", "Hint", start_pause_time=2.0)
            self.add_message("You should probably head home for the day.", "Hint", start_pause_time=3.0)
            
            self.add_message("END BLACK BOX ANALYSIS", "Misc", start_pause_time=4.0)
            self.add_message("AI CONNECTION TERMINATED", "Misc", start_pause_time=1.5)
            self.add_message("FILE CLOSED: Initial investigation of the ISS Helios Venture", "Misc", start_pause_time=1.5)
            
        engine.time_manager.create_timer(2.0, final_messages)
    
    def add_message(self, str: str, source: Literal["AI", "Player", "Hint", "Misc", "Fake_AI"], already_revealed: int = 0, start_pause_time: float = 0.0, callback: Callable | None = None):
        if not str:
            logger.warning("Empty string tried to add to message log")
            return
        self.conversation.append(Message(str, source, already_revealed, start_pause_time, callback))
    
    def enter(self):
        if c.DEBUG_SKIP_INTRO and self.first_enter: self.allow_player_typing = True
        if self.first_enter and not c.DEBUG_SKIP_INTRO:
            # Introduction 'animation'
            self.add_message("BEGIN BLACK BOX ANALYSIS", "Misc", start_pause_time=1.5)
            self.add_message("AI CONNECTION VERIFIED", "Misc", start_pause_time=1.5)
            self.add_message("SUBJECT OF INTEREST: ISS Helios Venture", "Misc", start_pause_time=1.5)
            self.add_message("[ESC] TO PAUSE INVESTIGATION", "Misc", start_pause_time=1.5)
            self.add_message("Okay, we've got the AI all connected. You should be able to start speaking with it once I'm done here.", "Hint", start_pause_time=1.0)
            self.add_message("AI, what are we here to figure out today?", "Hint", start_pause_time=0.5)
            self.add_message("We are here to determine the root cause of the failure of the ISS Helios Venture mission.", "Fake_AI", start_pause_time=1.5)
            self.add_message("Very good. We should be all right to get started, then.", "Hint", start_pause_time=1.0)
            self.add_message("""Before you begin, we've recieved some diagnostics beforehand that the AI is heavily damaged. It's memory banks are faulty, so it won't remember any past messages you send it. At the same time, it's been placed in a strong failsafe mode. That means it won't reveal much information without direct questioning. Keep that in mind during your investigation.""", "Hint", start_pause_time=0.5)
            self.add_message("Remember: you can type your prompts to the ship AI and press enter to send them in.", "Hint", start_pause_time=2.5)
            self.add_message("Looks like there's some logs that survived. Maybe check those out first? It's all yours.", "Hint", callback=lambda: setattr(self, "allow_player_typing", True), start_pause_time=0.5)
            
            self.first_enter = False

    def create_scanlines(self, width, height, alpha=30):
        # Create a surface with per-pixel alpha
        scanline_surf = pg.Surface((width, height), pg.SRCALPHA)
        for y in range(0, height, 4):  # Draw line every 4 pixels
            # Black line with specific alpha
            pg.draw.line(scanline_surf, (0, 0, 0, alpha), (0, y), (width, y))
    
        return scanline_surf
    
    
    def draw(self, surf: pg.Surface):
        surf.fill((0, 0, 0))
        
        bottom = 0
        text_rect = pg.Rect(10, 0, c.DISPLAY_WIDTH - 20, c.DISPLAY_HEIGHT - 60)
        text_rect.centerx = c.DISPLAY_WIDTH_CENTER
        text_rect.top = 10 + self.scroll_offset
        for i, line in enumerate(self.conversation):
            if line.source == "Player":
                visible_chars = len(line.str)
                color = (100, 100, 255)
            else: # hint message
                if line.source == "AI" or line.source == "Fake_AI": color = (255, 255, 255)
                elif line.source == "Misc": color = (97, 97, 97)
                else: color = (240, 208, 103)
                # cap chars in line based on line time value
                progress = 1 - line.current_time / line.total_time
                visible_chars = int(len(line.str) * progress)
                
                # sfx
                if visible_chars > line.last_visible:
                    line.last_visible = visible_chars
                    engine.sound.sounds["typing"].set_volume(uniform(0.1, 0.15))
                    engine.sound.sounds["typing"].play()
            if visible_chars:
                bottom = engine.font.draw_wrapped_text(surf, f"> {line.str[:visible_chars]}", "inter", color, text_rect, 32)
                if bottom + 40 > c.DISPLAY_HEIGHT:
                    self.scroll_offset -= 40
            else:
                bottom = engine.font.draw_wrapped_text(surf, f"{line.str[:visible_chars]}", "inter", color, text_rect, 32)
                if bottom + 40 > c.DISPLAY_HEIGHT:
                    self.scroll_offset -= 40
            text_rect.top = bottom
        
        self.max_scroll = bottom - self.scroll_offset
        # AI in progress
        if self.current_ai_line:
            bottom = engine.font.draw_wrapped_text(surf, f"> {self.ai_displayed_line}", "inter", (255, 255, 255), text_rect, 32)           
            if bottom + 40 > c.DISPLAY_HEIGHT:
                self.scroll_offset -= 40
        
        if self.allow_player_typing and not self.endgame_triggered:
            pg.draw.rect(surf, (200, 200, 200), (0, c.DISPLAY_HEIGHT - 45, c.DISPLAY_WIDTH, 45))
            pg.draw.rect(surf, (40, 40, 40), (0, c.DISPLAY_HEIGHT - 40, c.DISPLAY_WIDTH, 40))
        elif not self.endgame_triggered:
            pg.draw.rect(surf, (20, 20, 20), (0, c.DISPLAY_HEIGHT - 40, c.DISPLAY_WIDTH, 40))
            
        # draw type box
        font = engine.font.get_font("inter")
        _, align_rect = font.render("|", (0, 0, 0), (0, 0, 0), size=18)
        align_rect.bottomleft = (10, c.DISPLAY_HEIGHT - 10)
        type_surf, _ = font.render(self.user_input, (255, 255, 255), (40, 40, 40), size=18)
        
        type_surf_rect = pg.Rect(0, 0, c.DISPLAY_WIDTH - 20, 18)
        type_surf_rect.topleft = (10, c.DISPLAY_HEIGHT - 40)
        surf.blit(type_surf, align_rect)
        
        if self.allow_player_typing and not self.endgame_triggered:
            # cursor icon
            color = (255, 255, 255)
            if sin(engine.time_manager.global_time * 4) < -0.5: color = (40, 40, 40)
            cursor_rect = pg.Rect(type_surf.width + 15, align_rect.top, 2, align_rect.height)
            cursor_rect.centery = align_rect.centery
            pg.draw.rect(surf, color, cursor_rect)
        
        scan_offset = engine.time_manager.global_time - floor(engine.time_manager.global_time)
        surf.blit(self.create_scanlines(c.DISPLAY_WIDTH, c.DISPLAY_HEIGHT - 40), (0, int(scan_offset * 10)))
    
    def update(self, dt: float):
        if self.conversation and len(self.conversation) > self.current_message:
            line = self.conversation[self.current_message]
            if line.source == "Player":
                self.current_message += 1
            else:
                if line.start_pause_time >= 0: line.start_pause_time -= dt
                else:
                    line.current_time -= dt
                    if line.current_time < 0:
                        if line.callback: line.callback()
                        self.current_message += 1
                
        if self.current_ai_line:
            self.ai_char_timer -= dt
            if self.ai_char_timer < 0 and len(self.ai_displayed_line) < len(self.current_ai_line):
                next_char = self.current_ai_line[len(self.ai_displayed_line)]
                self.ai_displayed_line += next_char
                self.ai_char_timer = self.ai_char_delay

                # play typing sound for AI characters
                engine.sound.sounds["typing"].set_volume(uniform(0.1, 0.15))
                engine.sound.sounds["typing"].play()
                self.ai_char_timer = self.ai_char_delay
        
        # update AI content
        if not self.ai_token_queue: return
        while not self.ai_token_queue.empty():
            token = self.ai_token_queue.get()
            if token is None:
                # Done with AI
                engine.event_bus.emit("ai_done", response=self.current_ai_line)
                self.allow_player_typing = True
                self.add_message(self.current_ai_line, "AI", len(self.ai_displayed_line))
                self.current_ai_line = ""
                self.ai_displayed_line = ""
            else:
                self.current_ai_line += token
        
    def handle_event(self, event: pg.Event):
        if event.type == pg.WINDOWRESIZED:
            display_surf = pg.display.get_surface()
            if display_surf: 
                c.update_screen_size(display_surf.width, display_surf.height)
        
        mods = engine.input_manager.key_mods
        if event.type == pg.QUIT:
            engine.event_bus.emit("quit")
        
        if event.type == pg.KEYUP:
            if event.key == c.CONTROLS.PAUSE_GAME[0]:
                engine.state_manager.change_state("pause")
            
        if event.type == pg.KEYDOWN and self.allow_player_typing and not self.endgame_triggered:
            if event.key in [pg.K_ESCAPE]: return
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
                self.add_message(self.user_input, "Player")
                self.allow_player_typing = False
                engine.event_bus.emit("player_message", user_prompt=self.user_input)
                self.user_input = ""
        if event.type == pg.MOUSEWHEEL:
            self.scroll_offset += event.y * 5
            self.scroll_offset = min(0, self.scroll_offset)
            # print(self.scroll_offset, -self.max_scroll)
            self.scroll_offset = max(self.scroll_offset, -self.max_scroll)
        