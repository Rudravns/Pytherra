import pygame as pg
import os, sys
import math
import json

# Game Folder
from Game import utils

class Mouse():
    def __init__(self, size: int = 32):
        # FIX: Instantiate the Vector2 properly (previously was just the class reference)
        self.pos = pg.Vector2(0, 0)
        self.size = size
        self.rect = pg.Rect(0, 0, size, size)

        # Mouse
        self.DISTANCE = 4 * size # In Blocks before multiplied by size
        
        # Breaking
        self.hold_tick = 0
        self.block = None
        self.INSTANT = False

        # Blocks
        self.block_data = json.load(open("src/Jsons/block_data.json", "r"))
        self.hold = None
        self.deposit = None

        #debug
        self.debug = None
        self.debug_rect = []
        self.debug_line = ((0, 0))

    def update(self, player, world, camera: pg.Vector2, button: tuple[int, int, int], dt: float = 0):
        w, h, o, z = utils.SCALE["width"], utils.SCALE["height"], utils.SCALE["overall"], utils.SCALE["zoom"]
        
        # Prevent hold_tick explosions during lag spikes (e.g. window dragging)
        if dt > 0.05: 
            dt = 0.05 
        
        # Get raw screen pixels
        raw_x, raw_y = pg.mouse.get_pos()
        
        # Convert to logical world coordinates by un-scaling and adding camera position
        mouse_x = (raw_x / (w * z)) + camera.x
        mouse_y = (raw_y / (h * z)) + camera.y
        
        # Snap to world grid
        if not player.inv.show_inv:
            mouse_x -= mouse_x % self.size
            mouse_y -= mouse_y % self.size
        
        # Update rect
        self.rect.x = int(mouse_x)
        self.rect.y = int(mouse_y)

        # Reposition Mouse
        if not player.inv.show_inv:
            self.reposition_mouse(player, world, camera)
                    

        # Update pos
        self.pos.x = self.rect.x
        self.pos.y = self.rect.y

        #rects = world.get_nearby_rects(self.rect)
        #print(rects)

        # Mouse Inputs
        if player.inv.show_inv: 
            self.inventory(player, camera, click=button, dt=dt)
        else:
            if button[0]: # Left click
                self.left_click(player, world, dt)
            elif button[2]: # Right click
                self.right_click(player, world)

            if not button[0]:
                self.hold_tick = 0
                self.block = None

    def reposition_mouse(self, player, world, camera):
        px = player.rect.centerx - player.rect.centerx % self.size
        py = player.rect.centery - player.rect.centery % self.size
        dist_x = math.sqrt((self.rect.centerx - px)**2)
        dist_y = math.sqrt((self.rect.centery - py)**2)
        if int(dist_x) > self.DISTANCE:
            if self.rect.x > px:
                self.rect.x = px + self.DISTANCE
            else:
                self.rect.x = px - self.DISTANCE
        if int(dist_y) > self.DISTANCE:
            if self.rect.y > py:
                self.rect.y = py + self.DISTANCE
            else:
                self.rect.y = py - self.DISTANCE

        # Check line of sight
        done = False
        for i in range(10): #Try to do task 10 times, if not break
            done = self.line_of_sight(player, world, camera)
            if done: break
            
        if done:
            # Diagonal Check
            check = 0
            rect = self.rect
            self.debug_rect = []
        
            if player.rect.x >= self.rect.x:
                x = True # Left
            else:
                x = False # Right
            
            if player.rect.y >= self.rect.y:
                y = True # Bottom
            else:
                y = False # Top

            rects, _ = world.get_nearby_rects(self.rect)
            for _, rect_list in rects.items():
                for r in rect_list:
                    if y:
                        if r.y > self.rect.y and r.x == self.rect.x:
                            check += 1
                            rect = r
                            self.debug_rect.append(r)
                    else:
                        if r.y < self.rect.y and r.x == self.rect.x:
                            check += 1
                            rect = r
                            self.debug_rect.append(r)

                    if x:
                        if r.x > self.rect.x and r.y == self.rect.y:
                            check += 1
                            self.debug_rect.append(r)
                    else:
                        if r.x < self.rect.x and r.y == self.rect.y:
                            check += 1
                            self.debug_rect.append(r)
            
            if check == 2: self.rect = rect

    def line_of_sight(self, player, world, camera):
        p_pos = (player.rect.centerx, player.rect.y)

        if p_pos[0] >= self.rect.centerx:
            if p_pos[0] >= self.rect.right:
                x = self.rect.right + 1
            else:
                x = self.rect.centerx
        else:
            if p_pos[0] <= self.rect.left:
                x = self.rect.left - 1
            else:
                x = self.rect.centerx
        
        if p_pos[1] >= self.rect.centery:
            if p_pos[1] >= self.rect.bottom:
                y = self.rect.bottom + 1
            else:
                y = self.rect.centery
        else:
            if p_pos[1] <= self.rect.top:
                y = self.rect.top - 1
            else:
                y = self.rect.centery

        m_pos = (x, y)
        self.debug_line = m_pos
        line = (p_pos, m_pos)

        rects, _ = world.get_nearby_rects(self.rect, 2)
        for _, rect_list in rects.items():
            for r in rect_list:
                if r.clipline(line) and not r == self.rect:
                    self.rect = r
                    return False
        
        return True

    def left_click(self, player, world, dt):
        rects, raw = world.get_nearby_rects(self.rect)
        for block_id, rect_list in rects.items():
            for w in rect_list:
                if self.rect.colliderect(w):
                    # Check if block is breakable
                    if self.block_data[str(block_id)]["breakable"]:
                        multiplier = self.determine_multiplier(self.block_data[str(block_id)]["tool"], player.inv.hotbar[player.inv.hold])
                        if self.block == block_id:
                            if self.INSTANT: 
                                self.hold_tick = self.block_data[str(block_id)]["time"]
                            else: 
                                self.hold_tick += multiplier + dt

                            if self.hold_tick >= self.block_data[str(block_id)]["time"]:
                                self.remove_block(raw, player, world, block_id)
                                self.hold_tick = 0
                        else:
                            self.block = block_id
                            self.hold_tick = 0
                    return

    def determine_multiplier(self, requirement, hold, give_type: bool=False):
        if hold == None:
            return 1.0

        if hold[0] >= 100:
            new_hold = str(hold[0])
            tool = int(new_hold[1])
            material = int(new_hold[2])

            if tool == 0:
                tool = "pickaxe"
                mult = 6
            elif tool == 1:
                tool = "sword"
                mult = 0
            elif tool == 2:
                tool = "axe"
                mult = 3
            else:
                tool = "shovel"
                mult = 1

            if tool == requirement:
                mult *= material
                self.debug = mult
                if material == 0:
                    material = "wood"
                elif material == 1:
                    material = "stone"
                elif material == 2:
                    material = "iron"
                else:
                    material = "diamond"
                
                if give_type:
                    return (tool, material)
                else:
                    return float(1 + mult)
            else:
                if give_type:
                    return (tool, material)
                else:
                    return 1.0
        else:
            if give_type:
                return (None, None)
            else:
                return 1.0
    
    def remove_block(self, raw, player, world, id):
        pos = pg.Vector2(self.pos.x // self.size, self.pos.y // self.size)
        for block in raw[id]:
            if block[0] == pos.x and block[1] == pos.y:
                chunk, x = world.get_chunk_from_pos(int(self.pos.x))
                level = world.get_chunk(chunk)[x % self.size]
                for y in level:
                    if level[y] == id or (level[y] == 6 and id == 1):
                        if pos.y == y:
                            if not self.block_data[str(id)]["tool"] == None and not self.block_data[str(id)]["requirement"] == None:
                                tool = self.determine_multiplier(self.block_data[str(id)]["tool"], player.inv.hotbar[player.hold], give_type=True)
                                if tool[0] == self.block_data[str(id)]["tool"] and tool[1] == self.block_data[str(id)]["requirement"]: #pyright: ignore
                                    player.inv.update_inv(self.block_data, id=self.block_data[str(id)]["drop"])
                            else:
                                player.inv.update_inv(self.block_data, id=self.block_data[str(id)]["drop"])
                            
                            # Remember to modify this when silk touch support comes
                            del world.chunks[chunk][x % self.size][y]
                            break

    def right_click(self, player, world):
        rects, _ = world.get_nearby_rects(self.rect)
        if len(rects) > 0:
            # Checks if you are colliding with something
            cont = False
            for _, rect_list in rects.items():
                for w in rect_list:
                    # Checks if you are colliding with the player
                    if self.rect.colliderect(player.rect) or self.rect.center == w.center: return

                    x = abs(self.rect.x - w.x)
                    y = abs(self.rect.y - w.y)
                    dist = int(math.floor(math.sqrt((self.rect.x - w.x)**2 + (self.rect.y - w.y)**2)))
                    # Check if you are allowed to place a block
                    if dist == 32: cont = True

            if cont:
                chunk = world.get_chunk_from_pos(self.pos.x)
                x = chunk[1] % self.size
                if not player.inv.inventory[5][player.inv.hold] == None:
                    world.chunks[chunk[0]][x][self.pos.y // self.size] = player.inv.inventory[5][player.inv.hold][0]
                    player.inv.inventory[5][player.inv.hold][1] -= 1
                    if player.inv.inventory[5][player.inv.hold][1] == 0:
                        player.inv.inventory[5][player.inv.hold] = None

    def draw(self, screen: pg.Surface, player, world, camera: pg.Vector2):     
        w, h, o, z = utils.SCALE["width"], utils.SCALE["height"], utils.SCALE["overall"], utils.SCALE["zoom"]

        rx = (self.rect.x - camera.x) * (w * z)
        ry = (self.rect.y - camera.y) * (h * z)
        rw = self.size * (w * z)
        rh = self.size * (h * z)
        
        # Use floor/ceil to prevent floating point seams
        draw_rect = pg.Rect(math.floor(rx), math.floor(ry), math.ceil(rw), math.ceil(rh))
        
        # Draw mouse cursor, scaling the thickness slightly if scaled up heavily
        line_thickness = max(1, int(1 * (w * z)))
        if player.inv.show_inv: 
            if not self.hold == None:
                draw_rect.w = math.floor(30 * o)
                draw_rect.h = draw_rect.w
                if self.hold[0] < 100:
                    world.draw_rect(screen, draw_rect, self.hold[0])
                else:
                    player.inv.draw_rect(screen, draw_rect, self.hold[0])

                if self.hold[1] > 1:
                    utils.draw_text(screen, f"x{self.hold[1]}", 20, (255, 255, 255), (math.floor(draw_rect.x + 15), math.floor(draw_rect.y + 15)))
        else:
            pg.draw.rect(screen, (0, 0, 0), draw_rect, line_thickness)

    def inventory(self, player, camera, click: tuple, scroll: int=0, dt: float=0.0):
        w, h, o, z = utils.SCALE["width"], utils.SCALE["height"], utils.SCALE["overall"], utils.SCALE["zoom"]

        if scroll == 0: # Scroll is not finished (yet)... or might just get scrapped
            rx = (self.rect.x - camera.x) * (w * z)
            ry = (self.rect.y - camera.y) * (h * z)
            curser_rect = pg.Rect(math.floor(rx), math.floor(ry), 1, 1)

            for row in player.inv.inv_rects:
                for rect in row:
                    if curser_rect.colliderect(rect):
                        a = player.inv.inv_rects.index(row)
                        b = player.inv.inv_rects[a].index(rect)
                        if click[0] and self.hold_tick == 0: # Left Click
                            self.hold = player.inv.update_inv(self.block_data, hold=self.hold, location=[a, b])
                        elif click[2]: # Right Click
                            if self.hold == None:
                                self.hold = player.inv.update_inv(self.block_data, hold=self.hold, location=[a, b])
                                if not self.hold == None:
                                    self.deposit = [self.hold[0], math.ceil(self.hold[1] / 2)]
                                    self.hold[1] -= self.deposit[1]
                                    if self.hold[1] == 0:
                                        self.hold = None
                                    
                                    player.inv.update_inv(self.block_data, hold=self.deposit, location=[a, b])
                            else:
                                if math.floor(self.hold_tick) % 60 == 0:
                                    if player.inv.inventory[a][b] == None:
                                        self.deposit = [self.hold[0], 1]
                                        self.hold[1] -= self.deposit[1]
                                        if self.hold[1] < 1:
                                            self.hold = None

                                        player.inv.update_inv(self.block_data, hold=self.deposit, location=[a, b])

                                    elif self.hold[0] == player.inv.inventory[a][b][0]:
                                        self.deposit = [self.hold[0], 1]
                                        self.hold[1] -= self.deposit[1]
                                        if self.hold[1] < 1:
                                            self.hold = None
                                    
                                        player.inv.update_inv(self.block_data, hold=self.deposit, location=[a, b])

            if click[0] or click[2]:
                self.hold_tick += 1 + dt
            else:
                self.hold_tick = 0