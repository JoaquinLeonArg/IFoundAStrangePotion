import pygame

pygame.init()

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

POPUP_WIDTH = 400
POPUP_OFFSET_X = 4
POPUP_OFFSET_Y = 4

COLOR_BLACK = (0, 0, 0)
COLOR_LIGHTGRAY = (200, 200, 200)
COLOR_GRAY = (150, 150, 150)
COLOR_DARKGRAY = (50, 50, 50)
COLOR_DARKESTGRAY = (10, 10, 10)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_DARKRED = (160, 10, 10)
COLOR_COLORKEY = (255, 0, 255)

SPRITE_PLAYER = pygame.image.load('resources/sprite_player.png')
SPRITE_ENEMY_SLIME = pygame.image.load('resources/sprite_enemy_slime.png')
SPRITE_GUI_INFO = pygame.image.load('resources/sprite_gui_info.png')

MAP_WIDTH = [60]
MAP_HEIGHT = [50]

CAMERA_WIDTH = 40
CAMERA_HEIGHT = 20

LIGHT_RADIUS = 5

FONT_PERFECTDOS = pygame.font.Font('resources/Perfect DOS VGA 437 Win.ttf', 16)

LOG_MAX_LENGTH = 8
LOG_MAX_LENGTH_LONG = 20
LOG_WIDTH = 400

KEY_LOG = pygame.K_l
KEY_SEARCH = pygame.K_s
KEY_GRAB = pygame.K_g
KEY_INVENTORY = pygame.K_i
KEY_THROW = pygame.K_t
KEY_USE = pygame.K_u
KEY_EQUIPMENT = pygame.K_e
KEY_EQUIP = pygame.K_u
KEY_STATS = pygame.K_z
