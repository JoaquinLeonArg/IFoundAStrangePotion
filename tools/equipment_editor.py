import pygame
import sys
import json

"""
Room layout editor for I found a strange potion.

Written by Joaquín León.
"""

# Constants
WINDOW_SIZE = (1280, 720)

C_WHITE = (250, 250, 250)
C_LIGHTGRAY = (200, 200, 200)
C_GRAY = (120, 120, 120)
C_DARKGRAY = (50, 50, 50)
C_BLACK = (20, 20, 20)
C_GREEN = (100, 240, 100)
C_RED = (240, 100, 100)
C_BLUE = (100, 100, 240)

# General
def initialize():
    global SCREEN, DATA, FONT, EVENTS
    pygame.init()
    SCREEN = pygame.display.set_mode(WINDOW_SIZE, 0, 16)
    DATA = Data()
    FONT = pygame.font.Font('font.ttf', 16)
    EVENTS = []
    pygame.display.set_caption("Room Editor for IFASP")
    while True:
        EVENTS = pygame.event.get()
        handleInput()
        drawCycle()


def drawCycle():
    SCREEN.fill(C_BLACK)
    pygame.draw.rect(SCREEN, C_GRAY, pygame.Rect(0, 0, WINDOW_SIZE[0]*1/3, WINDOW_SIZE[1]))
    for e in DATA.UIElements:
        e.draw()
    pygame.display.flip()

def handleInput():
    for event in EVENTS:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            target = next(filter(lambda e: pointInRect(pygame.mouse.get_pos(), (e.x, e.y, e.width, e.height)), DATA.UIElements), None)
            if target:
                target.onClick()
        elif event.type == pygame.KEYDOWN and DATA.activeText:
            target = next(filter(lambda e: e.field == DATA.activeText, [a for a in DATA.UIElements if type(a) == TextField]))
            if event.key == pygame.K_BACKSPACE:
                target.content = target.content[0:-1]
            elif 97 <= event.key <= 122:
                if pygame.KMOD_SHIFT & pygame.key.get_mods():
                    target.content += chr(event.key - 32)
                else:
                    target.content += chr(event.key)
            elif 32 <= event.key <= 63:
                target.content += chr(event.key)
            DATA.data[DATA.equipmentIndex][target.field] = target.content

# Util
def pointInRect(point, rect):
    return rect[0]+rect[2] > point[0] > rect[0] and rect[1]+rect[3] > point[1] > rect[1]

# Data structures
class Data:
    def __init__(self):
        self.UIElements = []
        self.UIVariableElements = {
            'weapon': [],
            'armor': []
        }
        self.file = None
        self.data = None
        self.equipmentIndex = 0
        self.pageNumber = 0
        self.activeText = None
        self.mode = 'weapon'
        self.loadFile()
        self.initData()
        self.updateData()
        self.initUI()
        self.updateUI()
        self.UIElements.sort(key=lambda e: e.z)
    def loadFile(self):
        try:
            self.file = open('EquipmentData.dat', 'r')
        except:
            self.file = open('EquipmentData.dat', 'w+').close()
            self.file = open ('EquipmentData.dat', 'r')
        try:
            self.data = json.loads(self.file.read())
        except:
            self.data = [baseweapon(0)]
        self.file.close()
    def saveFile(self):
        self.file = open('EquipmentData.dat', 'w')
        self.file.write(json.dumps(self.data))
        self.file.close()
    def initUI(self):
        id = 0
        for y in range(24):
            for x in range(12):
                self.UIElements.append(ButtonSelectEquipment(5 + x*34, 5 + y*34, 1, id)) # Tiles
                id += 1

        # Common fields
        self.UIElements.append(TextField(448, 10, 1, 128, 'name', 'Name'))

        # Weapon
        self.UIVariableElements['weapon'].append(ChoiceList(448, 10, 1, 128, 'type', 'Weapon type', ['shortSword', 'longSword', 'spear']))

        # Armor
        self.UIVariableElements['armor'].append(ChoiceList(448, 10, 2, 128, 'slot', 'Equipment type', ['Head', 'Neck', 'Chest', 'Legs', 'Feet', 'Hands']))

        self.UIElements.append(ButtonAddEquipment(WINDOW_SIZE[0] - 150, WINDOW_SIZE[1]- 34, 1))
        self.UIElements.append(ButtonDeleteEquipment(WINDOW_SIZE[0] - 105, WINDOW_SIZE[1] - 34, 1))
        self.UIElements.append(ButtonSave(WINDOW_SIZE[0] - 60, WINDOW_SIZE[1] - 34, 1))
    def initData(self):
        self.equipmentIndex = len(self.data) - 1
    def updateUI(self):
        for e in self.UIElements + self.UIVariableElements[self.mode]:
            if type(e) is TextLabel:
                e.text = str(eval('self.{}'.format(e.variable)))
            if type(e) is ButtonSelectEquipment:
                e.id_equipment = e.id + 64 * self.pageNumber
                e.visible = len(self.data) > e.id_equipment
            if type(e) is TextField:
                e.content = self.data[self.equipmentIndex][e.field]
    def updateData(self):
        print(self.data)

class UIElement:
    def __init__(self, x, y, z, width, height):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.visible = True
    def draw(self):
        pass
    def onClick(self):
        DATA.updateData()
        DATA.updateUI()

class TextLabel(UIElement):
    def __init__(self, x, y, z, width, height, variable):
        super().__init__(x, y, z, width, height)
        self.variable = variable
        self.text = ''
    def draw(self):
        pygame.draw.rect(SCREEN, C_LIGHTGRAY, pygame.Rect(self.x, self.y, self.width, self.height))
        SCREEN.blit(FONT.render(self.text, False, C_BLACK, C_LIGHTGRAY), (self.x + 8, self.y + 8))
class Button(UIElement):
    def __init__(self, x, y, z, width, height, text, f, offset = (0, 0)):
        super().__init__(x, y, z, width, height)
        self.text = text
        self.f = f
        self.offset = offset
    def draw(self):
        pygame.draw.rect(SCREEN, C_LIGHTGRAY, pygame.Rect(self.x, self.y, self.width, self.height))
        SCREEN.blit(FONT.render(self.text, False, C_BLACK), (self.x + self.offset[0], self.y + self.offset[1]))
    def onClick(self):
        self.f(DATA)
        DATA.updateData()
        DATA.updateUI()
class ButtonImage(Button):
    def __init__(self, x, y, z, image, f):
        self.image = image
        super().__init__(x, y, z, self.image.get_width()+2, self.image.get_height()+2, '', f)
    def draw(self):
        pygame.draw.rect(SCREEN, C_DARKGRAY, pygame.Rect(self.x, self.y, self.width, self.height))
        SCREEN.blit(self.image, (self.x+1, self.y+1))
class ButtonSelectEquipment(ButtonImage):
    def __init__(self, x, y, z, id):
        super().__init__(x, y, z, pygame.Surface((32, 32)), lambda e: None)
        self.id = id
    def onClick(self):
        self.id_equipment = self.id + 64*DATA.pageNumber
        if self.visible:
            DATA.equipmentIndex = self.id_equipment
        DATA.updateData()
        DATA.updateUI()
    def draw(self):
        try:
            if self.visible:
                pygame.draw.rect(SCREEN, C_BLUE, pygame.Rect(self.x, self.y, self.width, self.height))
                if DATA.equipmentIndex == self.id_equipment:
                    pygame.draw.rect(SCREEN, C_GREEN, pygame.Rect(self.x, self.y, self.width, self.height), 2)
        except:
            pass
class ButtonAddEquipment(Button):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, 40, 32, 'ADD', lambda e: None, (8, 10))
    def onClick(self):
        if len(DATA.data) < 241:
            DATA.data.append(baseweapon())
        DATA.updateData()
        DATA.updateUI()
class ButtonDeleteEquipment(Button):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, 40, 32, 'DEL', lambda e: None, (8, 10))
    def onClick(self):
        if len(DATA.data) > 1:
            DATA.data.pop(DATA.mapIndex)
            if DATA.mapIndex > 0:
                DATA.mapIndex -= 1
        DATA.updateData()
        DATA.updateUI()
class ButtonSave(Button):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, 40, 32, 'SAVE', lambda e: None, (4, 10))
    def onClick(self):
        DATA.saveFile()

class TextField(UIElement):
    def __init__(self, x, y, z, width, field, text):
        super().__init__(x, y, z, width, 48)
        self.field = field
        self.text = text
        self.content = ''
    def draw(self):
        pygame.draw.rect(SCREEN, C_DARKGRAY, pygame.Rect(self.x, self.y + 24, self.width, self.height/2))
        SCREEN.blit(FONT.render(self.text, False, C_BLACK, C_LIGHTGRAY), (self.x + 4, self.y))
        SCREEN.blit(FONT.render(self.content, False, C_BLACK, C_LIGHTGRAY), (self.x + 4, self.y + 4 + 24))
    def onClick(self):
        DATA.activeText = self.field
        DATA.updateData()
        DATA.updateUI()

class Checkbox(UIElement):
    def __init__(self, x, y, z, text, default = False):
        super().__init__(x, y, z, 12, 12)
        self.text = text
        self.active = default
    def draw(self):
        if self.active:
            pygame.draw.rect(SCREEN, C_GREEN, pygame.Rect(self.x, self.y, 12, 12))
        else:
            pygame.draw.rect(SCREEN, C_RED, pygame.Rect(self.x, self.y, 12, 12))
        SCREEN.blit(FONT.render(self.text, False, C_BLACK, C_LIGHTGRAY), (self.x + 14, self.y))
    def onClick(self):
        self.active = not self.active
        DATA.data[DATA.mapIndex]['isBossRoom'] = self.active
        DATA.updateData()
        DATA.updateUI()
class CheckboxGroup(Checkbox):
    def __init__(self, x, y, z, id_number, text, group):
        super().__init__(x, y, z, id_number, text)
        self.id_number = id_number
        self.group = group
    def onClick(self):
        if not self.active:
            super().onClick()
            for e in DATA.UIElements:
                if e is not self and e.group == self.group:
                    e.active = False
class CheckboxGroupDefault(CheckboxGroup):
    def __init__(self, x, y, z, id_number, text, group):
        super().__init__(x, y, z, id_number, text, group)
        self.active = True

class ChoiceList(UIElement):
    def __init__(self, x, y, z, width, field, text, items):
        super().__init__(x, y, z, width, 512)
        self.fiels = field
        self.text = text
        self.items = items
    def draw(self):
        pygame.draw.rect(SCREEN, C_DARKGRAY, pygame.Rect(self.x, self.y, self.width, len(self.items)*24))


def baseweapon(id):
    return {
        'id': id,
        'type': 'weapon',
        'name': '',
        'description': '',
        'rarity': 0,
        'size': 0,
        'slot': 0,
        'stats': {},
        'statmods': [],
        'behaviormods': [],
        'requirements': {},
        'tags': [],
        'sprite': '../resources/graphics/equipment/sword1.png',
        'spriteattack': '../resources/graphics/effects/slash1.png'
    }

initialize()