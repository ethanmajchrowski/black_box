from typing import TYPE_CHECKING

import pygame as pg
from logger import logger

if TYPE_CHECKING:
    from event_bus import _EventBus

class GameState:
	def __init__(self):
		self.done = False
		self.prev_state: GameState
		self.name: str
	
	def enter(self):
		pass

	def exit(self):
		pass
	
	def update(self, dt: float):
		pass
		
	def handle_event(self, event: pg.Event):
		pass
		
	def draw(self, surf: pg.Surface):
		pass

class _StateManager:
	def __init__(self, engine_event_bus: "_EventBus") -> None:
		self.current_state: GameState = GameState()
		self.event_bus = engine_event_bus
    
	def switch_states(self, new_state: "GameState") -> None:
		if self.current_state:
			new_state.prev_state = self.current_state
			self.current_state.exit()

		self.current_state = new_state
		self.current_state.enter()
		self.event_bus.emit("switch_states", self.current_state)