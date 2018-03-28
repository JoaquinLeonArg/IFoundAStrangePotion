import pygame
import game_constants
import game_util
import random
import libtcodpy

pygame.init()

class MainMenu:
    def __init__(self):
        self.timer = 0

        self.option = 0
        self.characterNumber = 0

        self.surface_logo = pygame.Surface((game_constants.WINDOW_WIDTH, game_constants.WINDOW_HEIGHT))
        self.surface_options = pygame.Surface((game_constants.WINDOW_WIDTH, game_constants.WINDOW_HEIGHT))

        self.surface_options.set_colorkey(game_constants.COLOR_COLORKEY)

        self.optionsText = [game_constants.FONT_PERFECTDOS_LARGE.render('Start game', False, game_constants.COLOR_WHITE),
                        game_constants.FONT_PERFECTDOS_LARGE.render('Options', False, game_constants.COLOR_WHITE),
                        game_constants.FONT_PERFECTDOS_LARGE.render('Exit', False, game_constants.COLOR_WHITE)]

        self.rd_img = True
        self.rd_opt = True
        self.update_rects = []
class Game:
    def __init__(self):
        self.level = 0
        self.turn_counter = 0
        self.map = None
        self.light_map = None
        self.surface_map = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))
        self.surface_log = pygame.Surface((402, game_constants.WINDOW_HEIGHT - game_constants.CAMERA_HEIGHT*32))
        self.surface_effects = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))
        self.surface_status = pygame.Surface((game_constants.WINDOW_WIDTH - game_constants.LOG_WIDTH, game_constants.WINDOW_HEIGHT - game_constants.CAMERA_HEIGHT*32))
        self.surface_windows = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))
        self.surface_entities = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))
        self.log = []
        self.long_log = False
        self.creatures = []
        self.camera = Camera()
        self.windows = []
        self.popup_lock = False
        self.items = []
        self.entities = []
        self.controlsText = game_constants.TEXT_ONMAP
        self.visualeffects = []
        self.visualactiveeffects = []
        self.surface_effects.fill(game_constants.COLOR_COLORKEY)
        self.surface_effects.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface_status.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface_windows.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface_entities.fill(game_constants.COLOR_COLORKEY)
        self.surface_entities.set_colorkey(game_constants.COLOR_COLORKEY)

        self.player_moved = False

        self.rd_log = True
        self.rd_sta = True
        self.rd_win = True
        self.update_rects = []
    def addLogMessage(self, message, color):
        self.log.insert(0, (message, color))
        self.rd_log = True
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
    def updateOrder(self):
        self.entities.sort(key = lambda e: e.priority)
        self.creatures.sort(key = lambda c: c.priority)
    def generateMap(self, gen_function):
        self.map, self.items, self.entities, self.creatures = gen_function(game_constants.MAP_WIDTH[self.level], game_constants.MAP_HEIGHT[self.level])
        self.map_light_init()
        self.player.x = game_constants.MAP_WIDTH[self.level]//2
        self.player.y = game_constants.MAP_HEIGHT[self.level]//2
        self.creatures.append(self.player)
        game_util.map_light_update(self.light_map)
    def map_light_init(self):
        self.light_map = libtcodpy.map_new(game_constants.MAP_WIDTH[self.level], game_constants.MAP_HEIGHT[self.level])
        for x in range(game_constants.MAP_WIDTH[self.level]):
            for y in range(game_constants.MAP_HEIGHT[self.level]):
                libtcodpy.map_set_properties(self.light_map, x, y, self.map[x][y].transparent, self.map[x][y].passable)
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
    def images_at_loop(self, rects, colorkey = None):
        return self.images_at(rects, colorkey) + list(reversed(self.images_at(rects, colorkey)))
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
    def __init__(self):
        self.x = 0
        self.y = 0
    def update(self, x, y):
        self.x += (x-self.x-game_constants.CAMERA_WIDTH*16)*0.05
        self.y += (y-self.y-game_constants.CAMERA_HEIGHT*16)*0.05
        self.x = int(game_util.clamp(self.x, 0, game_constants.MAP_WIDTH[GAME.level]*32 - game_constants.CAMERA_WIDTH*32))
        self.y = int(game_util.clamp(self.y, 0, game_constants.MAP_HEIGHT[GAME.level]*32 - game_constants.CAMERA_HEIGHT*32))
class VisualEffect:
    def __init__(self, x, y, width, height, image = None, period = 0):
        self.time = 0
        self.x = x
        self.y = y
        self.visible = True
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.period = period
    def execute(self):
        self.time += 1
        if self.period > 0:
            self.time %= self.period
class ObjectMovement(VisualEffect):
    def __init__(self, parent, ix, iy, fx, fy, travelTime, images):
        self.parent = parent
        self.parent.visible = False
        self.x = ix
        self.y = iy
        self.frame = 0
        self.images = images
        self.image = images[0]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.xstep = (fx-ix)/travelTime
        self.ystep = (fy-iy)/travelTime
        self.surface = self.image
        self.travelTime = travelTime
    def execute(self):
        if self.travelTime > 0:
            self.x += self.xstep
            self.y += self.ystep
            self.travelTime -= 1
        else:
            GAME.visualactiveeffects.remove(self)
            self.parent.visible = True
        if libtcodpy.map_is_in_fov(GAME.light_map, self.parent.x, self.parent.y):
            self.visible = True
        else:
            self.visible = False
class Window:
    def __init__(self, parent, active, visible, image):
        self.x = game_constants.CAMERA_WIDTH*32 - game_constants.POPUP_WIDTH - game_constants.BORDER_THICKNESS*2
        self.y = 0
        self.width = game_constants.POPUP_WIDTH
        self.height = game_constants.CAMERA_HEIGHT*32
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.set_colorkey(game_constants.COLOR_COLORKEY)
        self.active = active
        self.visible = visible
        self.redraw = True
        self.parent = parent
        self.image = image
        self.descriptionWindow = None
        GAME.rd_win = True
    def draw(self):
        if self.visible:
            self.surface.fill(game_constants.COLOR_COLORKEY)
            if self.image != None:
                self.surface.blit(self.image, (0, 0))
            if self.title != '':
                game_util.draw_text(self.surface, self.title, game_constants.POPUP_OFFSET_X, game_constants.POPUP_OFFSET_Y, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
    def input(self):
        GAME.rd_win = True
    def destroy(self):
        if self in GAME.windows:
            GAME.windows.remove(self)
        if self.descriptionWindow in GAME.windows and self.descriptionWindow != None:
            self.descriptionWindow.destroy()
        if self.parent == None:
            GAME.player.active = True
        self.active = False
        GAME.surface_windows.fill(game_constants.COLOR_COLORKEY)
        GAME.rd_win = True
class WindowSelectable(Window):
    def __init__(self, parent, height, title, active, visible, image, bitems, binput, bquantity = None, descriptionWindow = None, itemType = 0):
        super().__init__(parent, active, visible, image)
        self.itemType = itemType
        self.height = height
        self.title = title
        self.bitems = bitems(self)
        if bquantity:
            self.bquantity = bquantity(self)
        else:
            self.bquantity = None
        self.binput = [action(self) for action in binput]
        self.getItems()
        if self.parent == None:
            self.y = game_constants.CAMERA_HEIGHT*32 - self.height - game_constants.BORDER_THICKNESS*2
        else:
            self.y = self.parent.y - self.height - 4
        self.index = 0
        GAME.player.active = False
        if descriptionWindow != None:
            self.descriptionWindow = descriptionWindow(self)
            self.descriptionWindow.item = self.items[0]
        else:
            self.descriptionWindow = None
    def input(self, key):
        super().input()
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
                self.surface.fill(game_constants.COLOR_DARKRED, pygame.Rect(4, self.index*16+yoffset, self.width - 8, 16))
                if self.itemType == 0:
                    for itemIndex in range(len(self.items)):
                        game_util.draw_text(self.surface, self.items[itemIndex].name, game_constants.POPUP_OFFSET_X, itemIndex*16+yoffset, game_constants.FONT_PERFECTDOS, self.items[itemIndex].color)
                        if len(self.quantities) == len(self.items):
                            text = game_constants.FONT_PERFECTDOS.render(str(self.quantities[itemIndex]), False, game_constants.COLOR_WHITE)
                            text_shadow = game_constants.FONT_PERFECTDOS.render(str(self.quantities[itemIndex]), False, game_constants.COLOR_SHADOW)
                            self.surface.blit(text_shadow, (self.width - text.get_width() - 4+2, itemIndex*16+yoffset+2))
                            self.surface.blit(text, (self.width - text.get_width() - 4, itemIndex*16+yoffset))
                elif self.itemType == 1:
                    for itemIndex in range(len(self.items)):
                        game_util.draw_text(self.surface, self.items[itemIndex][0], game_constants.POPUP_OFFSET_X, itemIndex*16+yoffset, game_constants.FONT_PERFECTDOS, self.items[itemIndex][1])
                        if len(self.quantities) == len(self.items):
                            text = game_constants.FONT_PERFECTDOS.render(str(self.quantities[itemIndex]), False, game_constants.COLOR_WHITE)
                            text_shadow = game_constants.FONT_PERFECTDOS.render(str(self.quantities[itemIndex]), False, game_constants.COLOR_SHADOW)
                            self.surface.blit(text_shadow, (self.width - text.get_width() - 4+2, itemIndex*16+yoffset+2))
                            self.surface.blit(text, (self.width - text.get_width() - 4, itemIndex*16+yoffset))
                GAME.surface_windows.blit(self.surface, (self.x, self.y))
        else:
            GAME.controlsText = game_constants.TEXT_ONMAP
            self.destroy()
    def getItems(self):
        self.items = self.bitems.execute()
        if self.bquantity != None:
            self.quantities = self.bquantity.execute()
        else:
            self.quantities = []
class Entity:
    def __init__(self, x, y, tags, sprite_list):
        self.x = x
        self.y = y
        self.tags = tags
        self.visible = True
        self.priority = 0
        self.sprite_list = sprite_list
        self.sprite = self.sprite_list[0]
        self.frame = 0
    def draw(self): # DRAW
        if self.visible:
            GAME.update_rects.append(GAME.surface_entities.blit(self.sprite, (self.x*32 - GAME.camera.x, self.y*32 - GAME.camera.y)))
    def update_frame(self):
        self.sprite = self.sprite_list[self.frame // game_constants.ANIMATION_WAIT % len(self.sprite_list)]
        self.frame += 1
    def move(self, dx, dy):
        pass
    def destroy(self):
        GAME.entities.remove(self)
class Creature(Entity):
    def __init__(self, x, y, tags, sprite_list, actions):
        super().__init__(x, y, tags, sprite_list)
        self.priority = 1
        self.actions = actions
    def isEnemy(self, target):
        return 'enemy' in self.tags
    def execute_action(self):
        for action in self.actions['turn']:
            action.execute()
    def move(self, dx = 0, dy = 0):
        super().move(dx, dy)
        if GAME.placeFree(self.x + dx, self.y + dy) and GAME.map[self.x + dx][self.y + dy].passable:
            GAME.visualactiveeffects.append(ObjectMovement(self, self.x*32, self.y*32, (self.x + dx)*32, (self.y + dy)*32, 8, [self.sprite]))
        for action in self.actions['move']:
            action.execute(dx, dy)
    def attack(self, obj):
        for action in self.actions['attack']:
            action.execute(obj)
    def damage(self, value, damageType, damageSubtype):
        for action in self.actions['takeDamage']:
            action.execute(value, damageType, damageSubtype)
    def die(self):
        for action in self.actions['death']:
            action.execute()
class Player(Creature):
    def __init__(self, x, y, sprite_list, stats, equipment, modifiers, status, actions):
        super().__init__(x, y, ['player'], sprite_list, actions)
        self.inventory = []
        self.name = 'Player'
        self.xp = 0
        self.level = 1
        self.equipment = equipment
        self.baseStats = stats
        self.stats = self.baseStats
        self.hp = self.stats[0]
        self.mana = self.stats[1]
        self.hunger = game_constants.MAX_HUNGER
        self.damageStat = 10 # PLACEHOLDER
        self.active = True
        self.priority = 2

        self.modifiers = modifiers
        self.status = status
        self.actions = actions
    def input(self, key):
        if self.active:
            if key == 'up':
                self.move(0, -1)
                game_util.map_light_update(GAME.light_map)
            elif key == 'down':
                self.move(0, 1)
                game_util.map_light_update(GAME.light_map)
            elif key == 'left':
                self.move(-1, 0)
                game_util.map_light_update(GAME.light_map)
            elif key == 'right':
                self.move(1, 0)
                game_util.map_light_update(GAME.light_map)
    def execute_action(self):
        self.recalculateStats()
        for action in self.actions['turn']:
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
        for action in self.actions['starve']:
            action.execute()
class Monster(Creature):
    def __init__(self, x, y, tags, sprite_list, name, actions, maxHp, drops):
        super().__init__(x, y, tags, sprite_list, actions)
        self.name = name
        self.maxHp = maxHp
        self.hp = maxHp
        self.damageStat = random.randint(1,6)
        self.drops = drops
        self.actions = actions
        self.tags = ['monster'] + tags
class Item(Entity):
    def __init__(self, x, y, tags, sprite_list, name, color, size, description):
        super().__init__(x, y, tags, sprite_list)
        self.name = name
        self.size = size
        self.color = color
        self.description = description
class Equipment(Item):
    def __init__(self, x, y, tags, sprite_list, name, color, size, description, slot, actionEquipment, requirements = []):
        super().__init__(x, y, tags, sprite_list, name, color, size, description)
        self.slot = slot
        self.itemType = 'equipment'
        self.actionEquipment = actionEquipment(self)
        self.requirements = [requirement(self) for requirement in requirements]
    def equip(self):
        self.actionEquipment.onEquip()
    def unequip(self):
        self.actionEquipment.onUnequip()
class Consumable(Item):
    def __init__(self, x, y, tags, sprite_list, name, color, size, description, effects, useCondition = [], charges = 1):
        super().__init__(x, y, tags, sprite_list, name, color, size, description)
        self.tags += ['target_self']
        self.onUse = effects
        self.useCondition = useCondition
        self.charges = charges
        self.displayCharges = self.charges == 1
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
    def __init__(self, x, y, tags, sprite_list, name, color, size, description, effects, initialTarget, maxRange, useCondition = [], charges = [], targetCondition = []):
        super().__init__(x, y,tags, sprite_list, name, color, size, description, effects, useCondition, charges)
        self.tags.remove('target_self')
        self.tags += ['target_map']
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
