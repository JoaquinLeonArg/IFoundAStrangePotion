from pyglet import *
import game_constants
import game_util
import libtcodpy

global GAME, SCREEN

class Game:
    def __init__(self):
        self.btiles = graphics.Batch()
        self.bentities = graphics.Batch()
        self.debug = True

        # Initialization of game structures
        self.inputs = {value: False for value in ['up', 'down', 'left', 'right', 'use', 'cancel', 'pass']}
        self.input_timers = {value: 0 for value in ['up', 'down', 'left', 'right', 'use', 'cancel', 'pass']}
        self.log = []
        self.creatures = []
        self.camera = Camera()
        self.window = None
        self.items = []
        self.entities = []
        self.gfx = []
        self.gfx_active = []
        self.player = None

        # General
        self.turn_counter = 0
        self.controlsText = game_constants.TEXT_ONMAP
        self.long_log = False
        self.show_minimap = 0

        # Level and map variables
        self.level = 0
        self.map = None
        self.light_map = None

        # Player Movement control
        self.player_moved = False
        self.movetimer = 10

        # Description Window
        self.draw_descriptionwindow = False

        # Popup window
        self.popup_target_y = 0
        self.popup_time = -1
        self.popup_lines = []

        # Surfaces positions
        self.status_position_x, self.status_position_y = (game_constants.STATUS_IDLE_X, game_constants.STATUS_IDLE_Y)
        self.popup_position_x, self.popup_position_y = (game_constants.POPUP_IDLE_X, game_constants.POPUP_IDLE_Y)
        self.log_position_x, self.log_position_y = (game_constants.LOG_IDLE_X, game_constants.LOG_IDLE_Y)

    def start(self, player, map):
        self.player = player
        self.generate_map(map)
        self.creatures.append(GAME.player)
    def input(self, key, value):
        self.inputs[key] = value
    def update_inputs(self):
        if self.player.active:
            for key in ['left', 'right', 'up', 'down']:
                if self.inputs[key] and not self.input_timers[key] and not self.gfx_active:
                    self.player.input(key)
                    break
        for key in self.inputs:
            if self.inputs[key]:
                self.input_timers[key] = (self.input_timers[key] + 1) % game_constants.ANIMATIONS['player_delay']
            else:
                self.input_timers[key] = 0
    def set_popup(self, message_lines, max_time):
        if not message_lines:
            self.popup_target_y = 0
            self.popup_time = -1
        else:
            self.popup_target_y = len(message_lines)*12 + 20
            self.popup_time = max_time
            self.popup_lines = message_lines
    def update_popuptime(self):
        if self.popup_time > 0:
            self.popup_time -= 1
        elif self.popup_time == 0:
            self.set_popup(None, 0)
            self.popup_time = -1
        if self.popup_time == -1 and self.popup_position_y == 0:
            self.popup_lines = []
    def add_log_message(self, message, color):
        for i in reversed(game_util.wrap_text(message, 46)):
            self.log.insert(0, (i, color))
    def entities_execute(self):
        for entity in self.entities + self.creatures + self.items:
            entity.event('turn', [entity])
    def place_free(self, x, y):
        for obj in self.creatures:
            if obj.x == x and obj.y == y:
                return False
        return True
    def update_order(self):
        self.entities.sort(key = lambda e: e.priority)
        self.creatures.sort(key = lambda c: c.priority)
    def generate_map(self, gen_function):
        self.map, self.items, self.entities, self.creatures, self.player.x, self.player.y = gen_function(game_constants.MAP_WIDTH[self.level], game_constants.MAP_HEIGHT[self.level])
        self.lightmap_init()
        self.creatures.append(self.player)
        game_util.map_light_update(self.light_map)
        self.level += 1
    def lightmap_init(self):
        self.light_map = libtcodpy.map_new(game_constants.MAP_WIDTH[self.level], game_constants.MAP_HEIGHT[self.level])
        for x in range(game_constants.MAP_WIDTH[self.level]):
            for y in range(game_constants.MAP_HEIGHT[self.level]):
                libtcodpy.map_set_properties(self.light_map, x, y, self.map[x][y].transparent, self.map[x][y].passable)

class Tile:
    def __init__(self, x, y, passable, transparent, sprite_list, behaviors=[]):
        self.x = x
        self.y = y
        self.sprite = sprite.Sprite(sprite_list, x=0, y=0, batch=GAME.btiles)
        self.passable = passable
        self.transparent = transparent
        self.behaviors = behaviors
        self.sprite_shadow = None
        self.discovered = False
        libtcodpy.map_set_properties(GAME.light_map, self.x, self.y, self.passable, self.transparent)
        # self.generate_sprite_shadow()
    def event(self, event_name, args):
        for e in sorted(self.behaviors, key=lambda x: x.priority):
            e.execute(event_name, self, args)
    '''def outline(self, side):
        if side == 0:  # Left
            pygame.draw.line(self.sprite, game_constants.COLORS['black'], (0, 0), (0, 31))
        if side == 1:  # Up
            pygame.draw.line(self.sprite, game_constants.COLORS['black'], (0, 0), (31, 0))
        if side == 2:  # Right
            pygame.draw.line(self.sprite, game_constants.COLORS['black'], (31, 0), (31, 31))
        if side == 3:  # Down
            pygame.draw.line(self.sprite, game_constants.COLORS['black'], (0, 31), (31, 31))'''

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
    def update(self, x, y):
        self.x += (x-self.x-game_constants.CAMERA_WIDTH*16)*0.05
        self.y += (-y+game_constants.MAP_HEIGHT[0]*32-self.y-game_constants.CAMERA_HEIGHT*16)*0.05
        self.x = int(game_util.clamp(self.x, 32, game_constants.MAP_WIDTH[0]*32 - game_constants.CAMERA_WIDTH*32 - 32))
        self.y = int(game_util.clamp(self.y, 32, game_constants.MAP_HEIGHT[0]*32 - game_constants.CAMERA_HEIGHT*32 - 32))
class VisualEffect:
    def __init__(self, x, y, visible):
        self.x = x
        self.y = y
        self.visible = visible
    def update(self):
        pass
    def destroy(self):
        if self in GAME.gfx_active:
            GAME.gfx_active.remove(self)
        if self in GAME.gfx:
            GAME.gfx.remove(self)
class AnimationOnce(VisualEffect):
    def __init__(self, x, y, images, frame_wait):
        super().__init__(x, y, True, images)
        self.counter_next = 0
        self.frame = 0
        self.frame_wait = frame_wait
    def update(self):
        self.counter_next += 1
        if self.counter_next == self.frame_wait:
            self.frame += 1
            if self.frame == len(self.images):
                self.destroy()
                return
            self.counter_next = 0
            self.image = self.images[self.frame]
class CreatureMoveVisualEffect(VisualEffect):
    def __init__(self, creature, to_pos):
        super().__init__(creature.x*32, creature.y*32, True)
        self.sprite = creature.sprite
        self.creature = creature
        self.creature.visible = False
        self.dx, self.dy = to_pos[0]*32, to_pos[1]*32
        self.timer = 0
        self.speed = self.dx / game_constants.ANIMATIONS['move_speed'], self.dy / game_constants.ANIMATIONS['move_speed']
    def update(self):
        super().update()
        self.timer += 1
        if self.timer == game_constants.ANIMATIONS['move_speed']:
            self.destroy()
        self.x += self.speed[0]
        self.y += self.speed[1]
    def destroy(self):
        super().destroy()
        self.creature.visible = True

class Window:
    def __init__(self, x, y):
        self.x, self.y = (x, y)
        self.surface = pygame.Surface((game_constants.WINDOW_WIDTH, game_constants.WINDOW_HEIGHT))
        self.surface.set_colorkey(game_constants.COLOR_COLORKEY)
        self.visible = True
        self.active = True
        GAME.player.active = False
    def draw(self):
        if not self.visible:
            return
        self.surface.fill(game_constants.COLOR_COLORKEY)
    def destroy(self):
        GAME.window = None
        GAME.player.active = True
        GAME.surface_windows.fill(game_constants.COLOR_COLORKEY)
    def input(self, key):
        if not self.active:
            return
class SelectTarget:
    def __init__(self, parent_window, window_name, item, marker_sprite):
        self.previousCamera = (GAME.camera.x, GAME.camera.y)
        self.max_range = item.maxRange
        self.valid_tiles = [(x, y) for x in range(-self.max_range, self.max_range + 1) for y in range(-self.max_range, self.max_range + 1) if item.targetCondition(x, y)]
        self.updatePosition()
        self.surface = pygame.Surface(((self.max_range + 1)*64, (self.max_range + 1)*64))
        self.surface.set_colorkey(game_constants.COLOR_COLORKEY)
        self.parent = parent_window
        self.marker_sprite = marker_sprite
        self.marker_x, self.marker_y = item.getInitialTarget()
        self.visible = True
        self.active = True
        self.redraw = True
        self.redraw_all = True
    def updatePosition(self):
        if (GAME.camera.x, GAME.camera.y) != self.previousCamera:
            self.previousCamera = (GAME.camera.x, GAME.camera.y)
        self.x = (GAME.player.x - self.max_range)*32 - GAME.camera.x
        self.y = (GAME.player.y - self.max_range)*32 - GAME.camera.y
    def draw(self):
        if self.redraw_all:
            self.redraw_all = False
            self.surface.set_alpha()
            self.surface.fill(game_constants.COLOR_COLORKEY)
            self.updatePosition()
            self.update()
            self.surface.set_alpha(150)
        GAME.rd_win = True
        SCREEN.blit(self.surface, (self.x, self.y))
        SCREEN.blit(self.marker_sprite, (self.marker_x*32, self.marker_y*32))
    def update(self):
        self.updatePosition()
        for x in range(-self.max_range, self.max_range + 1):
            for y in range(-self.max_range, self.max_range + 1):
                if (x, y) in self.valid_tiles and game_util.simpledistance((x, y), (0, 0)) <= self.max_range:
                    self.surface.fill(game_constants.COLOR_GREEN, ((self.max_range + x)*32, (self.max_range + y)*32, 32, 32))
    def destroy(self):
        if self in GAME.windows:
            GAME.windows.remove(self)
        if self.parent == None:
            GAME.player.active = True
        GAME.rd_win = True
    def input(self, key):
        self.basicControls(key)
        self.redraw_all = True
        GAME.rd_win = True
    def basicControls(self, key):
        pass

class Entity:
    def __init__(self, x, y, tags, img, behaviors=[]):
        self.x = x
        self.y = y
        self.behaviors = behaviors
        self.tags = tags
        self.visible = True
        self.priority = 0
        self.sprite = sprite.Sprite(image.Animation.from_image_sequence(image.TextureGrid(image.ImageGrid(img, 1, int(img.width/32), item_width=32, item_height=32)), game_constants.ANIMATIONS['speed'], loop=True),
                                    x=0, y=0, batch=GAME.bentities)
        self.last_seen_pos = None
        self.last_seen_visible = True
    def draw_last_seen(self):
        self.draw()
        '''if self.last_seen_visible and self.last_seen_pos:
            GAME.surface_entities.blit(self.sprites_shadow[self.last_seen_image], (self.last_seen_pos[0] * 32 - GAME.camera.x, self.last_seen_pos[1] * 32 - GAME.camera.y))'''
    def destroy(self):
        GAME.entities.remove(self)
    def event(self, event_name, args = ()):
        for e in sorted(self.behaviors, key = lambda x: x.priority):
            e.execute(event_name, self, args)
class Creature(Entity):
    def __init__(self, x, y, tags, sprite_list, behaviors, stats, statmods = []):
        super().__init__(x, y, tags, sprite_list, behaviors)
        self.priority = 1
        self.behaviors = behaviors
        self.stats = stats
        self.statmods = statmods
        self.currentHitPoints = self.get_stat('HitPoints')
        self.currentMagicPoints = self.get_stat('MagicPoints')
    def is_enemy(self):
        return 'enemy' in self.tags

    def get_stat(self, stat_name):
        statmods = sorted(self.statmods, key = lambda x: x.priority)
        amount = 0
        for mod in statmods:
            amount = mod.execute(self, stat_name, amount)
        return max(int((self.stats[stat_name + 'Flat']) * self.stats[stat_name + 'Mult'] / 100) + amount, game_constants.BASE_STATS[stat_name + 'Flat'])
class Player(Creature):
    def __init__(self, x, y, sprite_list, portrait_list, stats, equipment, inventory, modifiers, status, skilltree, behaviors, statmods = []):
        super().__init__(x, y, ['player'], sprite_list, behaviors, stats, statmods)
        self.inventory = inventory
        self.name = 'Player'
        self.portrait_list = portrait_list
        self.xp = 0
        self.level = 1
        self.equipment = equipment
        self.currentHunger = game_constants.MAX_HUNGER
        self.active = True
        self.priority = 2

        self.potion = None

        self.status = status
        self.skilltree = skilltree
        self.behaviors = behaviors
    def input(self, key):
        if self.active:
            if key == 'up':
                self.event('move', (0, -1))
                game_util.map_light_update(GAME.light_map)
            elif key == 'down':
                self.event('move', (0, 1))
                game_util.map_light_update(GAME.light_map)
            elif key == 'left':
                self.event('move', (-1, 0))
                game_util.map_light_update(GAME.light_map)
            elif key == 'right':
                self.event('move', (1, 0))
                game_util.map_light_update(GAME.light_map)
    def can_attack(self, relative_pos):
        if self.equipment[0] is None: # No weapon equipped
            return [creature for creature in GAME.creatures if creature is not self and (creature.x, creature.y) == (self.x + relative_pos[0], self.y + relative_pos[1]) and 'monster' in creature.tags]
        return self.equipment[0].attackTargets(relative_pos) # Weapon range
    def tiles_attack(self, relative_pos):
        if self.equipment[0] is None: # No weapon equipped
            return [(self.x + relative_pos[0], self.y + relative_pos[1])]
        return self.equipment[0].attackTiles(relative_pos) # Weapon range
class Monster(Creature):
    def __init__(self, x, y, tags, sprite_list, name, drops, behaviors, stats, statmods = []):
        super().__init__(x, y, tags, sprite_list, behaviors, stats, statmods)
        self.name = name
        self.drops = drops
        self.tags = ['monster'] + tags
class Item(Entity):
    def __init__(self, x, y, tags, sprite_list, name, rarity, size, flavor):
        super().__init__(x, y, tags, sprite_list)
        self.name = name
        self.size = size
        self.rarity = rarity
        if self.rarity == 'Common':
            self.color = game_constants.COLOR_WHITE
        elif self.rarity == 'Rare':
            self.color = game_constants.COLOR_BLUE
        elif self.rarity == 'Mythic':
            self.color = game_constants.COLOR_CYAN
        elif self.rarity == 'Antique':
            self.color = game_constants.COLOR_ORANGE
        if self.rarity == 'Divine':
            self.color = game_constants.COLOR_DARKRED
        else:
            self.color = game_constants.COLOR_LIGHTGRAY
        self.description = {'flavor': flavor}
class Equipment(Item):
    def __init__(self, x, y, name, rarity, size, flavor, slot, stats, mods, requirements, tags, sprite_list):
        super().__init__(x, y, tags, sprite_list, name, rarity, size, flavor)
        self.slot = slot
        self.itemType = 'equipment'
        self.stats = stats
        self.mods = mods
        self.requirements = requirements
        self.description = {'flavor': self.description['flavor'],
                            'stats': [i.getDescription for i in self.stats],
                            'mods': [i.getDescription for i in self.mods],
                            'requirements': [i.getDescription for i in self.requirements]}
    def equip(self):
        for stat in self.stats:
            GAME.player.statmods.append(stat)
        for mod in self.mods:
            GAME.player.behaviors.append(mod)
    def unequip(self):
        for stat in self.stats:
            GAME.player.statmods.remove(stat)
        for mod in self.mods:
            GAME.player.behaviors.remove(mod)
    def can_equip(self):
        return all(requirement.execute(GAME.player) for requirement in self.requirements)
class Weapon(Equipment):
    def __init__(self, x, y, name, rarity, size, flavor, stats, mods, requirements, tags, sprite_list, spriteattack_list):
        super().__init__(x, y, name, rarity, size, flavor, 0, stats, mods, requirements, tags, sprite_list)
        self.spriteattack_list = spriteattack_list
        self.itemType = 'weapon'
    def attack_targets(self, relative_pos):
        pass
    def attack_tiles(self, relative_pos):
        pass
class Consumable(Item):
    def __init__(self, x, y, tags, sprite_list, name, color, size, flavor, effects, useCondition = [], charges = 1):
        super().__init__(x, y, tags, sprite_list, name, color, size, flavor)
        self.tags += ['target_self']
        self.onUse = effects
        self.useCondition = useCondition
        self.charges = charges
        self.displayCharges = self.charges == 1
        self.itemType = 'consumable'
        self.used = False
    def use(self, *args):
        for action in self.onUse:
            action.execute()
        if self.used:
            GAME.player.inventory.remove(self)
    def condition(self):
        for condition in self.useCondition:
            if not condition.execute():
                return False
        return True
    def got_used(self):
        return self.used
'''class ConsumableMap(Consumable):
    def __init__(self, x, y, tags, sprite_list, name, color, size, flavor, effects, initialTarget, maxRange, useCondition = [], charges = [], targetCondition = []):
        super().__init__(x, y,tags, sprite_list, name, color, size, flavor, effects, useCondition, charges)
        self.tags.remove('target_self')
        self.tags += ['target_map']
        self.initialTarget = initialTarget(self)
        self.maxRange = maxRange
        self.conditions = targetCondition
    def getInitialTarget(self):
        return self.initialTarget.execute()
    def targetCondition(self, x, y):
        for condition in self.conditions:
            if not condition.execute(x, y):
                return False
        return True
    def use(self, x, y):
        for action in self.onUse:
            action.execute(x, y)
        if self.used:
            GAME.player.inventory.remove(self)'''

class ShortSword(Weapon):
    def attack_targets(self, relative_pos):
        return [creature for creature in GAME.creatures if creature is not self and (creature.x, creature.y) == (GAME.player.x, GAME.player.y) + relative_pos and 'monster' in creature.tags]
    def attack_tiles(self, relative_pos):
        return [(GAME.player.x + relative_pos[0], GAME.player.y + relative_pos[1])]
class LongSword(Weapon):
    def attack_targets(self, relative_pos): # TODO: Fix this behavior
        if relative_pos[0] == 0:
            return [creature for creature in GAME.creatures if creature is not self and creature.x in [GAME.player.x + 1, GAME.player.x, GAME.player.x - 1] and creature.y == GAME.player.y + relative_pos[1] and 'monster' in creature.tags]
        elif relative_pos[1] == 0:
            return [creature for creature in GAME.creatures if creature is not self and creature.x == GAME.player.x + relative_pos[0] and creature.y in [GAME.player.y + 1, GAME.player.y, GAME.player.y - 1] and 'monster' in creature.tags]
    def attack_tiles(self, relative_pos):
        if relative_pos[0] == 0:
            return [(GAME.player.x - 1, GAME.player.y + relative_pos[1]), (GAME.player.x, GAME.player.y + relative_pos[1]), (GAME.player.x + 1, GAME.player.y + relative_pos[1])]
        elif relative_pos[1] == 0:
            return [(GAME.player.x + relative_pos[0], GAME.player.y - 1), (GAME.player.x + relative_pos[0], GAME.player.y), (GAME.player.x + relative_pos[0], GAME.player.y + 1)]
class Spear(Weapon):
    def attack_targets(self, relative_pos): # TODO: Check if this is working as intended
        return [creature for creature in GAME.creatures if creature is not self and ((creature.x, creature.y) == (GAME.player.x, GAME.player.y) + relative_pos or (creature.x, creature.y) == (GAME.player.x, GAME.player.y) + relative_pos*2) and 'monster' in creature.tags]

'''class Potion:
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
            self.charges -= 1'''

'''class Spell:
    def __init__(self, name, description, sprite_list, effects, costs, cd):
        self.name = name
        self.description = description
        self.sprite_list = sprite_list
        self.effects = effects
        self.costs = costs
        self.cd = cd'''

class Component:
    def __init__(self, parent):
        self.parent = parent
class Skill:
    def __init__(self, index, pos, name, description, sprite, move, req, max_rank):
        self.index = index
        self.x , self.y = pos
        self.name = name
        self.description = description
        self.sprite = sprite
        self.move = move
        self.req = req
        self.maxRank = max_rank
        self.rank = 0
    def on_buy(self):
        if self.maxRank != -1:
            self.rank += 1
    def is_maxed(self):
        return self.rank == self.maxRank
