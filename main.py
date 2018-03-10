# IMPORT
import pygame
import libtcodpy
import random
import math
import sys
import profile
import util
import game_constants

# GAME
def game_init():
    global STATE, MENU, GAME, TILES, SCREEN, CLOCK, game_classes, game_content
    pygame.init()
    SCREEN = pygame.display.set_mode((game_constants.WINDOW_WIDTH, game_constants.WINDOW_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])

    import game_classes
    import game_content

    STATE = 0

    pygame.display.set_caption('I found a strange potion')
    SCREEN.set_alpha(None)

    MENU = game_classes.MainMenu()
    GAME = game_classes.Game()
    CLOCK = pygame.time.Clock()

    game_classes.GAME = GAME
    game_classes.SCREEN = SCREEN
    game_content.GAME = GAME
    game_content.SCREEN = SCREEN
    util.GAME = GAME
    util.SCREEN = SCREEN
def game_loop():
    while True:
        if STATE == 0:
            draw_menu()
            menu_input()
        elif STATE == 9:
            GAME.action = 'none'
            game_input()
            for entity in GAME.entities + GAME.items + GAME.creatures + GAME.player.inventory:
                entity.update_frame()
            if GAME.action != 'none':
                GAME.updateOrder()
                GAME.creaturesExecuteTurn()
                GAME.entitiesExecuteTurn()
                GAME.turn_counter += 1
            GAME.camera.update(GAME.player.x, GAME.player.y)
            draw_game()
        CLOCK.tick()
def game_input():
    events = pygame.event.get();
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif len(GAME.visualactiveeffects) == 0:
                GAME.player.input(event.key)
                GAME.rd_map = True
                GAME.rd_sta = True
                GAME.surface_entities.fill(game_constants.COLOR_COLORKEY)

                if event.key == game_constants.KEY_INVENTORY:
                    if GAME.windows == [] and len(GAME.player.inventory) > 0:
                        GAME.windows.append(game_content.Window_PlayerInventory())
                        GAME.controlsText = game_constants.TEXT_ONINVENTORY
                        GAME.rd_win = True
                if event.key == game_constants.KEY_SEARCH:
                    if GAME.windows == [] and len([item for item in GAME.items if (item.x == GAME.player.x and item.y == GAME.player.y)]) > 0:
                        GAME.windows.append(game_content.Window_SearchInventory())
                        GAME.controlsText = game_constants.TEXT_ONSEARCH
                        GAME.rd_win = True
                if event.key == game_constants.KEY_STATUS:
                    if GAME.windows == []:
                        GAME.windows.append(game_content.Window_Status())
                        GAME.controlsText = game_constants.TEXT_ONSTATUS
                        GAME.rd_win = True
                if event.key == game_constants.KEY_EQUIPMENT:
                    if GAME.windows == []:
                        GAME.windows.append(game_content.Window_Equipment())
                        GAME.controlsText = game_constants.TEXT_ONEQUIPMENT
                        GAME.rd_win = True

                if event.key == pygame.K_UP:
                    for window in GAME.windows:
                        if window.active:
                            window.input('up')
                            GAME.rd_win = True
                            return
                if event.key == pygame.K_DOWN:
                    for window in GAME.windows:
                        if window.active:
                            window.input('down')
                            GAME.rd_win = True
                            return
                if event.key == pygame.K_LEFT:
                    for window in GAME.windows:
                        if window.active:
                            window.input('left')
                            GAME.rd_win = True
                            return
                if event.key == pygame.K_RIGHT:
                    for window in GAME.windows:
                        if window.active:
                            window.input('right')
                            GAME.rd_win = True
                            return
                if event.key == game_constants.KEY_USE:
                    for window in GAME.windows:
                        if window.active:
                            window.input('use')
                            GAME.rd_win = True
                            return
                if event.key == game_constants.KEY_CANCEL:
                    for window in GAME.windows:
                        if window.active:
                            window.input('cancel')
                            GAME.rd_win = True
                            return
                if event.key == game_constants.KEY_LOG:
                    GAME.rd_log = True
                    if GAME.long_log:
                        GAME.long_log = False
                    else:
                        GAME.long_log = True
def menu_input():
    global STATE
    global MENU
    global GAME
    events = pygame.event.get();
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if STATE == 0:
            if event.type == pygame.KEYDOWN:
                MENU.rd_opt = True
                if event.key == pygame.K_UP:
                    MENU.option =  (MENU.option - 1) % 3
                    MENU.update = True
                    return
                if event.key == pygame.K_DOWN:
                    MENU.option =  (MENU.option + 1) % 3
                    MENU.update = True
                    return
                if event.key == game_constants.KEY_USE:
                    if MENU.option == 0:

                        STATE = 9
                        GAME.player = game_content.p_normal(game_constants.MAP_WIDTH[0]//2, game_constants.MAP_HEIGHT[0]//2)
                        generateMap()
                        GAME.creatures.append(GAME.player)

                        # FOR TESTING PURPOSES:
                        GAME.player.inventory += [game_content.i_magichelmet(0, 0), game_content.i_thunderrod(0, 0), game_content.i_thunderrod(0, 0), game_content.i_thunderrod(0, 0)]

                        GAME.light_map = map_light_init(GAME.map)
                        util.map_light_update(GAME.light_map)
                    return
                if event.key == game_constants.KEY_CANCEL:
                    MENU.option =  (MENU.option + 1) % 3
                    MENU.update = True
                    return


# DRAW
def draw_game():
    SCREEN.fill([255,255,255])

    if GAME.rd_log: # CHECK IF SURFACE_LOG NEEDS TO BE REDRAWN
        draw_log()
        GAME.rd_log = False
    if GAME.rd_sta: # CHECK IF SURFACE_STATUS NEEDS TO BE REDRAWN
        draw_status()
        GAME.rd_sta = False
    if GAME.rd_map: # CHECK IF SURFACE_LOG NEEDS TO BE REDRAWN
        draw_map()
        GAME.rd_map = False
    if GAME.rd_win: # CHECK IF SURFACE_WINDOWS NEEDS TO BE REDRAWN
        draw_windows()
        GAME.rd_win = False

    # BLIT ALL SURFACES INTO THE MAIN SURFACE
    for surface in [GAME.surface_map, GAME.surface_effects, GAME.surface_entities, GAME.surface_windows]: # DRAW ALL SURFACES AT (0, 0)
        SCREEN.blit(surface, (0, 0))
    GAME.update_rects.append(SCREEN.blit(GAME.surface_log, (0, game_constants.CAMERA_HEIGHT*32)))
    GAME.update_rects.append(SCREEN.blit(GAME.surface_status, (game_constants.LOG_WIDTH + 4, game_constants.CAMERA_HEIGHT*32))) # SURFACE_STATUS NEEDS TO BE DRAWN IN A DIFFERENT POSITION
    draw_effects() # THEY ARE DRAWN EVERY FRAME BECAUSE THEY ARE ANIMATED
    draw_entities() # SAME AS EFFECTS

    # FOR DEBUG PURPOSES
    GAME.update_rects.append(util.draw_text_bg(SCREEN, 'X: ' + str(GAME.player.x) + '   Y: ' + str(GAME.player.y), 10, 10, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK))
    GAME.update_rects.append(util.draw_text_bg(SCREEN, 'FPS: ' + str(math.floor(CLOCK.get_fps())), 10, 28, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK))
    GAME.update_rects.append(util.draw_text_bg(SCREEN, 'TURN: ' + str(GAME.turn_counter), 10, 46, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK))

    pygame.display.update(GAME.update_rects) # DRAW ALL THE SECTIONS ON THE SCREEN THAT UPDATED ON THIS CYCLE
    GAME.update_rects = [] # CLEAR THE LIST OF SECTIONS TO REDRAW

def draw_map():
    GAME.update_rects.append(GAME.surface_map.fill(game_constants.COLOR_BLACK))
    for x in range(0, game_constants.CAMERA_WIDTH):
        for y in range(0, game_constants.CAMERA_HEIGHT):
            if libtcodpy.map_is_in_fov(GAME.light_map, GAME.camera.x + x, GAME.camera.y + y):
                GAME.surface_map.blit(GAME.map[GAME.camera.x + x][GAME.camera.y + y].sprite, (x*32, y*32))
                GAME.map[GAME.camera.x + x][GAME.camera.y + y].discovered = True
            elif GAME.map[GAME.camera.x + x][GAME.camera.y + y].discovered == True:
                GAME.surface_map.blit(GAME.map[GAME.camera.x + x][GAME.camera.y + y].sprite_shadow, (x*32, y*32))
    pygame.draw.rect(GAME.surface_map, game_constants.COLOR_BORDER, pygame.Rect(game_constants.BORDER_THICKNESS, game_constants.BORDER_THICKNESS, game_constants.CAMERA_WIDTH*32-game_constants.BORDER_THICKNESS*2, game_constants.CAMERA_HEIGHT*32-game_constants.BORDER_THICKNESS*2), game_constants.BORDER_THICKNESS*2)
def draw_entities():
    for creature in GAME.creatures:
        if libtcodpy.map_is_in_fov(GAME.light_map, creature.x, creature.y):
            creature.draw()
    for entity in GAME.entities:
        if libtcodpy.map_is_in_fov(GAME.light_map, entity.x, entity.y):
            entity.draw()
    for item in GAME.items:
        if libtcodpy.map_is_in_fov(GAME.light_map, item.x, item.y):
            item.draw()
def draw_log():
    messages = game_constants.LOG_MAX_LENGTH
    height = min(game_constants.LOG_MAX_LENGTH*18 + 8, len(GAME.log)*18 + 8)

    GAME.surface_log.fill(game_constants.COLOR_DARKESTGRAY)
    for x in range(0, min(messages, len(GAME.log))):
        util.draw_text_bg(GAME.surface_log, GAME.log[x][0], 10, x*14 + 4, game_constants.FONT_PERFECTDOS_SMALL, GAME.log[x][1], game_constants.COLOR_DARKGRAY)
def draw_status():
    GAME.surface_status.blit(game_constants.SPRITE_STATUS, (0, 0))

    GAME.surface_status.blit(game_content.SPRITESHEET_ICONS.image_at((0, 0, 16, 16), colorkey = game_constants.COLOR_COLORKEY), (16, 8)) #DRAW HP
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_DARKESTGRAY, pygame.Rect(48, 8, 200, 13))
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_HP, pygame.Rect(48, 8, 200*GAME.player.hp/GAME.player.stats[0], 13))
    text = game_constants.FONT_PERFECTDOS.render(str(GAME.player.hp), False, game_constants.COLOR_WHITE)
    GAME.surface_status.blit(text, (256, 8))
    text = game_constants.FONT_PERFECTDOS.render(str(GAME.player.stats[0]), False, game_constants.COLOR_WHITE)
    GAME.surface_status.blit(text, (330 - text.get_width(), 8))

    GAME.surface_status.blit(game_content.SPRITESHEET_ICONS.image_at((0, 16, 16, 16), colorkey = game_constants.COLOR_COLORKEY), (16, 32)) #DRAW MANA
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_DARKESTGRAY, pygame.Rect(48, 32, 200, 13))
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_CYAN, pygame.Rect(48, 32, 200*GAME.player.mana/GAME.player.stats[1], 13))
    text = game_constants.FONT_PERFECTDOS.render(str(GAME.player.mana), False, game_constants.COLOR_WHITE)
    GAME.surface_status.blit(text, (256, 32))
    text = game_constants.FONT_PERFECTDOS.render(str(GAME.player.stats[1]), False, game_constants.COLOR_WHITE)
    GAME.surface_status.blit(text, (330 - text.get_width(), 32))

    GAME.surface_status.blit(game_content.SPRITESHEET_ICONS.image_at((16, 0, 16, 16), colorkey = game_constants.COLOR_COLORKEY), (16, 56)) #DRAW FOOD
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_DARKESTGRAY, pygame.Rect(48, 56, 80, 13))
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_HUNGER, pygame.Rect(48, 56, 80*GAME.player.hunger/game_constants.MAX_HUNGER, 13))

    GAME.surface_status.blit(game_content.SPRITESHEET_ICONS.image_at((32, 0, 16, 16), colorkey = game_constants.COLOR_COLORKEY), (138, 56)) #DRAW CARRY
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_DARKESTGRAY, pygame.Rect(168, 56, 80, 13))
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_YELLOW, pygame.Rect(168, 56, 80*GAME.player.currentWeight()/GAME.player.stats[10], 13))

    for textIndex in range(len(GAME.controlsText)): #DRAW CONTROLS
        xOffset = (textIndex // 3) *200
        util.draw_text(GAME.surface_status, GAME.controlsText[textIndex][0], 500 + xOffset, (textIndex%3)*16+4, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
        util.draw_text(GAME.surface_status, GAME.controlsText[textIndex][1], 550 + xOffset, (textIndex%3)*16+4, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
def draw_effects():
    for effect in (GAME.visualeffects + GAME.visualactiveeffects): # UPDATE ALL VISUAL EFFECTS AND DRAW THEM
        GAME.update_rects.append((effect.x - GAME.camera.x*32, effect.y - GAME.camera.y*32, effect.width, effect.height))
        effect.execute()
        if util.isinscreen(effect.x, effect.y):
            GAME.update_rects.append(SCREEN.blit(effect.surface, (effect.x - GAME.camera.x*32, effect.y - GAME.camera.y*32)))
def draw_windows():
    GAME.update_rects.append(GAME.surface_windows.fill(game_constants.COLOR_COLORKEY))
    for window in GAME.windows: # DRAW ALL VISIBLE IN-GAME WINDOWS
        if window.visible:
            window.draw()


def draw_menu():
    if MENU.rd_img:
        MENU.update_rects.append(MENU.surface_logo.blit(game_constants.SPRITE_TITLE, (0, 0)))
        MENU.rd_img = False
    if MENU.rd_opt:
        MENU.update_rects.append(MENU.surface_options.fill(game_constants.COLOR_COLORKEY))
        pygame.draw.rect(MENU.surface_options, game_constants.COLOR_DARKRED, pygame.Rect(game_constants.WINDOW_WIDTH/2 - 128,  game_constants.WINDOW_HEIGHT*3/4 + MENU.option*32, 256, 32))
        for textIndex in range(len(MENU.optionsText)):
            MENU.surface_options.blit(MENU.optionsText[textIndex], (game_constants.WINDOW_WIDTH/2 - MENU.optionsText[textIndex].get_width()/2, game_constants.WINDOW_HEIGHT*3/4 + textIndex*32))

    for surface in [MENU.surface_logo, MENU.surface_options]: # DRAW ALL SURFACES AT (0, 0)
        SCREEN.blit(surface, (0, 0))

    # FOR DEBUG PURPOSES
    MENU.update_rects.append(util.draw_text_bg(SCREEN, 'FPS: ' + str(math.floor(CLOCK.get_fps())), 10, 28, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK))

    pygame.display.update(MENU.update_rects)
    MENU.update_rects = []


#def draw_charselect():


# MAP
def generateMap():
    GAME.map, GAME.items, GAME.entities, GAME.creatures = map_init_dungeon(game_constants.MAP_WIDTH[GAME.level], game_constants.MAP_HEIGHT[GAME.level])


def map_init_noise(width, height):
    map_gen = []
    noise = libtcodpy.noise_new(2)
    libtcodpy.noise_set_type(noise, libtcodpy.NOISE_SIMPLEX)
    for x in range(0, width):
        aux = []
        for y in range(0, height):
            if libtcodpy.noise_get(noise, [(x+1)/3, y/3]) > 0.6:
                aux.append(Tile(False, True, False, 0, GAME.tiles.image_at((0, 0, 32, 32)), GAME.tiles.image_at((0, 32, 32, 32)))) # WALL
            else:
                aux.append(Tile(True, False, True, 0, GAME.tiles.image_at((32, 0, 32, 32)), GAME.tiles.image_at((32, 32, 32, 32)))) #F LOOR
        map_gen.append(aux)
    map_gen = map_set_borders(map_gen, width-1, height-1) # BORDERS
    return map_gen
def map_init_walk(width, height, floor_percent):
    map_gen = [[game_content.t_cave_wall(i, j) for j in range(height)] for i in range(width)]
    x = math.floor(width/2)
    y = math.floor(height/2)
    floor_left = math.floor(width * height * floor_percent)
    while floor_left > 0:
        if not map_gen[x][y].passable:
            map_gen[x][y] = game_content.t_cave_floor(x, y)
            floor_left -= 1
        direction = random.randint(0, 1)
        if direction == 0:
            x += random.randint(-1,1)
        else:
            y += random.randint(-1,1)
        if x >= width-4:
            x -= 4
        if x < 4:
            x += 4
        if y >= height-4:
            y -= 4
        if y < 4:
            y += 4
    map_gen = map_set_borders(map_gen, width-1, height-1)
    return map_gen
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
    monsters_pool = [[game_content.m_slime], []]


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
            if util.rectangle_intersects(newRoom, room):
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
        other_exits = sorted([exit_other for exit_other in room_exits if exit_other[2] != exit_init[2] and (exit_other[2], exit_init[2]) not in room_connections], key = lambda e: util.simpledistance((exit_init[0], exit_init[1]), (e[0], e[1])))
        if len(other_exits) > 0:
            exit_end = other_exits[0]
        else:
            exit_end = sorted([exit_other for exit_other in room_exits if exit_other[2] != exit_init[2]], key = lambda e: util.simpledistance((exit_init[0], exit_init[1]), (e[0], e[1])))[0]
        room_connections.append((exit_init[2], exit_end[2]))
        room_connections.append((exit_end[2], exit_init[2]))
        libtcodpy.path_compute(path, exit_init[0], exit_init[1], exit_end[0], exit_end[1])
        for i in range(libtcodpy.path_size(path)-1):
            x, y = libtcodpy.path_get(path, i)
            alg_array[x][y] = 3

    for x in range(len(alg_array)):
        for y in range(len(alg_array[x])):
            if alg_array[x][y] in [0, 1]:
                terrain[x][y] = game_content.t_cave_wall(x, y)
            else:
                terrain[x][y] = game_content.t_cave_floor(x, y)
            if alg_array[x][y] == 4:
                creatures.append(random.choice(monsters_pool[GAME.level])(x, y))
            if alg_array[x][y] == 7:
                entities.append(game_content.n_door(x, y, game_content.SPRITESHEET_ENTITIES.image_at((0, 32, 32, 32)), game_content.SPRITESHEET_ENTITIES.image_at((32, 32, 32, 32), colorkey = game_constants.COLOR_COLORKEY)))
                terrain[x][y].passable = False
                terrain[x][y].transparent = False
    return terrain, items, entities, creatures
def map_set_borders(map_array, width, height):
    for x in range(0, width):
        map_array[x][0] = game_content.t_unbreakable_wall(x, 0)
        if random.randint(0,2) == 0:
            map_array[x][0] = game_content.t_unbreakable_wall(x, 1)
        map_array[x][height] = game_content.t_unbreakable_wall(x, height)
        if random.randint(0,2) == 0:
            map_array[x][height-1] = game_content.t_unbreakable_wall(x, height-1)
    for y in range(0, height):
        map_array[0][y] = game_content.t_unbreakable_wall(0, y)
        if random.randint(0,2) == 0:
            map_array[1][y] = game_content.t_unbreakable_wall(1, y)
        map_array[width][y] = game_content.t_unbreakable_wall(width, y)
        if random.randint(0,2) == 0:
            map_array[width-1][y] = game_content.t_unbreakable_wall(width-1, y)
    return map_array

def map_light_init(map_array):
    width = len(map_array)
    height = len(map_array[0])
    light_map = libtcodpy.map_new(width, height)

    for x in range(0, width):
        for y in range(0, height):
            libtcodpy.map_set_properties(light_map, x, y, map_array[x][y].transparent, map_array[x][y].passable)
    return light_map


# EXECUTION
if __name__ == '__main__':
    game_init()
    game_loop()
