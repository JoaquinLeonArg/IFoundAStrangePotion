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
COLOR_LIGHTRED = (255, 100, 100)
COLOR_DARKRED = (160, 10, 10)
COLOR_GREEN = (0, 150, 0)
COLOR_YELLOW = (210, 210, 0)

COLOR_HEAL = (0, 200, 0)
COLOR_VENOM = (100, 10, 50)
COLOR_ALLY = (230, 230, 230)
COLOR_ENEMY = (160, 30, 30)
COLOR_INFO = (100, 100, 100)
COLOR_HP = (255, 0, 0)
COLOR_BORDER = (40, 40, 40)
COLOR_SHADOW = (20, 20, 20)
COLOR_HUNGER = (0, 200, 0)

COLOR_COLORKEY = (255, 0, 255)

EFFECTS_MAXTIME = 60
DAMAGEPOPUP_MAXTIME = 50

SPRITE_PLAYER = pygame.image.load('resources/player.png')
SPRITE_ENEMY_SLIME = pygame.image.load('resources/enemy_slime.png')
SPRITE_TITLE = pygame.image.load('resources/title.png')

MAP_WIDTH = [60]
MAP_HEIGHT = [50]

BORDER_THICKNESS = 2

CAMERA_WIDTH = 40
CAMERA_HEIGHT = 20

LIGHT_RADIUS = 8

FONT_PERFECTDOS = pygame.font.Font('resources/Perfect DOS VGA 437 Win.ttf', 16)
FONT_PERFECTDOS_LARGE = pygame.font.Font('resources/Perfect DOS VGA 437 Win.ttf', 32)

LOG_MAX_LENGTH = 4
LOG_MAX_LENGTH_LONG = 20
LOG_WIDTH = 400

KEY_LOG = pygame.K_l
KEY_SEARCH = pygame.K_f
KEY_INVENTORY = pygame.K_i
KEY_EQUIPMENT = pygame.K_e
KEY_STATS = pygame.K_z
KEY_STATUS = pygame.K_t

KEY_USE = pygame.K_s
KEY_CANCEL = pygame.K_c

TEXT_ONMAP = [('Arrows:', 'move'), ('I:', 'inventory'), ('F:', 'search'), ('E:', 'equipment'), ('Z:', 'stats'), ('L:', 'Short/Long log')]
TEXT_ONINVENTORY = [('Arrows:', 'move cursor'), ('U:', 'use/equip'), ('C:', 'cancel')]
TEXT_ONPOPUP = [('Arrows:', 'move cursor'), ('S:', 'select')]
TEXT_ONSEARCH = [('Arrows:', 'move cursor'), ('S:', 'grab'), ('C:', 'cancel')]
TEXT_ONSTATUS = [('Arrows:', 'move cursor'), ('C:', 'cancel')]
