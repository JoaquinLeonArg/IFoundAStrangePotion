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
TILES = {
    0: pygame.image.load('graphics/wall.png'),
    1: pygame.image.load('graphics/floor.png'),
    2: pygame.image.load('graphics/water.png'),
    3: pygame.image.load('graphics/lava.png'),
    4: pygame.image.load('graphics/glass.png'),
    5: pygame.image.load('graphics/void.png')
}
ENTITIES = {
    0: pygame.image.load('graphics/null.png'),
    1: pygame.image.load('graphics/door_entrance.png'),
    2: pygame.image.load('graphics/entrance.png'),
    3: pygame.image.load('graphics/creature_normal.png'),
    4: pygame.image.load('graphics/creature_elite.png'),
    5: pygame.image.load('graphics/chest.png'),
    6: pygame.image.load('graphics/loot_small.png'),
    7: pygame.image.load('graphics/loot_big.png'),
    8: pygame.image.load('graphics/merchant.png')
}

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
    pygame.draw.rect(SCREEN, C_GRAY, pygame.Rect(0, WINDOW_SIZE[1] - 134, WINDOW_SIZE[0], WINDOW_SIZE[1]))
    pygame.draw.rect(SCREEN, C_DARKGRAY, pygame.Rect(WINDOW_SIZE[0] - 250, 0, WINDOW_SIZE[0], WINDOW_SIZE[1]))
    for e in DATA.UIElements:
        e.draw()
    pygame.display.flip()

def handleInput():
    for event in EVENTS:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            target = next(filter(lambda e: pointInRect(pygame.mouse.get_pos(), (e.x, e.y, e.width, e.height)), DATA.UIElements), None)
            if target:
                target.onClick()

# Util
def pointInRect(point, rect):
    return rect[0]+rect[2] > point[0] > rect[0] and rect[1]+rect[3] > point[1] > rect[1]

# Data structures
class Data:
    def __init__(self):
        self.width = 8
        self.height = 8
        self.UIElements = []
        self.file = None
        self.data = None
        self.current_type = 'tiles'
        self.current_id = 0
        self.mapIndex = 0
        self.loadFile()
        self.initData()
        self.updateData()
        self.initUI()
        self.updateUI()
        self.UIElements.sort(key=lambda e: e.z)
    def loadFile(self):
        try:
            self.file = open('roomsData.dat', 'r')
        except:
            self.file = open('roomsData.dat', 'w+').close()
            self.file = open ('roomsData.dat', 'r')
        try:
            self.data = json.loads(self.file.read())
        except:
            self.data = [baseroom()]
        self.file.close()
    def saveFile(self):
        self.file = open('roomsData.dat', 'w')
        self.file.write(json.dumps(self.data))
        self.file.close()
    def initUI(self):
        for y in range(17):
            for x in range(24):
                self.UIElements.append(Tile(5 + x*34, 5 + y*34, 1, 34, x, y)) # Tiles

        self.UIElements.append(Checkbox(10, WINDOW_SIZE[1] - 100, 1, 'Is bossroom?')) # Bossroom checkbox

        self.UIElements.append(TextLabel(10, WINDOW_SIZE[1] - 60, 1, 36, 36, 'width')) # X dimension label
        self.UIElements.append(Button(47, WINDOW_SIZE[1] - 60, 1, 17, 17, '+', lambda e: e.changeWidth(1)))
        self.UIElements.append(Button(47, WINDOW_SIZE[1] - 42, 1, 17, 17, '-', lambda e: e.changeWidth(-1)))
        self.UIElements.append(TextLabel(80, WINDOW_SIZE[1] - 60, 1, 36, 36, 'height')) # Y dimension label
        self.UIElements.append(Button(117, WINDOW_SIZE[1] - 60, 1, 17, 17, '+', lambda e: e.changeHeight(1)))
        self.UIElements.append(Button(117, WINDOW_SIZE[1] - 42, 1, 17, 17, '-', lambda e: e.changeHeight(-1)))

        for i in range(6):
            self.UIElements.append(ButtonSelectEntity(250 + i*36, WINDOW_SIZE[1] - 110, 1, i, 'tiles'))
        for i in range(9):
            self.UIElements.append(ButtonSelectEntity(250 + i*36, WINDOW_SIZE[1] - 60, 1, i, 'entities'))

        for i in range(231):
            x = WINDOW_SIZE[0] - 246 + (i % 7)*34
            y = 6 + (i // 7)*20
            self.UIElements.append(ButtonSelectMap(x, y, 1, i))

        self.UIElements.append(ButtonAddRoom(WINDOW_SIZE[0] - 240, WINDOW_SIZE[1]- 34, 1))
        self.UIElements.append(ButtonDeleteRoom(WINDOW_SIZE[0] - 195, WINDOW_SIZE[1] - 34, 1))
        self.UIElements.append(ButtonSave(WINDOW_SIZE[0] - 150, WINDOW_SIZE[1] - 34, 1))
    def initData(self):
        self.mapIndex = len(self.data) - 1
        self.width = len(self.data[self.mapIndex]['layout']['tiles'][0])
        self.height = len(self.data[self.mapIndex]['layout']['tiles'])
    def changeWidth(self, value):
        self.width = min(max(self.width + value, 3), 24)
        self.updateUI()
    def changeHeight(self, value):
        self.height = min(max(self.height + value, 3), 17)
        self.updateUI()
    def updateUI(self):
        for e in self.UIElements:
            if type(e) is TextLabel:
                e.text = str(eval('self.{}'.format(e.variable)))
            if type(e) is Tile:
                e.visible = e.x_pos < self.width and e.y_pos < self.height
            if type(e) is ButtonSelectMap:
                e.visible = len(self.data) >= e.id_room
            if type(e) is Checkbox:
                e.active = self.data[self.mapIndex]['isBossRoom']
    def updateData(self):
        auxTiles = [[0 for _ in range(self.width)] for _ in range(self.height)]
        auxEntities = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for x in range(self.width):
            for y in range(self.height):
                try:
                    auxTiles[y][x] = self.data[self.mapIndex]['layout']['tiles'][y][x]
                    auxEntities[y][x] = self.data[self.mapIndex]['layout']['entities'][y][x]
                except:
                    pass
        self.data[self.mapIndex]['layout']['tiles'] = auxTiles
        self.data[self.mapIndex]['layout']['entities'] = auxEntities
        self.width = len(self.data[self.mapIndex]['layout']['tiles'][0])
        self.height = len(self.data[self.mapIndex]['layout']['tiles'])
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
class ButtonSelectEntity(ButtonImage):
    def __init__(self, x, y, z, image_index, entity_type):
        self.entity_id = image_index
        self.entity_type = entity_type
        if self.entity_type is 'tiles':
            self.image = TILES[image_index]
        elif self.entity_type is 'entities':
            self.image = ENTITIES[image_index]
        super().__init__(x, y, z, self.image, lambda: None)
    def onClick(self):
        DATA.current_id = self.entity_id
        DATA.current_type = self.entity_type
        DATA.updateData()
        DATA.updateUI()
    def draw(self):
        super().draw()
        if DATA.current_type == self.entity_type and DATA.current_id == self.entity_id:
            pygame.draw.rect(SCREEN, C_GREEN, pygame.Rect(self.x, self.y, self.image.get_width() + 2, self.image.get_height() + 2), 2)
class ButtonSelectMap(Button):
    def __init__(self, x, y, z, id_room):
        super().__init__(x, y, z, 33, 18, str(id_room),lambda e: None, (4, 2))
        self.id_room = id_room
    def onClick(self):
        if self.visible:
            DATA.mapIndex = self.id_room
            DATA.width = len(DATA.data[DATA.mapIndex]['layout']['tiles'][0])
            DATA.height = len(DATA.data[DATA.mapIndex]['layout']['tiles'])
        DATA.updateData()
        DATA.updateUI()
    def draw(self):
        try:
            if self.visible:
                if DATA.data[self.id_room]['isBossRoom']:
                    pygame.draw.rect(SCREEN, C_RED, pygame.Rect(self.x, self.y, self.width, self.height))
                else:
                    pygame.draw.rect(SCREEN, C_BLUE, pygame.Rect(self.x, self.y, self.width, self.height))
                SCREEN.blit(FONT.render(self.text, False, C_BLACK), (self.x + self.offset[0], self.y + self.offset[1]))
                if DATA.mapIndex == self.id_room:
                    pygame.draw.rect(SCREEN, C_GREEN, pygame.Rect(self.x, self.y, self.width, self.height), 2)
        except:
            pass
class ButtonAddRoom(Button):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, 40, 32, 'ADD', lambda e: None, (8, 10))
    def onClick(self):
        if len(DATA.data) < 241:
            DATA.data.append(baseroom())
        DATA.updateData()
        DATA.updateUI()
class ButtonDeleteRoom(Button):
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

class Tile(UIElement):
    def __init__(self, x, y, z, side, x_pos, y_pos):
        super().__init__(x, y, z, side, side)
        self.x_pos = x_pos
        self.y_pos = y_pos
    def draw(self):
        if self.visible:
            pygame.draw.rect(SCREEN, C_DARKGRAY, pygame.Rect(self.x, self.y, self.width, self.height))
            try:
                SCREEN.blit(TILES[DATA.data[DATA.mapIndex]['layout']['tiles'][self.y_pos][self.x_pos]], (self.x + 1, self.y + 1))
                SCREEN.blit(ENTITIES[DATA.data[DATA.mapIndex]['layout']['entities'][self.y_pos][self.x_pos]], (self.x + 1, self.y + 1))
            except:
                pass
    def onClick(self):
        if self.visible:
            DATA.data[DATA.mapIndex]['layout'][DATA.current_type][self.y_pos][self.x_pos] = DATA.current_id
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

def baseroom():
    return {'layout': {   'tiles': [[0, 0, 0],
                                                [0, 0, 0],
                                                [0, 0, 0]],
                                        'entities': [[0, 0, 0],
                                                    [0, 0, 0],
                                                    [0, 0, 0]]},
                          'isBossRoom': False,
                          'value': {    'danger': 0,
                                        'size': 0,
                                        'loot': 0}
                          }

initialize()