# pyright: reportArgumentType = false
import pygame as pg
import math
import utils
import Dualsense

class Player:
    def __init__(self, pos, size):
        self.pos = pg.Vector2(pos)
        # Fixed logical bounding box (doesn't change size internally on resize)
        self.rect = pg.Rect(self.pos.x, self.pos.y, size / 2, size)
        
        # Delta-time based physics configuration
        self.SPEED = 2500     # Acceleration in px/s^2
        self.MAX_SPEED = 400  # Max horizontal speed in px/s
        self.FRICTION = 12    # Friction deceleration coefficient
        self.GRAVITY = 2000   # Downward pull in px/s^2
        self.JUMP = 700       # Upward instantaneous impulse in px/s
        self.MAX_STEP = 32    # Maximum height they can walk over smoothly
        
        self.vel = pg.Vector2(0, 0)
        self.jump = True
        self.collide = ""

    def update(self, keys, world_rects: list[pg.Rect], dt: float):
        # Prevent physics explosions during lag spikes (e.g. window dragging)
        if dt > 0.05: 
            dt = 0.05 
            
        # Horizontal input acceleration
        acc_x = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            acc_x -= self.SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            acc_x += self.SPEED

        # Apply friction if no keys pressed
        if acc_x == 0:
            if self.vel.x > 0:
                self.vel.x -= self.FRICTION * self.SPEED * dt
                if self.vel.x < 0: self.vel.x = 0
            elif self.vel.x < 0:
                self.vel.x += self.FRICTION * self.SPEED * dt
                if self.vel.x > 0: self.vel.x = 0
        else:
            self.vel.x += acc_x * dt
            
        # Clamp to max speed
        if self.vel.x > self.MAX_SPEED: self.vel.x = self.MAX_SPEED
        if self.vel.x < -self.MAX_SPEED: self.vel.x = -self.MAX_SPEED

        # Vertical gravity
        self.vel.y += self.GRAVITY * dt

        # Jump
        if (keys[pg.K_SPACE] or keys[pg.K_UP] or keys[pg.K_w]) and not self.jump:
            self.vel.y = -self.JUMP
            self.jump = True

        self.collide = ""

        # Move horizontally and collide
        self.pos.x += self.vel.x * dt
        self.rect.x = int(self.pos.x)
        self.check_collision(world_rects, 'x')

        # Move vertically and collide
        self.pos.y += self.vel.y * dt
        self.rect.y = int(self.pos.y)
        self.check_collision(world_rects, 'y')

        # Failsafe: if they fall into the void, respawn high up
        if self.pos.y > 6000:
            self.pos.y = -1000
            self.vel.y = 0

    def check_collision(self, world_rects: list[pg.Rect], axis: str):
        for w in world_rects:
            if self.rect.colliderect(w):
                if axis == 'x':
                    if self.vel.x > 0: # Moving right
                        # Step-up logic
                        if self.rect.bottom - w.top <= self.MAX_STEP and not self.jump:
                            self.rect.bottom = w.top
                            self.pos.y = self.rect.y
                            self.collide = "step_right"
                        else:
                            self.rect.right = w.left
                            self.vel.x = 0
                            self.collide = "right"
                    elif self.vel.x < 0: # Moving left
                        # Step-up logic
                        if self.rect.bottom - w.top <= self.MAX_STEP and not self.jump:
                            self.rect.bottom = w.top
                            self.pos.y = self.rect.y
                            self.collide = "step_left"
                        else:
                            self.rect.left = w.right
                            self.vel.x = 0
                            self.collide = "left"
                    self.pos.x = self.rect.x
                    
                elif axis == 'y':
                    if self.vel.y > 0: # Falling
                        self.rect.bottom = w.top
                        self.vel.y = 0
                        self.jump = False
                        self.collide = "bottom"
                    elif self.vel.y < 0: # Hitting head
                        self.rect.top = w.bottom
                        self.vel.y = 0
                        self.collide = "top"
                    self.pos.y = self.rect.y

    def draw(self, screen: pg.Surface, camera: pg.Vector2, hbox=False):
        # Draw scales to exactly what utils.SCALE demands, leaving logic untouched
        scale_w, scale_h = utils.SCALE["width"], utils.SCALE["height"]
        
        rx1 = (self.rect.x - camera.x) * scale_w
        ry1 = (self.rect.y - camera.y) * scale_h
        rx2 = (self.rect.right - camera.x) * scale_w
        ry2 = (self.rect.bottom - camera.y) * scale_h
        
        draw_rect = pg.Rect(math.floor(rx1), math.floor(ry1), math.ceil(rx2 - rx1), math.ceil(ry2 - ry1))
        
        pg.draw.rect(screen, (0, 128, 255), draw_rect)
        if hbox:
            pg.draw.rect(screen, "red", draw_rect, 2)