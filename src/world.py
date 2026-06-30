import pygame as pg
from perlin_noise import PerlinNoise
import math
import utils

class World:
    def __init__(self, seed: int = 0):
        self.seed = seed
        self.noise = PerlinNoise(octaves=6, seed=seed)
        
        # Data structure: self.chunks[chunk_x][local_x][y] = block_id
        self.chunks = {}
        
        # Engine parameters
        self.BLOCK_SIZE = 32
        self.CHUNK_SIZE = 32 # Blocks per chunk width
        self.DEPTH_LIMIT = 40 # How far down blocks generate
        
        # Terrain generation parameters (from original code)
        self.scale = 70.0
        self.amplitude = 25
        self.base_height = 45
        
        # Block colors (0: Boundry, 1: Grass, 2: Dirt, 3: Stone, 4: Snow, 5: Water)
        self.COLORS = {
            0: (0, 0, 0), # Boundry, not meant to be drawn
            1: (34, 177, 76),   # Grass
            2: (121, 85, 58),   # Dirt
            3: (128, 128, 128), # Stone
            4: (240, 240, 240),  # Snow
            5: (100, 255, 150) # Water
        }

    def get_surface_y(self, world_x: int) -> int:
        """Returns the y-coordinate (in block space) of the surface at world_x."""
        h = self.noise([world_x / self.scale])
        h *= self.amplitude
        h += self.base_height
        return round(h)

    def get_chunk(self, chunk_x: int):
        if chunk_x not in self.chunks:
            self.generate_chunk(chunk_x, boundry=False)
        return self.chunks[chunk_x]

    def generate_chunk(self, chunk_x: int, boundry: bool = False):
        chunk = {}
        for local_x in range(self.CHUNK_SIZE):
            world_x = chunk_x * self.CHUNK_SIZE + local_x
            #print(world_x)
            surface_y = self.get_surface_y(world_x)
            #print(surface_y)

            # Smooth out terrain
            prev_surf_y = self.get_surface_y(world_x - 1)
            next_surf_y = self.get_surface_y(world_x + 1)
            if prev_surf_y == next_surf_y and surface_y != prev_surf_y: # <-- could also check for next_surf_y
                surface_y = prev_surf_y # could also set surface_y to next_surf_y
            
            column = {}
            # Generate column downwards
            start = 0 if boundry else surface_y
            for y in range(start, surface_y + self.DEPTH_LIMIT):
                depth = y - surface_y
                
                if depth == 0:
                    # Peaks (lower y coordinate values) get snow
                    block = 4 if y < 35 else 1 
                elif depth < 0 and boundry:
                    block = 0
                elif depth < 4:
                    block = 2
                else:
                    block = 3
                    
                column[y] = block
            chunk[local_x] = column
            
        self.chunks[chunk_x] = chunk

    def generate_world(self, size: int):
        size += size % 2

        for i in range(size + 1):
            self.generate_chunk(i - size//2)
        
        return True

    def get_nearby_rects(self, player_rect: pg.Rect) -> list[pg.Rect]:
        """Fetches block rects only in the immediate vicinity of the player."""
        rects = []
        
        # Calculate block coordinate bounds based on player rect + a 1-block margin
        start_bx = int((player_rect.left - self.BLOCK_SIZE) // self.BLOCK_SIZE)
        end_bx = int((player_rect.right + self.BLOCK_SIZE) // self.BLOCK_SIZE)
        start_by = int((player_rect.top - self.BLOCK_SIZE) // self.BLOCK_SIZE)
        end_by = int((player_rect.bottom + self.BLOCK_SIZE) // self.BLOCK_SIZE)
        
        for bx in range(start_bx, end_bx + 1):
            chunk_x = bx // self.CHUNK_SIZE
            local_x = bx % self.CHUNK_SIZE
            chunk = self.get_chunk(chunk_x)
            
            if local_x in chunk:
                for by in range(start_by, end_by + 1):
                    if by in chunk[local_x]:
                        rects.append(pg.Rect(bx * self.BLOCK_SIZE, by * self.BLOCK_SIZE, self.BLOCK_SIZE, self.BLOCK_SIZE))
        
        return rects

    def draw(self, screen: pg.Surface, camera: pg.Vector2):
        w, h = screen.get_size()
        scale_w, scale_h = utils.SCALE["width"], utils.SCALE["height"]
        
        # Calculate camera view bounds in logical world coordinates
        start_world_x = camera.x
        end_world_x = camera.x + w / scale_w
        start_world_y = camera.y
        end_world_y = camera.y + h / scale_h
        
        # Convert to block coordinates to efficiently iterate
        start_bx = int(start_world_x // self.BLOCK_SIZE)
        end_bx = int(end_world_x // self.BLOCK_SIZE)
        start_by = int(start_world_y // self.BLOCK_SIZE)
        end_by = int(end_world_y // self.BLOCK_SIZE)
        
        for bx in range(start_bx, end_bx + 1):
            chunk_x = bx // self.CHUNK_SIZE
            local_x = bx % self.CHUNK_SIZE
            chunk = self.get_chunk(chunk_x)
            
            if local_x in chunk:
                for by, block_id in chunk[local_x].items():
                    # Only draw blocks that are inside the vertical view bounds
                    if start_by <= by <= end_by:
                        # Calculate screen positions accurately to avoid floating point seams
                        rx1 = (bx * self.BLOCK_SIZE - camera.x) * scale_w
                        ry1 = (by * self.BLOCK_SIZE - camera.y) * scale_h
                        rx2 = ((bx + 1) * self.BLOCK_SIZE - camera.x) * scale_w
                        ry2 = ((by + 1) * self.BLOCK_SIZE - camera.y) * scale_h
                        
                        draw_rect = pg.Rect(math.floor(rx1), math.floor(ry1), math.ceil(rx2 - rx1), math.ceil(ry2 - ry1))
                        pg.draw.rect(screen, self.COLORS[block_id], draw_rect)
                    

if __name__ == "__main__":
    w = World()
    w.get_chunk(0)
    print(w.chunks)
    w.get_chunk(-1)
    w.get_chunk(1)
    print(len(w.chunks))