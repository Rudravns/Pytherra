import pygame as pg
import os, sys
from perlin_noise import PerlinNoise
import utils
import json


class World():
    def __init__(self):
        # Load world data from JSON file
        with open("src/world_data.json", "r") as f:
            data = json.load(f)
        
        self.rect = self.get_rects(data["world"])
        self.base_rect = self.get_rects(data["world"]) # For resizing
        self.screen = pg.display.get_surface()
        
    def resize(self):
        base_rect = self.base_rect.copy()
        for i, rect in enumerate(self.rect):
            rect.x = base_rect[i].x * utils.SCALE["width"]
            rect.y = base_rect[i].y * utils.SCALE["height"]
            rect.width = base_rect[i].width * utils.SCALE["width"]
            rect.height = base_rect[i].height * utils.SCALE["height"]

        return self.rect

    def draw(self):
        for rect in self.rect:
            pg.draw.rect(self.screen, "green", rect) # pyright: ignore[reportArgumentType]
    
    def get_rects(self, data):
        rects = []
        for item in data:
            rects.append(pg.Rect(item[0], item[1], item[2], item[3]))
        return rects

    def __str__(self):
        return f"{self.base_rect}"

if __name__ == "__main__":
    pg.init()
    w = World()
    print(w)
