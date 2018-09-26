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
C_BLACK = (20, 20, 20)
C_GREEN = (0, 200, 0)
C_RED = (200, 0, 0)

# General
def initialize():
    global SCREEN, DATA, FONT, EVENTS
    pygame.init()
    SCREEN = pygame.display.set_mode(WINDOW_SIZE, 0, 16)
    DATA = Data()
    FONT = pygame.font.Font('font.ttf', 12)
    EVENTS = []
    pygame.display.set_caption("Room Editor for IFASP")
    while True:
        EVENTS = pygame.event.get()
        DATA.update()
        handleInput()
        drawCycle()


def drawCycle():
    for x in range(DATA.width):
        for y in range(DATA.height):
            DATA.tiles[x][y].draw()
    for element in DATA.UIElements:
        element.draw()
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
        self.tiles = []
        self.UIElements = []
        self.file = None
        self.data = None
        self.initializeMap()
        self.loadFile()
    def update(self):
        self.UIElements.sort(key = lambda e: e.z)
    def initializeMap(self):
        self.tiles = [[Tile(x*34 + 32, y*34 + 32, 1, 32) for x in range(self.width)] for y in range(self.height)]
    def loadFile(self):
        self.file = open('roomsData.dat', 'r')
        self.data = json.loads(self.file.read())
        self.file.close()
    def saveFile(self):
        self.file = open('roomsData.dat', 'w')
        self.file.write(json.dumps(self.data))
        self.file.close()

class UIElement:
    def __init__(self, x, y, z, width, height):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
    def draw(self):
        pass
    def onClick(self):
        pass

class TextLabel(UIElement):
    def __init__(self, x, y, z, id_number, width, height, text):
        super().__init__(x, y, z, width, height)
        self.text = text
        self.id_number = id_number
    def draw(self):
        pygame.draw.rect(SCREEN, C_WHITE, pygame.Rect(self.x, self.y, self.width, self.height))
        SCREEN.blit(FONT.render(self.text, False, C_BLACK, C_WHITE), (self.x + 8, self.y + 8))

class Button(UIElement):
    def __init__(self, x, y, z, width, height, text, f):
        super().__init__(x, y, z, width, height)
        self.text = text
        self.f = f
    def draw(self):
        pygame.draw.rect(SCREEN, C_WHITE, pygame.Rect(self.x, self.y, self.width, self.height))
        SCREEN.blit(FONT.render(self.text, False, C_BLACK, C_WHITE), (self.x + 8, self.y + 8))
    def onClick(self):
        self.f(self)

class Tile(UIElement):
    def __init__(self, x, y, z, side):
        super().__init__(x, y, z, side, side)
    def draw(self):
        pygame.draw.rect(SCREEN, C_WHITE, pygame.Rect(self.x, self.y, self.width, self.height))
    def Onclick(self):
        pass

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
        SCREEN.blit(FONT.render(self.text, False, C_BLACK, C_WHITE), (self.x + 14, self.y))
    def onClick(self):
        self.active = not self.active

class CheckboxGroup(Checkbox):
    def __init__(self, x, y, z, id_number, text, group):
        super().__init__(x, y, z, id_number, text, False)
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

# Functions



initialize()
print(__name__)