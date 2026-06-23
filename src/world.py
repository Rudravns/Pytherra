import pygame as pg
import os, sys
from perlin_noise import PerlinNoise
import utils


class World():
    def __init__(self, pos, size):
        self.pos = pg.Vector2(pos)
        self.rect =[pg.Rect(self.pos[0], self.pos[1], size[0], size[1]), pg.Rect(200,500,200,50), pg.Rect(400, self.pos[1] - 20, 200, 200), pg.Rect(600, self.pos[1] - 40, 200, 200), pg.Rect(800, self.pos[1] - 60, 200, 200)]
        self.base_rect = self.rect.copy() # For resizing
        self.screen = pg.display.get_surface()
        
    def resize(self):
        for i, rect in enumerate(self.rect):
            rect.x = self.base_rect[i].x * utils.SCALE["width"]
            rect.y = self.base_rect[i].y * utils.SCALE["height"]
            rect.width = self.base_rect[i].width * utils.SCALE["width"]
            rect.height = self.base_rect[i].height * utils.SCALE["height"]

        return self.rect

    def draw(self):
        for rect in self.rect:
            pg.draw.rect(self.screen, "green", rect) # pyright: ignore[reportArgumentType]