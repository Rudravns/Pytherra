# Rename Project to Pytherra
import pygame as pg
import os, sys
import player, world, utils

class Main:
    def __init__(self):
        pg.init()
        
        # Screen setup
        self.screen = pg.display.set_mode((1000, 800), pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.BASE_SIZE = self.screen.get_size()
        self.dt = 0
        

        #debugs
        self.CONSOLE_DEBUG = True
        self.UI_DEBUG = True

        # Player
        self.player = player.Player((0, 0), 80) #Pos, Size

        # World
        self.world = world.World((0, self.screen.get_height() - 100), (self.screen.get_width(), 100)) #Pos, Size

    def run(self):
        while True:
            self.screen.fill((0, 0, 0)) # Clear the screen
            self.dt = self.clock.tick(120)/1000 # Limit to 120 FPS
            
            utils.draw_text(self.screen, f"FPS: {int(self.clock.get_fps())}", 40, (255, 255, 255), (10, 10))

            if self.UI_DEBUG: self.debug_UI()

            keys = pg.key.get_pressed()
            self.player.update(keys, self.world.rect, self.dt)
            
            self.draw()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return
                
                if event.type == pg.VIDEORESIZE:
                        if self.CONSOLE_DEBUG: print(f"Resized to {event.w, event.h}")
                        w, h = event.w, event.h
                        self.resize(w, h)

            self.resize()
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



if __name__ == "__main__":
    app = Main()
    app.run()
    pg.quit()

sys.exit()