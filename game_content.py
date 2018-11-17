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
class Window_PlayerInventory(game_classes.Window):
    def __init__(self):
        super().__init__(216, 150)
        self.sprite = game_constants.SPRITE_INVENTORYWINDOW
        self.index = [0, 0]
        self.onPopup = 'none'
        self.popupOptionsIndex = 0
        self.popupSelectionIndex = 0
        self.popupOptionsItems = {'equipment': ["Equip", "Drop", "Cancel"], 'weapon': ["Equip", "Drop", "Cancel"], 'consumable': ["Use", "Drop", "Cancel"]}
        self.realIndex = 0
        self.animation_step = 0
        self.item_x, self.item_y = 0, 0
        self.description_position = (442, 0)
        self.getItems()
    def input(self, key):
        super().input(key)
        if self.onPopup == 'none':
            if key == 'left':
                if self.index[0] - 1 >= 0:
                    self.index[0] -= 1
            if key == 'right':
                if self.index[0] + 1 <= 9:
                    self.index[0] += 1
            if key == 'up':
                if self.index[1] - 1 >= 0:
                    self.index[1] -= 1
            if key == 'down':
                if self.index[1] + 1 <= 7:
                    self.index[1] += 1
            self.realIndex = self.index[0] + self.index[1] * 10

            if key == 'use':
                if self.realIndex < len(self.items):
                    self.onPopup = 'options'
                    self.popupOptionsIndex = 0
            if key == 'cancel':
                self.destroy()

            if key in ['up', 'down', 'left', 'right']:
                self.animation_step = 0


        elif self.onPopup == 'options':
            options = self.popupOptionsItems[self.items[self.realIndex]['type']]
            if key == 'up':
                if self.popupOptionsIndex > 0:
                    self.popupOptionsIndex -= 1
            if key == 'down':
                if self.popupOptionsIndex < len(options) - 1:
                    self.popupOptionsIndex += 1
            if key == 'use':
                if options[self.popupOptionsIndex] == 'Cancel':
                    self.onPopup = 'none'
                if options[self.popupOptionsIndex] == 'Drop':
                    item = GAME.player.inventory.pop(self.realIndex)
                    item.x, item.y = GAME.player.x, GAME.player.y
                    GAME.items.append(item)
                    self.onPopup = 'none'
                    self.getItems()
                if options[self.popupOptionsIndex] == 'Equip':
                    if GAME.player.inventory[self.items[self.realIndex]['index']].canEquip():
                        equip = GAME.player.equipment[GAME.player.inventory[self.items[self.realIndex]['index']].slot]
                        new_equip = GAME.player.inventory[self.items[self.realIndex]['index']]
                        if equip:
                            equip.unequip()
                            GAME.player.inventory.append(equip)
                        GAME.player.equipment[new_equip.slot] = new_equip
                        new_equip.equip()
                        GAME.player.inventory.remove(new_equip)
                        self.onPopup = 'none'
                        self.getItems()
                    else:
                        GAME.addLogMessage('You don\'t meet the requeriments to equip this.', game_constants.COLOR_INFO)
            if key == 'cancel':
                self.onPopup = 'none'

    def draw(self):
        super().draw()
        self.animation_step += 1

        # Draw main window
        GAME.surface_windows.blit(self.sprite, (self.x, self.y))
        for index, sprites in enumerate(item['sprites'] for item in self.items):
            i = (index % 10, int(index / 10))
            GAME.surface_windows.blit(sprites[0], (self.x + i[0]*41 + 16, self.y + i[1]*42 + 49))
        pygame.draw.rect(GAME.surface_windows, game_constants.COLOR_MENUHIGHLIGHT, (self.x + self.index[0]*41 + 13, self.y + self.index[1]*42 + 43, 36, 36), 2)

        # Draw description window
        if self.realIndex < len(self.items):
            selected_item = self.items[self.realIndex]
            frame = int(self.animation_step / game_constants.ANIMATION_RATE) % len(selected_item['sprites'])
            GAME.surface_windows.blit(game_constants.SPRITE_INVENTORYDESCRIPTION, (self.x + self.description_position[0], self.y))
            GAME.surface_windows.blit(selected_item['sprites_big'][frame], (self.x + self.description_position[0] + 17, self.y + 20))
            game_util.draw_text(GAME.surface_windows, selected_item['name'], self.x + self.description_position[0] + 86, self.y + 8, game_constants.FONT_PERFECTDOS_MEDIUM, selected_item['color'])
            game_util.draw_text(GAME.surface_windows, selected_item['rarity'] + " " + selected_item['type'], self.x + self.description_position[0] + 86, self.y + 24, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
            for index, line in enumerate(game_util.wrap_text(selected_item['description']['flavor'], 42)):
                game_util.draw_text(GAME.surface_windows, line, self.x + self.description_position[0] + 86, self.y + 42 + 12*index, game_constants.FONT_PERFECTDOS_SMALL, game_constants.COLOR_DARKESTGRAY, shadow = False)

            # Equipment
            if selected_item['type'] == 'equipment' or selected_item['type'] == 'weapon':
                game_util.draw_text(GAME.surface_windows, 'Effects:', self.x + self.description_position[0] + 6, self.y + 86, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
                for index, line in enumerate(self.items[self.realIndex]['description']['stats'] + self.items[self.realIndex]['description']['mods']):
                    line = line()
                    game_util.draw_text(GAME.surface_windows, line[0], self.x + self.description_position[0] + 10, self.y + 100 + index*14, game_constants.FONT_PERFECTDOS_SMALL, line[1], shadow = False)
                game_util.draw_text(GAME.surface_windows, 'Requirements:', self.x + self.description_position[0] + 6, self.y + 162, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
                for index, line in enumerate(self.items[self.realIndex]['description']['requirements']):
                    line = line(GAME.player)
                    game_util.draw_text(GAME.surface_windows, line[0], self.x + self.description_position[0] + 10, self.y + 176 + index * 14, game_constants.FONT_PERFECTDOS_SMALL,
                                        line[1], shadow=False)

        # Draw popup
        if (self.onPopup == 'options' or self.onPopup == 'selection'):
            GAME.surface_windows.blit(game_constants.SPRITE_OPTIONSWINDOW, (self.x + self.description_position[0], self.y + 256))
            GAME.surface_windows.fill(game_constants.COLOR_MENUHIGHLIGHT, (self.x + self.description_position[0], self.y + 256 + 2 + 24*self.popupOptionsIndex, 118, 24))
            for index, option in enumerate(self.popupOptionsItems[selected_item['type']]):
                game_util.draw_text(GAME.surface_windows, option, self.x + self.description_position[0] + 8, self.y + 260 + index*24, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)

    def getItems(self):
        self.items = [{'index': GAME.player.inventory.index(item),
                       'name': item.name,
                       'sprites': item.sprite_list,
                       'sprites_big': [pygame.transform.scale(sprite, (64, 64)) for sprite in item.sprite_list],
                       'rarity': item.rarity,
                       'color':item.color,
                       'type': item.itemType,
                       'description': item.description} for item in GAME.player.inventory]

class Window_SearchInventory(game_classes.Window):
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

class Window_Equipment(game_classes.Window):
    def __init__(self):
        super().__init__(565, 210)
        self.sprite = game_constants.SPRITE_EQUIPMENTWINDOW
        self.index = 0
        self.item_positions = [(9, 124), (59, 50), (59, 97), (59, 147), (59, 197), (59, 247), (109, 124)]
        self.onPopup = 'none'
        self.popupIndex = 0
        self.popupOptions = {'equipped': ['Equip', 'Unequip', 'Drop'],
                             'free': ['Equip']}
        self.popupType = ''
        self.equipItems = []
        self.popupOptions_position = (160, 32)
        self.popupItems_position = (300, 32)
        self.getItems()
        self.xOffset = 0
        self.maxLength = 7
    def input(self, key):
        super().input(key)
        if self.onPopup == 'slot':
            if key == 'up' and self.popupIndex > 0:
                self.popupIndex -= 1
            if key == 'down' and self.popupIndex < len(self.popupOptions[self.popupType] ) - 1:
                self.popupIndex += 1
            if key == 'use':
                if self.popupIndex == 0: # Equip
                    self.getItems()
                    self.onPopup = 'equip'
                else: # Unequip or drop
                    equip = GAME.player.equipment[self.index]
                    equip.unequip()
                    if self.popupIndex == 1: # Unequip
                        GAME.player.inventory.append(equip)
                    else:
                        equip.x = GAME.player.x
                        equip.y = GAME.player.y
                        GAME.items.append(equip)
                    GAME.player.equipment[self.index] = None
                    self.getItems()
                    self.popupType = 'free'
                    self.popupIndex = 0
            if key == 'cancel':
                self.popupIndex = 0
                self.popupType = ''
                self.onPopup = 'none'

        elif self.onPopup == 'equip':
            if key == 'up' and self.popupIndex > 0:
                self.popupIndex -= 1
            if key == 'down' and self.popupIndex < len(self.equipItems) - 1:
                self.popupIndex += 1
            if key == 'use':
                if self.popupIndex != 0:
                    equip = GAME.player.equipment[self.index]
                    new_equip = self.equipItems[self.popupIndex]
                    if equip:
                        equip.unequip()
                        GAME.player.inventory.append(equip)
                    GAME.player.equipment[self.index] = new_equip
                    new_equip.equip()
                    GAME.player.inventory.remove(new_equip)
                    self.popupType = 'equipped'
                self.getItems()
                self.onPopup = 'slot'
                self.popupIndex = 0
            if key == 'cancel':
                self.popupIndex = 0
                self.onPopup = 'slot'

        elif self.onPopup == 'none':
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
            if key == 'use':
                self.onPopup = 'slot'
                if self.items[self.index]:
                    self.popupType = 'equipped'
                else:
                    self.popupType = 'free'
            if key == 'cancel':
                self.destroy()
    def draw(self):
        super().draw()
        GAME.surface_windows.blit(self.sprite, (self.x, self.y))
        pygame.draw.rect(GAME.surface_windows, game_constants.COLOR_GREEN, (self.item_positions[self.index][0]-2 + self.x, self.item_positions[self.index][1]-2 + self.y, 36, 36), 2)
        for index, item in enumerate(self.items):
            if item:
                GAME.surface_windows.blit(item.sprite, (self.item_positions[index][0] + self.x, self.item_positions[index][1] + self.y))
        if self.onPopup == 'slot':
            GAME.surface_windows.blit(game_constants.SPRITE_OPTIONSWINDOW, (self.x + self.popupOptions_position[0], self.y + self.popupOptions_position[1]))
            GAME.surface_windows.fill(game_constants.COLOR_MENUHIGHLIGHT, (self.x + self.popupOptions_position[0], self.y + self.popupOptions_position[1] + 2 + 24*self.popupIndex, 118, 24))
            for index, option in enumerate(self.popupOptions[self.popupType]):
                game_util.draw_text(GAME.surface_windows, option, self.x + self.popupOptions_position[0] + 8, self.y + self.popupOptions_position[1] + 6 + 24*index, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
        elif self.onPopup == 'equip':
            GAME.surface_windows.blit(game_constants.SPRITE_OPTIONSWINDOW, (self.x + self.popupOptions_position[0], self.y + self.popupOptions_position[1]))
            GAME.surface_windows.fill(game_constants.COLOR_MENUHIGHLIGHT, (self.x + self.popupOptions_position[0], self.y + self.popupOptions_position[1] + 2, 118, 24))
            for index, option in enumerate(self.popupOptions[self.popupType]):
                game_util.draw_text(GAME.surface_windows, option, self.x + self.popupOptions_position[0] + 8, self.y + self.popupOptions_position[1] + 6 + 24*index, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
            GAME.surface_windows.blit(game_constants.SPRITE_ITEMLIST, (self.x + self.popupItems_position[0], self.y + self.popupItems_position[1]))
            GAME.surface_windows.fill(game_constants.COLOR_MENUHIGHLIGHT, (self.x + self.popupItems_position[0], self.y + self.popupItems_position[1] + 2 + 24*self.popupIndex, 178, 24))
            for index, name in enumerate(["None"] + [item.name for item in self.equipItems[1:]]):
                game_util.draw_text(GAME.surface_windows, name, self.x + self.popupItems_position[0] + 8, self.y + self.popupItems_position[1] + 6 + 24*index, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
    def getItems(self):
        self.items = [item for item in GAME.player.equipment]
        self.equipItems = [None] + [item for item in GAME.player.inventory if item.slot == self.index and item.canEquip()]

class Window_Status(game_classes.Window):
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

class Window_Stats(game_classes.Window):
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

class Window_Trade(game_classes.Window):
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
    def __init__(self, priority):
        self.priority = priority
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
                linearDamage(parent, enemy, parent.getStat('PhyAttack'), 'physical', None)
            for tile in args[1]:
                if parent.equipment[0] and parent.equipment[0].spriteattack_list:
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
    def __init__(self, priority):
        self.priority = priority
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
            linearDamage(parent, GAME.player, parent.getStat('PhyAttack'), 'physical', None)
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
    if target.currentHitPoints + amount > target.getStat('HitPoints'):
        value = target.getStat('HitPoints') - target.currentHitPoints
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
    return game_classes.Monster(x, y, [], game_parsers.get_animation('resources/graphics/entities/slime.png'), 'Slime', [], [(behaviorMonsterBase(50))], slime_stats())

# PLAYABLE CHARACTERS
def p_normal(x, y):
        return game_classes.Player(
            x = x,
            y = y,
            sprite_list = game_parsers.get_animation('resources/graphics/entities/player.png', repeat = True),
            portrait_list = [pygame.Surface((32, 32))],
            stats = player_basicstats(),
            equipment = [None for _ in range(7)],
            inventory = [drill(0, 0) for _ in range(80)],
            modifiers = [],
            status = [],
            skilltree = [],
            behaviors = [(behaviorPlayerBase(50))]
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
        damage = math.ceil((amount)*(4**(-target.getStat('PhyArmor')/300)))
    elif maintype == 'magical':
        damage = math.ceil((amount)*(4**(-target.getStat('MagArmor')/300)))
    else:
        damage = 0
    GAME.addLogMessage(origin.name + ' damages ' + target.name + ' for ' + str(damage) + '.', game_constants.COLOR_LIGHTRED)
    origin.event('dodamage', (target, origin, damage, maintype, subtype))
    target.event('takedamage', (target, origin, damage, maintype, subtype))


def drill(x, y):
    return game_classes.LongSword(x, y, 'Adamantite drill', 'Mythic', 3, 'This is the drill that will pierce the heavens.', [game_effects.linearStat(10, 'PhyAttackFlat', 200), game_effects.linearStat(10, 'HitPointsFlat', 1000)], [game_effects.drillMod(10)], [game_effects.minimumStat('PhyAttack', 1)], ['drill'], game_parsers.get_animation('resources/graphics/equipment/drill1.png', repeat = True), [])

def stoneTileOnDestroy(parent):
    GAME.map[parent.x][parent.y] = game_classes.Tile(parent.x, parent.y, True, True, pygame.image.load('resources/graphics/tiles/floor_dirt.png'))