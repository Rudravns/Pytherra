# Rename Project to Pytherra
import pygame as pg
import os, sys
import random
import player, world, utils

class Main:
    def __init__(self):
        pg.init()
        os.system('cls' if os.name == 'nt' else "clear")
        
        # Screen setup
        self.screen = pg.display.set_mode((1000, 800), pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.BASE_SIZE = self.screen.get_size()
        self.dt = 0
        

        #debugs
        self.CONSOLE_DEBUG = True
        self.UI_DEBUG = True

        # Player
        self.player = player.Player((500, 400), 80) #Pos, Size

        # World
        self.world_data = world.World_data(seed=random.randint(1, 1000))
        heights = self.world_data.generate_area(pg.Vector2(100, 5), 1)
        self.world = world.World()
        self.world.import_gen_data(heights)

    def run(self):
        while True:
            self.screen.fill((0, 0, 0)) # Clear the screen
            self.dt = self.clock.tick(120)/1000 # Limit to 120 FPS

            os.system("clr" if os.name == "nt" else "clear")

            keys = pg.key.get_pressed()
            
            self.update_movement(keys)

            utils.draw_text(self.screen, f"FPS: {int(self.clock.get_fps())}", 40, (255, 255, 255), (10, 10))
            self.draw()
            if self.UI_DEBUG: self.debug_UI()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return
                    if event.key == pg.K_r:
                        self.screen = pg.display.set_mode((1000, 800), pg.RESIZABLE)
                        self.resize()
                
                if event.type == pg.VIDEORESIZE:
                        if self.CONSOLE_DEBUG: print(f"Resized to {event.w, event.h}")
                        w, h = event.w, event.h
                        self.resize(w, h)

        
            pg.display.update()

    def draw(self):
        self.player.draw(self.UI_DEBUG)
        self.world.draw()

    def debug_UI(self):
      utils.draw_text(self.screen, f"Player Position: {self.player.rect.x}, {self.player.rect.y}", 40, (255, 255, 255), (10, 40))
      utils.draw_text(self.screen, f"Last Player Position: {self.player.rect.x}, {self.player.rect.y}", 40, (255, 255, 255), (10, 80))
      utils.draw_text(self.screen, f"Player velocity: {round(self.player.vel.x, 3)}, {round(self.player.vel.y, 3)}", 40, (255, 255, 255), (10, 120))
      utils.draw_text(self.screen, f"Jump: {self.player.jump}", 40, (255, 255, 255), (10, 160))
      utils.draw_text(self.screen, f"Collision: {self.player.collide}", 40, (255, 255, 255), (10, 200))
      utils.draw_text(self.screen, f"Scale: {utils.SCALE}", 40, (255, 255, 255), (10, 240))
      utils.draw_text(self.screen, f"Seed: {self.world_data.seed}", 40, (255, 255, 255), (10, 280))



    def resize(self, w=None, h=None):
        if w is None:
            w = self.screen.get_width()
        if h is None:
            h = self.screen.get_height()

        utils.SCALE["width"] = w / self.BASE_SIZE[0]
        utils.SCALE["height"] = h / self.BASE_SIZE[1]
        utils.SCALE["overall"] = (utils.SCALE["width"] + utils.SCALE["height"]) / 2

        utils.cache.clear() # Clear the text cache to regenerate with new sizesDDDDD
        self.player.resize()
        self.world.resize()

    def update_movement(self, keys):
        old_x = self.player.pos.x
        old_y = self.player.pos.y

        self.player.update(keys, self.world.rect, self.dt)

        dx = self.player.pos.x - old_x
        dy = self.player.pos.y - old_y

        if dx != 0 or dy != 0:
            self.world.move(int(-dx), int(-dy))

            self.player.pos.x = old_x
            self.player.pos.y = old_y

            self.player.rect.x = int(old_x)
            self.player.rect.y = int(old_y)

            self.player.last_pos.x = old_x
            self.player.last_pos.y = old_y
            


if __name__ == "__main__":
    app = Main()
    app.run()
    pg.quit()

sys.exit()