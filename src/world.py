import pygame as pg
import os, sys
from perlin_noise import PerlinNoise
import utils
import json
import random


class World_data:
    def __init__(self, seed=0) -> None:
        """
        :Block Types:
        :0: Air
        :1: Grass
        :2: Dirt
        :3: Stone
        """
        self.noise = PerlinNoise(octaves=4, seed=seed)
        self.scale_factor = 50.0
        
        # Amplitude determines the maximum height variations of your terrain (e.g., hills can be up to 15 blocks tall/deep)
        self.amplitude = 15.0 
        
        # Base height is the flat floor level where the terrain starts (e.g., middle of your game screen)
        self.base_height = 10 
        
        self.max_min_x = [0,0]

        self.core_data = {}

    def generate_area(self, size: pg.Vector2, direction: int = 1) -> list[int]:
        """Generates a chunk of terrain heights and updates the boundaries."""
        
        x_inputs, start_x, end_x = self.__world_cord_area(size, direction)
       
        # FIX: Multiply the noise output by an amplitude to scale it, 
        # and optionally add a base_height so it doesn't default to ground level 0.
        y_outputs = [
            round(self.noise([x / self.scale_factor]) * self.amplitude + self.base_height) 
            for x in x_inputs
        ]

        # Update the tracking boundaries seamlessly
        if direction == 1:
            self.max_min_x[1] = end_x
        else:
            self.max_min_x[0] = start_x

        return y_outputs

    def generate_tiles(self, size: pg.Vector2, direction: int = 1):
        # get y inputs
        heights = self.generate_area(size, direction)

        # Here you would typically generate actual tile blocks (Grass, Dirt, Stone) 
        # using the generated heights for each x coordinate.
        for x in range(int(size.x)):
            # Example placeholder logic:
            x_coord = self.max_min_x[0] + x if direction != 1 else self.max_min_x[1] - int(size.x) + x
            terrain_height = heights[x]
            for y in range(int(size.y)):
                current = terrain_height-y

                

            # Now you have a varied height instead of all 0s!

    def __world_cord_area(self, size: pg.Vector2, direction: int = 1):
        chunk_width = int(size.x)
        if direction == 1:
            start_x = int(self.max_min_x[1])
            end_x = start_x + chunk_width
        else:
            end_x = int(self.max_min_x[0])
            start_x = end_x - chunk_width

        x_inputs = range(start_x, end_x)
        return x_inputs, start_x, end_x
    
    def __match_y_to_tile(self, y):
        
        block = 0
        #KIAN DO IT FROM HERE
        
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
        for rect in self.rect:
            rect.x += dx
            rect.y += dy

    def draw(self):
        for rect in self.rect:
            draw_rect = pg.Rect(
                rect.x - self.camera.x,
                rect.y - self.camera.y,
                rect.width,
                rect.height
            )

            pg.draw.rect(self.screen, "green", draw_rect) # pyright: ignore[reportArgumentType]
    
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
    pg.init() # Initialize pygame so Vector2 works
    seed = random.randint(1, 100)
    w = World_data(seed=seed)
    # Generate 10 columns of heights
    heights = w.generate_area(pg.Vector2(10, 5), 1)
    print(f"Seed {seed} generated heights:", heights)