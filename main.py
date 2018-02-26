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
        CLOCK.tick(120)
        if STATE == 0:
            draw_menu()
            menu_input()
        elif STATE == 9:
            GAME.action = 'none'
            game_input()
            if GAME.action != 'none':
                GAME.creaturesExecuteTurn()
                GAME.entitiesExecuteTurn()
                GAME.draw_map = True
            GAME.camera.update(GAME.player.x, GAME.player.y)
            draw_game()
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
            GAME.player.input(event.key)
            util.map_light_update(GAME.light_map)

            if event.key == game_constants.KEY_INVENTORY:
                if GAME.windows == [] and len(GAME.player.inventory) > 0:
                    GAME.windows.append(game_content.Window_PlayerInventory())
                    GAME.controlsText = game_constants.TEXT_ONINVENTORY
            if event.key == game_constants.KEY_SEARCH:
                if GAME.windows == [] and len([item for item in GAME.items if (item.x == GAME.player.x and item.y == GAME.player.y)]) > 0:
                    GAME.windows.append(game_content.Window_SearchInventory())
                    GAME.controlsText = game_constants.TEXT_ONSEARCH
            if event.key == game_constants.KEY_STATUS:
                if GAME.windows == []:
                    GAME.windows.append(game_content.Window_Status())
                    GAME.controlsText = game_constants.TEXT_ONSTATUS
            if event.key == game_constants.KEY_EQUIPMENT:
                if GAME.windows == []:
                    GAME.windows.append(game_content.Window_Equipment())
                    GAME.controlsText = game_constants.TEXT_ONEQUIPMENT

            if event.key == pygame.K_UP:
                for window in GAME.windows:
                    if window.active:
                        window.input('up')
                        return
            if event.key == pygame.K_DOWN:
                for window in GAME.windows:
                    if window.active:
                        window.input('down')
                        return
            if event.key == pygame.K_LEFT:
                for window in GAME.windows:
                    if window.active:
                        window.input('left')
                        return
            if event.key == pygame.K_RIGHT:
                for window in GAME.windows:
                    if window.active:
                        window.input('right')
                        return
            if event.key == game_constants.KEY_USE:
                for window in GAME.windows:
                    if window.active:
                        window.input('use')
                        return
            if event.key == game_constants.KEY_CANCEL:
                for window in GAME.windows:
                    if window.active:
                        window.input('cancel')
                        return
            if event.key == game_constants.KEY_LOG:
                GAME.draw_log = True
                if GAME.long_log:
                    GAME.long_log = False
                else:
                    GAME.long_log = True
def menu_input():
    global STATE
    global GAME
    events = pygame.event.get();
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if STATE == 0:
            if event.type == pygame.KEYDOWN:
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
                        GAME.player = game_content.p_normal(25, 30)
                        GAME.creatures.append(GAME.player)

                        # FOR TESTING PURPOSES:
                        GAME.creatures += [game_content.m_slime(23, 26) for i in range(5)]
                        GAME.player.inventory += [game_content.i_magichelmet(0, 0)]

                        generateMap()
                        GAME.light_map = map_light_init(GAME.map)
                        util.map_light_update(GAME.light_map)
                    return
                if event.key == game_constants.KEY_CANCEL:
                    MENU.option =  (MENU.option + 1) % 3
                    MENU.update = True
                    return

def generateMap():
    GAME.map = map_init_dungeon(game_constants.MAP_WIDTH[GAME.level], game_constants.MAP_HEIGHT[GAME.level])

# DRAW
def draw_game():
    GAME.surface_log.fill(game_constants.COLOR_COLORKEY)
    GAME.surface_effects.fill(game_constants.COLOR_COLORKEY)
    GAME.surface_log_bg.fill(game_constants.COLOR_COLORKEY)
    GAME.surface_status.fill(game_constants.COLOR_BLACK)
    if GAME.draw_log:
        if GAME.long_log:
            height = min(game_constants.LOG_MAX_LENGTH_LONG*18 + 8, len(GAME.log)*18 + 8)
        else:
            height = min(game_constants.LOG_MAX_LENGTH*18 + 8, len(GAME.log)*18 + 8)
        GAME.surface_log_bg.fill(game_constants.COLOR_DARKESTGRAY, pygame.Rect(0, game_constants.WINDOW_HEIGHT - height, game_constants.LOG_WIDTH, height))
    draw_map()
    draw_log()
    draw_status()
    SCREEN.blit(GAME.surface_map, (0, 0))
    SCREEN.blit(GAME.surface_effects, (0, 0))
    SCREEN.blit(GAME.surface_log_bg, (0, 0))
    SCREEN.blit(GAME.surface_log, (0, 0))
    SCREEN.blit(GAME.surface_status, (game_constants.LOG_WIDTH + 4, game_constants.CAMERA_HEIGHT*32))
    for effect in GAME.visualeffects:
        effect.execute()
        if util.isinscreen(effect.x, effect.y):
            effect.draw()
    for window in GAME.windows:
        if window.visible:
            window.draw()

    if GAME.draw_map:
        GAME.draw_map = False

    #DEBUG
    util.draw_text_bg(SCREEN, 'X: ' + str(GAME.player.x) + '   Y: ' + str(GAME.player.y), 10, 10, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK)
    util.draw_text_bg(SCREEN, 'FPS: ' + str(math.floor(CLOCK.get_fps())), 10, 28, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK)
    pygame.display.flip()
def draw_menu():
    SCREEN.blit(game_constants.SPRITE_TITLE.convert(), (0, 0))
    texts = [game_constants.FONT_PERFECTDOS_LARGE.render('Start game', False, game_constants.COLOR_WHITE),
            game_constants.FONT_PERFECTDOS_LARGE.render('Options', False, game_constants.COLOR_WHITE),
            game_constants.FONT_PERFECTDOS_LARGE.render('Exit', False, game_constants.COLOR_WHITE)]
    pygame.draw.rect(SCREEN, game_constants.COLOR_DARKRED, pygame.Rect(game_constants.WINDOW_WIDTH/2 - 128,  game_constants.WINDOW_HEIGHT*3/4 + MENU.option*32, 256, 32))
    for textIndex in range(len(texts)):
        SCREEN.blit(texts[textIndex], (game_constants.WINDOW_WIDTH/2 - texts[textIndex].get_width()/2, game_constants.WINDOW_HEIGHT*3/4 + textIndex*32))
    #DEBUG
    util.draw_text_bg(SCREEN, 'FPS: ' + str(math.floor(CLOCK.get_fps())), 10, 28, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK)
    pygame.display.flip()
#def draw_charselect():

def draw_map():
    if GAME.draw_map == True:
        GAME.surface_map.fill(game_constants.COLOR_BLACK)
        for x in range(0, game_constants.CAMERA_WIDTH):
            for y in range(0, game_constants.CAMERA_HEIGHT):
                if True:#libtcodpy.map_is_in_fov(GAME.light_map, GAME.camera.x + x, GAME.camera.y + y):
                    GAME.surface_map.blit(GAME.map[GAME.camera.x + x][GAME.camera.y + y].sprite, (x*32, y*32))
                    GAME.map[GAME.camera.x + x][GAME.camera.y + y].discovered = True
                elif GAME.map[GAME.camera.x + x][GAME.camera.y + y].discovered == True:
                    GAME.surface_map.blit(GAME.map[GAME.camera.x + x][GAME.camera.y + y].sprite_shadow, (x*32, y*32))
        pygame.draw.rect(GAME.surface_map, game_constants.COLOR_BORDER, pygame.Rect(game_constants.BORDER_THICKNESS, game_constants.BORDER_THICKNESS, game_constants.CAMERA_WIDTH*32-game_constants.BORDER_THICKNESS*2, game_constants.CAMERA_HEIGHT*32-game_constants.BORDER_THICKNESS*2), game_constants.BORDER_THICKNESS*2)
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
    if GAME.draw_log == True:
        if GAME.long_log:
            messages = game_constants.LOG_MAX_LENGTH_LONG
        else:
            messages = game_constants.LOG_MAX_LENGTH
        for x in range(0, min(messages, len(GAME.log))):
            util.draw_text_bg(GAME.surface_log, GAME.log[x][0], 10, game_constants.WINDOW_HEIGHT - x*18 - 20, game_constants.FONT_PERFECTDOS, GAME.log[x][1], game_constants.COLOR_DARKGRAY)
        GAME.draw_log == False
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
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_HUNGER, pygame.Rect(48, 56, 80*GAME.player.hunger/100, 13))

    GAME.surface_status.blit(game_content.SPRITESHEET_ICONS.image_at((32, 0, 16, 16), colorkey = game_constants.COLOR_COLORKEY), (138, 56)) #DRAW CARRY
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_DARKESTGRAY, pygame.Rect(168, 56, 80, 13))
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_YELLOW, pygame.Rect(168, 56, 80*GAME.player.currentWeight()/GAME.player.stats[10], 13))

    for textIndex in range(len(GAME.controlsText)): #DRAW CONTROLS
        xOffset = (textIndex // game_constants.LOG_MAX_LENGTH-1) *200
        util.draw_text(GAME.surface_status, GAME.controlsText[textIndex][0], 620 + xOffset, (textIndex%game_constants.LOG_MAX_LENGTH-1)*16+24, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
        util.draw_text(GAME.surface_status, GAME.controlsText[textIndex][1], 700 + xOffset, (textIndex%game_constants.LOG_MAX_LENGTH-1)*16+24, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)

# MAP
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


    alg_array = [[0 for j in range(height)] for i in range(width)]
    rooms = []
    room_exits = []
    room_connections = []
    rooms_size = [(10, 10)]

    available_spots = [(x, y) for x in range(width) for y in range(height) if x > 6 and x < width - 12 and y > 6 and y < height - 12]
    for x in range(len(available_spots)):
        append = True
        i, j = available_spots.pop(random.randint(0, len(available_spots)-1))
        for w, h in rooms_size:
            newRoom = (i, j, w, h) #X, Y, W, H
            for room in rooms:
                if util.rectangle_intersects(newRoom, room):
                    append = False
                    break
            if append == True:
                rooms.append(newRoom)
                break
    print(rooms)
    for roomIndex in range(len(rooms))[0:]:
        room = rooms[roomIndex]
        if room[2] == 10 and room[3] == 10:
            room_layout = random.choice(room_prefabs_10x10)
            for x in range(room[2]):
                for y in range(room[3]):
                    alg_array[x + room[0]][y + room[1]] = int(room_layout[x*10 + y])
                    if int(room_layout[x*10 + y]) == 7:
                        room_exits.append((x + room[0], y + room[1], roomIndex))
    for exit_init in room_exits:
        path = libtcodpy.path_new_using_function(width, height, path_cost, alg_array, 0)
        print(exit_init)
        other_exits = sorted([exit_other for exit_other in room_exits if exit_other[2] != exit_init[2] and (exit_other[2], exit_init[2]) not in room_connections], key = lambda e: util.simpledistance((exit_init[0], exit_init[1]), (e[0], e[1])))
        if len(other_exits) > 0:
            exit_end = other_exits[0]
        else:
            exit_end = sorted([exit_other for exit_other in room_exits if exit_other[2] != exit_init[2]], key = lambda e: util.simpledistance((exit_init[0], exit_init[1]), (e[0], e[1])))[0]
        room_connections.append((exit_init[2], exit_end[2]))
        room_connections.append((exit_end[2], exit_init[2]))
        libtcodpy.path_compute(path, exit_init[0], exit_init[1], exit_end[0], exit_end[1])
        for i in range(libtcodpy.path_size(path)):
            x, y = libtcodpy.path_get(path, i)
            alg_array[x][y] = 3

    for x in range(len(alg_array)):
        for y in range(len(alg_array[x])):
            if alg_array[x][y] == 0 or alg_array[x][y] == 1:
                alg_array[x][y] = game_content.t_cave_wall(x, y)
            else:
                alg_array[x][y] = game_content.t_cave_floor(x, y)
    return alg_array

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
