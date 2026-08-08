# Rename Project to Pytherra
import pygame as pg
import os, sys
import random, time, threading

# Player folder
from Player import player
# Controls folder
from Controls import mouse
# Game folder
from Game import world, loading, utils

class pytherra:
    def __init__(self, seed:int = None): # pyright: ignore[reportArgumentType]
        pg.init()
        #os.system('cls' if os.name == 'nt' else "clear")
        
        # Screen setup
        self.screen = pg.display.set_mode((1000, 800), pg.RESIZABLE)
        pg.display.set_caption("Pytherra")
        self.clock = pg.time.Clock()
        self.BASE_SIZE = (1000, 800)
        self.dt = 0

        # Debugs
        self.CONSOLE_DEBUG = False
        self.UI_DEBUG = True
        self.GAME_DEBUG = True

        # Generate seed and World
        self.seed = random.randint(0, 10000) if seed is None else seed
        self.WORLD_SIZE = 10**2 # In chunks (In blocks = self.world_size * 16)
        self.world = world.World(seed=self.seed)

        # Spawn the player dynamically above the terrain at x = 0
        spawn_x = 0
        # Calculate exact surface block y-coordinate, convert to pixels, go 200px higher
        spawn_y = self.world.get_surface_y(0)[0] * self.world.BLOCK_SIZE - 200
        self.player = player.Player((spawn_x, spawn_y), 50) # Pos, Size
        
        # Mouse
        self.mouse = mouse.Mouse(size=self.world.BLOCK_SIZE)

        # Initialize camera
        self.camera = pg.Vector2(0, 0)

        #Setup textures
        #init_textures()

    def run(self):
        # Instantiate and run the loading screen by passing 'self' (the main game application)
        # This lets the loading screen access self.world to pre-generate chunks before playing!
        l = loading.Loading(self)
        l.run()

        self.camera.x = self.player.rect.centerx - (self.screen.get_width() / 2) / (utils.SCALE["width"] * utils.SCALE["zoom"])
        self.camera.y = self.player.rect.centery - (self.screen.get_height() / 2) / (utils.SCALE["height"] * utils.SCALE["zoom"])

        while True:
            # Clear screen (Sky blue)
            self.screen.fill((135, 206, 235)) 
            
            # Limit to 120 FPS, get delta time in seconds
            self.dt = self.clock.tick(120) / 1000.0 

            keys = pg.key.get_pressed()
            buttons = pg.mouse.get_pressed()
            self.update_game(keys, buttons)
            self.draw()

            if self.UI_DEBUG: 
                self.debug_UI()
            if self.CONSOLE_DEBUG:
                self.debug_console()
            if self.GAME_DEBUG:
                self.mouse.INSTANT = True # type: ignore
            else:
                self.mouse.INSTANT = False

            scroll = 0
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return
                    if event.key == pg.K_r:
                        self.screen = pg.display.set_mode((1000, 800), pg.RESIZABLE)
                        self.resize(1000, 800)
                    if event.key == pg.K_c:
                        self.world.Simple_color = not self.world.Simple_color
                    if event.key == pg.K_n and self.GAME_DEBUG:
                        self.player.NO_CLIP = not self.player.NO_CLIP # pyright: ignore[reportAttributeAccessIssue]
                    
                    # Debug toggles
                    if event.key == pg.K_F1:
                        self.GAME_DEBUG = not self.GAME_DEBUG
                    if event.key == pg.K_F2:
                        self.CONSOLE_DEBUG = not self.CONSOLE_DEBUG
                    if event.key == pg.K_F3:
                        self.UI_DEBUG = not self.UI_DEBUG
                    
                    # Zooming
                    if event.key == pg.K_EQUALS:
                        utils.SCALE["zoom"] += 0.1
                    if event.key == pg.K_MINUS:
                        utils.SCALE["zoom"] -= 0.1
                    
                    # Inventory
                    if event.key == pg.K_1:
                        self.player.inv.hold = 0
                    if event.key == pg.K_2:
                        self.player.inv.hold = 1
                    if event.key == pg.K_3:
                        self.player.inv.hold = 2
                    if event.key == pg.K_4:
                        self.player.inv.hold = 3
                    if event.key == pg.K_5:
                        self.player.inv.hold = 4
                    if event.key == pg.K_6:
                        self.player.inv.hold = 5
                    if event.key == pg.K_7:
                        self.player.inv.hold = 6
                    if event.key == pg.K_8:
                        self.player.inv.hold = 7
                    if event.key == pg.K_9:
                        self.player.inv.hold = 8

                    if event.key == pg.K_e:
                        self.player.inv.show_inv = not self.player.inv.show_inv
                        self.mouse.hold_tick = 0
                    
                if event.type == pg.MOUSEWHEEL:
                    if abs(event.x) > abs(event.y):
                        scroll = -event.x
                        if not self.player.inv.show_inv: self.player.inv.scroll_inv(-event.x)
                    else:
                        scroll = -event.y
                        if not self.player.inv.show_inv: self.player.inv.scroll_inv(-event.y)

                if event.type == pg.VIDEORESIZE:
                    if self.CONSOLE_DEBUG: print(f"Resized to {event.w, event.h}")
                    self.resize(event.w, event.h)
            
            self.mouse.inventory(self.player, self.camera, buttons, scroll)
            
            pg.display.update()

    def update_game(self, keys, buttons):
        # Get active blocks ONLY around the player
        nearby_rects, _ = self.world.get_nearby_rects(self.player.rect, 2)
        
        # Update physical world state
        if self.player.NO_CLIP: self.player.no_clip(keys)
        else: self.player.update(keys, self.mouse.block_data, nearby_rects, self.dt)

        # Update mouse
        self.mouse.update(self.player, self.world, self.camera, buttons, self.dt)
        
        self.update_camera()

    def update_camera(self):
        # LERP (smoothly animate) camera to follow player accounting for current zoom scale
        target_x = self.player.rect.centerx - (self.screen.get_width() / 2) / (utils.SCALE["width"] * utils.SCALE["zoom"])
        target_y = self.player.rect.centery - (self.screen.get_height() / 2) / (utils.SCALE["height"] * utils.SCALE["zoom"])
        
        # Higher multiplier = faster, snapier camera
        self.camera.x += (target_x - self.camera.x) * 10 * self.dt
        self.camera.y += (target_y - self.camera.y) * 10 * self.dt

    def draw(self):
        # Draw everything relatively to the camera
        self.world.draw(self.screen, self.camera, self.GAME_DEBUG)
        self.player.draw(self.screen, self.world, self.camera, self.GAME_DEBUG)
        self.mouse.draw(self.screen, self.player, self.world, self.camera)
        if self.GAME_DEBUG:
            w, h, o, z = utils.SCALE["width"], utils.SCALE["height"], utils.SCALE["overall"], utils.SCALE["zoom"]
            px = (self.player.rect.centerx - self.camera.x) * (w * z)
            py = (self.player.rect.top - self.camera.y) * (h * z)
            mx = (self.mouse.debug_line[0] - self.camera.x) * (w * z)
            my = (self.mouse.debug_line[1] - self.camera.y) * (h * z)
            pg.draw.line(self.screen, (255, 0, 0), (int(px), int(py)), (int(mx), int(my)))

            for r in self.mouse.debug_rect:
                rx = (r.x - self.camera.x) * (w * z)
                ry = (r.y - self.camera.y) * (h * z)
                rw = r.w * (w * z)
                rh = r.h * (h * z)

                draw_rect =pg.Rect(int(rx), int(ry), int(rw), int(rh))
                pg.draw.rect(self.screen, (0, 0, 255), draw_rect, 1)

    def debug_UI(self):
        utils.draw_text(self.screen, f"FPS: {int(self.clock.get_fps())}", 40, (255, 255, 255), (10, 10))
        utils.draw_text(self.screen, f"Player Pos: {int(self.player.pos.x)}, {int(self.player.pos.y)}", 40, (255, 255, 255), (10, 40))
        utils.draw_text(self.screen, f"Velocity: {round(self.player.vel.x, 2)}, {round(self.player.vel.y, 2)}", 40, (255, 255, 255), (10, 70))
        utils.draw_text(self.screen, f"Grounded (not jump): {not self.player.jump}", 40, (255, 255, 255), (10, 100))
        utils.draw_text(self.screen, f"Collision: {self.player.collide}", 40, (255, 255, 255), (10, 130))
        utils.draw_text(self.screen, f"Scale: W:{round(utils.SCALE['width'], 2)}, H:{round(utils.SCALE['height'],2)}, O:{round(utils.SCALE['overall'],2)}, Z:{round(utils.SCALE['zoom'],2)}", 40, (255, 255, 255), (10, 160))
        utils.draw_text(self.screen, f"Seed: {self.seed}", 40, (255, 255, 255), (10, 190))
        utils.draw_text(self.screen, f"Block Pos: {self.player.pos.x//self.world.BLOCK_SIZE}, {self.player.pos.y//self.world.BLOCK_SIZE}", 40, (255, 255, 255), (10, 220))
        utils.draw_text(self.screen, f"Loaded Chunks: {len(self.world.chunks)}", 40, (255, 255, 255), (10, 250))
        utils.draw_text(self.screen, f"World Size: {self.WORLD_SIZE}", 40, (255, 255, 255), (10, 280))
        utils.draw_text(self.screen, f"Current Chunk: {self.world.get_chunk_from_pos(int(self.player.pos.x))[0]}", 40, (255, 255, 255), (10, 310))
        utils.draw_text(self.screen, f"Hold Tick: {self.mouse.hold_tick}", 40, (255, 255, 255), (10, 340))
        if self.player.fall_tick >= 10:
            color = (255, 0 ,0)
        else:
            color = (0, 255, 0)
        utils.draw_text(self.screen, f"{self.player.fall_tick}", 40, color, (10, 370))
        utils.draw_text(self.screen, f"{self.player.inv.result}", 40, (255, 255, 255), (10, 400))




    def debug_console(self):
        # \033[H moves the cursor to the top left.
        # \033[J clears the screen from the cursor down.
        sys.stdout.write("\033[H\033[J")

        chunk = self.world.get_chunk_from_pos(int(self.player.pos.x))
        surface = self.world.get_surface_y(int(self.player.pos.x // self.world.BLOCK_SIZE))
        
        print(chunk, surface)
        if not self.mouse.debug == None: 
            print(self.mouse.debug)
        print(self.player.debug)

        # Flush stdout to ensure it prints immediately
        sys.stdout.flush()

    def resize(self, w, h):
        """
        Updates rendering scale. We no longer call player.resize() or world.resize()
        because the physical logical coordinate space is kept pristine. We only apply 
        scaling factors when projecting entities to the screen!
        """
        # Calculate a single uniform scale factor using the minimum ratio 
        # to ensure the aspect ratio never warps/stretches.
        uniform_scale = min(w / self.BASE_SIZE[0], h / self.BASE_SIZE[1])
        
        utils.SCALE["width"] = uniform_scale
        utils.SCALE["height"] = uniform_scale
        utils.SCALE["overall"] = uniform_scale

        utils.cache.clear() # Clear the text cache to regenerate fonts with new sizes

if __name__ == "__main__":
    app = pytherra(0)
    app.run()
    pg.quit()
    sys.exit()