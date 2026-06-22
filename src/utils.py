import pygame
import os, sys

cache = {} #only text
SCALE = { #W/H ratio
            "width": 1.0,
            "height": 1.0,
            "overall": 1.0
        }
RESIZED = False

def create_text(text, font_size, color):
    key = (text, font_size, color)
    if key in cache:
        return cache[key]
    
    font = pygame.font.SysFont(None, int(font_size))
    rendered_text = font.render(text, True, color)
    cache[key] = rendered_text
    return rendered_text

def draw_text(screen: pygame.Surface, text: str, font_size: int, color: tuple, pos: tuple):
    rendered_text = create_text(text, scale_font_size(font_size, SCALE), color)
    screen.blit(rendered_text, (pos[0] * SCALE["width"], pos[1] * SCALE["height"]))

def scale_font_size(base_size, scale):
    return int(min(scale["width"], scale["height"]) * base_size)


