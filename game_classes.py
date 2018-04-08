import pygame
import game_constants
import game_util
import random
import libtcodpy

pygame.init()

class Window_Description:
    def __init__(self):
        self.content_surface = pygame.Surface((game_constants.DESCWINDOW_WIDTH, game_constants.DESCWINDOW_HEIGHT))
        self.content_surface.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface = pygame.Surface((game_constants.DESCWINDOW_WIDTH, game_constants.DESCWINDOW_HEIGHT))
        self.surface.set_colorkey(game_constants.COLOR_COLORKEY)
        self.reset()
        self.index = 0
        self.need_redraw = True
        self.x = 0
        self.y = 0
    def updateInfo(self, icon_list, name, color, typename, content):
        self.surface.fill(game_constants.COLOR_COLORKEY)
        self.content_surface.fill(game_constants.COLOR_COLORKEY)
        self.icon = [pygame.transform.scale2x(icon_list[i]) for i in range(len(icon_list))]
        self.name = game_constants.FONT_PERFECTDOS.render(name, False, color)
        self.typename = game_constants.FONT_PERFECTDOS_SMALL.render(typename, False, game_constants.COLOR_WHITE)
        for lineIndex in range(len(content)):
            xoffset = 0
            for element in content[lineIndex]:
                text = game_constants.FONT_PERFECTDOS.render(element[0], False, element[1])
                self.surface.blit(text, (xoffset + 16, 96 + lineIndex*16))
                xoffset += text.get_width()
        self.index = 0
        self.need_redraw = True
    def update(self):
        self.index = (self.index + 1) % len(self.icon)
    def reset(self):
        self.updateInfo([game_constants.SPRITE_NULL], '', game_constants.COLOR_WHITE, '', [])
    def draw(self):
        if self.need_redraw:
            self.surface.blit(game_constants.SPRITE_DESCRIPTIONWINDOW, (0, 0))
            self.surface.blit(self.content_surface, (0, 0))
            self.surface.blit(self.name, (100, 24))
            self.surface.blit(self.typename, (100, 44))
            self.surface.blit(game_constants.SPRITE_BACK_68X68, (16, 16))
            self.surface.blit(self.icon[0], (16, 16)) # 0 is a placeholder, no animation shown
            self.need_redraw = False
            GAME.update_rects.append(GAME.surface_windows.blit(self.surface, (self.x, self.y)))

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
        # Initialization of game structures
        self.log = []
        self.creatures = []
        self.camera = Camera()
        self.windows = []
        self.items = []
        self.entities = []
        self.visualeffects = []
        self.visualactiveeffects = []
        self.descriptionWindow = Window_Description()

        # General
        self.turn_counter = 0
        self.controlsText = game_constants.TEXT_ONMAP
        self.long_log = False

        # Level and map variables
        self.level = 0
        self.map = None
        self.light_map = None

        # Surfaces definition
        self.surface_map = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))
        self.surface_log = pygame.Surface((402, game_constants.WINDOW_HEIGHT - game_constants.CAMERA_HEIGHT*32))
        #self.surface_effects = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))
        self.surface_status = pygame.Surface((game_constants.WINDOW_WIDTH - game_constants.LOG_WIDTH, game_constants.WINDOW_HEIGHT - game_constants.CAMERA_HEIGHT*32))
        self.surface_windows = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))
        self.surface_entities = pygame.Surface((game_constants.CAMERA_WIDTH*32, game_constants.CAMERA_HEIGHT*32))

        # Colorkeys and surface initialization
        #self.surface_effects.fill(game_constants.COLOR_COLORKEY)
        #self.surface_effects.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface_status.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface_windows.set_colorkey(game_constants.COLOR_COLORKEY)
        self.surface_windows.set_alpha(None)
        self.surface_entities.fill(game_constants.COLOR_COLORKEY)
        self.surface_entities.set_colorkey(game_constants.COLOR_COLORKEY)

        # Player Movement control
        self.player_moved = False
        self.movetimer = 10

        # Redraw surfaces control
        self.rd_log = True
        self.rd_sta = True
        self.rd_win = True
        self.update_rects = [] # Currently not used

        # Description Window
        self.draw_descriptionwindow = False
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
        self.lightmapInit()
        self.player.x = game_constants.MAP_WIDTH[self.level]//2
        self.player.y = game_constants.MAP_HEIGHT[self.level]//2
        self.creatures.append(self.player)
        game_util.map_light_update(self.light_map)
    def lightmapInit(self):
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
        self.sprite = sprite.convert()
        self.sprite_shadow = sprite_shadow.convert()
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
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.sprite = sprite.convert()
        self.surface = pygame.Surface((self.sprite.get_width(), self.sprite.get_height()))
        self.parent = None
        self.redraw = True
        self.visible = True
        self.active = True
        self.popup = None
        GAME.rd_win = True
        GAME.player.active = False
    def draw(self):
        if not self.visible:
            return
        if self.redraw:
            self.update()
        GAME.surface_windows.blit(self.surface, (self.x, self.y))
    def update(self):
        self.surface.blit(self.sprite, (0, 0))
    def destroy(self):
        if self in GAME.windows:
            GAME.windows.remove(self)
        if self.parent == None:
            GAME.player.active = True
        GAME.rd_win = True
    def input(self, key):
        if not self.active:
            return
    def popupInput(self, key):
        pass
    def destroyPopup(self):
        self.popup.destroy()
        self.popup = None
        self.active = True
        GAME.rd_win = True
class WindowList(Window):
    def __init__(self, x, y, sprite, descriptable):
        super().__init__(x, y, sprite)
        self.index = 0
        self.getItems()
    def input(self, key):
        if self.popup == None:
            super().input(key)
            self.getItems()
            self.basicControls(key)
            self.redraw = True
        else:
            self.popup.input(key)
            self.popup.redraw = True
        GAME.rd_win = True
    def basicControls(self, key):
        if key == 'up':
            self.index = (self.index - 1) % len(self.items)
        elif key == 'down':
            self.index = (self.index + 1) % len(self.items)
        elif key == 'cancel':
            self.destroy()
    def getItems(self):
        self.items = []
    def update(self):
        super().update()
    # def updateDescription(self):
    #     if self.needDesc:
    #         GAME.descriptionWindow.x = self.x - game_constants.DESCWINDOW_WIDTH
    #         GAME.descriptionWindow.y = min(self.index*16+self.yoffset + 32, game_constants.CAMERA_HEIGHT*32 - game_constants.DESCWINDOW_HEIGHT)
class WindowPopup(WindowList):
    def __init__(self, parent_window, window_name, x, y, sprite, options_list):
        super().__init__(x, y, sprite, False)
        self.parent_window = parent_window
        self.window_name = window_name
        self.items = options_list
    def input(self, key):
        super().input(key)
        self.basicControls(key)
        self.redraw = True
        GAME.rd_win = True
    def update(self):
        super().update()
        self.surface.fill(game_constants.COLOR_DARKRED, pygame.Rect(4, self.index*16 + 8, self.surface.get_width() - 8, 16)) # Highlight selected item
        for itemIndex in range(len(self.items)): # Draw item names
            game_util.draw_text_bg(self.surface, self.items[itemIndex][0], game_constants.POPUP_OFFSET_X, itemIndex*16 + 8, game_constants.FONT_PERFECTDOS, self.items[itemIndex][1], game_constants.COLOR_SHADOW)
    def basicControls(self, key):
        if key == 'up':
            self.index = (self.index - 1) % len(self.items)
        elif key == 'down':
            self.index = (self.index + 1) % len(self.items)
        elif key == 'cancel':
            self.parent_window.popupInput('cancel')
        elif key == 'use':
            self.parent_window.popupInput('use')
    def getItems(self):
        pass
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
    def draw(self):
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
    def __init__(self, x, y, sprite_list, portrait_list, stats, equipment, modifiers, status, actions, skilltree):
        super().__init__(x, y, ['player'], sprite_list, actions)
        self.inventory = []
        self.name = 'Player'
        self.portrait_list = portrait_list
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

        self.potion = None

        self.modifiers = modifiers
        self.status = status
        self.actions = actions
        self.skilltree = skilltree
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
class Potion():
    def __init__(self, name, sprite_list, actions, conditions, startCharges, maxCharges, description):
        self.name = name
        self.sprite_list = sprite_list
        self.actions = actions
        self.conditions = conditions
        self.charges = startCharges
        self.maxCharges = maxCharges
        self.description = description
    def drink(self):
        if self.charges > 0 and all([condition.execute() for condition in self.conditions]):
            for action in self.actions:
                action.execute()
            self.charges -= 1

class Component:
    def __init__(self, parent, priority = 0):
        self.parent = parent
        self.priority = priority
class Skill:
    def __init__(self, index, pos, name, description, sprite, move, req, maxRank):
        self.index = index
        self.x , self.y = pos
        self.name = name
        self.description = description
        self.sprite = sprite
        self.move = move
        self.req = req
        self.maxRank = maxRank
        self.rank = 0
    def onBuy(self):
        if self.maxRank != -1:
            self.rank += 1
