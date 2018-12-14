from pyglet import *

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
ANIMATION_RATE = 5

ANIMATIONS = {
    'speed': 0.1,
    'move_speed': 5,
    'player_delay': 5
}

COLORS_BASE = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),

    'green1': (0, 200, 0),
    'green2': (0, 160, 0),
    'green3': (0, 120, 0),
    'green4': (0, 80, 0),
    'green5': (0, 30, 0),

    'blue1': (0, 0, 200),
    'blue2': (0, 0, 160),
    'blue3': (0, 0, 120),
    'blue4': (0, 0, 80),
    'blue5': (0, 0, 30),

    'lightblue': (100, 100, 200)
}
COLORS = {
    'health_bar': COLORS_BASE['green2'],
    'magic_bar': COLORS_BASE['lightblue']
}

TILE_SPRITES = {
    'cave_dirt': resource.image('resources/graphics/tiles/floor_dirt.png')
}

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
COLOR_MENUHIGHLIGHT = (100, 100, 200)
COLOR_POSITIVESTAT = (100, 200, 100)
COLOR_NEGATIVESTAT = (200, 100, 100)
COLOR_COLORKEY = (255, 0, 255)

SPRITES = {
    'player': resource.image('resources/graphics/entities/player.png'),
    'door_closed': resource.image('resources/graphics/entities/door_closed.png'),
    'door_open': resource.image('resources/graphics/entities/door_open.png'),
    'tall_grass': resource.image('resources/graphics/entities/tall_grass.png'),
    'tall_grass_destroyed': resource.image('resources/graphics/entities/tall_grass_destroyed.png'),
    'slime': resource.image('resources/graphics/entities/tall_grass_destroyed.png')
}
UI_SPRITES = {
    'status_window': resource.image('resources/graphics/ui/ui_status.png')
}

SPRITE_PLAYER = resource.image('resources/player2.png')
SPRITE_ENEMY_SLIME = resource.image('resources/enemy_slime.png')
SPRITE_TITLE = resource.image('resources/title.png')
SPRITE_INVENTORYWINDOW = resource.image('resources/graphics/ui/ui_inventory.png')
SPRITE_EQUIPMENTWINDOW = resource.image('resources/graphics/ui/ui_equipment.png')
SPRITE_OPTIONSWINDOW = resource.image('resources/graphics/ui/ui_options.png')
SPRITE_STATUS = resource.image('resources/graphics/ui/ui_status.png')
SPRITE_SKILLTREE = resource.image('resources/graphics/skilltree.png')
SPRITE_TRADEWINDOW = resource.image('resources/graphics/window_trade.png')
SPRITE_LOG = resource.image('resources/graphics/ui/ui_log.png')
SPRITE_POPUP = resource.image('resources/graphics/ui/ui_popup.png')
SPRITE_ITEMLIST = resource.image('resources/graphics/ui/ui_itemlist.png')
SPRITE_INVENTORYDESCRIPTION = resource.image('resources/graphics/ui/ui_inventorydescription.png')
SPRITE_MARKER = resource.image('resources/graphics/marker.png')
SPRITE_BACK_68X68 = resource.image('resources/graphics/back_68x68.png')

MAP_WIDTH = [50, 60, 60, 50]
MAP_HEIGHT = [50, 60, 70, 60]

BORDER_THICKNESS = 2

CAMERA_WIDTH = 40
CAMERA_HEIGHT = 22

LIGHT_RADIUS = 8
MAX_HUNGER = 1000

LOG_MAX_LENGTH = 8
LOG_MAX_LENGTH_LONG = 20
LOG_WIDTH = 400

KEY_MAPUP = 264 #8
KEY_MAPDOWN = 258 #2
KEY_MAPLEFT = 260 #4
KEY_MAPRIGHT = 262 #6

KEY_LOG = window.key.L
KEY_SEARCH = window.key.F
KEY_INVENTORY = window.key.I
KEY_EQUIPMENT = window.key.E
KEY_STATS = window.key.Z
KEY_STATUS = window.key.T
KEY_SKILLTREE = window.key.K
KEY_MINIMAP = window.key.M
KEY_PASSTURN = window.key.W
KEY_USE = window.key.S
KEY_CANCEL = window.key.C

MONSTERS_POOL = [[0], [0], [0], [0], [0], [0]]

CHANCE_WALL1TREASURE = 0.5

BASE_STATS = {
    'HitPointsFlat': 10,
    'HitPointsMult': 100,
    'MagicPointsMult': 100,
    'MagicPointsFlat': 1,

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
UI_POSITIONS = {
    'status': {
        'idle_x': WINDOW_WIDTH / 2 - UI_SPRITES['status_window'].width / 2,
        'idle_y': UI_SPRITES['status_window'].height - 60,
        'hidden_y': - UI_SPRITES['status_window'].height
    },
    'popup': {
        'idle_x': 220,
        'idle_y': 200
    },
    'log': {
        'idle_x': 100,
        'idle_y': 100
    }
}