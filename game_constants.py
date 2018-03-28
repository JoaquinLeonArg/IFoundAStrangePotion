import pygame

pygame.init()

WINDOW_WIDTH = 1280 # NATIVE RESOLUTION, DO NOT TOUCH!
WINDOW_HEIGHT = 720

GAME_RESOLUTION_WIDTH = 1280 # WINDOW RESOLUTION
GAME_RESOLUTION_HEIGHT = 720

POPUP_WIDTH = 400
POPUP_OFFSET_X = 12
POPUP_OFFSET_Y = 10

ANIMATION_WAIT = 20

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
COLOR_CYAN = (0, 100, 255)

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

SPRITE_PLAYER = pygame.image.load('resources/player2.png')
SPRITE_ENEMY_SLIME = pygame.image.load('resources/enemy_slime.png')
SPRITE_TITLE = pygame.image.load('resources/title.png')
SPRITE_DESCRIPTIONWINDOW = pygame.image.load('resources/descriptionwindow.png')
SPRITE_ITEMSWINDOW = pygame.image.load('resources/itemswindow.png')
SPRITE_STATUS = pygame.image.load('resources/status.png')
SPRITE_OPTIONSWINDOW = pygame.image.load('resources/optionswindow.png')

MAP_WIDTH = [50, 60, 60, 50]
MAP_HEIGHT = [50, 60, 70, 60]

BORDER_THICKNESS = 2

CAMERA_WIDTH = 40
CAMERA_HEIGHT = 20

LIGHT_RADIUS = 8
MAX_HUNGER = 1000

FONT_PERFECTDOS = pygame.font.Font('resources/Perfect DOS VGA 437 Win.ttf', 16)
FONT_PERFECTDOS_SMALL = pygame.font.Font('resources/Perfect DOS VGA 437 Win.ttf', 14)
FONT_PERFECTDOS_MEDIUM = pygame.font.Font('resources/Perfect DOS VGA 437 Win.ttf', 20)
FONT_PERFECTDOS_LARGE = pygame.font.Font('resources/Perfect DOS VGA 437 Win.ttf', 32)

LOG_MAX_LENGTH = 6
LOG_MAX_LENGTH_LONG = 20
LOG_WIDTH = 400


KEY_MAPUP = 264 #8
KEY_MAPDOWN = 258 #2
KEY_MAPLEFT = 260 #4
KEY_MAPRIGHT = 262 #6

KEY_LOG = pygame.K_l
KEY_SEARCH = pygame.K_f
KEY_INVENTORY = pygame.K_i
KEY_EQUIPMENT = pygame.K_e
KEY_STATS = pygame.K_z
KEY_STATUS = pygame.K_t

KEY_USE = pygame.K_s
KEY_CANCEL = pygame.K_c

TEXT_ONMAP = [('I:', 'inventory'), ('E:', 'equipment'), ('F:', 'search'), ('T:', 'status'), ('Z', 'stats')]
TEXT_ONINVENTORY = [('S:', 'select'), ('C:', 'go back')]
TEXT_ONPOPUP = [('S:', 'select'), ('C:', 'go back')]
TEXT_ONSEARCH = [('S:', 'grab'), ('C:', 'go back')]
TEXT_ONSTATUS = [('C:', 'go back')]
TEXT_ONEQUIPMENT = [('S:', 'select'), ('C:', 'go back')]

MONSTERS_POOL = [[0], [0], [0], [0], [0], [0]]
