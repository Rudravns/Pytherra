# Rename Project to Pytherra
import pygame as pg
import os, sys
import random, time, threading
import player, world, loading, utils

class Main:
    def __init__(self):
        pg.init()
        os.system('cls' if os.name == 'nt' else "clear")
        
        # Screen setup
        self.screen = pg.display.set_mode((1000, 800), pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.BASE_SIZE = (1000, 800)
        self.dt = 0
        
        # Debugs
        self.CONSOLE_DEBUG = True
        self.UI_DEBUG = True

        # Generate seed and World
        self.seed = random.randint(0, 10000)
        self.WORLD_SIZE = 10**2 # In chunks (In blocks = self.world_size * 16)
        self.world = world.World(seed=self.seed)
        
        # Spawn the player dynamically above the terrain at x = 0
        spawn_x = 0
        # Calculate exact surface block y-coordinate, convert to pixels, go 200px higher
        spawn_y = self.world.get_surface_y(0) * self.world.BLOCK_SIZE - 200
        self.player = player.Player((spawn_x, spawn_y), 80) # Pos, Size
        
        # Initialize camera
        self.camera = pg.Vector2(0, 0)
        
        # Trigger initial scale configuration
        self.resize(self.screen.get_width(), self.screen.get_height())

    def run(self):
        """
        l = loading.Loading(self.screen)
        l.run()
        """

        while True:
            # Clear screen (Sky blue)
            self.screen.fill((135, 206, 235)) 
            
            # Limit to 120 FPS, get delta time in seconds
            self.dt = self.clock.tick(0) / 1000.0 

            keys = pg.key.get_pressed()
            self.update_game(keys)
            self.draw()

            if self.UI_DEBUG: 
                self.debug_UI()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return
                    if event.key == pg.K_r:
                        self.screen = pg.display.set_mode((1000, 800), pg.RESIZABLE)
                        self.resize(1000, 800)
                
                if event.type == pg.VIDEORESIZE:
                    if self.CONSOLE_DEBUG: print(f"Resized to {event.w, event.h}")
                    self.resize(event.w, event.h)

            pg.display.update()

    def update_game(self, keys):
        # Get active blocks ONLY around the player
        nearby_rects = self.world.get_nearby_rects(self.player.rect)
        
        # Update physical world state
        self.player.update(keys, nearby_rects, self.dt)
        
        # LERP (smoothly animate) camera to follow player accounting for current zoom scale
        target_x = self.player.rect.centerx - (self.screen.get_width() / 2) / utils.SCALE["width"]
        target_y = self.player.rect.centery - (self.screen.get_height() / 2) / utils.SCALE["height"]
        
        # Higher multiplier = faster, snapier camera
        self.camera.x += (target_x - self.camera.x) * 10 * self.dt
        self.camera.y += (target_y - self.camera.y) * 10 * self.dt

    def draw(self):
        # Draw everything relatively to the camera
        self.world.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera, self.UI_DEBUG)

    def debug_UI(self):
        utils.draw_text(self.screen, f"FPS: {int(self.clock.get_fps())}", 40, (255, 255, 255), (10, 10))
        utils.draw_text(self.screen, f"Player Pos: {int(self.player.pos.x)}, {int(self.player.pos.y)}", 40, (255, 255, 255), (10, 40))
        utils.draw_text(self.screen, f"Velocity: {round(self.player.vel.x, 2)}, {round(self.player.vel.y, 2)}", 40, (255, 255, 255), (10, 70))
        utils.draw_text(self.screen, f"Grounded (not jump): {not self.player.jump}", 40, (255, 255, 255), (10, 100))
        utils.draw_text(self.screen, f"Collision: {self.player.collide}", 40, (255, 255, 255), (10, 130))
        utils.draw_text(self.screen, f"Scale: W:{round(utils.SCALE['width'], 2)}, H:{round(utils.SCALE['height'],2)}", 40, (255, 255, 255), (10, 160))
        utils.draw_text(self.screen, f"Seed: {self.seed}", 40, (255, 255, 255), (10, 190))
        utils.draw_text(self.screen, f"Block Pos: {self.player.pos.x//self.world.BLOCK_SIZE}, {self.player.pos.y//self.world.BLOCK_SIZE}", 40, (255, 255, 255), (10, 220))
        utils.draw_text(self.screen, f"Loaded Chunks: {len(self.world.chunks)}", 40, (255, 255, 255), (10, 250))
        utils.draw_text(self.screen, f"World Size: {self.WORLD_SIZE}", 40, (255, 255, 255), (10, 280))


    def resize(self, w, h):
        """
        Updates rendering scale. We no longer call player.resize() or world.resize()
        because the physical logical coordinate space is kept pristine. We only apply 
        scaling factors when projecting entities to the screen!
        """
        utils.SCALE["width"] = w / self.BASE_SIZE[0]
        utils.SCALE["height"] = h / self.BASE_SIZE[1]
        utils.SCALE["overall"] = (utils.SCALE["width"] + utils.SCALE["height"]) / 2

        utils.cache.clear() # Clear the text cache to regenerate fonts with new sizes

if __name__ == "__main__":
    app = Main()
    app.run()
    pg.quit()
    sys.exit()