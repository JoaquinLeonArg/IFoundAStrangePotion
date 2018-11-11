# IMPORT
import pygame
import libtcodpy
import random
import math
import game_util
import game_constants
import game_mapping
import game_effects
import sys

# GAME
def game_init():
    global STATE, MENU, GAME, TILES, SCREEN, GAMEWINDOW, CLOCK, game_classes, game_content
    pygame.init()
    GAMEWINDOW = pygame.display.set_mode((game_constants.GAME_RESOLUTION_WIDTH, game_constants.GAME_RESOLUTION_HEIGHT), 0, 16)

    import game_classes
    import game_content

    GAME = game_classes.Game()
    MENU = game_classes.MainMenu()
    CLOCK = pygame.time.Clock()
    SCREEN = pygame.Surface((game_constants.WINDOW_WIDTH, game_constants.WINDOW_HEIGHT))
    STATE = 0

    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])

    pygame.display.set_caption('I found a strange potion')

    game_classes.GAME = GAME
    game_classes.SCREEN = SCREEN
    game_content.GAME = GAME
    game_content.SCREEN = SCREEN
    game_util.GAME = GAME
    game_util.SCREEN = SCREEN
    game_mapping.SCREEN = SCREEN
    game_effects.GAME = GAME

def game_loop():
    while True:
        if STATE == 0:
            draw_menu()
            menu_input()
        elif STATE == 9:
            GAME.action = 'none'
            if GAME.movetimer > 0:
                GAME.movetimer -= 1
            GAME.camera.update(GAME.player.x * 32, GAME.player.y * 32)
            game_input()
            for entity in GAME.entities + GAME.items + GAME.creatures + GAME.player.inventory:
                entity.update_frame()
            if GAME.action != 'none':
                GAME.updateOrder()
                GAME.entitiesExecuteTurn()
                GAME.turn_counter += 1
            draw_game()
        CLOCK.tick(60)
def game_input():
    events = pygame.event.get()
    keystates = pygame.key.get_pressed()

    if not GAME.visualactiveeffects and GAME.movetimer is 0 and GAME.player.active:
        if keystates[pygame.K_UP]:
            GAME.player.input('up')
        elif keystates[pygame.K_DOWN]:
            GAME.player.input('down')
        elif keystates[pygame.K_LEFT]:
            GAME.player.input('left')
        elif keystates[pygame.K_RIGHT]:
            GAME.player.input('right')
        elif keystates[game_constants.KEY_PASSTURN]:
            GAME.player.input('pass')

        if keystates[game_constants.KEY_MAPUP]:
            GAME.camera.update(GAME.camera.x + game_constants.CAMERA_WIDTH*16, GAME.camera.y + game_constants.CAMERA_HEIGHT*16 - 128)
        elif keystates[game_constants.KEY_MAPDOWN]:
            GAME.camera.update(GAME.camera.x + game_constants.CAMERA_WIDTH*16, GAME.camera.y + game_constants.CAMERA_HEIGHT*16 + 128)
        elif keystates[game_constants.KEY_MAPLEFT]:
            GAME.camera.update(GAME.camera.x + game_constants.CAMERA_WIDTH*16 - 128, GAME.camera.y + game_constants.CAMERA_HEIGHT*16)
        elif keystates[game_constants.KEY_MAPRIGHT]:
            GAME.camera.update(GAME.camera.x + game_constants.CAMERA_WIDTH*16 + 128, GAME.camera.y + game_constants.CAMERA_HEIGHT*16)

    for event in events:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and not GAME.visualactiveeffects:

                if event.key == game_constants.KEY_INVENTORY and not GAME.window:
                    GAME.window = game_content.Window_PlayerInventory()
                elif event.key == game_constants.KEY_SEARCH and not GAME.window:
                    if len([item for item in GAME.items if (item.x == GAME.player.x and item.y == GAME.player.y)]) > 0:
                        GAME.window = game_content.Window_SearchInventory()
                    else:
                        GAME.addLogMessage('Nothing here.', game_constants.COLOR_GRAY)
                elif event.key == game_constants.KEY_STATUS and not GAME.window:
                    GAME.window= game_content.Window_Status()
                elif event.key == game_constants.KEY_STATS and not GAME.window:
                    GAME.window = game_content.Window_Stats()
                elif event.key == game_constants.KEY_EQUIPMENT and not GAME.window:
                    GAME.window = game_content.Window_Equipment()
                elif event.key == game_constants.KEY_SKILLTREE and not GAME.window:
                    GAME.window = game_content.Window_SkillTree()

                if GAME.window:
                    if event.key == pygame.K_LEFT:
                        GAME.window.input('left')
                    elif event.key == pygame.K_RIGHT:
                        GAME.window.input('right')
                    elif event.key == pygame.K_UP:
                        GAME.window.input('up')
                    elif event.key == pygame.K_DOWN:
                        GAME.window.input('down')
                    elif event.key == game_constants.KEY_USE:
                        GAME.window.input('use')
                    elif event.key == game_constants.KEY_CANCEL:
                        GAME.window.input('cancel')

                if event.key == game_constants.KEY_LOG:
                    GAME.long_log = not GAME.long_log
                if event.key == game_constants.KEY_MINIMAP:
                    GAME.show_minimap = (GAME.show_minimap + 1) % 3
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
                        GAME.generateMap(game_mapping.mapgen_dungeon)
                        GAME.creatures.append(GAME.player)
                    return
                if event.key == game_constants.KEY_CANCEL:
                    MENU.option =  (MENU.option + 1) % 3
                    MENU.update = True
                    return

# DRAW
def draw_game():
    draw_log()
    draw_status()
    draw_map()
    draw_entities()
    draw_windows()

    # BLIT ALL SURFACES INTO THE MAIN SURFACE
    for surface in [GAME.surface_map, GAME.surface_entities, GAME.surface_windows]: # DRAW ALL SURFACES AT (0, 8)
        SCREEN.blit(surface, (0, 8))
    draw_effects() # THEY ARE DRAWN EVERY FRAME BECAUSE THEY ARE ANIMATED
    SCREEN.blit(GAME.surface_log, (GAME.log_position_x, GAME.log_position_y))
    SCREEN.blit(GAME.surface_status, (GAME.status_position_x, GAME.status_position_y)) # SURFACE_STATUS NEEDS TO BE DRAWN IN A DIFFERENT POSITION

    draw_minimap()

    # FOR DEBUG PURPOSES
    #GAME.update_rects.append(game_util.draw_text_bg(SCREEN, 'X: ' + str(GAME.player.x) + '   Y: ' + str(GAME.player.y), 10, 30, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK))
    GAME.update_rects.append(game_util.draw_text_bg(SCREEN, 'FPS: ' + str(math.floor(CLOCK.get_fps())), 10, 48, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK))
    #GAME.update_rects.append(game_util.draw_text_bg(SCREEN, 'TURN: ' + str(GAME.turn_counter), 10, 66, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK))

    SCREEN.fill((0, 0, 0), (0, 0, game_constants.CAMERA_WIDTH * 32, 8))
    SCREEN.fill((0, 0, 0), (0, game_constants.CAMERA_HEIGHT * 32 + 8, game_constants.CAMERA_WIDTH * 32, 8))

    pygame.display.flip()
    pygame.transform.scale(SCREEN, (game_constants.GAME_RESOLUTION_WIDTH, game_constants.GAME_RESOLUTION_HEIGHT), GAMEWINDOW)

def draw_map():
    GAME.update_rects.append(GAME.surface_map.fill(game_constants.COLOR_BLACK))
    for x in range(math.floor(GAME.camera.x/32), math.ceil(GAME.camera.x/32) + game_constants.CAMERA_WIDTH):
        for y in range(math.floor(GAME.camera.y/32), math.ceil(GAME.camera.y/32) + game_constants.CAMERA_HEIGHT):
            if libtcodpy.map_is_in_fov(GAME.light_map, x, y):
                GAME.surface_map.blit(GAME.map[x][y].sprite, (x*32 - GAME.camera.x, y*32 - GAME.camera.y))
                GAME.map[x][y].discovered = True
            elif GAME.map[x][y].discovered:
                GAME.surface_map.blit(GAME.map[x][y].sprite_shadow, (x*32 - GAME.camera.x, y*32 - GAME.camera.y))
    pygame.draw.rect(GAME.surface_map, game_constants.COLOR_BORDER, pygame.Rect(game_constants.BORDER_THICKNESS, game_constants.BORDER_THICKNESS, game_constants.CAMERA_WIDTH*32-game_constants.BORDER_THICKNESS*2, game_constants.CAMERA_HEIGHT*32-game_constants.BORDER_THICKNESS*2), game_constants.BORDER_THICKNESS*2)
def draw_minimap():
    if GAME.window:
        return
    minimap_ratio = (GAME.show_minimap + 1)*2
    minimap_x = 10
    minimap_y = game_constants.CAMERA_HEIGHT*32-len(GAME.map[0])*minimap_ratio-100
    minimap_width = len(GAME.map)*minimap_ratio
    minimap_height = len(GAME.map[0])*minimap_ratio
    if GAME.show_minimap != 2:
        pygame.draw.rect(SCREEN, game_constants.COLOR_DARKGRAY, pygame.Rect(minimap_x, minimap_y, minimap_width, minimap_height))
        for x in range(len(GAME.map)):
            for y in range(len(GAME.map[x])):
                if GAME.map[x][y].discovered:
                    if GAME.map[x][y].passable:
                        pygame.draw.rect(SCREEN, game_constants.COLOR_GRAY, pygame.Rect(minimap_x+x*minimap_ratio, minimap_y+y*minimap_ratio, minimap_ratio, minimap_ratio))
                    else:
                        pygame.draw.rect(SCREEN, game_constants.COLOR_WHITE, pygame.Rect(minimap_x+x*minimap_ratio, minimap_y+y*minimap_ratio, minimap_ratio, minimap_ratio))
        pygame.draw.rect(SCREEN, game_constants.COLOR_YELLOW, pygame.Rect(minimap_x+GAME.player.x*minimap_ratio, minimap_y+GAME.player.y*minimap_ratio, minimap_ratio, minimap_ratio))
def draw_entities():
    GAME.update_rects.append(GAME.surface_entities.fill(game_constants.COLOR_COLORKEY))
    for i in GAME.creatures + GAME.entities + GAME.items:
        if libtcodpy.map_is_in_fov(GAME.light_map, i.x, i.y):
            i.draw()
        else:
            i.draw_last_seen()
def draw_log():
    if GAME.player.y < 7:
        GAME.log_position_y += min((game_constants.LOG_HIDDEN_Y - GAME.log_position_y)*0.1, 1)
    else:
        GAME.log_position_y += min((game_constants.LOG_IDLE_Y - GAME.log_position_y)*0.1, 1)
    GAME.surface_log.blit(game_constants.SPRITE_LOG, (0, 0))
    for x in range(0, min(game_constants.LOG_MAX_LENGTH, len(GAME.log))):
        game_util.draw_text(GAME.surface_log, GAME.log[x][0], 10, x*14 + 10, game_constants.FONT_PERFECTDOS_SMALL, GAME.log[x][1])
def draw_status():
    GAME.surface_status.fill(game_constants.COLOR_COLORKEY)
    GAME.updatePopupTime()
    if abs(GAME.popup_target_y - GAME.popup_position_y) < 1:
        GAME.popup_position_y = GAME.popup_target_y
    GAME.popup_position_y += (GAME.popup_target_y - GAME.popup_position_y)*0.1
    if GAME.player.y > len(GAME.map) - 7:
        GAME.status_position_y += min((game_constants.STATUS_HIDDEN_Y - GAME.status_position_y)*0.1, game_constants.WINDOW_HEIGHT*32 - 1)
    else:
        GAME.status_position_y += min((game_constants.STATUS_IDLE_Y - GAME.status_position_y)*0.1, game_constants.WINDOW_HEIGHT*32 - 1)
    if GAME.popup_position_y != 0:
        GAME.surface_status.blit(game_constants.SPRITE_POPUP, (GAME.popup_position_x, 128 - GAME.popup_position_y))
    for index, line in enumerate(GAME.popup_lines):
        game_util.draw_text(GAME.surface_status, line, GAME.popup_position_x + 24, 128 - GAME.popup_position_y + 12*index + 8,game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
    GAME.surface_status.blit(game_constants.SPRITE_STATUS, (0, 128))
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_HP, (91, 8 + 128, 77*(GAME.player.currentHitPoints // GAME.player.getMaxHitPoints()), 13))
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_YELLOW, (91, 8 + 128 + 18, 77 * (GAME.player.currentMagicPoints // GAME.player.getMaxMagicPoints()), 13))
    #pygame.draw.rect(GAME.surface_status, game_constants.COLOR_BROWN, (91, 8 + 128 + 18*2, 77 * (GAME.player.getCurrentCarry() // GAME.player.getMaxCarry()), 13)) # TODO: Fix this
def draw_effects():
    for effect in (GAME.visualeffects + GAME.visualactiveeffects): # UPDATE ALL VISUAL EFFECTS AND DRAW THEM
        effect.update()
        effect.draw()
def draw_windows():
    GAME.surface_windows.fill(game_constants.COLOR_COLORKEY)
    if GAME.window:
        GAME.window.draw()

def draw_menu():
    sin = math.sin(MENU.timer)
    MENU.timer += 0.1
    if STATE == 0:
        if MENU.rd_img:
            MENU.update_rects.append(MENU.surface_logo.blit(game_constants.SPRITE_TITLE, (0, 0)))
            MENU.rd_img = False
        if MENU.rd_opt:
            MENU.update_rects.append(MENU.surface_options.fill(game_constants.COLOR_COLORKEY))
            pygame.draw.rect(MENU.surface_options, game_constants.COLOR_DARKRED, pygame.Rect(game_constants.WINDOW_WIDTH/2 - 128,  game_constants.WINDOW_HEIGHT*3/4 + MENU.option*32 - sin*2, 256, 32 + sin*4))
            for i, text in enumerate(MENU.optionsText):
                MENU.surface_options.blit(text, (game_constants.WINDOW_WIDTH/2 - text.get_width()/2, game_constants.WINDOW_HEIGHT*3/4 + i*32))

        for surface in [MENU.surface_logo, MENU.surface_options]: # DRAW ALL SURFACES AT (0, 0)
            SCREEN.blit(surface, (0, 0))


    # FOR DEBUG PURPOSES
    MENU.update_rects.append(game_util.draw_text_bg(SCREEN, 'FPS: ' + str(math.floor(CLOCK.get_fps())), 10, 28, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK))

    pygame.transform.scale(SCREEN, (game_constants.GAME_RESOLUTION_WIDTH, game_constants.GAME_RESOLUTION_HEIGHT), GAMEWINDOW)

    pygame.display.update(MENU.update_rects)
    MENU.update_rects = []
#def draw_charselect():

# MAPsss
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


# EXECUTION
if __name__ == '__main__':
    pygame.init()
    game_init()
    game_loop()
