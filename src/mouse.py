import pygame as pg
import os, sys
import math
import utils
import json

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
        if not player.show_inv:
            mouse_x -= mouse_x % self.size
            mouse_y -= mouse_y % self.size
        
        # Update rect
        self.rect.x = int(mouse_x)
        self.rect.y = int(mouse_y)

        # Reposition Mouse
        if not player.show_inv:
            self.reposition_mouse(player, world, camera)
                    

        # Update pos
        self.pos.x = self.rect.x
        self.pos.y = self.rect.y

        #rects = world.get_nearby_rects(self.rect)
        #print(rects)

        # Mouse Inputs
        if player.show_inv: 
            self.inventory(player, camera, click=button)
        else:
            if button[0]: # Left click
                self.left_click(player, world, dt)
            elif button[2]: # Right click
                self.right_click(player, world)

        if not button[0]:
            #self.debug = "Not Button"
            self.hold_tick = 0
            self.block = None

    def reposition_mouse(self, player, world, camera):
        px = player.rect.centerx - player.rect.centerx % self.size
        py = player.rect.centery - player.rect.centery % self.size
        dist_x = math.sqrt((self.rect.centerx - px)**2)
        dist_y = math.sqrt((self.rect.centery - py)**2)
        #self.debug = (dist_x, dist_y)
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
            self.debug = check

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
                        multiplier = self.determine_multiplier(self.block_data[str(block_id)]["tool"])
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

    def determine_multiplier(self, tool) -> float:
        # Once player inventory is implemented, finish this function
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
                            # Remember to modify this when silk touch support comes
                            player.update_inv(self.block_data, id=self.block_data[str(id)]["drop"])
                            del world.chunks[chunk][x % self.size][y]
                            break
                    """
                    else:
                        debug = []
                        for n in world.chunks[0].keys():
                            debug.append(world.get_surface_y(n)[0])
                        self.debug = debug
                    """

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
                if not player.inventory[5][player.hold] == None:
                    world.chunks[chunk[0]][x][self.pos.y // self.size] = player.inventory[5][player.hold][0]
                    player.inventory[5][player.hold][1] -= 1
                    if player.inventory[5][player.hold][1] == 0:
                        player.inventory[5][player.hold] = None

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
        if player.show_inv: 
            if not self.hold == None:
                draw_rect.w = math.floor(30 * o)
                draw_rect.h = draw_rect.w
                world.draw_rect(screen, draw_rect, self.hold[0])
                utils.draw_text(screen, f"x{self.hold[1]}", 20, (255, 255, 255), (math.floor(draw_rect.x + 15), math.floor(draw_rect.y + 15)))
        else:
            pg.draw.rect(screen, (0, 0, 0), draw_rect, line_thickness)

    def inventory(self, player, camera, click: tuple, scroll: int=0):
        w, h, o, z = utils.SCALE["width"], utils.SCALE["height"], utils.SCALE["overall"], utils.SCALE["zoom"]

        if scroll == 0:
            rx = (self.rect.x - camera.x) * (w * z)
            ry = (self.rect.y - camera.y) * (h * z)
            curser_rect = pg.Rect(math.floor(rx), math.floor(ry), 1, 1)
            
            for row in player.inv_rects:
                for rect in row:
                    if curser_rect.colliderect(rect):
                        a = player.inv_rects.index(row)
                        b = player.inv_rects[a].index(rect)
                        if self.hold_tick == 0 and (click[0] or click[2]):
                            if click[0]:
                                self.hold = player.update_inv(self.block_data, hold=self.hold, location=[a, b])
                            elif click[2]:
                                cont = True
                                if self.hold == None:
                                    self.hold = player.update_inv(self.block_data, hold=self.hold, location=[a, b])
                                elif player.inv_rects[a][b] == None:
                                    pass
                                else:
                                    cont = self.hold[0] == player.inv_rects[a][b][0]
                                
                                if not self.hold == None and cont:
                                    self.deposit = [self.hold[0], math.ceil(self.hold[1] / 2)]
                                    self.hold[1] -= self.deposit[1]
                                    if self.hold[1] == 0:
                                        self.hold = None
                                    
                                    if self.deposit[1] > 0:
                                        player.update_inv(self.block_data, hold=self.deposit, location=[a, b])

                        else:
                            pass

                        if click[0] or click[2]:
                            self.hold_tick += 1
                        else:
                            self.hold_tick = 0