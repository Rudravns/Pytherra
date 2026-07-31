import pygame as pg
import json
import math

# Game Folder
from Game import utils
from Game.texture import TOOL_TEXTURE_CACHE, init_tool_textures, resize_tools

class Inventory():
    def __init__(self):
        # Inventory stuff
        self.inv_data = json.load(open("src/Jsons/inventory.json", "r"))
        self.inventory = self.setup_inventory()
        self.inv_rects = [[], [], [], [], [], []]
        self.hotbar = self.inventory[5]
        self.hold = 0 # Location of hotbar

        #Crafting
        self.craft = [[None, None, None], [None, None, None], [None, None, None]]
        self.craft_rects = [[], [], []]

        self.show_inv = False

        self.scroll = 0
        
        # RENDERING
        self.COLORS = {
            0: [(50, 50, 50), (100, 100, 100), (150, 150, 150), (200, 200, 200)], # Pickaxe
            1: [(50, 0, 0), (100, 0, 0), (150, 0, 0), (200, 0, 0)], # Sword
            2: [(0, 50, 0), (0, 100, 0), (0, 150, 0), (0, 200, 0)], # Axe
            3: [(0, 0, 50), (0, 0, 100), (0, 0, 150), (0, 0, 200)], # Shovel
            4: (100, 120, 80), # Stick
            "Sprite_sheet": None
        }

        init_tool_textures()
        resize_tools(16, 16)

    def setup_inventory(self):
        inv = []
        for y in range(6):
            row = []
            for x in range(9):
                row.append(self.inv_data[str(y)][x])
            inv.append(row)
        return inv
    
    def scroll_inv(self, scroll):
        self.scroll += abs(scroll)
        if self.scroll / 4 > 1:
            self.scroll = 0
            self.hold += int(scroll / abs(scroll))
        
        if self.hold > 8:
            self.hold = 0
        elif self.hold < 0:
            self.hold = 8

    def update_inv(self, block_data: dict, loc: list, id: int = 0, hold: list[int, int] = None, location: tuple[int, int] = None): #pyright: ignore
        # Check if using mouse in inventory
        if not location == None:
            prev_item = loc[location[0]][location[1]]
            loc[location[0]][location[1]] = hold
            if not prev_item == None and not hold == None:
                if prev_item[0] == hold[0]:
                    if prev_item[0] < 100 or hold[0] < 100:
                        if prev_item[1] > 0 and hold[1] > 0:
                            loc[location[0]][location[1]][1] += prev_item[1]
                            if loc[location[0]][location[1]][1] > block_data[str(id)]["max"]:
                                num = loc[location[0]][location[1]][1] - block_data[str(id)]["max"]
                                loc[location[0]][location[1]][1] = block_data[str(id)]["max"]
                                return [hold[0], num]
                        return
                    else:
                        return prev_item
            return prev_item

        # Check inventory for same id
        for y in range(5, -1, -1): # Hotbar --> top of inventory
            for x in range(9): # Left to right
                slot = loc[y][x]
                if not slot == None:
                    if id < 100:
                        if slot[0] == id and slot[1] < block_data[str(id)]["max"]:
                            slot[1] += 1
                            loc[y][x] = slot
                            return
                    else:
                        if slot[0] == id and slot[1] < 1:
                            slot[1] += 1
                            loc[y][x] = slot
                            return
        
        # If not found, find an available slot
        for y in range(5, -1, -1): # Hotbar --> top of inventory
            for x in range(9): # Left to right
                slot = loc[y][x]
                if slot == None:
                    slot = [id, 1]
                    loc[y][x] = slot
                    return

    def draw_inventory(self, screen, world):
        self.inv_rects = [[], [], [], [], [], []]
        self.craft_rects = [[], [], []]
        o = utils.SCALE["overall"]

        #Hotbar
        bar_size = 60 * o
        gap = 6 * o
        x = (screen.get_width() // 2 - bar_size // 2) - (bar_size + gap) * 4
        y = screen.get_height() - bar_size * 2

        # Background
        size = 16 * o
        rx1 = x - size
        ry1 = y - size
        rx2 = bar_size * 9 + gap * 8 + size * 2
        ry2 = bar_size + size * 2
        back_rect = pg.Rect(math.floor(rx1), math.floor(ry1), math.floor(rx2), math.floor(ry2))
        # draw alpha
        a_screen = pg.Surface((screen.get_width(), screen.get_height()), pg.SRCALPHA)
        pg.draw.rect(a_screen, (0, 0, 0, 128), back_rect)
        pg.draw.rect(a_screen, (0, 0, 0, 255), back_rect, math.floor(2 * o))

        screen.blit(a_screen, (0, 0))

        # Items
        for i in range(9):
            new_x = x + (bar_size + gap) * i
            if i == self.hold:
                color = (255, 255, 255)
            else:
                color = (0, 0, 0)
            
            draw_rect = pg.Rect(math.floor(new_x), math.floor(y), math.floor(bar_size), math.floor(bar_size))
            if self.show_inv: self.inv_rects[5].append(draw_rect)

            pg.draw.rect(screen, color, draw_rect, math.floor(2 * o))

            if not self.inventory[5][i] == None:
                self.draw_item(screen, world, draw_rect, bar_size, self.inventory[5][i])



        # Rest of Inventory
        if self.show_inv:
            y -= (bar_size + gap) * 5 + 60
            
            # Draw Background
            rx1 = x - size
            ry1 = y - size
            rx2 = bar_size * 9 + gap * 8 + size * 2
            ry2 = bar_size * 5 + gap * 4 + size * 2
            back_rect = pg.Rect(math.floor(rx1), math.floor(ry1), math.floor(rx2), math.floor(ry2))
            pg.draw.rect(screen, (200, 200, 200), back_rect)

            # Draw Items
            for i in range(5):
                new_y = y + (bar_size + gap) * i
                for n in range(9):
                    new_x = x + (bar_size + gap) * n

                    draw_rect = pg.Rect(math.floor(new_x), math.floor(new_y), math.floor(bar_size), math.floor(bar_size))
                    self.inv_rects[i].append(draw_rect)

                    pg.draw.rect(screen, (160, 160, 160), draw_rect)
                    pg.draw.rect(screen, (0, 0, 0), draw_rect, math.floor(2 * o))

                    if not self.inventory[i][n] == None:
                        self.draw_item(screen, world, draw_rect, bar_size, self.inventory[i][n])     



            # Draw Crafting
            x += (bar_size + gap) * 4
            y -= (bar_size + gap) * 3 + size

            # Draw Background
            rx1 = x - size
            ry1 = y - size
            rx2 = bar_size * 5 + gap * 4 + size * 2
            ry2 = bar_size * 3 + gap * 2 + size * 2

            draw_rect = pg.Rect(math.floor(rx1), math.floor(ry1), math.floor(rx2), math.floor(ry2))
            pg.draw.rect(screen, (200, 200, 200), draw_rect)

            # Draw Items
            for i in range(3):
                new_y = y + (bar_size + gap) * i
                for n in range(3):
                    new_x = x + (bar_size + gap) * n

                    draw_rect = pg.Rect(math.floor(new_x), math.floor(new_y), math.floor(bar_size), math.floor(bar_size))
                    self.craft_rects[i].append(draw_rect)

                    pg.draw.rect(screen, (160, 160, 160), draw_rect)
                    pg.draw.rect(screen, (0, 0, 0), draw_rect, math.floor(2 * o))

                    if not self.craft[i][n] == None:
                        self.draw_item(screen, world, draw_rect, bar_size, self.craft[i][n])     

    def draw_item(self, screen, world, draw_rect, bar_size, block):
        rect = pg.Rect(0, 0, math.floor(bar_size / 2), math.floor(bar_size / 2))
        rect.center = draw_rect.center
        if block[0] < 100:
            world.draw_rect(screen, rect, block[0])
        else:
            self.draw_rect(screen, rect, block[0])
        
        size = 20
        text_pos = (math.floor(rect.x + bar_size / 4), math.floor(rect.y + bar_size / 4))
        if block[1] > 1: 
            utils.draw_text(screen, f"x{block[1]}", size, (255, 255, 255), (text_pos[0], text_pos[1]), scale_pos = False)

    def draw_rect(self, screen, rect, id):
        new_id = str(id)
        tool = int(new_id[1])
        material = int(new_id[2])

        try:
            text:pg.Surface = TOOL_TEXTURE_CACHE[tool][material]
            screen.blit(pg.transform.scale(text,(rect.w, rect.h)).convert_alpha(), rect)
        except (TypeError, KeyError):
            pg.draw.rect(screen, self.COLORS[tool][material], rect) # Fallback if texture asset doesn't exist    