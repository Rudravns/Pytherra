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
        self.FRICTION = 0.6 #World Dependent
        self.GRAVITY = 24 #World Dependent
        self.JUMP = 12
        self.vel = pg.Vector2(0, 0)
        
        #base_stuff
        self.BASE_SPEED = self.SPEED
        self.BASE_FRICTION = self.FRICTION
        self.BASE_GRAVITY = self.GRAVITY
        self.BASE_JUMP = self.JUMP
        
        self.jump = True

        #debug
        self.collide = ""

    def update(self, key, world: list[pg.Rect], dt):
        if key[pg.K_LEFT] or key[pg.K_a]:
            self.vel.x -= self.SPEED * dt
        if key[pg.K_RIGHT] or key[pg.K_d]:
            self.vel.x += self.SPEED * dt
        if (key[pg.K_SPACE] or key[pg.K_UP] or key[pg.K_w]) and not self.jump:
            self.vel.y -= self.JUMP
            self.jump = True

        # Apply friction and gravity
        self.vel.x *= self.FRICTION
        self.pos.x += self.vel.x
        self.vel.y += self.GRAVITY * dt
        self.pos.y += self.vel.y

        # Failsafe for falling out of the world
        if self.rect.top > self.screen.get_height(): # pyright: ignore[reportOptionalMemberAccess]
            #self.pos.y -= self.vel.y
            self.pos.y *= utils.SCALE["height"]
            #self.vel.y = 0
        
        self.collide = ""
        self.rect.x = int(self.pos.x)
        self.check_collision(world, (self.rect.x, None))
        self.rect.y = int(self.pos.y)
        self.check_collision(world, (None, self.rect.y))

        self.last_pos = self.pos.copy()

    def check_collision(self, world: list[pg.Rect], move: tuple):
        # Check for collision with the world
        for w in world:
            print(w)
            if w.colliderect(self.rect):
                # If colliding, reset position and velocity
                # Fixed collision (Happy)
                if move[0] is None: # Vertical movement
                    self.rect.y -= self.vel.y

                    if self.vel.y > 0:
                        self.rect.bottom = w.top
                        self.jump = False
                        self.collide = "top"
                    elif self.vel.y < 0:
                        self.rect.top = w.bottom
                        self.collide = "bottom"
                    
                    self.vel.y = 0
                    self.pos.y = self.rect.y
                if move[1] is None: # Horizontal movement
                    self.rect.x -= self.vel.x

                    if self.vel.x > 0:
                        self.rect.right = w.left
                        self.collide = "left"
                    elif self.vel.x < 0:
                        self.rect.left = w.right
                        self.collide = "right"

                    self.vel.x = 0
                    self.pos.x = self.rect.x
                if (move[0] is None and move[1] is None) or (move[0] is not None and move[1] is not None): # Error in input, should not happen
                    raise ValueError("Error: Invalid tuple value for move. X : {move[0]}, Y: {move[1]}")
    
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