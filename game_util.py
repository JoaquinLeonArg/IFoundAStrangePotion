import math
import pygame
import game_constants
import libtcodpy

# UTIL
def clamp(value, minv, maxv):
    return int(max(minv, min(value, maxv)))
def distance(object1, object2):
    return math.sqrt((object1.x - object2.x)**2 + (object1.y - object2.y)**2)
def simpledistance(coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
def isinscreen(x, y):
    return (x > GAME.camera.x) and (x < (GAME.camera.x + game_constants.CAMERA_WIDTH*32)) and (y > GAME.camera.y) and (y < (GAME.camera.y + game_constants.CAMERA_HEIGHT*32))
def rectangle_intersects(r1, r2):
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    return not (x1 + w1 + 1 < x2 or x1 > x2 + w2 + 1 or y1 + h1 + 1 < y2 or y1 > y2 + h2 + 1)
def sign(value):
    if value < 0:
        return -1
    if value > 0:
        return 1
    return 0
def add_dicts(dict_base, dict_add):
    new_dict = {}
    for key in dict_base:
        if key in dict_add:
            new_dict[key] = dict_add[key]
        else:
            new_dict[key] = dict_base[key]
    return new_dict

# TEXT
def draw_text(surface, text, x, y, font, text_color):
    rect1 = surface.blit(font.render(text, False, game_constants.COLOR_SHADOW), (x+1, y+1))
    rect2 = surface.blit(font.render(text, False, text_color), (x, y))
    return rect1, rect2
def draw_text_bg(surface, text, x, y, font, text_color, bg_color):
    text_surface = font.render(text, False, text_color)
    rect = pygame.draw.rect(surface, bg_color, pygame.Rect(x, y, text_surface.get_width(), text_surface.get_height()))
    surface.blit(font.render(text, False, game_constants.COLOR_SHADOW), (x+1, y+1))
    surface.blit(font.render(text, False, text_color), (x, y))
    return rect

# OTHER
def map_light_update(light_map):
    libtcodpy.map_compute_fov(light_map, GAME.player.x, GAME.player.y, game_constants.LIGHT_RADIUS, True, libtcodpy.FOV_DIAMOND)