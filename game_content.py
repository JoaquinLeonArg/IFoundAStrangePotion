import game_classes
import game_constants
import game_parsers
import game_mapping
import game_effects
import random
import math
import game_util
import pygame
import libtcodpy
import sys

pygame.init()

global GAME
GAME = None


# WINDOWS
class Window_PlayerInventory(game_classes.WindowList):
    def __init__(self):
        self.items = []
        super().__init__(0, 336, game_constants.SPRITE_ITEMSWINDOW, True)
    def input(self, key):
        if self.items:
            super().input(key)
            if key == 'use':
                item = GAME.player.inventory[self.index]
                self.active = False
                if item.itemType == 'consumable':
                    self.popup = game_classes.WindowPopupList(self, 'consumable', self.x + self.surface.get_width(), self.y, game_constants.SPRITE_OPTIONSWINDOW, [("Use", game_constants.COLOR_WHITE), ("Drop", game_constants.COLOR_WHITE), ("Cancel", game_constants.COLOR_WHITE)])
                elif item.itemType == 'equipment':
                    if GAME.player.inventory[self.index].canEquip():
                        color = game_constants.COLOR_WHITE
                    else:
                        color = game_constants.COLOR_DARKGRAY
                    self.popup = game_classes.WindowPopupList(self, 'equipment', self.x + self.surface.get_width(), self.y, game_constants.SPRITE_OPTIONSWINDOW, [("Equip", color), ("Drop", game_constants.COLOR_WHITE), ("Cancel", game_constants.COLOR_WHITE)])
                GAME.windows.append(self.popup)
        if key == 'cancel':
            super().input(key)
            GAME.player.active = True
    def update(self):
        super().update()
        game_util.draw_text_bg(self.surface, 'Inventory', game_constants.POPUP_OFFSET_X + 4, game_constants.POPUP_OFFSET_Y, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_SHADOW) # Draw title
        if self.items:
            self.surface.fill(game_constants.COLOR_DARKRED, pygame.Rect(4, self.index*16 + 32, self.surface.get_width() - 8, 16)) # Highlight selected item
            for itemIndex in range(len(self.items)): # Draw item names
                game_util.draw_text_bg(self.surface, self.items[itemIndex][1], game_constants.POPUP_OFFSET_X, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, self.items[itemIndex][2], game_constants.COLOR_SHADOW)
        else:
            game_util.draw_text_bg(self.surface, '- Empty -', game_constants.POPUP_OFFSET_X + 64,
                                   32, game_constants.FONT_PERFECTDOS, game_constants.COLOR_GRAY,
                                   game_constants.COLOR_SHADOW)
    def getItems(self):
        self.items = [(item.sprite_list, item.name, item.color, item.itemType, item.description) for item in GAME.player.inventory]
    def popupInput(self, key):
        super().popupInput(key)
        if key == 'use':
            if self.popup.index == 0: # Use
                item = GAME.player.inventory[self.index]
                if self.popup.window_name == 'consumable':
                    if item.condition():
                        if 'target_self' in item.tags:
                            item.use()
                            self.getItems()
                            self.destroyPopup()
                            GAME.action = 'item'
                            if self.index > 0:
                                self.index -= 1
                            #GAME.controlsText = game_constants.TEXT_ONINVENTORY
                        elif 'target_map' in item.tags:
                            self.destroyPopup()
                            self.popup = game_classes.SelectTarget(self, 'consumable_map', item, game_constants.SPRITE_MARKER)
                            GAME.windows.append(self.popup)
                            self.visible = False
                elif self.popup.window_name == 'equipment':
                    if item.canEquip():
                        if GAME.player.equipment[item.slot] == None:
                            GAME.player.equipment[item.slot] = item
                            item.equip()
                        else:
                            equipped = GAME.player.equipment[item.slot]
                            equipped.unequip()
                            GAME.player.inventory.append(equipped)
                            GAME.player.equipment[item.slot] = item
                            item.equip()
                        GAME.player.inventory.remove(item)
                        self.getItems()
                        self.destroyPopup()
                        if self.index > 0:
                            self.index -= 1
            elif self.popup.index == 1: # Drop
                item = GAME.player.inventory.pop(self.index)
                item.x, item.y = GAME.player.x, GAME.player.y
                GAME.items.append(item)
                self.getItems()
                self.destroyPopup()
                if self.index > 0:
                    self.index -= 1
                #GAME.controlsText = game_constants.TEXT_ONINVENTORY
            elif self.popup.index == 2: # Cancel
                self.destroyPopup()
                #GAME.controlsText = game_constants.TEXT_ONINVENTORY
        if key == 'cancel':
            self.destroyPopup()
class Window_SearchInventory(game_classes.WindowList):
    def __init__(self):
        super().__init__(0, 336, game_constants.SPRITE_ITEMSWINDOW, True)
    def input(self, key):
        super().input(key)
        if key == 'use':
            item = [item for item in GAME.items if (item.x == GAME.player.x and item.y == GAME.player.y)][self.index]
            if item.size <= GAME.player.getMaxCarry() - GAME.player.getCurrentCarry() and len(GAME.player.inventory) < 30:
                GAME.player.inventory.append(item)
                GAME.items.remove(item)
                self.getItems()
                if len(self.items) == 0:
                    self.destroy()
                if self.index > 0:
                    self.index -= 1
            else:
                GAME.addLogMessage('You are carrying too much.', game_constants.COLOR_INFO)
        if key == 'cancel':
            GAME.player.active = True
            # GAME.controlsText = game_constants.TEXT_ONMAP
    def update(self):
        super().update()
        game_util.draw_text_bg(self.surface, 'Found items', game_constants.POPUP_OFFSET_X + 4, game_constants.POPUP_OFFSET_Y, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_SHADOW) # Draw title
        self.surface.fill(game_constants.COLOR_DARKRED, pygame.Rect(4, self.index*16 + 32, self.surface.get_width() - 8, 16)) # Highlight selected item
        for itemIndex in range(len(self.items)): # Draw item names
            game_util.draw_text_bg(self.surface, self.items[itemIndex][1], game_constants.POPUP_OFFSET_X, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, self.items[itemIndex][2], game_constants.COLOR_SHADOW)
    def getItems(self):
        self.items = [(item.sprite_list, item.name, item.color, item.itemType, item.description) for item in GAME.items if item.x == GAME.player.x and item.y == GAME.player.y]
class Window_Equipment(game_classes.WindowList):
    def __init__(self):
        super().__init__(565, 150, game_constants.SPRITE_ITEMSWINDOW, True)
        self.item_positions = [(9, 98), (59, 24), (59, 71), (59, 121), (59, 171), (59, 221), (109, 98)]
    def input(self, key):
        if key == 'up' and self.index in [2, 3, 4, 5]:
            self.index -= 1
        if key == 'down' and self.index in [1, 2, 3, 4]:
            self.index += 1
        if key == 'left':
            if self.index in [1, 2, 3, 4, 5]:
                self.index = 0
            elif self.index == 6:
                self.index = 2
        if key == 'right':
            if self.index in [1, 2, 3, 4, 5]:
                self.index = 6
            elif self.index == 0:
                self.index = 2
        if key == 'cancel':
            GAME.windows.remove(self)
            GAME.player.active = True
    def update(self):
        super().update()
        pygame.draw.rect(self.surface, game_constants.COLOR_GREEN, (self.item_positions[self.index][0]-2, self.item_positions[self.index][1]-2, 34, 34), 2)
        for index, item in enumerate(self.items):
            if item:
                self.surface.blit(item.sprite, self.item_positions[index])
    def getItems(self):
        self.items = [item for item in GAME.player.equipment]
    '''def popupInput(self, key):
        super().popupInput(key)
        if key == 'use':
            if self.popup.index == 0:
                equipped = GAME.player.equipment[self.index]
                if equipped != None:
                    equipped.unequip()
                    GAME.player.inventory.append(equipped)
                    GAME.player.equipment[self.index] = None
            else:
                item = GAME.player.inventory[self.popup.items[self.popup.index - 1][2]]
                if GAME.player.equipment[item.slot] == None:
                    GAME.player.equipment[item.slot] = item
                    item.equip()
                else:
                    equipped = GAME.player.equipment[self.index]
                    equipped.unequip()
                    GAME.player.inventory.append(equipped)
                    GAME.player.equipment[item.slot] = item
                    item.equip()
                GAME.player.inventory.remove(item)
            self.getItems()
            self.destroyPopup()
            GAME.action = 'item'
            #GAME.controlsText = game_constants.TEXT_ONINVENTORY
        if key == 'cancel':
            self.destroyPopup()'''
class Window_Status(game_classes.WindowList):
    def __init__(self):
        for status in GAME.player.status:
            status.update()
        self.items = []
        super().__init__(0, 336, game_constants.SPRITE_ITEMSWINDOW, True)
    def input(self, key):
        super().input(key)
        if key == 'cancel':
            GAME.player.active = True
            # GAME.controlsText = game_constants.TEXT_ONMAP
    def update(self):
        for status in GAME.player.status:
            status.update()
        super().update()
        game_util.draw_text_bg(self.surface, 'Status', game_constants.POPUP_OFFSET_X + 4, game_constants.POPUP_OFFSET_Y, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_SHADOW) # Draw title
        self.surface.fill(game_constants.COLOR_DARKRED, pygame.Rect(4, self.index*16 + 32, self.surface.get_width() - 8, 16)) # Highlight selected item
        for itemIndex in range(len(self.items)): # Draw item names
            game_util.draw_text_bg(self.surface, self.items[itemIndex][0], game_constants.POPUP_OFFSET_X, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, self.items[itemIndex][1], game_constants.COLOR_SHADOW)
            if self.items[itemIndex][2] is not None:
                game_util.draw_text_bg(self.surface, str(self.items[itemIndex][2]), self.surface.get_width() - game_constants.POPUP_OFFSET_X - 48, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, self.items[itemIndex][1], game_constants.COLOR_SHADOW)
    def getItems(self):
        self.items = [(status.name, status.color, status.turns) for status in GAME.player.status]
class Window_Stats(game_classes.WindowList):
    def __init__(self):
        super().__init__(0, 336, game_constants.SPRITE_ITEMSWINDOW, True)
    def input(self, key):
        super().input(key)
        if key == 'cancel':
            GAME.player.active = True
            # GAME.controlsText = game_constants.TEXT_ONMAP
    def update(self):
        super().update()
        game_util.draw_text_bg(self.surface, 'Stats', game_constants.POPUP_OFFSET_X + 4, game_constants.POPUP_OFFSET_Y, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_SHADOW) # Draw title
        self.surface.fill(game_constants.COLOR_DARKRED, pygame.Rect(4, self.index*16 + 32, self.surface.get_width() - 8, 16)) # Highlight selected item
        for itemIndex in range(len(self.items)): # Draw item names
            game_util.draw_text_bg(self.surface, self.items[itemIndex][0], game_constants.POPUP_OFFSET_X, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_SHADOW)
            game_util.draw_text_bg(self.surface, str(self.items[itemIndex][1]), self.surface.get_width() - game_constants.POPUP_OFFSET_X - 48, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_SHADOW)
    def getItems(self):
        self.items =    [('Max HP: ', GAME.player.getMaxHitPoints()),
                        ('Max MP: ', GAME.player.getMaxMagicPoints()),
                        ('Physical Attack: ', GAME.player.getPhyAttack()),
                        ('Magical Atack: ', GAME.player.getMagAttack())]
class Window_SkillTree(game_classes.Window):
    def __init__(self):
        super().__init__(190, 16, game_constants.SPRITE_SKILLTREE)
        self.index = 0
    def input(self, key):
        super().input(key)
        current_skill = GAME.player.skilltree[self.index]
        if key == 'use':
            skills_check = any(skill.isMaxed() for skill in GAME.player.skilltree if skill.index in current_skill.req) or len(current_skill.req) == 0
            if skills_check:
                if current_skill.isNotMaxed():
                    current_skill.onBuy()
                else:
                    GAME.addLogMessage('Skill already maxed out.', game_constants.COLOR_INFO)
            else:
                GAME.addLogMessage('You need to unlock at least one skill previous to this one first.', game_constants.COLOR_INFO)
        if key == 'left' and current_skill.move[0] != None:
            self.index = current_skill.move[0]
        if key == 'right' and current_skill.move[1] != None:
            self.index = current_skill.move[1]
        if key == 'up' and current_skill.move[2] != None:
            self.index = current_skill.move[2]
        if key == 'down' and current_skill.move[3] != None:
            self.index = current_skill.move[3]
        if key == 'cancel':
            self.destroy()
            GAME.player.active = True
    def update(self):
        super().update()
        current_skill = next(skill for skill in GAME.player.skilltree if skill.index == self.index)
        for skill in GAME.player.skilltree:
            for skill_index in skill.req:
                other_skill = next(skill for skill in GAME.player.skilltree if skill.index == skill_index)
                if other_skill.rank == other_skill.maxRank:
                    color = game_constants.COLOR_WHITE
                else:
                    color = game_constants.COLOR_GRAY
                pygame.draw.line(self.surface, color, (skill.x*32 + 48, skill.y*32 + 64), (other_skill.x*32 + 48, other_skill.y*32 + 96), 3)
            self.surface.blit(skill.sprite, (skill.x*32 + 32, skill.y*32 + 64))
            if skill == current_skill:
                color = game_constants.COLOR_WHITE
            elif skill.rank == skill.maxRank:
                color = game_constants.COLOR_YELLOW
            elif skill.rank > 0:
                color = game_constants.COLOR_GREEN
            else:
                color = game_constants.COLOR_GRAY
            pygame.draw.rect(self.surface, color, (skill.x*32 + 32, skill.y*32 + 64, 32, 32), 3)
class Window_Trade(game_classes.WindowList):
    def __init__(self, items):
        super().__init__(0, 336, game_constants.SPRITE_TRADEWINDOW, True)
        self.wx = 0
        self.items = items
    def input(self, key):
        super().input(key)
        if key == 'left':
            if self.wx == 1:
                self.wx = 0
        if key == 'right':
            if self.wx == 0:
                self.wx = 1
        if key == 'use':
            pass
        if key == 'cancel':
            GAME.player.active = True
            # GAME.controlsText = game_constants.TEXT_ONMAP
    def update(self):
        super().update()
        game_util.draw_text_bg(self.surface, 'Trade', game_constants.POPUP_OFFSET_X + 4, game_constants.POPUP_OFFSET_Y, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_SHADOW) # Draw title
        self.surface.fill(game_constants.COLOR_DARKRED, pygame.Rect(4, self.index*16 + 32, self.surface.get_width() - 8, 16)) # Highlight selected item
        for itemIndex in range(len(self.items)): # Draw item names
            if self.items[itemIndex] is None:
                game_util.draw_text_bg(self.surface, self.equipmentNames[itemIndex], game_constants.POPUP_OFFSET_X, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, game_constants.COLOR_DARKGRAY, game_constants.COLOR_SHADOW)
            else:
                game_util.draw_text_bg(self.surface, self.items[itemIndex][1], game_constants.POPUP_OFFSET_X, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, self.items[itemIndex][2], game_constants.COLOR_SHADOW)
    def getItems(self):
        self.items = [(item.sprite_list, item.name, item.color, item.slot, item.description) if item is not None else None for item in GAME.player.equipment]
    def popupInput(self, key):
        super().popupInput(key)
        if key == 'use':
            if self.popup.index == 0:
                equipped = GAME.player.equipment[self.index]
                if equipped is not None:
                    equipped.unequip()
                    GAME.player.inventory.append(equipped)
                    GAME.player.equipment[self.index] = None
            else:
                item = GAME.player.inventory[self.popup.items[self.popup.index - 1][2]]
                if GAME.player.equipment[item.slot] is None:
                    GAME.player.equipment[item.slot] = item
                    item.equip()
                else:
                    equipped = GAME.player.equipment[self.index]
                    equipped.unequip()
                    GAME.player.inventory.append(equipped)
                    GAME.player.equipment[item.slot] = item
                    item.equip()
                GAME.player.inventory.remove(item)
            self.getItems()
            self.destroyPopup()
            GAME.action = 'item'
            #GAME.controlsText = game_constants.TEXT_ONINVENTORY
        if key == 'cancel':
            self.destroyPopup()
#class Window_Potion(game_classes.Window):
class Window_EquipSpell(game_classes.Window):
    def __init__(self):
        super().__init__(int(GAME.status_position_x) + 242 , int(GAME.status_position_y) + 72, pygame.Surface((362, 32)))
        self.images = game_parsers.get_animation('resources/graphics/ui/pointer.png', True)
        self.image_index = 0
        self.animation_timer = 0
        self.index = 0
    def update(self):
        super().update()
        self.surface.blit(self.images[self.image_index], (62*self.index, 0))
    def draw(self):
        self.redraw = True
        super().draw()
        if self.animation_timer > 8:
            self.animation_timer = 0
            self.image_index = (self.image_index + 1) % len(self.images)
        self.animation_timer += 1
    def input(self, key):
        if not self.active:
            return
        if key == 'left':
            self.index = (self.index - 1) % 6
        elif key == 'right':
            self.index = (self.index + 1) % 6
        GAME.rd_win = True

# BEHAVIORS
class behaviorPlayerBase():
    def execute(self, event, parent, args = ()):
        if event == 'move':
            GAME.movetimer = 8
            dx, dy = (args[0], args[1])
            targets = parent.canAttack((dx, dy))
            tiles = parent.tilesAttack((dx, dy))
            if targets:
                parent.event('attack', args = (targets, tiles))
                GAME.action = 'attack'
                return
            for entity in GAME.entities: # Movement to a tile with an open-able entity.
                if entity.x == parent.x + dx and entity.y == parent.y + dy:
                    if 'openable' in entity.tags:
                        if not entity.isOpen:
                            entity.open()
                            return
                    elif 'exit' in entity.tags:
                        GAME.level += 1
                        GAME.generateMap(game_mapping.mapgen_dungeon(100, 100))
            if GAME.placeFree(parent.x + dx, parent.y + dy): # Movement to a free tile.
                if GAME.map[parent.x + dx][parent.y + dy].passable:
                    GAME.visualactiveeffects.append(game_classes.CreatureMoveVisualEffect(parent, (parent.x, parent.y), (dx, dy), GAME.movetimer))
                    parent.x += dx
                    parent.y += dy
                    GAME.action = 'move'
            parent.currentHunger = max(0, parent.currentHunger - int(parent.stats['HungerFlat']*parent.stats['HungerMult']/100))
            if parent.currentHunger == 0:
                parent.damage(1, 'starvation', None)
        elif event == 'attack':
            for enemy in args[0]:
                linearDamage(parent, enemy, parent.getPhyAttack(), 'physical', None)
            for tile in args[1]:
                if parent.equipment[0] is not None:
                    GAME.visualeffects.append(game_classes.AnimationOnce(*tile, parent.equipment[0].spriteattack_list, game_constants.ANIMATION_WAIT*2))
        if event == 'takedamage':
            origin, amount, type, subtype = args[1], args[2], args[3], args[4]
            if  parent.currentHitPoints - amount <= 0:
                parent.event('die', parent)
                return
            else:
                parent.currentHitPoints -= amount
        elif event == 'die':
            pygame.quit()
            sys.exit()
class behaviorMonsterBase():
    def execute(self, event, parent, args = ()):
        if event == 'turn':
            if game_util.distance(parent, GAME.player) <= 1:
                parent.event('attack', [parent])
            elif game_util.distance(parent, GAME.player) <= 3:
                relative_pos = (parent.x - GAME.player.x, parent.y - GAME.player.y)
                if abs(relative_pos[0]) >= abs(relative_pos[1]) and relative_pos[0] != 0:
                    parent.event('move', (parent, (-game_util.sign(relative_pos[0]), 0)))
                elif abs(relative_pos[0]) <= abs(relative_pos[1]) and relative_pos[1] != 0:
                    parent.event('move', (parent, (0, -game_util.sign(relative_pos[1]))))
        if event == 'move':
            dx, dy = args[1][0], args[1][1]
            if GAME.placeFree(parent.x + dx, parent.y + dy): # Movement to a free tile.
                if GAME.map[parent.x + dx][parent.y + dy].passable:
                    GAME.visualactiveeffects.append(game_classes.CreatureMoveVisualEffect(parent, (parent.x, parent.y), (dx, dy), GAME.movetimer))
                    parent.x += dx
                    parent.y += dy
        if event == 'attack':
            linearDamage(parent, GAME.player, parent.getPhyAttack(), 'physical', None)
        if event == 'takedamage':
            origin, amount, type, subtype = args[1], args[2], args[3], args[4]
            if parent.currentHitPoints - amount <= 0:
                parent.event('die', [parent])
                return
            else:
                parent.currentHitPoints -= amount
        if event == 'die':
            GAME.creatures.remove(parent)

# DIRECT EFFECTS
def e_flatheal(target, amount):
    if target.currentHitPoints + amount > target.getMaxHitPoints():
        value = target.getMaxHitPoints() - target.currentHitPoints
        GAME.addLogMessage(target.name + ' heals to max!', game_constants.COLOR_HEAL)
    else:
        value = amount
        GAME.addLogMessage(target.name + ' heals for ' + str(value) + '.', game_constants.COLOR_HEAL)
    target.currentHitPoints += value

# CONDITIONS
def c_notusable():
    return False
def c_creatureinlocation(x, y):
    for creature in GAME.creatures:
        if creature.x == x and creature.y == y:
            return True
    return False

# ENTITIES
class n_door(game_classes.Entity):
    def __init__(self, x, y):
        super().__init__(x, y, ['openable', 'door', 'impassable'], game_parsers.get_animation('resources/graphics/entities/door_closed.png'))
        self.sprite_open = game_parsers.get_animation('resources/graphics/entities/door_open.png')
        self.isOpen = False
    def open(self):
        self.isOpen = True
        self.sprite_list = self.sprite_open
        GAME.map[self.x][self.y].passable = True
        GAME.map[self.x][self.y].transparent = True
        libtcodpy.map_set_properties(GAME.light_map, self.x, self.y, True, True)
        game_util.map_light_update(GAME.light_map)
        GAME.action = 'open'
    def destroy(self):
        super().destroy()
        GAME.map[self.x][self.y].passable = True
        GAME.map[self.x][self.y].transparent = True
        libtcodpy.map_set_properties(GAME.light_map, self.x, self.y, True, True)
        game_util.map_light_update(GAME.light_map)
    def execute_action(self):
        pass
def n_exit(x, y):
    return game_classes.Entity(x, y, ['exit'], [game_parsers.get_animation('resources/graphics/entities/door_open.png')])

# MONSTERS
def m_slime(x, y):
    return game_classes.Monster(x, y, [], game_parsers.get_animation('resources/graphics/entities/slime.png'), 'Slime', [], [(behaviorMonsterBase(), 50)], slime_stats())

# PLAYABLE CHARACTERS
def p_normal(x, y):
        return game_classes.Player(
            x = x,
            y = y,
            sprite_list = game_parsers.get_animation('resources/graphics/entities/player.png', repeat = True),
            portrait_list = [pygame.Surface((32, 32))],
            stats = player_basicstats(),
            equipment = [None for _ in range(7)],
            inventory = [drill(0, 0)],
            modifiers = [],
            status = [],
            skilltree = [],
            behaviors = [(behaviorPlayerBase(), 50)]
            )

def player_basicstats():
    stats = {
        'PhyAttackFlat': 15,
        'PhyAttackMult': 20,
        'HitPointsFlat': 100,
        'PhyArmorFlat': 20
    }
    return game_util.add_dicts(game_constants.BASE_STATS, stats)
def slime_stats():
    stats = {
        'PhyAttackFlat': 2,
        'PhyAttackMult': 10,
        'PhyArmorFlat': 5
    }
    return game_util.add_dicts(game_constants.BASE_STATS, stats)

def equipment(name, x = 0, y = 0):
    item = game_parsers.get_equipment(name)
    return game_classes.Equipment(x, y, *(item[i] if i != 9 else game_parsers.get_animation('resources/graphics/equipment/' + item[i] + '.png', repeat = True) for i in range(10)))
def weapon(name, x = 0, y = 0):
    item = game_parsers.get_weapon(name)
    weapontype = item[4]
    temp = [item[i] for i in range(len(item)) if i != 4]
    return eval('game_classes.{}'.format(weapontype))(x, y, *(game_parsers.get_animation('resources/graphics/equipment/{}.png'.format(temp[i]), repeat = True) if i == 8 else game_parsers.get_animation('resources/graphics/effects/{}.png'.format(temp[i])) if i == 9 else temp[i] for i in range(11)))

def linearDamage(origin, target, amount, maintype, subtype):
    if maintype == 'physical':
        damage = math.ceil((amount)*(4**(-target.getPhyArmor()/300)))
    elif maintype == 'magical':
        damage = math.ceil((amount)*(4**(-target.getMagArmor()/300)))
    GAME.addLogMessage(origin.name + ' damages ' + target.name + ' for ' + str(damage) + '.', game_constants.COLOR_LIGHTRED)
    origin.event('dodamage', (target, origin, damage, maintype, subtype))
    target.event('takedamage', (target, origin, damage, maintype, subtype))


def drill(x, y):
    return game_classes.ShortSword(x, y, 'Adamantite drill', 'Mythic', 3, 'This is the drill that will pierce the heavens.', [], [], [(game_effects.drillMod(), 10)], [], ['drill'], game_parsers.get_animation('resources/graphics/equipment/drill1.png', repeat = True), [])

def stoneTileOnDestroy(parent):
    GAME.map[parent.x][parent.y] = game_classes.Tile(parent.x, parent.y, True, True, pygame.image.load('resources/graphics/tiles/floor_dirt.png'))