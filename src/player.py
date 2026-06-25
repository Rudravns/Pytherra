import pygame as pg
import os, sys, utils

class Player():
    def __init__(self, pos, size):
        self.pos = pg.Vector2(pos)
        
        self.rect = pg.Rect(self.pos.x, self.pos.y, size, size)
        self.base_rect = pg.Rect(self.pos.x, self.pos.y, size, size) # For resizing
        self.last_pos = self.pos.copy()

        self.screen = pg.display.get_surface()
        self.prev_scale = {"width": 1.0, "height": 1.0, "overall": 1.0}

        self.SPEED = 500
        self.FRICTION = 0.6 #World Dependent
        self.GRAVITY = 24 #World Dependent
        self.JUMP = 12
        self.MAX_STEP = 20
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
            #checks if the player is still out of the world after the failsafe
            if self.pos.y > self.screen.get_height(): # pyright: ignore[reportOptionalMemberAccess]
                self.rect.y = self.screen.get_height() - self.rect.height # pyright: ignore[reportOptionalMemberAccess]
                while self.rect.collideobjectsall(world):
                    self.rect.y -= 1
                
                self.pos.y = self.rect.y

            self.vel.y = 0
        
        self.collide = ""
        self.rect.y = int(self.pos.y)
        self.check_collision(world, (None, self.rect.y))
        self.rect.x = int(self.pos.x)
        self.check_collision(world, (self.rect.x, None))

        self.last_pos = self.pos.copy()

    def check_collision(self, world: list[pg.Rect], move: tuple):
        # Check for collision with the world
        for w in world:
            if w.colliderect(self.rect):
                # If colliding, reset position and velocity
                # Fixed collision (Happy)
                if move[0] is None and move[1] is not None: # Vertical movement
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
                elif move[1] is None and move[0] is not None: # Horizontal movement
                    self.rect.x -= self.vel.x

                    if self.vel.x > 0:
                        self.rect.right = w.left
                        self.collide = "left"
                    elif self.vel.x < 0:
                        self.rect.left = w.right
                        self.collide = "right"

                    self.pos.x = self.rect.x

                    check = self.rect.bottom - w.top
                    if (abs(check) >= 0 and abs(check) <= self.MAX_STEP * utils.SCALE["height"]) and not self.jump:
                        self.rect.bottom = w.top
                        self.rect.x += self.vel.x
                        self.collide = "top"
                        pass

                    self.vel.x = 0
                else: # Error in input, should not happe
                   
                    raise ValueError(f"Error: Invalid tuple value for move. X : {move[0]}, Y: {move[1]}")
    
    def draw(self, hbox=False):
        pg.draw.rect(self.screen, (0, 128, 255), self.rect)

        if hbox:
            pg.draw.rect(self.screen, "red", self.rect, 2)
    
    def resize(self):
        check = False
        for n in utils.SCALE:
            if self.prev_scale[n] != utils.SCALE[n]: check = True

        if check:
            # Calculate the ratio difference since the last resize
            ratio_w = utils.SCALE["width"] / self.prev_scale["width"]
            ratio_h = utils.SCALE["height"] / self.prev_scale["height"]

            # Apply this ratio to the player's true position and velocity
            self.pos.x *= ratio_w
            self.pos.y *= ratio_h
            self.vel.x *= ratio_w
            self.vel.y *= ratio_h
            
            # Sync the rect coordinates
            self.rect.x = int(self.pos.x)
            self.rect.y = int(self.pos.y)

            # Record the new scale for the next resize event
            for n in utils.SCALE:
                self.prev_scale[n] = utils.SCALE[n]
        
        # We can still scale width/height via base_rect because the player's physical size is static relative to scale
        self.rect.width = self.base_rect.width * utils.SCALE["overall"]
        self.rect.height = self.base_rect.height * utils.SCALE["overall"]

        self.SPEED = self.BASE_SPEED * utils.SCALE["width"]
        self.GRAVITY = self.BASE_GRAVITY * utils.SCALE["height"]
        self.JUMP = self.BASE_JUMP * utils.SCALE["height"]

        return self.rect