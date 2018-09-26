import game_effects
import game_constants
import pygame

def parse_equipment():
    # Equipment = (name, rarity, size, description, slot, stats, mods, requirements, tags, sprite)
    items = []
    file = open('resources/ArmorData.csv', 'r')
    for line in file.read().split('\n')[1:-1]: # Divide by line
        values = line.split(';') # Divide each line by field
        # values[0] and values[1] are already in the correct format.
        values[2] = int(values[2]) # '15' ---> 15
        # values[3] is also in the correct format.
        values[4] = int(values[4]) # '15' ---> 15
        values[5] = list(((a.split(': ')[0], int(a.split(': ')[1])) for a in values[5].split(', '))) # ['MaxHealth: 100', ...] ---> [('MaxHealth', 100), ...]
        values[6] = values[6].split(', ') if values[6] else [] # Separate functions
        values[6] = list(eval('game_effects.{}'.format(f).replace('>', ',')) for f in values[6]) if values[6] else [] # "function(a< b< c)" ---> "function(a, b, c)"
        values[7] = values[7].split(', ') if values[7] else []
        values[8] = values[8].split(', ') if values[8] else []
        # values[9] gets processed later.
        items.append(list(values))
    file.close()
    return items
def parse_weapons():
    # Weapon = (name, rarity, size, description, type, stats, mods, requirements, tags, sprite, sprite_attack)
    items = []
    file = open('resources/WeaponData.csv', 'r')
    for line in file.read().split('\n')[1:-1]: # Divide by line
        values = line.split(';') # Divide each line by field
        # values[0] and values[1] are already in the correct format.
        values[2] = int(values[2]) # '15' ---> 15
        # values[3] and values[4] are also in the correct format.
        values[5] = list(((a.split(': ')[0], int(a.split(': ')[1])) for a in values[5].split(', '))) # ['MaxHealth: 100', ...] ---> [('MaxHealth', 100), ...]
        values[6] = values[6].split(', ') if values[6] else [] # Separate functions
        values[6] = list(eval('game_effects.{}'.format(f).replace('>', ',')) for f in values[6]) if values[6] else [] # "function(a< b< c)" ---> "function(a, b, c)"
        values[7] = values[7].split(', ') if values[7] else []
        values[8] = values[8].split(', ') if values[8] else []
        # values[9] gets processed later
        items.append(list(values))
    file.close()
    return items

def get_animation(filename, repeat = False):
    image = pygame.image.load(filename).convert()
    frame_qty = int(image.get_width()/32)
    frames = [pygame.Surface((32, 32)).convert() for i in range(frame_qty)]
    for i in range(len(frames)):
        frames[i].blit(image, (0, 0), (i*32, 0, 32, 32))
        frames[i].set_colorkey(game_constants.COLOR_COLORKEY, pygame.RLEACCEL)
    if repeat:
        return frames + list(reversed(frames))
    else:
        return frames
def get_equipment(item_name):
    return next(i for i in equipment if i[0] == item_name)
def get_weapon(item_name):
    return next(i for i in weapons if i[0] == item_name)

equipment = parse_equipment()
weapons = parse_weapons()