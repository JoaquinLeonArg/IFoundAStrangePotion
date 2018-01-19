import pygame

pygame.init()

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

COLOR_BLACK = (0, 0, 0)
COLOR_DARKGRAY = (100, 100, 100)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_DARKRED = (160, 10, 10)
COLOR_COLORKEY = (255, 0, 255)

SPRITE_PLAYER = pygame.image.load('resources/sprite_player.png')
SPRITE_ENEMY_SLIME = pygame.image.load('resources/sprite_enemy_slime.png')
SPRITE_GUI_INFO = pygame.image.load('resources/sprite_gui_info.png')

MAP_WIDTH = [60]
MAP_HEIGHT = [50]

CAMERA_WIDTH = 28
CAMERA_HEIGHT = 18

LIGHT_RADIUS = 5

FONT_PERFECTDOS = pygame.font.Font('resources/Perfect DOS VGA 437 Win.ttf', 16)

LOG_MAX_LENGTH = 8
