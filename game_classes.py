import pygame
import game_constants
import util
import random

pygame.init()

class MainMenu:
    def __init__(self):
        self.option = 0
        self.characterNumber = 0
        self.update = True
class Game:
    def __init__(self):
        self.level = 0
        self.map = None
        self.draw_map = True
        self.light_map = None
        self.surface_map = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))
        self.surface_log = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.WINDOW_HEIGHT))
        self.surface_effects = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))
        self.surface_log_bg = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.WINDOW_HEIGHT))
        self.surface_status = pygame.Surface((game_constants.WINDOW_WIDTH - game_constants.LOG_WIDTH, game_constants.WINDOW_HEIGHT - game_constants.CAMERA_HEIGHT*32))
        self.log = []
        self.long_log = False
        self.draw_log = True
        self.creatures = []
        self.camera = Camera(0, 0, game_constants.MAP_WIDTH[self.level], game_constants.MAP_HEIGHT[self.level], game_constants.CAMERA_WIDTH, game_constants.CAMERA_HEIGHT)
        self.windows = []
        self.popup_lock = False
        self.items = []
        self.entities = []
        self.controlsText = game_constants.TEXT_ONMAP
        self.visualeffects = []
        self.surface_log_bg.set_alpha(200)
        self.surface_log.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface_effects.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface_log_bg.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface_status.set_colorkey(game_constants.COLOR_COLORKEY)
    def addLogMessage(self, message, color):
        self.log.insert(0, (message, color))
        self.draw_log = True
    def creaturesExecuteTurn(self):
        for creature in self.creatures:
            creature.execute_action()
    def entitiesExecuteTurn(self):
        for entity in self.entities:
            entity.execute_action()
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
    def __init__(self, x, y, passable, transparent, damage, sprite, sprite_shadow):
        self.x = x
        self.y = y
        self.passable = passable
        self.transparent = transparent
        self.damage = damage
        self.sprite = sprite
        self.sprite_shadow = sprite_shadow
        self.discovered = False
    def onDestroy(self):
        return

class Camera:
    def __init__(self, min_x, min_y, max_x, max_y, width, height):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x - width
        self.max_y = max_y - height
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
    def update(self, x, y):
        self.x = util.clamp(x-self.width/2, self.min_x, self.max_x)
        self.y = util.clamp(y-self.height/2, self.min_y, self.max_y)

class VisualEffect:
    def __init__(self, x, y, width, height, image = None, period = 0):
        self.time = 0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.period = period
    def execute(self):
        self.time += 1
        if self.period > 0:
            self.time %= self.period
    def draw(self): # DRAW
        SCREEN.blit(self.surface, (self.x - GAME.camera.x*32, self.y - GAME.camera.y*32))

class Window:
    def __init__(self, parent, title, active, visible):
        self.x = game_constants.CAMERA_WIDTH*32 - game_constants.POPUP_WIDTH - game_constants.BORDER_THICKNESS*2
        self.y = 0
        self.width = game_constants.POPUP_WIDTH
        self.height = game_constants.CAMERA_HEIGHT*32
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.set_colorkey(game_constants.COLOR_COLORKEY)
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
            self.surface.fill(game_constants.COLOR_COLORKEY)
            self.surface.fill(game_constants.COLOR_DARKESTGRAY, pygame.Rect(0, 0, self.width, self.height))
            if self.title != '':
                util.draw_text(self.surface, self.title, game_constants.POPUP_OFFSET_X, game_constants.POPUP_OFFSET_Y, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
class WindowSelectable(Window):
    def __init__(self, parent, title, active, visible, bitems, binput, bquantity = None):
        super().__init__(parent, title, active, visible)
        self.bitems = bitems(self)
        if bquantity:
            self.bquantity = bquantity(self)
        else:
            self.bquantity = None
        self.binput = [action(self) for action in binput]
        self.getItems()
        self.getQuantities()
        if title == None:
            self.height = len(self.items)*16
        else:
            self.height = len(self.items)*16+32
        if self.parent == None:
            self.y = game_constants.CAMERA_HEIGHT*32 - self.height - game_constants.BORDER_THICKNESS*2
        else:
            self.y = self.parent.y - self.height - 4
        self.index = 0
        GAME.player.active = False
    def input(self, key):
        for action in self.binput:
            action.execute(key)
    def draw(self):
        super().draw()
        if self.visible and len(self.items) > 0:
            if len(self.items) > 0:
                if self.title == None:
                    yoffset = 0
                else:
                    yoffset = 32
                self.surface.fill(game_constants.COLOR_DARKRED, pygame.Rect(0, self.index*16+yoffset, self.width, 16))
                for itemIndex in range(len(self.items)):
                    util.draw_text(self.surface, self.items[itemIndex][0], game_constants.POPUP_OFFSET_X, itemIndex*16+yoffset, game_constants.FONT_PERFECTDOS, self.items[itemIndex][1])
                    if len(self.quantities) == len(self.items):
                        text = game_constants.FONT_PERFECTDOS.render(str(self.quantities[itemIndex]), False, game_constants.COLOR_WHITE)
                        text_shadow = game_constants.FONT_PERFECTDOS.render(str(self.quantities[itemIndex]), False, game_constants.COLOR_SHADOW)
                        self.surface.blit(text_shadow, (self.width - text.get_width() - 4+2, itemIndex*16+yoffset+2))
                        self.surface.blit(text, (self.width - text.get_width() - 4, itemIndex*16+yoffset))
                SCREEN.blit(self.surface, (self.x, self.y))
        else:
            GAME.controlsText = game_constants.TEXT_ONMAP
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
    def getQuantities(self):
        if self.bquantity != None:
            self.quantities = self.bquantity.execute()
        else:
            self.quantities = []

class Entity:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.sprite = sprite
    def draw(self): # DRAW
        GAME.surface_map.blit(self.sprite, ((self.x - GAME.camera.x)*32, (self.y - GAME.camera.y)*32))
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
    def damage(self, value, damageType, damageSubtype):
        for action in self.actionTakeDamage:
            action.execute(value, damageType, damageSubtype)
    def die(self):
        for action in self.actionDeath:
            action.execute()
class Player(Creature):
    def __init__(self, x, y, sprite, modifiers, status, actionMove, actionStarve, actionAttack, actionDeath, actionTakeDamage, actionTurn):
        super().__init__(x, y, sprite)
        self.inventory = []
        self.name = 'Player'
        self.tag = 'human'
        self.xp = 0
        self.capacity = 100
        self.equipment = [None for i in range(8)]
        self.baseStats = [100 for i in range(14)]
        self.stats = self.baseStats
        self.hp = self.stats[0]
        self.hunger = 100
        self.damageStat = 10 # PLACEHOLDER
        self.active = True

        self.modifiers = modifiers
        self.status = status
        self.actionMove = actionMove
        self.actionStarve = actionStarve
        self.actionAttack = actionAttack
        self.actionDeath = actionDeath
        self.actionTakeDamage = actionTakeDamage
        self.actionTurn = actionTurn
    def input(self, key):
        if self.active: #TODO: PASARLO AL PLAYER
            if key == pygame.K_UP:
                self.move(0, -1)
                GAME.action = 'move'
            elif key == pygame.K_DOWN:
                self.move(0, 1)
                GAME.action = 'move'
            elif key == pygame.K_LEFT:
                self.move(-1, 0)
                GAME.action = 'move'
            elif key == pygame.K_RIGHT:
                self.move(1, 0)
                GAME.action = 'move'
    def move(self, dx, dy):
        if self.active:
            super().move(dx, dy)
    def execute_action(self):
        self.recalculateStats()
        for action in self.actionTurn:
            action.execute()
    def recalculateStats(self):
        self.modifiers = sorted(self.modifiers, key = lambda action: action.priority, reverse = True)
        self.stats = [stat for stat in self.baseStats]
        for modifier in self.modifiers:
            modifier.execute()
        if self.hp > self.stats[0]:
            self.hp = self.stats[0]
    def currentWeight(self):
        return sum([item.size for item in self.inventory] + [item.size for item in self.equipment if item != None])
    def onStarve(self):
        for action in self.actionStarve:
            action.execute()

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
class ConsumableMap(Consumable):
    def __init__(self, x, y, sprite, name, color, size, onUse, initialTarget, maxRange, targetCondition = [], useCondition = [], charges = 1):
        super().__init__(x, y, sprite, name, color, size, onUse, useCondition = [], charges = 1, target = 'map')
        self.initialTarget = initialTarget(self)
        self.maxRange = maxRange
        self.conditions = targetCondition
    def initialTarget(self):
        return initialTarget.execute()
    def targetCondition(self, x, y):
        for condition in self.conditions:
            if not condition.execute(x, y):
                return False
        return True
    def use(self, x, y):
        for action in self.onUse:
            action.execute(x, y)
        if self.used:
            GAME.player.inventory.remove(self)

class Component:
    def __init__(self, parent, priority = 0):
        self.parent = parent
        self.priority = priority
