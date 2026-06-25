import pygame as pg
import os, sys
from perlin_noise import PerlinNoise
import utils
import json

class World_data:
    def __init__(self) -> None:
        """
        :Block Types:
        :0: Air
        :1: Grass
        :2: Dirt
        :3: Stone
        """
    def generate_area(self, size:tuple[int,int]):
        pass


class World():
    def __init__(self):
        # Load world data from JSON file
        with open("src/world_data.json", "r") as f:
            data = json.load(f)
        
        self.rect = self.get_rects(data["world"])
        self.base_rect = self.get_rects(data["world"]) # For resizing
        self.screen = pg.display.get_surface()
        self.camera = pg.Vector2(0, 0)
        
    def resize(self):
        base_rect = self.base_rect.copy()
        for i, rect in enumerate(self.rect):
            rect.x = base_rect[i].x * utils.SCALE["width"]
            rect.y = base_rect[i].y * utils.SCALE["height"]
            rect.width = base_rect[i].width * utils.SCALE["width"]
            rect.height = base_rect[i].height * utils.SCALE["height"]

        return self.rect
    def move(self, dx, dy):
        self.camera.x += dx
        self.camera.y += dy

        for rect in self.rect:
            rect.x += dx
            rect.y += dy
            
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
    
    def save_dict(self):
      
        return {}


def test():
    import matplotlib.pyplot as plt
    # 1. Initialize noise generator
    # Lower octaves = smoother transitions; higher octaves = more jagged waves
    noise = PerlinNoise(octaves=4, seed=42)

    # 2. Define your x inputs
    x_inputs = list(range(0, 200))

    # 3. Generate y outputs
    # Dividing 'x' by a scale factor (e.g., 50.0) is crucial for a smooth output
    scale_factor = 50.0
    y_outputs = [noise([x / scale_factor]) for x in x_inputs]

    # 4. Plot the mapping
    plt.figure(figsize=(10, 4))
    plt.plot(x_inputs, y_outputs, label='Smooth Perlin Curve', color='blue')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.grid(True)
    plt.legend()
    plt.show()



if __name__ == "__main__":
    test()

   