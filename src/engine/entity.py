from logger import logger
import pygame as pg
from pygame.math import Vector2


class Entity:
    def __init__(self, x: int, y: int, collision_radius: int) -> None:
        self.pos: Vector2 = Vector2(x, y)
        self.radius = collision_radius
        self.desired_velocity = Vector2()
    
    @property
    def collision_rect(self):
        return pg.Rect(
            self.pos.x - self.radius,
            self.pos.y - self.radius,
            self.radius * 2,
            self.radius * 2
    )
    
    def update(self, dt: float):
        self.collision_rect.center = self.pos