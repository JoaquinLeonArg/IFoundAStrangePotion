import game_effects
import game_constants
import pygame

def parse_equipment():
    items = []
    file = open('resources/ArmorData.csv', 'r')
    for line in file.read().split('\n')[1:-1]: # Divide by line
        values = line.split(';') # Divide each line by field
        print(values)
        values[2] = int(values[2]) # '15' ---> 15
        values[4] = int(values[4]) # '15' ---> 15
        values[5] = list(((a.split(': ')[0], int(a.split(': ')[1])) for a in values[5].split(', '))) # ['MaxHealth: 100', ...] ---> [('MaxHealth', 100), ...]
        values[6] = values[6].split(', ') if values[6] else [] # Separate functions
        values[6] = list(eval('game_effects.{}'.format(f).replace('>', ',')) for f in values[6]) if values[6] else [] # "function(a< b< c)" ---> "function(a, b, c)"
        values[7] = values[7].split(', ') if values[7] else []
        values[8] = values[8].split(', ') if values[8] else []
        # Values[9] gets processed later
        items.append(tuple(i for i in values))
    return items

def get_animation(filename):
    image = pygame.image.load(filename).convert()
    frames = [pygame.Surface((32, 32)).convert() for i in range(4)]
    for i in range(len(frames)):
        frames[i].blit(image, (0, 0), (i*32, 0, 32, 32))
        frames[i].set_colorkey(game_constants.COLOR_COLORKEY, pygame.RLEACCEL)
    return frames + list(reversed(frames))

def get_equipment(item_name):
    return next(i for i in equipment if i[0] == item_name)

equipment = parse_equipment()

print(get_equipment('Cowboy hat'))
