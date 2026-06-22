import pygame as pg
import os, sys, utils

class Player():
    def __init__(self, pos, size):
        self.pos = pg.Vector2(pos)
        
        self.rect = pg.Rect(self.pos.x, self.pos.y, size, size)
        self.base_rect = pg.Rect(self.pos.x, self.pos.y, size, size) # For resizing
        self.last_pos = self.pos.copy()

        self.screen = pg.display.get_surface()

        self.SPEED = 500
        self.FRICTION = 0.6 #Wrld Dependent
        self.GRAVITY = 24 #World Dependent
        self.JUMP = 12
        self.vel = pg.Vector2(0, 0)
        
        #base_stuff
        self.BASE_SPEED = self.SPEED
        self.BASE_FRICTION = self.FRICTION
        self.BASE_GRAVITY = self.GRAVITY
        self.BASE_JUMP = self.JUMP
        
        self.jump = True

    def update(self, key, world: list[pg.Rect], dt):
        if key[pg.K_LEFT] or key[pg.K_a]:
            self.vel.x -= self.SPEED
        if key[pg.K_RIGHT] or key[pg.K_d]:
            self.vel.x += self.SPEED
        if (key[pg.K_SPACE] or key[pg.K_w]) and not self.jump:
            self.vel.y -= self.JUMP
            self.jump = True

        # Apply gravity
        self.vel.x *= self.FRICTION * dt
        self.pos.x += self.vel.x
        self.vel.y += self.GRAVITY * dt
        self.pos.y += self.vel.y

        # Failsafe for falling out of the world
        if self.rect.top > self.screen.get_height(): # pyright: ignore[reportOptionalMemberAccess]
            #self.pos.y -= self.vel.y
            self.pos.y *= utils.SCALE["height"]
            #self.vel.y = 0

        
        # Check for collision with the world
        for w in world:
            print(w)
            if w.colliderect(self.rect):
                # If colliding, reset position and velocity
                
                self.pos.x = self.rect.x
                self.pos.y = self.rect.y
                self.vel.y = 0
                self.last_pos = self.pos.copy()
                self.jump = False

        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
    
    def draw(self, hbox= False):
        pg.draw.ellipse(self.screen, (0, 128, 255), self.rect, 0) # pyright: ignore[reportArgumentType]
        if hbox: pg.draw.rect(self.screen, 'red', self.rect, 2)  # pyright: ignore[reportArgumentType]
    
    def resize(self):
        #self.base_rect = self.base_rect.copy()

        #self.rect.x = self.base_rect.x * utils.SCALE["width"]
        #self.rect.y = self.base_rect.y * utils.SCALE["height"]
        self.rect.width = self.base_rect.width * utils.SCALE["overall"]
        self.rect.height = self.base_rect.height * utils.SCALE["overall"]

        self.SPEED = self.BASE_SPEED * utils.SCALE["width"]
        self.GRAVITY = self.BASE_GRAVITY * utils.SCALE["height"]
        self.JUMP = self.BASE_JUMP * utils.SCALE["height"]

        return self.rect