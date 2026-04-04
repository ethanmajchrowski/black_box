from typing import TYPE_CHECKING

import pygame as pg
from pygame.math import Vector2

from logger import logger

if TYPE_CHECKING:
    from entity import Entity

import core.configuration as c

class _PhysicsManager:
    def __init__(self) -> None:
        self.horizontal_segments = []
        self.vertical_segments = []
        self.movement_queue: list["Entity"] = []

    def add_collision_mesh(self, collision_mesh: list):
        """Currently only accepts a list of line segments ((x1, y1), (x2, y2))"""
        for (start_x, start_y), (end_x, end_y) in collision_mesh:
            if start_x == end_x: 
                self.vertical_segments.append(((start_x, start_y), (end_x, end_y)))
            else:
                self.horizontal_segments.append(((start_x, start_y), (end_x, end_y)))
    
    def update(self, dt: float):
        while self.movement_queue:
            entity = self.movement_queue.pop()
            try:
                self._resolve_motion(entity, dt)
            except Exception as e:
                logger.fatal(f"PhysicsManager failed to resolve motion for entity {entity} with exception {e}")
                
    def _resolve_motion(self, entity: "Entity", dt: float):
        # determine x- collisions
        ### iterate all vertical collision
        dx = entity.desired_velocity.x * dt
        target_move_rect = entity.collision_rect.move(dx * 10, 0).scale_by(1.0, 0.9)
        if c.PHYSICS_VIS: pg.draw.rect(pg.display.get_surface(), (0, 255, 0), target_move_rect, 1) #type: ignore
        
        for (start_x, start_y), (end_x, end_y) in self.vertical_segments:
            if target_move_rect.clipline(start_x, start_y, end_x, end_y):
                break
        else:
            entity.pos.x += dx
            
        # determine y-collision
        ### iterate all horizontal lines
        dy = entity.desired_velocity.y * dt
        target_move_rect = entity.collision_rect.move(0, dy * 10).scale_by(0.9, 1.0)
        if c.PHYSICS_VIS: pg.draw.rect(pg.display.get_surface(), (0, 0, 255), target_move_rect, 1) #type: ignore
        
        for (start_x, start_y), (end_x, end_y) in self.horizontal_segments:
            if target_move_rect.clipline(start_x, start_y, end_x, end_y): 
                break
        else:
            entity.pos.y += dy
        
        if c.PHYSICS_VIS: pg.draw.rect(pg.display.get_surface(), (255, 0, 0), entity.collision_rect, 1) #type: ignore
    
    def move_entity(self, entity: "Entity"):
        """Move an entity while resolving collisions.

        Args:
            entity (any): Any entity with .pos (Vector2), .desired_velocity (Vector2), and .collision_rect (Rect)
            dt (float): delta time
        """
        self.movement_queue.append(entity)

