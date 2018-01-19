# IMPORT
import pygame
import libtcodpy
import random
import math

import constants

# CLASSES
class Game:
    def __init__(self):
        self.level = 0
        self.map = None
        self.light_map = None
        self.surface_map = pygame.Surface((constants.MAP_WIDTH[self.level]*32, constants.MAP_HEIGHT[self.level]*32))
        self.surface_info = pygame.Surface((constants.WINDOW_WIDTH - constants.CAMERA_WIDTH*32, constants.WINDOW_HEIGHT))
        self.surface_log = pygame.Surface((constants.CAMERA_WIDTH*32, constants.WINDOW_HEIGHT - constants.CAMERA_HEIGHT*32))
        self.tiles = Spritesheet('resources/tiles.png')
        self.player = Player(30, 25, constants.SPRITE_PLAYER, 10, 10)
        self.creatures = [self.player]
        self.log = []
        self.camera = Camera(0, 0, constants.MAP_WIDTH[self.level], constants.MAP_HEIGHT[self.level], constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT, self.player)
        self.window_inventory = PlayerInventory(256)
        self.window_floor = FloorInventory(256)
        self.windows = [self.window_inventory, self.window_floor]
        self.items = [Item(30, 25, constants.SPRITE_ENEMY_SLIME, 'PEPE THE FROG', 1), Item(30, 25, constants.SPRITE_ENEMY_SLIME, 'Slime meat!!!', 1), Item(0, 0, constants.SPRITE_ENEMY_SLIME, 'Slime meat', 1)]
    def addLogMessage(self, message, color):
        self.log.insert(0, (message, color))
    def creaturesExecuteTurn(self):
        for creature in self.creatures:
            creature.execute_action()
    def updateCamera(self):
        self.camera.update()
    def generateMap(self):
        self.map = map_init_walk(constants.MAP_WIDTH[self.level], constants.MAP_HEIGHT[self.level], 0.5)
    def initLight(self):
        self.light_map = map_light_init(self.map)
        map_light_update(self.light_map)

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
    def __init__(self, width):
        self.x = constants.CAMERA_WIDTH*32 - width
        self.y = 0
        self.width = width
        self.height = constants.CAMERA_HEIGHT*32
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.set_colorkey(constants.COLOR_COLORKEY)
        self.active = False
        self.visible = False
    def setActive(self):
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
            self.getItems()
            self.surface.fill(constants.COLOR_COLORKEY)
            self.surface.fill(constants.COLOR_DARKGRAY, pygame.Rect(0, 0, self.width, self.height))
class WindowSelectable(Window):
    def setActive(self):
        super().setActive()
        self.index = 0
    def input(self, key):
        if key == 'up':
            self.index = (self.index - 1) % len(self.items)
        if key == 'down':
            self.index = (self.index + 1) % len(self.items)
class PlayerInventory(WindowSelectable):
    def __init__(self, width):
        super().__init__(width)
    def draw(self):
        super().draw()
        if len(self.items) > 0 and self.visible:
            self.surface.fill(constants.COLOR_DARKRED, pygame.Rect(0, self.index*16+32, self.width, 16))
            draw_text(self.surface, 'INVENTORY', 4, 8, constants.FONT_PERFECTDOS, constants.COLOR_WHITE)
            for x in range(len(self.items)):
                draw_text(self.surface, GAME.player.inventory[x].name, 4, x*16+32, constants.FONT_PERFECTDOS, constants.COLOR_WHITE)
            SCREEN.blit(self.surface, (self.x, self.y))
        elif self.active:
            self.setActive()
    def getItems(self):
        self.items = GAME.player.inventory
        if len(self.items) > 0:
            self.height = min(len(self.items)*16 + 32, constants.CAMERA_HEIGHT*32)
            self.y = constants.CAMERA_HEIGHT*32 - self.height
    def input(self, key):
        super().input(key)
        if key == 't':
            GAME.player.throwItem(self.index)
            if self.index > 0:
                self.index -= 1
class FloorInventory(WindowSelectable):
    def __init(self, width):
        super().__init__(width)
    def draw(self):
        super().draw()
        if len(self.items) > 0:
            self.surface.fill(constants.COLOR_DARKRED, pygame.Rect(0, self.index*16+32, self.width, 16))
            draw_text(self.surface, 'FOUND ITEMS', 4, 8, constants.FONT_PERFECTDOS, constants.COLOR_WHITE)
            for x in range(len(self.items)):
                draw_text(self.surface, self.items[x][0].name, 4, x*16+32, constants.FONT_PERFECTDOS, constants.COLOR_WHITE)
            SCREEN.blit(self.surface, (self.x, self.y))
        elif self.active:
            self.setActive()
    def getItems(self):
        self.items = []
        for i in range(len(GAME.items)):
            if (GAME.items[i].x == GAME.player.x and GAME.items[i].y == GAME.player.y):
                self.items.append((GAME.items[i], i))
        if len(self.items) > 0:
            self.height = min(len(self.items)*16 + 32, constants.CAMERA_HEIGHT*32)
            self.y = constants.CAMERA_HEIGHT*32 - self.height
    def input(self, key):
        super().input(key)
        if key == 'g':
            GAME.player.pickupItem(self.items[self.index][1])
            if self.index > 0:
                self.index -= 1

class Entity:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.sprite = sprite
    def draw(self, surface, camera): # DRAW
        surface.blit(self.sprite, ((self.x - camera.x)*32, (self.y - camera.y)*32))
class Creature(Entity):
    def __init__(self, x, y, sprite, maxHp):
        super().__init__(x, y, sprite)
        self.maxhp = maxHp
        self.hp = maxHp
        self.tag = 'neutral'
    def move(self, dx, dy): # CHECK FOR CREATURE IN THE MOVING TILE AND ATTACK. IF NOT, MOVE.
        for obj in GAME.creatures:
            if (obj is not self and obj.x == self.x + dx and obj.y == self.y + dy and self.isEnemy(obj)):
                self.attack(obj, 5)
                return
        if GAME.map[self.x + dx][self.y + dy].passable:
            self.x += dx
            self.y += dy
    def isEnemy(self, target):
        return self.tag != target.tag
    def execute_action(self):
        return
class Player(Creature):
    def __init__(self, x, y, sprite, maxHp, maxResource):
        super().__init__(x, y, sprite, maxHp)
        self.maxResource = maxResource
        self.inventory = [Item(0, 0, constants.SPRITE_ENEMY_SLIME, 'Slime meat', 1), Item(0, 0, constants.SPRITE_ENEMY_SLIME, 'Slime meat', 1), Item(0, 0, constants.SPRITE_ENEMY_SLIME, 'Slime meat', 1)]
        self.name = 'Player'
        self.tag = 'human'
        self.xp = 0
        self.capacity = 100
        self.active = True
    def move(self, dx, dy):
        if self.active:
            super().move(dx, dy)
    def attack(self, obj, dmg): # PRINT ATTACK MESSAGE AND DAMAGE.
        GAME.log.insert(0, (self.name + ' attacks ' + obj.name + ' for ' + str(dmg) + ' damage!', constants.COLOR_WHITE))
        obj.damage(dmg)
    def damage(self, value): # REDUCE HP AND CHECK IF DEAD.
        self.hp -= value
    def canPickup(self, item):
        if self.capacity >= item.size:
            return True
        else:
            return False
    def pickupItem(self, itemIndex):
        item = GAME.items.pop(itemIndex)
        self.inventory.append(item)
        self.capacity -= item.size
    def throwItem(self, itemIndex):
        item = self.inventory.pop(itemIndex)
        item.x = self.x
        item.y = self.y
        GAME.items.append(item)

class Monster(Creature):
    def __init__(self, x, y, sprite, name, maxHp, drops):
        super().__init__(x, y, sprite, maxHp)
        self.name = name
        self.tag = 'monster'
    def attack(self, obj, dmg): # PRINT ATTACK MESSAGE AND DAMAGE.
        GAME.log.insert(0, (self.name + ' attacks ' + obj.name + ' for ' + str(dmg) + ' damage!', constants.COLOR_RED))
        obj.damage(dmg)
    def damage(self, value): # REDUCE HP AND CHECK IF DEAD.
        self.hp -= value
        if self.hp <= 0:
            GAME.creatures.remove(self)
            for item in drops:
                item.x = self.x
                item.y = self.y
                GAME.items.append(item)
    def execute_action(self): # TAKE A TURN
        if self.hp > 0:
            rnd = random.randint(0, 5)
            if rnd == 0:
                self.move(1, 0)
            if rnd == 1:
                self.move(-1, 0)
            if rnd == 2:
                self.move(0, 1)
            if rnd == 3:
                self.move(0, -1)

class Item(Entity):
    def __init__(self, x, y, sprite, name, size):
        super().__init__(x, y, sprite)
        self.name = name
        self.size = size
#class Equipment(Item):
#class Consumable(Item):


# GAME
def game_init():
    global GAME, TILES, SCREEN
    pygame.init()

    SCREEN = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
    GAME = Game()
    GAME.generateMap()
    GAME.initLight()
def game_loop():
    current_action = "none"
    while True:
        current_action = game_input()
        if current_action != "none":
            GAME.creaturesExecuteTurn()
        GAME.updateCamera()
        draw_game()
def game_input():
    events = pygame.event.get();
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if GAME.player.active:
                if event.key == pygame.K_UP:
                    GAME.player.move(0, -1)
                    map_light_update(GAME.light_map)
                    return "move"
                if event.key == pygame.K_DOWN:
                    GAME.player.move(0, 1)
                    map_light_update(GAME.light_map)
                    return "move"
                if event.key == pygame.K_LEFT:
                    GAME.player.move(-1, 0)
                    map_light_update(GAME.light_map)
                    return "move"
                if event.key == pygame.K_RIGHT:
                    GAME.player.move(1, 0)
                    map_light_update(GAME.light_map)
                    return "move"
            if event.key == pygame.K_UP:
                for window in GAME.windows:
                    if window.active:
                        window.input('up')
                        return "none"
            if event.key == pygame.K_DOWN:
                for window in GAME.windows:
                    if window.active:
                        window.input('down')
                        return "none"
            if event.key == pygame.K_t:
                for window in GAME.windows:
                    if window.active:
                        window.input('t')
                        return "none"
            if event.key == pygame.K_g:
                for window in GAME.windows:
                    if window.active:
                        window.input('g')
                        return "none"
            if event.key == pygame.K_i:
                GAME.window_inventory.setActive()
                return "none"
            if event.key == pygame.K_s:
                GAME.window_floor.setActive()
                return "move"
    return "none"


# DRAW
def draw_game():
    SCREEN.fill(constants.COLOR_BLACK)
    GAME.surface_map.fill(constants.COLOR_BLACK)
    GAME.surface_info.fill(constants.COLOR_BLACK)
    GAME.surface_log.fill(constants.COLOR_BLACK)
    #GAME.surface_log.set_colorkey(constants.COLOR_COLORKEY)
    draw_map()
    draw_info()
    draw_log()
    for creature in GAME.creatures:
        if libtcodpy.map_is_in_fov(GAME.light_map, creature.x, creature.y):
            creature.draw(GAME.surface_map, GAME.camera)
    SCREEN.blit(GAME.surface_map, (0, 0))
    SCREEN.blit(GAME.surface_info, (constants.CAMERA_WIDTH*32, 0))
    SCREEN.blit(GAME.surface_log, (0, constants.CAMERA_HEIGHT*32))
    for window in GAME.windows:
        if window.visible:
            window.draw()
    draw_text_bg(SCREEN, 'X: ' + str(GAME.player.x) + '   Y: ' + str(GAME.player.y), 10, 10, constants.FONT_PERFECTDOS, constants.COLOR_WHITE, constants.COLOR_BLACK)

    pygame.display.flip()
def draw_map():
    for x in range(0, constants.CAMERA_WIDTH):
        for y in range(0, constants.CAMERA_HEIGHT):
            if libtcodpy.map_is_in_fov(GAME.light_map, GAME.camera.x + x, GAME.camera.y + y):
                GAME.surface_map.blit(GAME.map[GAME.camera.x + x][GAME.camera.y + y].sprite, (x*32, y*32))
                GAME.map[GAME.camera.x + x][GAME.camera.y + y].discovered = True
            elif GAME.map[GAME.camera.x + x][GAME.camera.y + y].discovered == True:
                GAME.surface_map.blit(GAME.map[GAME.camera.x + x][GAME.camera.y + y].sprite_shadow, (x*32, y*32))
def draw_info():
    GAME.surface_info.blit(constants.SPRITE_GUI_INFO, (0, 0))
def draw_log():
    for x in range(0, min(constants.LOG_MAX_LENGTH, len(GAME.log))):
        draw_text_bg(GAME.surface_log, GAME.log[x][0], 10, constants.WINDOW_HEIGHT-constants.CAMERA_HEIGHT*32-20-x*16, constants.FONT_PERFECTDOS, GAME.log[x][1], constants.COLOR_BLACK)
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
def map_init_walk(width, height, floor_percent): # TODO: ARREGLAR ALGORITMO DE GENERACION CON RANDOM WALK
    map_gen = [[Tile(False, True, False, 0, GAME.tiles.image_at((0, 0, 32, 32)), GAME.tiles.image_at((0, 32, 32, 32))) for i in range(height)] for j in range(width)]
    x = math.floor(width/2)
    y = math.floor(height/2)
    floor_left = math.floor(width * height * floor_percent)
    while floor_left > 0:
        if map_gen[x][y].passable == False:
            map_gen[x][y] = Tile(True, False, True, 0, GAME.tiles.image_at((32, 0, 32, 32)), GAME.tiles.image_at((32, 32, 32, 32)))
            floor_left -= 1
        x += random.randint(-1,1)
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


# EXECUTION
if __name__ == '__main__':
    game_init()
    game_loop()
