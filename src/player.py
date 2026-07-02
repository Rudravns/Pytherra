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
        self.JUMP = 600      # Upward instantaneous impulse in px/s
        self.MAX_STEP = 32    # Maximum height they can walk over smoothly
        self.NO_CLIP = False   # If True, player ignores collisions entirely
        
        self.vel = pg.Vector2(0, 0)
        self.jump = True
        self.collide = ""
        self.in_water = False # Track if player is currently submerged

        self.collidable = [1, 2, 3, 4, 6] # Block IDs that the player can collide with (Grass, Dirt, Stone, Snow, Sand)
        self.semi_collidable = [5]        # Block IDs that the player can pass through with fluid physics (Water)
        self.not_collidable = [0]         # Block IDs that the player completely ignores (Air)

    def update(self, keys, world_rects: dict[int, list[pg.Rect]], dt: float):
        # Prevent physics explosions during lag spikes (e.g. window dragging)
        if dt > 0.05: 
            dt = 0.05 
        
        # 1. Pre-pass check: Is the player currently inside water (semi-collidable)?
        in_water = False
        for block_id in self.semi_collidable:
            if block_id in world_rects:
                for wr in world_rects[block_id]:
                    if self.rect.colliderect(wr):
                        in_water = True
                        break
            if in_water:
                break
        self.in_water = in_water

        # 2. Horizontal input acceleration
        acc_x = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            acc_x -= self.SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            acc_x += self.SPEED

        # Apply friction/fluid drag if no horizontal keys are pressed
        if acc_x == 0:
            current_friction = self.FRICTION
            if self.in_water:
                current_friction *= 1.8 # Extra liquid resistance slows horizontal movement down
                
            if self.vel.x > 0:
                self.vel.x -= current_friction * self.SPEED * dt
                if self.vel.x < 0: self.vel.x = 0
            elif self.vel.x < 0:
                self.vel.x += current_friction * self.SPEED * dt
                if self.vel.x > 0: self.vel.x = 0
        else:
            self.vel.x += acc_x * dt
            
        # Clamp to max speed (slower horizontal movement while swimming)
        max_speed = self.MAX_SPEED
        if self.in_water:
            max_speed *= 0.55 # 55% speed in water for a heavy fluid feel
            
        if self.vel.x > max_speed: self.vel.x = max_speed
        if self.vel.x < -max_speed: self.vel.x = -max_speed

        # 3. Vertical gravity and jump inputs (Minecraft style)
        if self.in_water:
            # Slower sinking: apply only a fraction of gravity
            self.vel.y += self.GRAVITY * 0.15 * dt
            
            # Limit sinking speed so the player drifts downward gently
            if self.vel.y > 90: 
                self.vel.y = 90
            
            # Swim upwards: Holding jump lets you float up continuously
            if keys[pg.K_SPACE] or keys[pg.K_UP] or keys[pg.K_w]:
                self.vel.y = -180 # Upward swimming velocity
            
            # Set jump to True in water. This ensures you cannot initiate a 
            # solid-ground jump the exact moment you leave the water's surface.
            self.jump = True
        else:
            # Normal gravity
            self.vel.y += self.GRAVITY * dt

            # Normal Jump (requires solid ground landing)
            if (keys[pg.K_SPACE] or keys[pg.K_UP] or keys[pg.K_w]) and not self.jump:
                self.vel.y = -self.JUMP
                self.jump = True 

        self.collide = ""

        # 4. Move vertically and check collisions (separating X and Y axes prevents sticking)
        self.pos.y += self.vel.y * dt
        self.rect.y = int(self.pos.y)
        self.check_collision(world_rects, 'y')

        # 5. Move horizontally and check collisions
        self.pos.x += self.vel.x * dt
        self.rect.x = int(self.pos.x)
        self.check_collision(world_rects, 'x')

        # Failsafe: if they fall into the void, respawn high up
        if self.pos.y > 6000:
            self.pos.y = -1000
            self.vel.y = 0

    def no_clip(self, keys):
        self.vel.x = 0
        self.vel.y = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.pos.x -= self.MAX_SPEED // 10
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.pos.x += self.MAX_SPEED // 10
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.pos.y -= self.MAX_SPEED // 10
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.pos.y += self.MAX_SPEED // 10
        
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

    def check_collision(self, world_rects: dict[int, list[pg.Rect]], axis: str):
        block_collided_with = False

        for block_id, rect_list in world_rects.items():
            # Only collide solidly with actual solid block types
            if block_id not in self.collidable:
                continue

            for w in rect_list:
                if self.rect.colliderect(w):
                    if axis == 'x':
                        if self.vel.x > 0: # Moving right
                            # Step-up logic (allow step-up if grounded OR if swimming)
                            if self.rect.bottom - w.top <= self.MAX_STEP and (not self.jump or self.in_water):
                                self.rect.bottom = w.top
                                self.pos.y = self.rect.y
                                self.collide = "step_right"
                                block_collided_with = block_id
                            else:
                                self.rect.right = w.left
                                self.vel.x = 0
                                self.collide = "right"
                                block_collided_with = block_id
                        elif self.vel.x < 0: # Moving left
                            # Step-up logic (allow step-up if grounded OR if swimming)
                            if self.rect.bottom - w.top <= self.MAX_STEP and (not self.jump or self.in_water):
                                self.rect.bottom = w.top
                                self.pos.y = self.rect.y
                                self.collide = "step_left"
                                block_collided_with = block_id
                            else:
                                self.rect.left = w.right
                                self.vel.x = 0
                                self.collide = "left"
                                block_collided_with = block_id
                        self.pos.x = self.rect.x
                        
                    elif axis == 'y':
                        if self.vel.y > 0: # Falling
                            self.rect.bottom = w.top
                            self.vel.y = 0
                            self.jump = False
                            self.collide = "bottom"
                            block_collided_with = block_id
                        elif self.vel.y < 0: # Hitting head
                            self.rect.top = w.bottom
                            self.vel.y = 0
                            self.collide = "top"
                            block_collided_with = block_id
                        self.pos.y = self.rect.y

        return block_collided_with, self.collide
    

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