import pygame

pygame.init()

WINDOW_WIDTH = 1280 # NATIVE RESOLUTION, DO NOT TOUCH!
WINDOW_HEIGHT = 720

GAME_RESOLUTION_WIDTH = 1280 # WINDOW RESOLUTION
GAME_RESOLUTION_HEIGHT = 720

POPUP_WIDTH = 400
POPUP_HEIGHT = 336
POPUP_OFFSET_X = 12
POPUP_OFFSET_Y = 10
DESCWINDOW_WIDTH = 430
DESCWINDOW_HEIGHT = 200

ANIMATION_WAIT = 2

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
COLOR_ORANGE = (100, 50, 20)
COLOR_BLUE = (10, 10, 200)
COLOR_BROWN = (160, 90, 0)

COLOR_HEAL = (0, 200, 0)
COLOR_VENOM = (100, 10, 50)
COLOR_ALLY = (230, 230, 230)
COLOR_ENEMY = (160, 30, 30)
COLOR_INFO = (100, 100, 100)
COLOR_HP = (255, 0, 0)
COLOR_BORDER = (40, 40, 40)
COLOR_SHADOW = (10, 10, 10)
COLOR_HUNGER = (0, 200, 0)

COLOR_COLORKEY = (255, 0, 255)

SPRITE_PLAYER = pygame.image.load('resources/player2.png')
SPRITE_ENEMY_SLIME = pygame.image.load('resources/enemy_slime.png')
SPRITE_TITLE = pygame.image.load('resources/title.png')
SPRITE_DESCRIPTIONWINDOW = pygame.image.load('resources/graphics/window_description.png')
SPRITE_ITEMSWINDOW = pygame.image.load('resources/itemswindow.png')
SPRITE_OPTIONSWINDOW = pygame.image.load('resources/optionswindow.png')
SPRITE_STATUS = pygame.image.load('resources/graphics/ui/ui_status.png')
SPRITE_SKILLTREE = pygame.image.load('resources/graphics/skilltree.png')
SPRITE_TRADEWINDOW = pygame.image.load('resources/graphics/window_trade.png')
SPRITE_LOG = pygame.image.load('resources/graphics/ui/ui_log.png')
SPRITE_POPUP = pygame.image.load('resources/graphics/ui/ui_popup.png')
SPRITE_POINTER = pygame.image.load('resources/graphics/ui/pointer.png')

SPRITE_MARKER = pygame.image.load('resources/graphics/marker.png')

SPRITE_BACK_68X68 = pygame.image.load('resources/graphics/back_68x68.png')

SPRITE_NULL = pygame.Surface((0, 0))

MAP_WIDTH = [50, 60, 60, 50]
MAP_HEIGHT = [50, 60, 70, 60]

BORDER_THICKNESS = 2

CAMERA_WIDTH = 40
CAMERA_HEIGHT = 22

LIGHT_RADIUS = 8
MAX_HUNGER = 1000

FONT_PERFECTDOS = pygame.font.Font('resources/Perfect DOS VGA 437 Win.ttf', 16)
FONT_PERFECTDOS_SMALL = pygame.font.Font('resources/Perfect DOS VGA 437 Win.ttf', 14)
FONT_PERFECTDOS_MEDIUM = pygame.font.Font('resources/Perfect DOS VGA 437 Win.ttf', 20)
FONT_PERFECTDOS_LARGE = pygame.font.Font('resources/Perfect DOS VGA 437 Win.ttf', 32)

LOG_MAX_LENGTH = 8
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
KEY_SKILLTREE = pygame.K_k
KEY_MINIMAP = pygame.K_m

KEY_USE = pygame.K_s
KEY_CANCEL = pygame.K_c

TEXT_ONMAP = [('I:', 'inventory'), ('E:', 'equipment'), ('F:', 'search'), ('T:', 'status'), ('Z', 'stats')]
TEXT_ONINVENTORY = [('S:', 'select'), ('C:', 'go back')]
TEXT_ONPOPUP = [('S:', 'select'), ('C:', 'go back')]
TEXT_ONSEARCH = [('S:', 'grab'), ('C:', 'go back')]
TEXT_ONSTATUS = [('C:', 'go back')]
TEXT_ONEQUIPMENT = [('S:', 'select'), ('C:', 'go back')]

MONSTERS_POOL = [[0], [0], [0], [0], [0], [0]]

CHANCE_WALL1TREASURE = 0.5

BASE_STATS = {
    'HitPointsFlat': 20,
    'HitPointsMult': 100,
    'MagicPointsMult': 100,
    'MagicPointsFlat': 0,

    'HealingMult': 100,
    'MaxCarry': 10,
    'HungerFlat': 1,
    'HungerMult': 100,

    'PhyArmorFlat': 0,
    'PhyArmorMult': 100,
    'MagArmorFlat': 0,
    'MagArmorMult': 100,
    'DamageReceivedMult': 100,

    'HitPointsRegenFlat': 0,
    'HitPointsRegenMult': 100,
    'PhyAttackFlat': 0,
    'PhyAttackMult': 100,
    'PhyCritDamage': 0,
    'PhyCritChance': 0,
    'PhyBleedChance': 0,
    'PhyBleedMult': 100,
    'PhyBleedDuration': 0,
    'PhyStunChance': 0,
    'PhyStunDuration': 0,
    'PhyConfuseChance': 0,
    'PhyConfuseDuration': 0,
    'StrEffectivenessMult': 100,
    'StrDuration': 0,

    'MagicPointsRegenFlat': 0,
    'MagicPointsRegenMult': 100,
    'MagAttackFlat': 0,
    'MagAttackMult': 100,
    'MagCritDamage': 0,
    'MagCritChance': 0,
    'MagBleedChance': 0,
    'MagBleedMult': 100,
    'MagBleedDuration': 0,
    'MagStunChance': 0,
    'MagStunDuration': 0,
    'MagConfuseChance': 0,
    'MagConfuseDuration': 0,
    'EmpEffectivenessMult': 100,
    'EmpDuration': 0
}

# Surfaces positions
STATUS_IDLE_X = (CAMERA_WIDTH*32 - SPRITE_STATUS.get_width()) // 2
STATUS_IDLE_Y = CAMERA_HEIGHT*32 - SPRITE_STATUS.get_height() - 128
STATUS_HIDDEN_X = STATUS_IDLE_X
STATUS_HIDDEN_Y = CAMERA_HEIGHT*32
POPUP_IDLE_X = 220
POPUP_IDLE_Y = 0
LOG_IDLE_X = CAMERA_WIDTH * 32 - SPRITE_LOG.get_width() - 24
LOG_IDLE_Y = 24
LOG_HIDDEN_X = LOG_IDLE_X
LOG_HIDDEN_Y = 0 # TODO Fix log reappearing slowly because of negative Y position