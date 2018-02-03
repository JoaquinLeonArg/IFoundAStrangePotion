# IMPORT
import pygame
import libtcodpy
import random
import math
import sys

import constants

# MAIN CLASSES
class Game:
    def __init__(self):
        self.level = 0
        self.map = None
        self.light_map = None
        self.surface_map = pygame.Surface((constants.MAP_WIDTH[self.level]*32, constants.MAP_HEIGHT[self.level]*32))
        self.surface_log = pygame.Surface((constants.CAMERA_WIDTH*32, constants.WINDOW_HEIGHT))
        self.surface_status = pygame.Surface((constants.WINDOW_WIDTH - constants.LOG_WIDTH, constants.WINDOW_HEIGHT - constants.CAMERA_HEIGHT*32))
        self.tiles = Spritesheet('resources/tiles.png')
        self.consumables = Spritesheet('resources/consumables.png')
        self.log = []
        self.long_log = False
        self.player = Player(30, 25, constants.SPRITE_PLAYER)
        self.creatures = [self.player]
        self.camera = Camera(0, 0, constants.MAP_WIDTH[self.level], constants.MAP_HEIGHT[self.level], constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT, self.player)
        self.windows = []
        self.popup_lock = False
        self.items = []
        self.entities = []
        self.controlsText = constants.TEXT_ONMAP
    def initGame(self):
        self.creatures += [Slime(23, 25) for i in range(5)]
        self.player.inventory += [Bomb(0, 0) for i in range(8)]
    def addLogMessage(self, message, color):
        self.log.insert(0, (message, color))
    def creaturesExecuteTurn(self):
        for creature in self.creatures:
            creature.execute_action()
    def entitiesExecuteTurn(self):
        for entity in self.entities:
            entity.execute_action()
    def updateCamera(self):
        self.camera.update()
    def generateMap(self):
        self.map = map_init_walk(constants.MAP_WIDTH[self.level], constants.MAP_HEIGHT[self.level], 0.5)
    def initLight(self):
        self.light_map = map_light_init(self.map)
        map_light_update(self.light_map)
    def placeFree(self, x, y):
        for obj in self.creatures:
            if (obj.x == x and obj.y == y):
                return False
        return True

class Spritesheet(object):
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert()
    def image_at(self, rectangle, colorkey = None): # Load a specific image from a specific rectangle
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    def images_at(self, rects, colorkey = None): # Load a whole bunch of images and return them as a list
        return [self.image_at(rect, colorkey) for rect in rects]
    def load_strip(self, rect, image_count, colorkey = None): # Load a whole strip of images
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)
class Tile:
    def __init__(self, passable, destructable, transparent, damage, sprite, sprite_shadow):
        self.passable = passable
        self.destructable = destructable
        self.transparent = transparent
        self.damage = damage
        self.sprite = sprite
        self.sprite_shadow = sprite_shadow
        self.discovered = False
class Camera:
    def __init__(self, min_x, min_y, max_x, max_y, width, height, follow_object):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x - width
        self.max_y = max_y - height
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.follow_object = follow_object
    def update(self):
        self.x = util_clamp(self.follow_object.x-self.width/2, self.min_x, self.max_x)
        self.y = util_clamp(self.follow_object.y-self.height/2, self.min_y, self.max_y)

class Window:
    def __init__(self, parent, title, active, visible):
        self.x = constants.CAMERA_WIDTH*32 - constants.POPUP_WIDTH
        self.y = 0
        self.width = constants.POPUP_WIDTH
        self.height = constants.CAMERA_HEIGHT*32
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.set_colorkey(constants.COLOR_COLORKEY)
        self.active = active
        self.visible = visible
        self.parent = parent
        self.title = title
    def switchActive(self):
        if not self.active:
            for window in GAME.windows:
                window.visible = False
                window.active = False
            GAME.player.active = False
            self.active = True
            self.visible = True
        else:
            GAME.player.active = True
            self.active = False
            self.visible = False
    def draw(self):
        if self.visible:
            self.surface.fill(constants.COLOR_COLORKEY)
            self.surface.fill(constants.COLOR_DARKGRAY, pygame.Rect(0, 0, self.width, self.height))
            if self.title != '':
                draw_text(self.surface, self.title, constants.POPUP_OFFSET_X, constants.POPUP_OFFSET_Y, constants.FONT_PERFECTDOS, constants.COLOR_WHITE)
class WindowSelectable(Window):
    def __init__(self, parent, title, active, visible, bitems, binput, bquantity = []):
        super().__init__(parent, title, active, visible)
        self.bitems = bitems(self)
        self.binput = [action(self) for action in binput]
        self.getItems()
        if title == None:
            self.height = len(self.items)*16
        else:
            self.height = len(self.items)*16+32
        if self.parent == None:
            self.y = constants.CAMERA_HEIGHT*32 - self.height
        else:
            self.y = self.parent.y - self.height - 4
        self.index = 0
        GAME.player.active = False
    def input(self, key):
        for action in self.binput:
            action.execute(key)
    def draw(self):
        super().draw()
        if len(self.items) > 0 and self.visible:
            if self.title == None:
                self.surface.fill(constants.COLOR_DARKRED, pygame.Rect(0, self.index*16, self.width, 16))
                for itemIndex in range(len(self.items)):
                    draw_text(self.surface, self.items[itemIndex][0], constants.POPUP_OFFSET_X, itemIndex*16, constants.FONT_PERFECTDOS, self.items[itemIndex][1])
            else:
                self.surface.fill(constants.COLOR_DARKRED, pygame.Rect(0, self.index*16+32, self.width, 16))
                for itemIndex in range(len(self.items)):
                    draw_text(self.surface, self.items[itemIndex][0], constants.POPUP_OFFSET_X, itemIndex*16+32, constants.FONT_PERFECTDOS, self.items[itemIndex][1])
            SCREEN.blit(self.surface, (self.x, self.y))
        else:
            GAME.controlsText = constants.TEXT_ONMAP
            self.destroy()
    def destroy(self):
        if self in GAME.windows:
            GAME.windows.remove(self)
        if self.parent == None:
            GAME.player.active = True
        self.visible = False
        self.active = False
    def getItems(self):
        self.items = self.bitems.execute()

class Window_PlayerInventory(WindowSelectable):
    def __init__(self):
        super().__init__(None, 'Inventory', True, True, b_wind_inventory_items, [b_wind_arrowkeys_input, b_wind_inventory_input])
class Window_SearchInventory(WindowSelectable):
    def __init__(self):
        super().__init__(None, 'Found items', True, True, b_wind_search_items, [b_wind_arrowkeys_input, b_wind_search_input])

# class InfoPanel(Window):

class Entity:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.sprite = sprite
    def draw(self, surface, camera): # DRAW
        surface.blit(self.sprite, ((self.x - camera.x)*32, (self.y - camera.y)*32))
class Creature(Entity):
    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite)
        self.tag = 'neutral'
    def move(self, dx, dy): # CHECK FOR CREATURE IN THE MOVING TILE AND ATTACK. IF NOT, MOVE.
        for obj in GAME.creatures:
            if (obj.x == self.x + dx and obj.y == self.y + dy):
                return
        if GAME.map[self.x + dx][self.y + dy].passable:
            self.x += dx
            self.y += dy
    def isEnemy(self, target):
        return self.tag != target.tag
    def execute_action(self):
        for action in self.actionTurn:
            action.execute()
    def move(self, dx = 0, dy = 0):
        for action in self.actionMove:
            action.execute(dx, dy)
    def attack(self, obj):
        for action in self.actionAttack:
            action.execute(obj)
    def damage(self, value):
        for action in self.actionTakeDamage:
            action.execute(value)
    def die(self):
        for action in self.actionDeath:
            action.execute()
class Player(Creature):
    def __init__(self, x, y, sprite):
        super().__init__(x, y, sprite)
        self.inventory = []
        self.name = 'Player'
        self.tag = 'human'
        self.xp = 0
        self.capacity = 100
        self.equipment = [None for i in range(8)]
        self.stats = [100 for i in range(14)]
        self.hp = self.stats[0]
        self.damageStat = 10 # PLACEHOLDER
        self.active = True
        self.actionMove = [b_play_move(self)]
        self.actionAttack = [b_crea_simpleattack(self)]
        self.actionDeath = [b_play_death(self)]
        self.actionTakeDamage = [b_crea_takedamage(self)]
    def input(self, key):
        if self.active: #TODO: PASARLO AL PLAYER
            if key == pygame.K_UP:
                self.move(0, -1)
                GAME.action = 'move'
                map_light_update(GAME.light_map)
            elif key == pygame.K_DOWN:
                self.move(0, 1)
                GAME.action = 'move'
                map_light_update(GAME.light_map)
            elif key == pygame.K_LEFT:
                self.move(-1, 0)
                GAME.action = 'move'
                map_light_update(GAME.light_map)
            elif key == pygame.K_RIGHT:
                self.move(1, 0)
                GAME.action = 'move'
                map_light_update(GAME.light_map)
    def move(self, dx, dy):
        if self.active:
            super().move(dx, dy)
    def execute_action(self):
        return
    def currentWeight(self):
        return sum([item.size for item in self.inventory] + [item.size for item in self.equipment if item != None])
class Monster(Creature):
    def __init__(self, x, y, sprite, name, maxHp, drops, actionTurn, actionMove, actionAttack, actionTakeDamage, actionDeath):
        super().__init__(x, y, sprite)
        self.name = name
        self.maxHp = maxHp
        self.hp = maxHp
        self.damageStat = random.randint(1,6)
        self.drops = drops
        self.actionTurn = actionTurn
        self.actionMove = actionMove
        self.actionAttack = actionAttack
        self.actionTakeDamage = actionTakeDamage
        self.actionDeath = actionDeath
        self.tag = 'monster'
    def antistuck(self):
        for creature in GAME.creatures:
            if (creature is not self and self.x == creature.x and self.y == creature.y):
                self.x += 1
                self.y += 1
                self.antistuck()

class Item(Entity):
    def __init__(self, x, y, sprite, name, color, size):
        super().__init__(x, y, sprite)
        self.name = name
        self.size = size
        self.color = color
class Equipment(Item):
    def __init__(self, x, y, sprite, name, color, size, slot, actionEquipment):
        super().__init__(x, y, sprite, name, color, size)
        self.slot = slot
        self.itemType = 'equipment'
        self.actionEquipment = actionEquipment(self)
    def equip(self):
        self.actionEquipment.onEquip()
    def unequip(self):
        self.actionEquipment.onUnequip()
class Consumable(Item):
    def __init__(self, x, y, sprite, name, color, size, onUse, useCondition = [], charges = 1, target = 'self'):
        super().__init__(x, y, sprite, name, color, size)
        self.onUse = onUse
        self.useCondition = useCondition
        self.charges = charges
        self.displayCharges = self.charges == 1
        self.target = target
        self.itemType = 'consumable'
        self.used = False
    def use(self):
        for action in self.onUse:
            action.execute()
        if self.used:
            GAME.player.inventory.remove(self)
    def condition(self):
        for condition in self.useCondition:
            if not condition.execute():
                return False
        return True
    def gotUsed(self):
        return self.used


class Component:
    def __init__(self, parent, priority = 0):
        self.parent = parent
        self.priority = priority

# GAME
def game_init():
    global GAME, TILES, SCREEN, CLOCK
    pygame.init()

    SCREEN = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
    GAME = Game()
    GAME.initGame()
    GAME.generateMap()
    GAME.initLight()

    CLOCK = pygame.time.Clock()
def game_loop():
    while True:
        CLOCK.tick(60)
        GAME.action = 'none'
        game_input()
        if GAME.action != 'none':
            GAME.creaturesExecuteTurn()
            GAME.entitiesExecuteTurn()
        GAME.updateCamera()
        draw_game()
def game_input():
    events = pygame.event.get();
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            GAME.player.input(event.key)

            if event.key == constants.KEY_INVENTORY:
                if GAME.windows == []:
                    GAME.windows = [Window_PlayerInventory()]
                    GAME.controlsText = constants.TEXT_ONINVENTORY
            if event.key == constants.KEY_SEARCH:
                if GAME.windows == []:
                    GAME.windows = [Window_SearchInventory()]
                    GAME.controlsText = constants.TEXT_ONSEARCH

            if event.key == pygame.K_UP:
                for window in GAME.windows:
                    if window.active:
                        window.input('up')
                        return
            if event.key == pygame.K_DOWN:
                for window in GAME.windows:
                    if window.active:
                        window.input('down')
                        return
            if event.key == constants.KEY_USE:
                for window in GAME.windows:
                    if window.active:
                        window.input('use')
                        return
            if event.key == constants.KEY_CANCEL:
                for window in GAME.windows:
                    if window.active:
                        window.input('cancel')
                        return
            if event.key == constants.KEY_LOG:
                if GAME.long_log:
                    GAME.long_log = False
                else:
                    GAME.long_log = True


# DRAW
def draw_game():
    SCREEN.fill(constants.COLOR_BLACK)
    GAME.surface_map.fill(constants.COLOR_BLACK)
    GAME.surface_log.fill(constants.COLOR_COLORKEY)
    GAME.surface_status.fill(constants.COLOR_COLORKEY)
    if GAME.long_log:
        height = min(constants.LOG_MAX_LENGTH_LONG*18 + 8, len(GAME.log)*18 + 8)
        GAME.surface_log.fill(constants.COLOR_DARKESTGRAY, pygame.Rect(0, constants.WINDOW_HEIGHT - height, constants.LOG_WIDTH, height))
    else:
        height = min(constants.LOG_MAX_LENGTH*18 + 8, len(GAME.log)*18 + 8)
        GAME.surface_log.fill(constants.COLOR_DARKESTGRAY, pygame.Rect(0, constants.WINDOW_HEIGHT - height, constants.LOG_WIDTH, height))
    GAME.surface_log.set_colorkey(constants.COLOR_COLORKEY)
    GAME.surface_status.set_colorkey(constants.COLOR_COLORKEY)
    draw_map()
    draw_log()
    draw_status()
    for creature in GAME.creatures:
        if libtcodpy.map_is_in_fov(GAME.light_map, creature.x, creature.y):
            creature.draw(GAME.surface_map, GAME.camera)
    for entity in GAME.entities:
        if libtcodpy.map_is_in_fov(GAME.light_map, entity.x, entity.y):
            entity.draw(GAME.surface_map, GAME.camera)
    SCREEN.blit(GAME.surface_map, (0, 0))
    SCREEN.blit(GAME.surface_log, (0, 0))
    SCREEN.blit(GAME.surface_status, (constants.LOG_WIDTH, constants.CAMERA_HEIGHT*32))
    for window in GAME.windows:
        if window.visible:
            window.draw()

    #DEBUG
    draw_text_bg(SCREEN, 'X: ' + str(GAME.player.x) + '   Y: ' + str(GAME.player.y), 10, 10, constants.FONT_PERFECTDOS, constants.COLOR_WHITE, constants.COLOR_BLACK)
    draw_text_bg(SCREEN, 'FPS: ' + str(math.floor(CLOCK.get_fps())), 10, 28, constants.FONT_PERFECTDOS, constants.COLOR_WHITE, constants.COLOR_BLACK)

    pygame.display.flip()
def draw_map():
    for x in range(0, constants.CAMERA_WIDTH):
        for y in range(0, constants.CAMERA_HEIGHT):
            if libtcodpy.map_is_in_fov(GAME.light_map, GAME.camera.x + x, GAME.camera.y + y):
                GAME.surface_map.blit(GAME.map[GAME.camera.x + x][GAME.camera.y + y].sprite, (x*32, y*32))
                GAME.map[GAME.camera.x + x][GAME.camera.y + y].discovered = True
            elif GAME.map[GAME.camera.x + x][GAME.camera.y + y].discovered == True:
                GAME.surface_map.blit(GAME.map[GAME.camera.x + x][GAME.camera.y + y].sprite_shadow, (x*32, y*32))
    pygame.draw.rect(GAME.surface_map, constants.COLOR_BORDER, pygame.Rect(constants.BORDER_THICKNESS, constants.BORDER_THICKNESS, constants.CAMERA_WIDTH*32-constants.BORDER_THICKNESS*2, constants.CAMERA_HEIGHT*32-constants.BORDER_THICKNESS*2), constants.BORDER_THICKNESS*2)
def draw_log():
    if GAME.long_log:
        messages = constants.LOG_MAX_LENGTH_LONG
    else:
        messages = constants.LOG_MAX_LENGTH
    for x in range(0, min(messages, len(GAME.log))):
        draw_text_bg(GAME.surface_log, GAME.log[x][0], 10, constants.WINDOW_HEIGHT - x*18 - 20, constants.FONT_PERFECTDOS, GAME.log[x][1], constants.COLOR_DARKGRAY)
def draw_status():
    draw_text_bg(GAME.surface_status, 'HP', 32, 16, constants.FONT_PERFECTDOS, constants.COLOR_WHITE, constants.COLOR_DARKESTGRAY)
    pygame.draw.rect(GAME.surface_status, constants.COLOR_DARKESTGRAY, pygame.Rect(64, 16, 200, 16))
    pygame.draw.rect(GAME.surface_status, constants.COLOR_HP, pygame.Rect(64, 16, 200*GAME.player.hp/GAME.player.stats[0], 16))
    draw_text(GAME.surface_status, str(GAME.player.hp) + ' / ' + str(GAME.player.stats[0]), 122, 16, constants.FONT_PERFECTDOS, constants.COLOR_WHITE)
    for textIndex in range(len(GAME.controlsText)):
        xOffset = (textIndex // constants.LOG_MAX_LENGTH-1) *200
        draw_text(GAME.surface_status, GAME.controlsText[textIndex][0], 620 + xOffset, (textIndex%constants.LOG_MAX_LENGTH-1)*16+24, constants.FONT_PERFECTDOS, constants.COLOR_WHITE)
        draw_text(GAME.surface_status, GAME.controlsText[textIndex][1], 700 + xOffset, (textIndex%constants.LOG_MAX_LENGTH-1)*16+24, constants.FONT_PERFECTDOS, constants.COLOR_WHITE)

def draw_text(surface, text, x, y, font, text_color):
    surface.blit(font.render(text, False, text_color), (x, y))
def draw_text_bg(surface, text, x, y, font, text_color, bg_color):
    surface.blit(font.render(text, False, text_color, bg_color), (x, y))


# MAP
def map_init_noise(width, height):
    map_gen = []
    noise = libtcodpy.noise_new(2)
    libtcodpy.noise_set_type(noise, libtcodpy.NOISE_SIMPLEX)
    for x in range(0, width):
        aux = []
        for y in range(0, height):
            if libtcodpy.noise_get(noise, [(x+1)/3, y/3]) > 0.6:
                aux.append(Tile(False, True, False, 0, GAME.tiles.image_at((0, 0, 32, 32)), GAME.tiles.image_at((0, 32, 32, 32)))) # WALL
            else:
                aux.append(Tile(True, False, True, 0, GAME.tiles.image_at((32, 0, 32, 32)), GAME.tiles.image_at((32, 32, 32, 32)))) #F LOOR
        map_gen.append(aux)
    map_gen = map_set_borders(map_gen, width-1, height-1) # BORDERS
    return map_gen
def map_init_walk(width, height, floor_percent):
    map_gen = [[Tile(False, True, False, 0, GAME.tiles.image_at((0, 0, 32, 32)), GAME.tiles.image_at((0, 32, 32, 32))) for i in range(height)] for j in range(width)]
    x = math.floor(width/2)
    y = math.floor(height/2)
    floor_left = math.floor(width * height * floor_percent)
    while floor_left > 0:
        if map_gen[x][y].passable == False:
            map_gen[x][y] = Tile(True, False, True, 0, GAME.tiles.image_at((32, 0, 32, 32)), GAME.tiles.image_at((32, 32, 32, 32)))
            floor_left -= 1
        direction = random.randint(0, 1)
        if direction == 0:
            x += random.randint(-1,1)
        else:
            y += random.randint(-1,1)
        if x >= width-4:
            x -= 4
        if x < 4:
            x += 4
        if y >= height-4:
            y -= 4
        if y < 4:
            y += 4
    map_gen = map_set_borders(map_gen, width-1, height-1)
    return map_gen

def map_set_borders(map_array, width, height):
    for x in range(0, width):
        map_set_bedrock(map_array, x, 0)
        if random.randint(0,2) == 0:
            map_set_bedrock(map_array, x, 1)
        map_set_bedrock(map_array, x, height)
        if random.randint(0,2) == 0:
            map_set_bedrock(map_array, x, height-1)
    for y in range(0, height):
        map_set_bedrock(map_array, 0, y)
        if random.randint(0,2) == 0:
            map_set_bedrock(map_array, 1, y)
        map_set_bedrock(map_array, width, y)
        if random.randint(0,2) == 0:
            map_set_bedrock(map_array, width-1, y)
    return map_array

def map_set_wall(map_array, x, y):
    map_array[x][y] = Tile(False, True, False, 0, GAME.tiles.image_at((0, 0, 32, 32)), GAME.tiles.image_at((0, 32, 32, 32)))
def map_set_floor(map_array, x, y):
    map_array[x][y] = Tile(True, False, True, 0, GAME.tiles.image_at((32, 0, 32, 32)), GAME.tiles.image_at((32, 32, 32, 32)))
def map_set_bedrock(map_array, x, y):
    map_array[x][y] = Tile(False, False, False, 0, GAME.tiles.image_at((64, 0, 32, 32)), GAME.tiles.image_at((64, 32, 32, 32)))

def map_light_init(map_array):
    width = len(GAME.map)
    height = len(GAME.map[0])
    light_map = libtcodpy.map_new(width, height)

    for x in range(0, width):
        for y in range(0, height):
            libtcodpy.map_set_properties(light_map, x, y, GAME.map[x][y].transparent, GAME.map[x][y].passable)
    return light_map
def map_light_update(light_map):
    libtcodpy.map_compute_fov(light_map, GAME.player.x, GAME.player.y, constants.LIGHT_RADIUS, True, libtcodpy.FOV_DIAMOND)


# UTIL
def util_clamp(value, minv, maxv):
    return int(max(minv, min(value, maxv)))
def util_distance(object1, object2):
    return math.sqrt((object1.x - object2.x) * (object1.x - object2.x) + (object1.y - object2.y) * (object1.y - object2.y))
def util_simpledistance(coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2
    return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))


# BEHAVIOR CLASSES
    # PLAYER BEHAVIOR
class b_wind_arrowkeys_input(Component):
    def execute(self, key):
        if key == 'up':
            self.parent.index = (self.parent.index - 1) % len(self.parent.items)
        if key == 'down':
            self.parent.index = (self.parent.index + 1) % len(self.parent.items)
        if key == 'cancel':
            self.parent.destroy()

class b_wind_inventory_items(Component):
    def execute(self):
        return [(item.name, item.color) for item in GAME.player.inventory]
class b_wind_inventory_input(Component):
    def execute(self, key):
        if key == 'use':
            if GAME.player.inventory[self.parent.index].itemType == 'consumable':
                self.parent.popupwindow = WindowSelectable(self.parent, None, True, True, b_wind_popupinventoryc_items, [b_wind_arrowkeys_input, b_wind_popupinventoryc_input])
                GAME.controlsText = constants.TEXT_ONPOPUP
            elif GAME.player.inventory[self.parent.index].itemType == 'equipment':
                self.parent.popupwindow = WindowSelectable(self.parent, None, True, True, b_wind_popupinventorye_items, [b_wind_arrowkeys_input, b_wind_popupinventorye_input])
            GAME.windows.append(self.parent.popupwindow)
            self.parent.active = False
        if key == 'cancel':
            GAME.player.active = True
            GAME.controlsText = constants.TEXT_ONMAP
class b_wind_popupinventorye_items(Component):
    def execute(self):
        return [('Equip', constants.COLOR_WHITE), ('Throw', constants.COLOR_WHITE), ('Cancel', constants.COLOR_WHITE)]
class b_wind_popupinventorye_input(Component):
    def execute(self, key):
        if key == 'use':
            if self.parent.index == 0: #EQUIP
                if GAME.player.equipment[self.parent.parent.items[self.parent.parent.index].slot] != None:
                    GAME.player.inventory.append(GAME.player.equipment[self.parent.parent.items[self.parent.parent.index].slot])
                GAME.player.equipment[self.parent.parent.items[self.parent.parent.index].slot] = self.parent.parent.items[self.parent.parent.index]
                GAME.player.equipment.pop(self.parent.parent.items[self.parent.parent.index])
                self.parent.parent.getItems()
                self.parent.parent.active = True
                self.parent.destroy()
            if self.parent.index == 1: #THROW
                item = GAME.player.inventory.pop(self.parent.parent.index)
                item.x = GAME.player.x
                item.y = GAME.player.y
                GAME.items.append(item)
                self.parent.parent.getItems()
                self.parent.parent.active = True
                self.parent.destroy()
            if self.parent.index == 2: #CANCEL
                self.parent.parent.active = True
                self.parent.destroy()
class b_wind_popupinventoryc_items(Component):
    def execute(self):
        colorUse = constants.COLOR_GRAY
        if GAME.player.inventory[self.parent.parent.index].condition():
                colorUse = constants.COLOR_WHITE
        return [('Use', colorUse), ('Throw', constants.COLOR_WHITE), ('Cancel', constants.COLOR_WHITE)]
class b_wind_popupinventoryc_input(Component):
    def execute(self, key):
        if key == 'use':
            if self.parent.index == 0: #USE
                if GAME.player.inventory[self.parent.parent.index].condition():
                    if GAME.player.inventory[self.parent.index].target == 'self':
                        GAME.player.inventory[self.parent.parent.index].use()
                        self.parent.parent.getItems()
                        self.parent.parent.active = True
                        GAME.action = 'item'
                        GAME.controlsText = constants.TEXT_ONINVENTORY
                        self.parent.destroy()
            if self.parent.index == 1: #THROW
                item = GAME.player.inventory.pop(self.parent.parent.index)
                item.x = GAME.player.x
                item.y = GAME.player.y
                GAME.items.append(item)
                self.parent.parent.getItems()
                self.parent.parent.active = True
                GAME.controlsText = constants.TEXT_ONINVENTORY
                self.parent.destroy()
            if self.parent.index == 2: #CANCEL
                self.parent.parent.active = True
                GAME.controlsText = constants.TEXT_ONINVENTORY
                self.parent.destroy()
        if key == 'cancel':
            self.parent.parent.active = True
            GAME.controlsText = constants.TEXT_ONINVENTORY
class b_wind_search_items(Component):
    def execute(self):
        return [(item.name, item.color) for item in GAME.items if (item.x == GAME.player.x and item.y == GAME.player.y)]
class b_wind_search_input(Component):
    def execute(self, key):
        if key == 'use':
            item = [item for item in GAME.items if (item.x == GAME.player.x and item.y == GAME.player.y)][self.parent.index]
            if item.size <= GAME.player.capacity - GAME.player.currentWeight():
                GAME.player.inventory.append(item)
                GAME.items.remove(item)
                self.parent.getItems()
            else:
                GAME.addLogMessage('You are carrying too much.', constants.COLOR_INFO)
        if key == 'cancel':
            GAME.player.active = True
            GAME.controlsText = constants.TEXT_ONMAP
            self.parent.destroy()



class b_play_move(Component):
    def execute(self, dx = 0, dy = 0):
        if GAME.placeFree(self.parent.x + dx, self.parent.y + dy):
            if GAME.map[self.parent.x + dx][self.parent.y + dy].passable:
                self.parent.x += dx
                self.parent.y += dy
        else:
            for creature in GAME.creatures:
                if (creature is not self and creature.x == self.parent.x + dx and creature.y == self.parent.y + dy):
                    self.parent.attack(creature)
                    break
class b_play_death(Component):
    def execute(self):
        pygame.quit()
        exit()

# CREATURES BEHAVIOR
class b_crea_simpleturn(Component):
    def execute(self):
        self.parent.antistuck()
        if util_distance(self.parent, GAME.player) == 1:
            self.parent.attack(GAME.player)
        else:
            self.parent.move()
class b_crea_randommove(Component):
    def execute(self, dx = 0, dy = 0):
        rnd = random.randint(1,5)
        if rnd == 0:
            dx, dy = (-1, 0)
        elif rnd == 1:
            dx, dy = (1, 0)
        elif rnd == 2:
            dx, dy = (0, -1)
        elif rnd == 3:
            dx, dy = (0, 1)
        else:
            dx, dy = (0, 0)
        if GAME.placeFree(self.parent.x + dx, self.parent.y + dy):
            if GAME.map[self.parent.x + dx][self.parent.y + dy].passable:
                self.parent.x += dx
                self.parent.y += dy
class b_crea_takedamage(Component):
    def execute(self, damage):
        self.parent.hp -= damage
        if self.parent.hp <= 0:
            self.parent.die()
class b_crea_simpledeath(Component):
    def execute(self):
        for drop in self.parent.drops:
            rnd = random.random()
            if rnd < drop[1]:
                drop[0].x = self.parent.x
                drop[0].y = self.parent.y
                GAME.items.append(drop[0])
        GAME.creatures.remove(self.parent)
class b_crea_simpleattack(Component):
    def execute(self, receiver):
        receiver.damage(self.parent.damageStat)
        GAME.addLogMessage(self.parent.name + ' attacks ' + receiver.name + ' for ' + str(self.parent.damageStat) + ' damage!', constants.COLOR_RED)

# EFFECTS
class b_effe_getused(Component):
    def execute(self):
        self.parent.used = True
class b_effe_flatheal(Component):
    def __init__(self, parent, amount):
        super().__init__(parent)
        self.amount = amount
    def execute(self):
        if self.parent.hp + self.amount > self.parent.stats[0]:
            value = self.parent.stats[0] - self.parent.hp
            GAME.addLogMessage(self.parent.name + ' heals to max!', constants.COLOR_HEAL)
        else:
            value = self.amount
            GAME.addLogMessage(self.parent.name + ' heals for ' + str(value) + '.', constants.COLOR_HEAL)
        self.parent.hp += value
class b_effe_percheal(Component):
    def __init__(self, parent, percent = 0.25):
        super().__init__(parent)
        self.percent = percent
    def execute(self):
        if math.floor(self.parent.stats[0]*self.percent + self.parent.hp) > self.parent.stats[0]:
            value = self.parent.stats[0] - self.parent.hp
            GAME.addLogMessage(self.parent.name + ' heals to max!', constants.COLOR_HEAL)
        else:
            value = math.floor(self.parent.stats[0]*self.percent)
            GAME.addLogMessage(self.parent.name + ' heals for ' + str(value) + '.', constants.COLOR_HEAL)
        self.parent.hp += value
class b_effe_venom(Component):
    def __init__(self, parent, amount, turns = -1):
        super().__init__(parent)
        self.amount = amount
        self.turns = turns
    def execute(self):
        if self.turns != 0:
            self.turns -= 1
            GAME.addLogMessage(self.parent.name + ' takes ' + str(self.amount) + ' damage from venom.', consants.COLOR_VENOM)
            self.parent.damage(self.amount)

# CONDITIONS
class b_cond_playnotfullhealth(Component):
    def execute(self):
        return GAME.player.hp < GAME.player.stats[0]
class b_effe_createbomb(Component):
    def __init__(self, parent, turns, radius, damage):
        super().__init__(parent)
        self.turns = turns
        self.radius = radius
        self.damage = damage
    def execute(self):
        GAME.entities.append(e_bomb(GAME.player.x, GAME.player.y, GAME.consumables.image_at((32, 0, 32, 32), constants.COLOR_COLORKEY), self.turns, self.radius, self.damage))
        GAME.addLogMessage('The bomb will explode in ' + str(self.turns) + ' turns!', constants.COLOR_ALLY)

# ENTITIES
class e_bomb(Entity):
    def __init__(self, x, y, sprite, turns, radius, damage):
        super().__init__(x, y, sprite)
        self.turns = turns
        self.radius = radius
        self.damage = damage
    def execute_action(self):
        if self.turns > 0:
            self.turns -= 1
        else:
            for tilex in range(self.x - self.radius, self.x + self.radius):
                for tiley in range(self.y - self.radius, self.y + self.radius):
                    print(util_simpledistance((tilex, tiley), (self.x, self.y)))
                    if tilex < constants.MAP_WIDTH[GAME.level] and tiley < constants.MAP_HEIGHT[GAME.level]:
                        if util_simpledistance((tilex, tiley), (self.x, self.y)) < self.radius and GAME.map[tilex][tiley].destructable:
                            map_set_floor(GAME.map, tilex, tiley)
                            libtcodpy.map_set_properties(GAME.light_map, tilex, tiley, GAME.map[tilex][tiley].transparent, GAME.map[tilex][tiley].passable)
            GAME.addLogMessage('You hear a loud explosion.', constants.COLOR_INFO)
            GAME.entities.remove(self)



# MONSTERS
class Slime(Monster):
    def __init__(self, x, y):
        super().__init__(x, y, constants.SPRITE_ENEMY_SLIME, 'Slime', 10, [(MinorHealPotion(0, 0), 1)], [b_crea_simpleturn(self)], [b_crea_randommove(self)], [b_crea_simpleattack(self)], [b_crea_takedamage(self)], [b_crea_simpledeath(self)])
# CONSUMABLES
class MinorHealPotion(Consumable):
    def __init__(self, x, y):
        super().__init__(x, y, GAME.consumables.image_at((0, 0, 32, 32)), 'Minor heal potion', constants.COLOR_WHITE, 1, [b_effe_flatheal(GAME.player, 10), b_effe_getused(self)], [b_cond_playnotfullhealth(GAME.player)])
class Bomb(Consumable):
    def __init__(self, x, y):
        super().__init__(x, y, GAME.consumables.image_at((32, 0, 32, 32)), 'Bomb', constants.COLOR_RED, 3, [b_effe_createbomb(None, 5, 5, 10), b_effe_getused(self)])

# EXECUTION
if __name__ == '__main__':
    game_init()
    game_loop()
