import pygame
from typing import Tuple
from render.colors import Color


class Track:
    
    BRUSH_LIMIT_SIZE = 25
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.surface.fill(Color.WHITE)
        self.brush_size = 50
        self.last_position = None

    def draw(self, position: Tuple[int, int], color: Tuple[int, int, int]):
        if self.last_position:
            self.draw_interpolated(self.last_position, position, color)
        else:
            pygame.draw.circle(self.surface, color, position, self.brush_size)
        self.last_position = position
        
    def adjust_brush_size(self, amount: int):
        self.brush_size = max(Track.BRUSH_LIMIT_SIZE, self.brush_size + amount)

    def draw_interpolated(self, start: Tuple[int, int], end: Tuple[int, int], color: Tuple[int, int, int]):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = max(abs(dx), abs(dy))
        
        for i in range(distance):
            x = int(start[0] + float(i) / distance * dx)
            y = int(start[1] + float(i) / distance * dy)
            pygame.draw.circle(self.surface, color, (x, y), self.brush_size)

    def reset_last_position(self):
        self.last_position = None

    def get_surface(self) -> pygame.Surface:
        return self.surface