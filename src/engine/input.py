import pygame as pg

class _InputManager:
    def __init__(self) -> None:
        self.keys: pg.key.ScancodeWrapper
        self.key_mods: int
        self.mouse_pos = pg.Vector2()
    
    def setup(self):
        self.keys = pg.key.get_pressed()
        self.key_mods = pg.key.get_mods()

    def update(self, dt):
        self.keys = pg.key.get_pressed()
        self.key_mods = pg.key.get_mods()
        self.mouse_pos = pg.Vector2(pg.mouse.get_pos())
        
# from engine.event_bus import event_bus

# from typing import TYPE_CHECKING, Any
# if TYPE_CHECKING:
#     from engine.camera import Camera

# from logger import logger
# # TODO: DOES THIS NEED TO EXIST?
# class InputManager:
#     def __init__(self) -> None:
#         self.camera: Camera
#         self.last_mouse_pos: tuple[int, int]
#         # self.last_mouse_pos_snapped: tuple[int, int]
#         self.held_keys: Any = None

#     def handle_input(self):
#         self.held_keys = pg.key.get_pressed()

#         self.last_mouse_pos = pg.mouse.get_pos()
#         wmp = self.camera.screen_to_world(self.last_mouse_pos)

#         # # Snap to top-left of the tile using half-tile granularity
#         # tile_width = c.BASE_MACHINE_WIDTH
#         # tile_height = c.BASE_MACHINE_HEIGHT
#         # half_width = tile_width / 2
#         # half_height = tile_height / 2

#         # tile_x = int(wmp[0] // half_width * half_width)
#         # tile_y = int(wmp[1] // half_height * half_height)
#         # self.last_mouse_pos_snapped = (tile_x, tile_y)  # This is the tile top-left corner (snap point)
        
#         for event in pg.event.get():
#             if event.type == pg.QUIT:
#                 event_bus.emit("quit")
            
#             if event.type == pg.MOUSEMOTION:
#                 ...

#             if event.type == pg.MOUSEBUTTONDOWN:
#                 world_pos = self.camera.screen_to_world(event.pos)
#                 event_bus.emit("mouse_down", world_pos, event.pos, event.button)
            
#             if event.type == pg.MOUSEBUTTONUP:
#                 world_pos = self.camera.screen_to_world(event.pos)
#                 event_bus.emit("mouse_up", world_pos, event.pos, event.button)
            
#             if event.type == pg.KEYDOWN:
#                 event_bus.emit("key_down", event.key)
            
#             if event.type == pg.KEYUP:
#                 event_bus.emit("key_up", event.key)

        
# input_manager = InputManager()