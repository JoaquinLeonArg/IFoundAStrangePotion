import game_classes
import game_constants
import random
import math
import game_util
import pygame
import libtcodpy
import sys

pygame.init()

################################################# CONSTANTS #################################################

SPRITESHEET_PLAYER = game_classes.Spritesheet('resources/graphics/player.png')
SPRITESHEET_TILES = game_classes.Spritesheet('resources/tiles.png')
SPRITESHEET_CONSUMABLES = game_classes.Spritesheet('resources/consumables.png')
SPRITESHEET_ENTITIES = game_classes.Spritesheet('resources/entities.png')
SPRITESHEET_ICONS = game_classes.Spritesheet('resources/icons.png')
SPRITESHEET_MONSTERS = game_classes.Spritesheet('resources/graphics/monsters_animated.png')
SPRITESHEET_EQUIPMENT_HEAD = game_classes.Spritesheet('resources/graphics/equipment_head_animated.png')
SPRITESHEET_PORTRAITS = game_classes.Spritesheet('resources/graphics/character_faces.png')
SPRITESHEET_SKILLICONS = game_classes.Spritesheet('resources/graphics/skill_icons.png')

################################################# CLASSES #################################################

# WINDOWS
class Window_PlayerInventory(game_classes.WindowList):
    def __init__(self):
        super().__init__(0, 336, game_constants.SPRITE_ITEMSWINDOW, True)
    def input(self, key):
        super().input(key)
        if key == 'use':
            item = GAME.player.inventory[self.index]
            self.active = False
            if item.itemType == 'consumable':
                self.popup = game_classes.WindowPopupList(self, 'consumable', self.x + self.surface.get_width(), self.y, game_constants.SPRITE_OPTIONSWINDOW, [("Use", game_constants.COLOR_WHITE), ("Drop", game_constants.COLOR_WHITE), ("Cancel", game_constants.COLOR_WHITE)])
                # GAME.controlsText = game_constants.TEXT_ONPOPUP
            elif item.itemType == 'equipment':
                if GAME.player.inventory[self.index].canEquip():
                    color = game_constants.COLOR_WHITE
                else:
                    color = game_constants.COLOR_DARKGRAY
                self.popup = game_classes.WindowPopupList(self, 'equipment', self.x + self.surface.get_width(), self.y, game_constants.SPRITE_OPTIONSWINDOW, [("Equip", color), ("Drop", game_constants.COLOR_WHITE), ("Cancel", game_constants.COLOR_WHITE)])
                # GAME.controlsText = game_constants.TEXT_ONPOPUP
            GAME.windows.append(self.popup)
            # GAME.windows.append(self.popupwindow)
        elif key == 'cancel':
            GAME.player.active = True
            # GAME.controlsText = game_constants.TEXT_ONMAP
    def update(self):
        super().update()
        game_util.draw_text_bg(self.surface, 'Inventory', game_constants.POPUP_OFFSET_X + 4, game_constants.POPUP_OFFSET_Y, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_SHADOW) # Draw title
        self.surface.fill(game_constants.COLOR_DARKRED, pygame.Rect(4, self.index*16 + 32, self.surface.get_width() - 8, 16)) # Highlight selected item
        for itemIndex in range(len(self.items)): # Draw item names
            game_util.draw_text_bg(self.surface, self.items[itemIndex][1], game_constants.POPUP_OFFSET_X, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, self.items[itemIndex][2], game_constants.COLOR_SHADOW)
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
            if item.size <= GAME.player.stats[10] - GAME.player.currentWeight() and len(GAME.player.inventory) < 30:
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
        super().__init__(0, 336, game_constants.SPRITE_ITEMSWINDOW, True)
        self.equipmentNames = ['- Main hand -', '- Head      -', '- Chest     -', '- Legs      -', '- Feet      -', '- Hand      -', '- Neck      -']
    def input(self, key):
        super().input(key)
        if key == 'use':
            available_items = [('None', game_constants.COLOR_GRAY, -1)] + [(item.name, item.color, GAME.player.inventory.index(item)) for item in GAME.player.inventory if item.itemType == 'equipment' and item.slot == self.index and item.canEquip()]
            self.active = False
            self.popup = game_classes.WindowPopupList(self, 'equipable', self.x + self.surface.get_width(), self.y, game_constants.SPRITE_OPTIONSWINDOW, available_items)
            GAME.windows.append(self.popup)
            # UPDATE GAME CONTROLS TEXT
        if key == 'cancel':
            GAME.player.active = True
            # GAME.controlsText = game_constants.TEXT_ONMAP
    def update(self):
        super().update()
        game_util.draw_text_bg(self.surface, 'Equipment', game_constants.POPUP_OFFSET_X + 4, game_constants.POPUP_OFFSET_Y, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_SHADOW) # Draw title
        self.surface.fill(game_constants.COLOR_DARKRED, pygame.Rect(4, self.index*16 + 32, self.surface.get_width() - 8, 16)) # Highlight selected item
        for itemIndex in range(len(self.items)): # Draw item names
            if self.items[itemIndex] == None:
                game_util.draw_text_bg(self.surface, self.equipmentNames[itemIndex], game_constants.POPUP_OFFSET_X, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, game_constants.COLOR_DARKGRAY, game_constants.COLOR_SHADOW)
            else:
                game_util.draw_text_bg(self.surface, self.items[itemIndex][1], game_constants.POPUP_OFFSET_X, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, self.items[itemIndex][2], game_constants.COLOR_SHADOW)
    def getItems(self):
        self.items = [(item.sprite_list, item.name, item.color, item.slot, item.description) if item != None else None for item in GAME.player.equipment]
    def popupInput(self, key):
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
            self.destroyPopup()
class Window_Status(game_classes.WindowList):
    def __init__(self):
        for status in GAME.player.status:
            status.update()
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
            if self.items[itemIndex][2] != None:
                game_util.draw_text_bg(self.surface, String(self.items[itemIndex][2]), self.surface.get_width() - game_constants.POPUP_OFFSET_X - 48, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, self.items[itemIndex][1], game_constants.COLOR_SHADOW)
    def getItems(self):
        self.items = [(status.name, status.color, status.turns) for status in GAME.player.status]
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
            if self.items[itemIndex] == None:
                game_util.draw_text_bg(self.surface, self.equipmentNames[itemIndex], game_constants.POPUP_OFFSET_X, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, game_constants.COLOR_DARKGRAY, game_constants.COLOR_SHADOW)
            else:
                game_util.draw_text_bg(self.surface, self.items[itemIndex][1], game_constants.POPUP_OFFSET_X, itemIndex*16 + 32, game_constants.FONT_PERFECTDOS, self.items[itemIndex][2], game_constants.COLOR_SHADOW)
    def getItems(self):
        self.items = [(item.sprite_list, item.name, item.color, item.slot, item.description) if item != None else None for item in GAME.player.equipment]
    def popupInput(self, key):
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
            self.destroyPopup()
#class Window_Potion(game_classes.Window):

# BEHAVIORS
def b_playerbase(event, args = None):
    if event == 'move':
        GAME.movetimer = 10
        dx, dy = (args[0], args[1])
        for entity in GAME.entities: # Movement to a tile with an open-able entity.
            if entity.x == GAME.player.x + dx and entity.y == GAME.player.y + dy:
                if 'openable' in entity.tags:
                    if not entity.isOpen:
                        entity.open()
                        return
                elif 'exit' in entity.tags:
                    entity.changeLevel()
        if GAME.placeFree(GAME.player.x + dx, GAME.player.y + dy): # Movement to a free tile.
            if GAME.map[GAME.player.x + dx][GAME.player.y + dy].passable:
                GAME.player.x += dx
                GAME.player.y += dy
                GAME.action = 'move'
        else:
            for creature in GAME.creatures: # Movement to a tile with an enemy.
                if (creature is not GAME.player and creature.x == GAME.player.x + dx and creature.y == GAME.player.y + dy):
                    return
        GAME.player.currentHunger = max(0, GAME.player.currentHunger - GAME.player.stats['HungerFlat'])
        if GAME.player.currentHunger == 0:
            GAME.player.damage(1, 'starvation', None)
    elif event == 'death':
        pygame.quit()
        sys.exit()

#STATUS
class s_hunger(game_classes.Component):
    def update(self):
        self.turns = None
        if GAME.player.currentHunger > 50:
            self.name = 'Well fed'
            self.color = game_constants.COLOR_GREEN
        elif GAME.player.currentHunger > 30:
            self.name = 'Hungry'
            self.color = game_constants.COLOR_YELLOW
        else:
            self.name = 'Starving'
            self.color = game_constants.COLOR_RED
class s_health(game_classes.Component):
    def update(self):
        self.turns = None
        if self.parent.hp > self.parent.stats[0]*0.5:
            self.name = 'Healty'
            self.color = game_constants.COLOR_GREEN
        elif self.parent.hp > self.parent.stats[0]*0.3:
            self.name = 'Wounded'
            self.color = game_constants.COLOR_YELLOW
        else:
            self.name = 'Dying'
            self.color = game_constants.COLOR_RED

# EFFECTS
class e_getused(game_classes.Component):
    def execute(self, x=0, y=0):
        self.parent.used = True

        # DIRECT EFFECTS
class e_flatheal(game_classes.Component):
    def __init__(self, parent, amount):
        super().__init__(parent)
        self.amount = amount
    def execute(self):
        if self.parent.hp + self.amount > self.parent.stats[0]:
            value = self.parent.stats[0] - self.parent.hp
            GAME.addLogMessage(self.parent.name + ' heals to max!', game_constants.COLOR_HEAL)
        else:
            value = self.amount
            GAME.addLogMessage(self.parent.name + ' heals for ' + str(value) + '.', game_constants.COLOR_HEAL)
        self.parent.hp += value
class e_percheal(game_classes.Component):
    def __init__(self, parent, percent = 0.25):
        super().__init__(parent)
        self.percent = percent
    def execute(self):
        if math.floor(self.parent.stats[0]*self.percent + self.parent.hp) > self.parent.stats[0]:
            value = self.parent.stats[0] - self.parent.hp
            GAME.addLogMessage(self.parent.name + ' heals to max!', game_constants.COLOR_HEAL)
        else:
            value = math.floor(self.parent.stats[0]*self.percent)
            GAME.addLogMessage(self.parent.name + ' heals for ' + str(value) + '.', game_constants.COLOR_HEAL)
        self.parent.hp += value
class e_venom(game_classes.Component):
    def __init__(self, parent, amount, turns = -1):
        super().__init__(parent)
        self.amount = amount
        self.turns = turns
    def execute(self):
        if self.turns != 0:
            self.turns -= 1
            GAME.addLogMessage(self.parent.name + ' takes ' + str(self.amount) + ' damage from venom.', consants.COLOR_VENOM)
            self.parent.damage(self.amount)
class e_createbomb(game_classes.Component):
    def __init__(self, parent, turns, radius, damage):
        super().__init__(parent)
        self.turns = turns
        self.radius = radius
        self.damage = damage
    def execute(self):
        GAME.entities.append(n_bomb(self.parent.x, self.parent.y, SPRITESHEET_CONSUMABLES.image_at((32, 0, 32, 32), game_constants.COLOR_COLORKEY), self.turns, self.radius, self.damage))
        GAME.addLogMessage('The bomb will explode in ' + str(self.turns) + ' turns!', game_constants.COLOR_ALLY)
class e_eat(game_classes.Component):
    def __init__(self, parent, amount):
        super().__init__(parent)
        self.amount = amount
    def execute(self):
        if self.parent.hunger + self.amount > game_constants.MAX_HUNGER:
            value = game_constants.MAX_HUNGER - self.parent.hunger
            GAME.addLogMessage(self.parent.name + ' is full!', game_constants.COLOR_HEAL)
        else:
            value = self.amount
            GAME.addLogMessage(self.parent.name + ' eats.', game_constants.COLOR_HEAL)
        self.parent.hunger += value

        # DISTANCE EFFECTS

class e_createbomb_l():
    def __init__(self, turns, radius, damage):
        self.turns = turns
        self.radius = radius
        self.damage = damage
    def execute(self, x, y):
        GAME.entities.append(n_bomb(x, y, SPRITESHEET_CONSUMABLES.image_at((32, 0, 32, 32), game_constants.COLOR_COLORKEY), self.turns, self.radius, self.damage))
        GAME.addLogMessage('The bomb will explode in ' + str(self.turns) + ' turns!', game_constants.COLOR_ALLY)
class e_damage_l():
    def __init__(self, amount, damageType, damageSubtype):
        self.amount = amount
        self.damageType = damageType
        self.damageSubtype = damageSubtype
    def execute(self, x, y):
        for game_classes.Monster in GAME.creatures:
            if game_classes.Monster.x == x and game_classes.Monster.y == y:
                game_classes.Monster.damage(self.amount, self.damageType, self.damageSubtype)

# CONDITIONS
def c_playnotfullhealth():
    return GAME.player.currentHitPoints < GAME.player.getMaxHitPoints
def c_playnotfullhunger():
    return GAME.player.currentHunger < game_constants.MAX_HUNGER
def c_notusable():
    return False
def c_creatureinlocation(x, y):
    for creature in GAME.creatures:
        if creature.x == x and creature.y == y:
            return True
    return False

# ENTITIES
class n_door(game_classes.Entity):
    def __init__(self, x, y, sprite_closed, sprite_open):
        super().__init__(x, y, ['openable', 'door', 'impassable'], [sprite_closed])
        self.sprite_open = sprite_open
        self.isOpen = False
    def open(self):
        self.isOpen = True
        self.sprite_list = [self.sprite_open]
        GAME.map[self.x][self.y].passable = True
        GAME.map[self.x][self.y].transparent = True
        libtcodpy.map_set_properties(GAME.light_map, self.x, self.y, True, True)
        game_util.map_light_update(GAME.light_map)
    def destroy(self):
        super().destroy()
        GAME.map[self.x][self.y].passable = True
        GAME.map[self.x][self.y].transparent = True
        libtcodpy.map_set_properties(GAME.light_map, self.x, self.y, True, True)
        game_util.map_light_update(GAME.light_map)
    def execute_action(self):
        pass
class n_bomb(game_classes.Entity):
    def __init__(self, x, y, sprite, turns, radius, damage):
        super().__init__(x, y, ['explosive', 'impassable'], [sprite])
        self.turns = turns
        self.radius = radius
        self.damage = damage
        GAME.visualactiveeffects.append(game_classes.ObjectMovement(self, GAME.player.x*32, GAME.player.y*32, x*32, y*32, 100, [SPRITESHEET_CONSUMABLES.image_at((32, 0, 32, 32), colorkey = game_constants.COLOR_COLORKEY)]))
    def execute_action(self):
        if self.turns > 0:
            self.turns -= 1
        else:
            for game_classes.Tilex in range(self.x - self.radius, self.x + self.radius+1):
                for game_classes.Tiley in range(self.y - self.radius, self.y + self.radius+1):
                    if game_classes.Tilex < game_constants.MAP_WIDTH[GAME.level] and game_classes.Tiley < game_constants.MAP_HEIGHT[GAME.level]:
                        if game_util.simpledistance((game_classes.Tilex, game_classes.Tiley), (self.x, self.y)) <= self.radius:
                            GAME.visualeffects.append(v_square_fadeout(game_classes.Tilex, game_classes.Tiley, game_constants.COLOR_RED))
                            GAME.map[game_classes.Tilex][game_classes.Tiley].onDestroy()
            for creature in GAME.creatures:
                if game_util.distance(self, creature) <= self.radius:
                    creature.damage(self.damage, 'physical', 'explosion')
            for entity in GAME.entities:
                if game_util.simpledistance((entity.x, entity.y), (self.x, self.y)) <= self.radius:
                    entity.destroy()
            game_util.map_light_update(GAME.light_map)
            GAME.addLogMessage('You hear a loud explosion.', game_constants.COLOR_INFO)
class n_exit(game_classes.Entity):
    def __init__(self, x, y):
        super().__init__(x, y, ['exit'], [SPRITESHEET_ENTITIES.image_at((64, 0, 32, 32), colorkey = game_constants.COLOR_COLORKEY)])
    def changeLevel(self):
        GAME.level += 1
        GAME.generateMap(map_init_dungeon)

# VISUALS
class v_square_fadeout(game_classes.VisualEffect):
    def __init__(self, x, y, color):
        super().__init__(x*32, y*32, 32, 32)
        pygame.draw.rect(self.surface, color, (0, 0, 32, 32))
        self.maxtime = random.randint(15, 60)
    def execute(self):
        super().execute()
        self.surface.set_alpha(255*(self.maxtime - self.time)/self.maxtime)
        if self.time > self.maxtime:
            GAME.visualeffects.remove(self)

# TILES
class t_cave_wall(game_classes.Tile):
    def __init__(self, x, y):
        if random.random() <= game_constants.CHANCE_WALL1TREASURE:
            self.has_treasure = True
            sprite_normal = SPRITESHEET_TILES.image_at((0, 32*random.choice([0, 1, 2]), 32, 32)) #TODO: CHANGE TO TREASURE ROCK SPRITE
            sprite_dark = SPRITESHEET_TILES.image_at((0, 32*random.choice([0, 1, 2]) + 96, 32, 32))
        else:
            self.has_treasure = False
            sprite_normal = SPRITESHEET_TILES.image_at((0, 32*random.choice([0, 1, 2]), 32, 32))
            sprite_dark = SPRITESHEET_TILES.image_at((0, 32*random.choice([0, 1, 2]) + 96, 32, 32))
        super().__init__(x, y, False, False, sprite_normal, sprite_dark)
    def onDestroy(self):
        GAME.map[self.x][self.y] = t_cave_floor(self.x, self.y) # Destructable
        if self.has_treasure:
            #GAME.items.append(i_diamond(self.x, self.y)) #TODO: Put gold or something here
            pass
class t_cave_floor(game_classes.Tile):
    def __init__(self, x, y):
        rnd = random.choice([0, 1, 2])
        super().__init__(x, y, True, True, SPRITESHEET_TILES.image_at((32, 32*rnd, 32, 32)), SPRITESHEET_TILES.image_at((32, 32*rnd + 96, 32, 32)))
class t_unbreakable_wall(game_classes.Tile):
    def __init__(self, x, y):
        rnd = random.choice([0, 1, 2])
        super().__init__(x, y, False, False, SPRITESHEET_TILES.image_at((64, 32*rnd, 32, 32)), SPRITESHEET_TILES.image_at((64, 32*rnd + 96, 32, 32)))

# MONSTERS
class m_slime(game_classes.Monster):
    def __init__(self, x, y):
        super().__init__(x, y, [], [SPRITESHEET_MONSTERS.image_at((0, 0, 32, 32))], 'Slime', 100, [], [])

# SPECIAL ITEMS
class i_null(game_classes.Item):
    def __init__(self):
        self.itemType = ''
        self.name = ''
        self.x = 0
        self.y = 0
        self.tags = ['item']
        self.description = []
        self.color = game_constants.COLOR_GRAY
        self.sprite_list = None
class i_equipnull(game_classes.Item):
    def __init__(self):
        self.itemType = 'equipment'
        self.name = 'None'
        self.x = 0
        self.y = 0
        self.tag = ['item']
        self.description = []
        self.color = game_constants.COLOR_GRAY
        self.sprite_list = None

# CONSUMABLES
class i_minorhealpotion(game_classes.Consumable):
    def __init__(self, x, y):
        super().__init__(x = x,
                         y = y,
                         tags = ['healing', 'potion'],
                         sprite_list = [SPRITESHEET_CONSUMABLES.image_at((0, 0, 32, 32), game_constants.COLOR_COLORKEY)],
                         name = 'Minor heal potion',
                         color = game_constants.COLOR_WHITE,
                         size = 1,
                         description = [[('Heals the user.', game_constants.COLOR_WHITE)],
                                    [('* Amount: ', game_constants.COLOR_WHITE), ('10', game_constants.COLOR_GREEN)]],
                         effects = [e_flatheal(GAME.player, 10), e_getused(self)],
                         useCondition = [(c_playnotfullhealth, [])])
class i_bomb(game_classes.Consumable):
    def __init__(self, x, y):
        super().__init__(x = x,
                         y = y,
                         tags = ['placeable'],
                         sprite_list = [SPRITESHEET_CONSUMABLES.image_at((32, 0, 32, 32), game_constants.COLOR_COLORKEY)],
                         name = 'Bomb',
                         color = game_constants.COLOR_WHITE,
                         size = 3,
                         description = [[('Drops a bomb under the user\'s feet.', game_constants.COLOR_WHITE)],
                                     [('* Turns until explosion: ', game_constants.COLOR_WHITE), ('4', game_constants.COLOR_GRAY)],
                                     [('* Explosion damage: ', game_constants.COLOR_WHITE), ('10', game_constants.COLOR_RED)],
                                     [('* Explosion radius: ', game_constants.COLOR_WHITE), ('4', game_constants.COLOR_GRAY)]],
                         effects = [e_createbomb(GAME.player, 4, 4, 10), e_getused(self)])
class i_meat(game_classes.Consumable):
    def __init__(self, x, y):
        super().__init__(x = x,
                         y = y,
                         tags = ['edible', 'meat'],
                         sprite_list = [SPRITESHEET_CONSUMABLES.image_at((64, 0, 32, 32), game_constants.COLOR_COLORKEY)],
                         name = 'Meat',
                         color = game_constants.COLOR_WHITE,
                         size = 4,
                         description = [[('Replenishes the user food bar.', game_constants.COLOR_WHITE)],
                                    [('* Amount: ', game_constants.COLOR_WHITE), ('10 HP', game_constants.COLOR_GREEN)]],
                         effects = [e_eat(GAME.player, 80), e_getused(self)],
                         useCondition = [c_playnotfullhunger(GAME.player)])
class i_throwablebomb(game_classes.ConsumableMap):
    def __init__(self, x, y):
        super().__init__(x = x,
                         y = y,
                         tags = [],
                         sprite_list = [SPRITESHEET_CONSUMABLES.image_at((32, 0, 32, 32), game_constants.COLOR_COLORKEY)],
                         name = 'Throwable bomb',
                         color = game_constants.COLOR_WHITE,
                         size = 3,
                         description = [[('Throws a bomb.', game_constants.COLOR_WHITE)],
                                     [('* Maximum range to throw: ', game_constants.COLOR_WHITE), ('4', game_constants.COLOR_GRAY)],
                                     [('* Turns until explosion: ', game_constants.COLOR_WHITE), ('4', game_constants.COLOR_GRAY)],
                                     [('* Explosion damage: ', game_constants.COLOR_WHITE), ('10', game_constants.COLOR_RED)],
                                     [('* Explosion radius: ', game_constants.COLOR_WHITE), ('4', game_constants.COLOR_GRAY)]],
                         effects = [e_createbomb_l(4, 4, 10), e_getused(self)],
                         initialTarget = c_initonplayer,
                         maxRange = 4)
class i_thunderrod(game_classes.ConsumableMap):
    def __init__(self, x, y):
        super().__init__(x = x,
                         y = y,
                         tags = ['rod', 'magical'],
                         sprite_list = [SPRITESHEET_CONSUMABLES.image_at((96, 0, 32, 32), game_constants.COLOR_COLORKEY)],
                         name = 'Lightning rod',
                         color = game_constants.COLOR_WHITE,
                         size = 1,
                         description = [],
                         effects = [e_damage_l(5, 'magical', 'lightning'), e_getused(self)],
                         initialTarget = c_initonplayer,
                         maxRange = 8,
                         targetCondition = [c_creatureinlocation(self)],
                         charges = 3)
class i_diamond(game_classes.Consumable):
    def __init__(self, x, y):
        super().__init__(x = x,
                         y = y,
                         tags = [],
                         sprite_list = [SPRITESHEET_CONSUMABLES.image_at((96, 0, 32, 32), game_constants.COLOR_COLORKEY)],
                         name = 'Diamond',
                         color = game_constants.COLOR_CYAN,
                         size = 3,
                         description = [],
                         effects = [],
                         useCondition = [c_notusable])

# EQUIPMENT BEHAVIORS
class b_doublehealth(game_classes.Component):
    def execute(self):
        self.parent.stats[0] *= 2

# EQUIPMENT
class i_magichelmet_action(game_classes.Component):
    def onEquip(self):
        self.parent.modifiers = [b_doublehealth(GAME.player)]
        for modifier in self.parent.modifiers:
            GAME.player.modifiers.append(modifier)
    def onUnequip(self):
        for modifier in self.parent.modifiers:
            GAME.player.modifiers.remove(modifier)
class i_magichelmet(game_classes.Equipment):
    def __init__(self, x, y):
        super().__init__(x = x,
                        y = y,
                        tags = ['magical'],
                        sprite_list = SPRITESHEET_EQUIPMENT_HEAD.images_at_loop([(i*32, 0, 32, 32) for i in range(4)], colorkey = game_constants.COLOR_COLORKEY),
                        name = 'Magic helmet',
                        color = game_constants.COLOR_WHITE,
                        size = 6,
                        description = [[('Increases user health by ', game_constants.COLOR_WHITE), ('100 %', game_constants.COLOR_RED)]],
                        slot = 2,
                        actionEquipment = i_magichelmet_action,
                        requirements = [c_playnotfullhealth])

# SKILL TREES
class skill_healthup(game_classes.Skill):
    def __init__(self, index, pos, move, req, maxRank):
        super().__init__(index, pos, 'Health Up', [], SPRITESHEET_SKILLICONS.image_at((0, 0, 32, 32)), move, req, maxRank)
    def onBuy(self):
        super().onBuy()
        GAME.player.baseStats[0] += 20*self.rank
class skill_fullheal(game_classes.Skill):
    def __init__(self, index, pos, move, req, maxRank):
        super().__init__(index, pos, 'Full Heal', [], SPRITESHEET_SKILLICONS.image_at((0, 0, 32, 32)), move, req, maxRank)
    def onBuy(self):
        super().onBuy()
        GAME.player.hp = GAME.player.stats[0]

# PLAYABLE CHARACTERS
class p_normal(game_classes.Player):
    def __init__(self, x, y):
        super().__init__(x = x,
                        y = y,
                        sprite_list = SPRITESHEET_PLAYER.images_at_loop([(i*32, 0, 32, 32) for i in range(8)], colorkey = game_constants.COLOR_COLORKEY),
                        portrait_list = [SPRITESHEET_PORTRAITS.image_at((0, 0, 64, 64), colorkey = game_constants.COLOR_COLORKEY)],
                        stats = player_basicstats(),
                        equipment = [None for i in range(8)],
                        modifiers = [],
                        status = [s_health(self), s_hunger(self)],
                        skilltree = [skill_healthup(0, (8, 0), (None, 2, None, 1), [], 3),
                                    skill_fullheal(1, (8, 2), (None, None, 0, None), [0], 1),
                                    skill_fullheal(2, (18, 0), (0, None, 0, 3), [], 1),
                                    skill_fullheal(3, (16, 2), (1, 4, 2, None), [2], 1),
                                    skill_fullheal(4, (20, 2), (3, None, 2, 5), [2], 1),
                                    skill_fullheal(5, (20, 4), (None, None, 4, None), [4], 1)],
                        behaviors = [(b_playerbase, 50)]
                        )

################################################# FUNCTIONS #################################################

# MAP GENERATORS

MONSTERS = [None]

def map_init_dungeon(width, height):
    def path_cost(xFrom, yFrom, xTo, yTo, alg_array):
        if alg_array[xTo][yTo] == 0:
            return 1
        if alg_array[xTo][yTo] == 3:
            return 0.01
        else:
            return 10

    room_prefabs_10x10 = []
    f = open('resources/map_prefabs/map_prefabs[10x10].csv', 'r').read().split('\n') # 10x10
    for i in range(len(f[0]) // 10):
        for j in range(len(f) // 10):
            room = ''
            for y in range(10):
                for x in range(10):
                    room += f[j*10 + x][i*10 + y]
            room_prefabs_10x10.append(room)
    room_prefabs_5x5 = []
    f = open('resources/map_prefabs/map_prefabs[5x5].csv', 'r').read().split('\n') # 10x10
    for i in range(len(f[0]) // 5):
        for j in range(len(f) // 5):
            room = ''
            for y in range(5):
                for x in range(5):
                    room += f[j*5 + x][i*5 + y]
            room_prefabs_5x5.append(room)


    alg_array = [[0 for j in range(height)] for i in range(width)]
    terrain = [[0 for j in range(height)] for i in range(width)]
    items = []
    entities = []
    creatures = []

    rooms = []
    room_exits = []
    room_connections = []
    rooms_size = [(10, 10), (5, 5)]

    rooms.append((width//2-3, height//2-3, 6, 6))
    for x in range(width//2-3, width//2+3):
        for y in range(height//2-3, height//2+3):
            if y == height//2 and (x == width//2-3 or x == width//2+3):
                alg_array[x][y] = 7
                room_exits.append((x, y, -1))
            else:
                alg_array[x][y] = 2
    available_spots = [(x, y) for x in range(width) for y in range(height) if x > 6 and x < width - 12 and y > 6 and y < height - 12]
    for x in range(len(available_spots)):
        append = True
        i, j = available_spots.pop(random.randint(0, len(available_spots)-1))
        w, h = random.choice(rooms_size)
        newRoom = (i, j, w, h) #X, Y, W, H
        for room in rooms:
            if game_util.rectangle_intersects(newRoom, room):
                append = False
        if append == True:
            rooms.append(newRoom)
    for roomIndex in range(len(rooms))[0:]:
        room = rooms[roomIndex]
        if room[2] == 10 and room[3] == 10:
            room_layout = random.choice(room_prefabs_10x10)
            for x in range(room[2]):
                for y in range(room[3]):
                    alg_array[x + room[0]][y + room[1]] = int(room_layout[x*10 + y])
                    if int(room_layout[x*10 + y]) == 7:
                        room_exits.append((x + room[0], y + room[1], roomIndex))
        elif room[2] == 5 and room[3] == 5:
            room_layout = random.choice(room_prefabs_5x5)
            for x in range(room[2]):
                for y in range(room[3]):
                    alg_array[x + room[0]][y + room[1]] = int(room_layout[x*5 + y])
                    if int(room_layout[x*5 + y]) == 7:
                        room_exits.append((x + room[0], y + room[1], roomIndex))
    for exit_init in room_exits:
        path = libtcodpy.path_new_using_function(width, height, path_cost, alg_array, 0)
        other_exits = sorted([exit_other for exit_other in room_exits if exit_other[2] != exit_init[2] and (exit_other[2], exit_init[2]) not in room_connections], key = lambda e: game_util.simpledistance((exit_init[0], exit_init[1]), (e[0], e[1])))
        if len(other_exits) > 0:
            exit_end = other_exits[0]
        else:
            exit_end = sorted([exit_other for exit_other in room_exits if exit_other[2] != exit_init[2]], key = lambda e: game_util.simpledistance((exit_init[0], exit_init[1]), (e[0], e[1])))[0]
        room_connections.append((exit_init[2], exit_end[2]))
        room_connections.append((exit_end[2], exit_init[2]))
        libtcodpy.path_compute(path, exit_init[0], exit_init[1], exit_end[0], exit_end[1])
        for i in range(libtcodpy.path_size(path)-1):
            x, y = libtcodpy.path_get(path, i)
            alg_array[x][y] = 3

    for x in range(len(alg_array)):
        for y in range(len(alg_array[x])):
            if alg_array[x][y] in [0, 1]:
                terrain[x][y] = t_cave_wall(x, y)
            else:
                terrain[x][y] = t_cave_floor(x, y)
            if alg_array[x][y] == 4:
                creatures.append(m_slime(x, y))
            if alg_array[x][y] == 7:
                entities.append(n_door(x, y, SPRITESHEET_ENTITIES.image_at((0, 32, 32, 32)), SPRITESHEET_ENTITIES.image_at((32, 32, 32, 32), colorkey = game_constants.COLOR_COLORKEY)))
                terrain[x][y].passable = False
                terrain[x][y].transparent = False
    possible_exits = [(x, y) for x in range(2, width-2) for y in range(2, height-2) if (alg_array[x-1][y-1] not in [0, 1] and alg_array[x][y-1] not in [0, 1] and alg_array[x+1][y-1] not in [0, 1] and alg_array[x-1][y] not in [0, 1] and alg_array[x][y] not in [0, 1] and alg_array[x+1][y] not in [0, 1] and alg_array[x-1][y+1] not in [0, 1] and alg_array[x][y+1] not in [0, 1] and alg_array[x+1][y+1] not in [0, 1])]
    entities.append(n_exit(*random.choice(possible_exits)))
    return terrain, items, entities, creatures
def map_set_borders(map_array, width, height):
    for x in range(0, width):
        map_array[x][0] = t_unbreakable_wall(x, 0)
        if random.randint(0,2) == 0:
            map_array[x][0] = t_unbreakable_wall(x, 1)
        map_array[x][height] = t_unbreakable_wall(x, height)
        if random.randint(0,2) == 0:
            map_array[x][height-1] = t_unbreakable_wall(x, height-1)
    for y in range(0, height):
        map_array[0][y] = t_unbreakable_wall(0, y)
        if random.randint(0,2) == 0:
            map_array[1][y] = t_unbreakable_wall(1, y)
        map_array[width][y] = t_unbreakable_wall(width, y)
        if random.randint(0,2) == 0:
            map_array[width-1][y] = t_unbreakable_wall(width-1, y)
    return map_array

def player_basicstats():
    return {   'HitPointsFlat': 0,
                'HitPointsMult': 1,

                'MagicPointsMult': 1,
                'MagicPointsFlat': 0,

                'ExpGainedMult': 1,
                'HealingMult': 1,
                'HungerFlat': 0,
                'MaxCarry': 0,
                'DamageReceivedMult': 1,

                'HitPointsRegenFlat': 0,
                'HitPointsRegenMult': 1,
                'PhyAttackFlat': 0,
                'PhysAttackMult': 1,
                'PhyCritDamage': 0,
                'PhyCritChance': 0,
                'PhyBleedChance': 0,
                'PhyBleedMult': 1,
                'PhyBleedDuration': 0,
                'PhyStunChance': 0,
                'PhyStunDuration': 0,
                'PhyConfuseChance': 0,
                'PhyConfuseDuration': 0,
                'StrEffectivenessMult': 1,
                'StrDuration': 0,

                'MagicPointsRegenFlat': 0,
                'MagicPointsRegenMult': 1,
                'MagAttackFlat': 0,
                'MagAttackMult': 1,
                'MagCritDamage': 0,
                'MagCritChance': 0,
                'MagBleedChance': 0,
                'MagBleedMult': 1,
                'MagBleedDuration': 0,
                'MagStunChance': 0,
                'MagStunDuration': 0,
                'MagConfuseChance': 0,
                'MagConfuseDuration': 0,
                'EmpEffectivenessMult': 1,
                'EmpDuration': 0
    }
