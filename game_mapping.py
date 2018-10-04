import game_content
import game_constants
import game_classes
import game_parsers
import game_util
import random
import libtcodpy
import pygame

pygame.init()

#Tiles: {-2: Wall (Algorithm), -1: Floor (Algorithm), 0: Wall, 1: Floor, 2: Water, 3: Lava, 4: Glass, 5: Void}
TILES = {
    -2: (False, False, pygame.image.load('resources/graphics/tiles/wall.png')), # Wall (algorithm)
    -1: (True, True, pygame.image.load('resources/graphics/tiles/floor_dirt.png')), # Floor (algorithm)
    0: (False, False, pygame.image.load('resources/graphics/tiles/wall.png')), # Wall
    1: (True, True, pygame.image.load('resources/graphics/tiles/floor.png')), # Floor
    2: (True, True, pygame.image.load('resources/graphics/tiles/water.png')), # Water
    3: (True, True, pygame.image.load('resources/graphics/tiles/lava.png')), # Lava
    4: (True, True, pygame.image.load('resources/graphics/tiles/glass.png')), # Glass
    5: (True, True, pygame.image.load('resources/graphics/tiles/void.png')) # Void
}

ENEMIES = [
    game_content.m_slime
]

def path_cost(_1, _2, x, y, array):
    if array[x][y] == -1:
        return 0.7
    elif array[x][y] == -2:
        return 1
    else:
        return 20

def mapgen_dungeon(width, height):
    # Initialize structures.
    tiles = [[-2 for _ in range(width)] for _ in range(height)]
    items = []
    entities = []
    creatures = []
    doors = []

    rooms = []
    room_exits = []

    # Set a 3 x 3 starting room, randomly allocated, contained within the limits of the map.
    x_init = random.randint(6, width - 6)
    y_init = random.randint(6, height - 6)
    player_x = x_init + 1
    player_y = y_init + 1
    rooms.append({'x': x_init, 'y':  y_init, 'width': 3, 'height': 3})
    room_exits.append((player_x, player_y, -1))
    for i in range(x_init, x_init + 3):
        for j in range(y_init, y_init + 3):
            tiles[i][j] = -1

    # Try to add as many rooms as possible.
    for t in range(100):
        room = game_parsers.get_room(boss = False)
        room_width = len(room['layout']['tiles'][0])
        room_height = len(room['layout']['tiles'])
        available_spots = [(x, y) for x in range(3, width - room_width - 3) for y in range(3, height - room_height - 3) if tiles[y][x] == -2]
        random.shuffle(available_spots)
        for (x, y) in available_spots[::2]:
            if all((not game_util.rectangle_intersects((x, y, room_width, room_height), (e['x'], e['y'], e['width'], e['height'])) for e in rooms)):
                rooms.append({'x': x, 'y': y, 'width': room_width, 'height': room_height})
                for i in range(room_width):
                    for j in range(room_height):
                        tiles[x + i][y + j] = room['layout']['tiles'][j][i]
                        entity = room['layout']['entities'][j][i]
                        if entity == 1:
                            room_exits.append((x + i,  y + j, t))
                        if entity == 2:
                            room_exits.append((x + i, y + j, t))
                            entities.append(game_content.n_door(x + i, y + j))
                            doors.append((x + i, y + j))
                        if entity == 3 or entity == 4:
                            creatures.append(random.choice(ENEMIES)(x + i, y + j))
                        if entity == 5 or entity == 6 or entity == 7:
                            items.append(game_content.weapon('Holy sword', x = x + i, y = y + j))

                break

    for (x, y, r) in room_exits:
        path = libtcodpy.path_new_using_function(width, height, path_cost, tiles, 0)
        try:
            other_exit = sorted([(o_x, o_y, o_r) for (o_x, o_y, o_r) in room_exits if r != o_r], key = lambda n: game_util.simpledistance((n[0], n[1]), (x, y)))[0]
        except Exception as e:
            print(e)
            other_exit = (x, y, r)
        libtcodpy.path_compute(path, x, y, other_exit[0], other_exit[1])
        print('Starting path from {}, {} to {}, {}'.format(x, y, other_exit[0], other_exit[1]))
        for i in range(libtcodpy.path_size(path)-1):
            a, b = libtcodpy.path_get(path, i)
            print('Path (step {}): {}, {}'.format(i, a, b))
            tiles[a][b] = -1

    for i in range(len(tiles)):
        for j in range(len(tiles[i])):
            tiles[i][j] = game_classes.Tile(i, j, *TILES[tiles[i][j]])

    for door in doors:
        tiles[door[0]][door[1]].passable = False
        tiles[door[0]][door[1]].transparent = False

    for i in tiles:
        print(str(i))
    print('ITEMS: {}\nENTITIES: {}\nCREATURES: {}\nPLAYER: x = {}, y = {}'.format(items, entities, creatures, player_x, player_y))
    return tiles, items, entities, creatures, player_x, player_y

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