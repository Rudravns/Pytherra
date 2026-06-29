import pygame
import os, sys

cache = {} #only text
SCALE = { #W/H ratio
            "width": 1.0,
            "height": 1.0,
            "overall": 1.0
        }
RESIZED = False

# TEXT

def create_text(text, font_size, color):
    key = (text, font_size, color)
    check = check_in_cache(key)
    if check == key: return cache[key]
    
    font = pygame.font.SysFont(None, int(font_size))
    rendered_text = font.render(text, True, color)
    cache[key] = rendered_text
    return rendered_text

def draw_text(screen: pygame.Surface, text: str, font_size: int, color: tuple, pos: tuple):
    rendered_text = create_text(text, scale_font_size(font_size, SCALE), color)
    screen.blit(rendered_text, (pos[0] * SCALE["width"], pos[1] * SCALE["height"]))

def check_in_cache(key): # DO NOT CALL THIS IN OTHER SCRIPTS, IT WILL ERROR
    # Check to see if the script is being called in utils.py
    caller_frame = sys._getframe(1)
    calling_script = caller_frame.f_code.co_filename
    script = find_location(calling_script, "utils.py")
    
    if script == None:
        raise SystemExit("This function can only be called in utils.py")
    
    # Actual check in cache
    return key if key in cache else None

def remove_from_cache(text: str, font_size: int, color: tuple):
    key = (text, font_size, color)
    check = check_in_cache(key)
    if check == key: del cache[key]


def scale_font_size(base_size, scale):
    return int(min(scale["width"], scale["height"]) * base_size)



# FILES

def find_location(string: str, goal: str):
    origin_text = string
    concact_text = origin_text
    text = ""

    i = 0

    for l in origin_text:
        i += 1

        if l == "/" or l == "\\":
            if text == goal:
                return text + concact_text
            text = ""
        else:
            text = text + l
        
        concact_text.removeprefix(l)
    
    if text == goal:
        return text + concact_text
    
    return None

    

if __name__ == "__main__":
    pygame.init()
    create_text("Hello World", 16, (255, 255, 255))
    remove_from_cache("Hello World", 16, (255, 255, 255))