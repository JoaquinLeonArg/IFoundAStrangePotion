from pyglet import *
import game_effects
import game_content
import game_constants
import game_classes
import game_parsers
import game_util
import random
import libtcodpy

#Tiles: {-2: Wall (Algorithm), -1: Floor (Algorithm), 0: Wall, 1: Floor, 2: Water, 3: Lava, 4: Glass, 5: Void}
TILES_DUNGEON = {
    -2: (False, False, resource.image('resources/graphics/tiles/wall.png'), [game_effects.StoneOnDestroy(1)]), # Wall (algorithm)
    -1: (True, True, resource.image('resources/graphics/tiles/floor_dirt.png')), # Floor (algorithm)
    0: (False, False, resource.image('resources/graphics/tiles/wall.png'), [game_effects.StoneOnDestroy(1)]), # Wall
    1: (True, True, resource.image('resources/graphics/tiles/floor.png')), # Floor
    2: (True, True, resource.image('resources/graphics/tiles/water.png')), # Water
    3: (True, True, resource.image('resources/graphics/tiles/lava.png')), # Lava
    4: (True, True, resource.image('resources/graphics/tiles/glass.png')), # Glass
    5: (True, True, resource.image('resources/graphics/tiles/void.png')) # Void
}

TILES_FOREST = {
    0: (True, True, resource.image('resources/graphics/tiles/grass.png')), # Floor
    1: (False, False, resource.image('resources/graphics/tiles/tree.png'), [game_effects.StoneOnDestroy(1)]) # Wall
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
    tiles_return = [[-2 for _ in range(width)] for _ in range(height)]
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
                            entities.append(game_content.EntityDoor(x + i, y + j))
                            doors.append((x + i, y + j))
                        if entity == 3 or entity == 4:
                            creatures.append(random.choice(ENEMIES)(x + i, y + j))
                        if entity == 5 or entity == 6 or entity == 7:
                            #items.append(game_content.weapon('Holy sword', x = x + i, y = y + j))
                            pass

                break

    for (x, y, r) in room_exits:
        path = libtcodpy.path_new_using_function(width, height, path_cost, tiles, 0)
        try:
            other_exit = sorted([(o_x, o_y, o_r) for (o_x, o_y, o_r) in room_exits if r != o_r], key = lambda n: game_util.simpledistance((n[0], n[1]), (x, y)))[0]
        except Exception as e:
            print(e)
            other_exit = (x, y, r)
        libtcodpy.path_compute(path, x, y, other_exit[0], other_exit[1])
        for i in range(libtcodpy.path_size(path)-1):
            a, b = libtcodpy.path_get(path, i)
            tiles[a][b] = -1

    for i in range(len(tiles)):
        for j in range(len(tiles[i])):
            tiles_return[i][j] = game_classes.Tile(i, j, *TILES_DUNGEON[tiles[i][j]])
            if len(tiles) - 1 > i > 0 and len(tiles[0]) - 1 > j > 0 and tiles[i][j] in [-2, 0]:
                if tiles[i - 1][j] not in [-2, 0]:
                    tiles_return[i][j].outline(0)
                if tiles[i][j - 1] not in [-2, 0]:
                    tiles_return[i][j].outline(1)
                if tiles[i + 1][j] not in [-2, 0]:
                    tiles_return[i][j].outline(2)
                if tiles[i][j + 1] not in [-2, 0]:
                    tiles_return[i][j].outline(3)
                tiles_return[i][j].generate_sprite_shadow()


    for door in doors:
        tiles_return[door[0]][door[1]].passable = False
        tiles_return[door[0]][door[1]].transparent = False

    return tiles_return, items, entities, creatures, player_x, player_y

def mapgen_woods(width, height):
    # Initialize structures.
    tiles = [[1 if random.random() < 0.44 else 0 for _ in range(height)] for _ in range(width)]
    tiles_return = [[0 for _ in range(height)] for _ in range(width)]
    items = []
    entities = []
    creatures = []

    # Set starting position.
    player_x, player_y = random.randrange(10, width - 10), random.randrange(10, height - 10)
    new_tiles = tiles
    for l in range(200):
        for i in range(width):
            for j in range(height):
                if width - 2 > i > 3 and height - 2 > j > 3:  # Middle section of the map
                    surrounding_walls = sum(tiles[x][y] for x in range(i - 1, i + 2) for y in range(j - 1, j + 2))
                    surrounding_walls_bigger = sum(tiles[x][y] for x in range(i - 2, i + 3) for y in range(j - 2, j + 3))
                else:  # Borders of the map
                    surrounding_walls = 9
                    surrounding_walls_bigger = 16
                if surrounding_walls_bigger < 4:
                    if random.random() < 0.5:
                        n = 1
                    else:
                        n = 2
                    for x in range(i - 2, i + 3):
                        for y in range(j - 2, j + 3):
                            if random.random() < 0.85:
                                tiles[x][y] = n
                elif surrounding_walls >= 6 and tiles[i][j] == 0:
                    new_tiles[i][j] = 1
                elif surrounding_walls <= 4 and tiles[i][j] == 1:
                    new_tiles[i][j] = 0
        if new_tiles == tiles:
            break
        else:
            tiles = new_tiles

    for i in range(width):
        for j in range(height):
            if tiles[i][j] != 2:
                tiles_return[i][j] = game_classes.Tile(i, j, *TILES_FOREST[tiles[i][j]])
            else:
                tiles_return[i][j] = game_classes.Tile(i, j, *TILES_FOREST[0])
                entities.append(game_content.EntityTallGrass(i, j))
                tiles_return[i][j].transparent = False

    return tiles_return, items, entities, creatures, player_x, player_y




'''def map_set_borders(map_array, width, height):
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
    return map_array'''