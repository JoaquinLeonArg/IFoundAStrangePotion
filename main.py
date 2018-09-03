# IMPORT
import pygame
import libtcodpy
import random
import math
import game_util
import game_constants
import sys

# GAME
def game_init():
    global STATE, MENU, GAME, TILES, SCREEN, GAMEWINDOW, CLOCK, game_classes, game_content
    pygame.init()
    GAMEWINDOW = pygame.display.set_mode((game_constants.GAME_RESOLUTION_WIDTH, game_constants.GAME_RESOLUTION_HEIGHT), 0, 16)
    SCREEN = pygame.Surface((game_constants.WINDOW_WIDTH, game_constants.WINDOW_HEIGHT))

    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])

    import game_classes
    import game_content

    STATE = 0

    pygame.display.set_caption('I found a strange potion')

    MENU = game_classes.MainMenu()
    GAME = game_classes.Game()
    CLOCK = pygame.time.Clock()

    game_classes.GAME = GAME
    game_classes.SCREEN = SCREEN
    game_content.GAME = GAME
    game_content.SCREEN = SCREEN
    game_util.GAME = GAME
    game_util.SCREEN = SCREEN
def game_loop():
    while True:
        if STATE == 0:
            draw_menu()
            menu_input()
        elif STATE == 9:
            GAME.action = 'none'
            if GAME.movetimer > 0:
                GAME.movetimer -= 1
            game_input()
            GAME.descriptionWindow.update()
            for entity in GAME.entities + GAME.items + GAME.creatures + GAME.player.inventory:
                entity.update_frame()
            if GAME.action != 'none':
                GAME.updateOrder()
                GAME.creaturesExecuteTurn()
                GAME.entitiesExecuteTurn()
                GAME.turn_counter += 1
            GAME.camera.update(GAME.player.x*32, GAME.player.y*32)
            draw_game()
        CLOCK.tick()
def game_input():
    events = pygame.event.get();
    keystates = pygame.key.get_pressed()

    if len(GAME.visualactiveeffects) == 0 and GAME.movetimer == 0:
        if GAME.player.active and keystates[pygame.K_UP]:
            GAME.player.input('up')
            GAME.rd_sta = True
            return
        elif GAME.player.active and keystates[pygame.K_DOWN]:
            GAME.player.input('down')
            GAME.rd_sta = True
            return
        elif GAME.player.active and keystates[pygame.K_LEFT]:
            GAME.player.input('left')
            GAME.rd_sta = True
            return
        elif GAME.player.active and keystates[pygame.K_RIGHT]:
            GAME.player.input('right')
            GAME.rd_sta = True
            return

    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif len(GAME.visualactiveeffects) == 0:
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
                if event.key == game_constants.KEY_SKILLTREE:
                    if GAME.windows == []:
                        GAME.windows.append(game_content.Window_SkillTree())
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
                        GAME.generateMap(game_content.map_init_dungeon)
                        GAME.creatures.append(GAME.player)
                    return
                if event.key == game_constants.KEY_CANCEL:
                    MENU.option =  (MENU.option + 1) % 3
                    MENU.update = True
                    return

# DRAW
def draw_game():
    #SCREEN.fill([255,255,255])

    if GAME.rd_log: # CHECK IF SURFACE_LOG NEEDS TO BE REDRAWN
        draw_log()
        GAME.rd_log = False
    if GAME.rd_sta: # CHECK IF SURFACE_STATUS NEEDS TO BE REDRAWN
        draw_status()
        GAME.rd_sta = False
    draw_map()
    draw_entities() # SAME AS EFFECTS

    # BLIT ALL SURFACES INTO THE MAIN SURFACE
    # , GAME.surface_effects
    for surface in [GAME.surface_map, GAME.surface_entities, GAME.surface_windows]: # DRAW ALL SURFACES AT (0, 0)
        SCREEN.blit(surface, (0, 0))
    draw_effects() # THEY ARE DRAWN EVERY FRAME BECAUSE THEY ARE ANIMATED
    GAME.update_rects.append(SCREEN.blit(GAME.surface_log, (0, game_constants.CAMERA_HEIGHT*32)))
    GAME.update_rects.append(SCREEN.blit(GAME.surface_status, (game_constants.LOG_WIDTH + 4, game_constants.CAMERA_HEIGHT*32))) # SURFACE_STATUS NEEDS TO BE DRAWN IN A DIFFERENT POSITION

    if GAME.rd_win: # CHECK IF SURFACE_WINDOWS NEEDS TO BE REDRAWN
        GAME.rd_win = False
        draw_windows()
        if GAME.draw_descriptionwindow:
            GAME.descriptionWindow.draw()

    # FOR DEBUG PURPOSES
    GAME.update_rects.append(game_util.draw_text_bg(SCREEN, 'X: ' + str(GAME.player.x) + '   Y: ' + str(GAME.player.y), 10, 10, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK))
    GAME.update_rects.append(game_util.draw_text_bg(SCREEN, 'FPS: ' + str(math.floor(CLOCK.get_fps())), 10, 28, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK))
    GAME.update_rects.append(game_util.draw_text_bg(SCREEN, 'TURN: ' + str(GAME.turn_counter), 10, 46, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK))

    pygame.display.flip() # FOR RESOLUTION CHANGE SIMPLICITY. TEST PERFORMANCE EFFECTS AND SEE WHAT'S BETTER.
    #pygame.display.update(GAME.update_rects) # DRAW ALL THE SECTIONS ON THE SCREEN THAT UPDATED ON THIS CYCLE
    pygame.transform.scale(SCREEN, (game_constants.GAME_RESOLUTION_WIDTH, game_constants.GAME_RESOLUTION_HEIGHT), GAMEWINDOW)
    GAME.update_rects = [] # CLEAR THE LIST OF SECTIONS TO REDRAW

def draw_map():
    GAME.update_rects.append(GAME.surface_map.fill(game_constants.COLOR_BLACK))
    for x in range(math.floor(GAME.camera.x/32), math.ceil(GAME.camera.x/32) + game_constants.CAMERA_WIDTH):
        for y in range(math.floor(GAME.camera.y/32), math.ceil(GAME.camera.y/32) + game_constants.CAMERA_HEIGHT):
            if libtcodpy.map_is_in_fov(GAME.light_map, x, y):
                GAME.surface_map.blit(GAME.map[x][y].sprite, (x*32 - GAME.camera.x, y*32 - GAME.camera.y))
                GAME.map[x][y].discovered = True
            elif GAME.map[x][y].discovered == True:
                GAME.surface_map.blit(GAME.map[x][y].sprite_shadow, (x*32 - GAME.camera.x, y*32 - GAME.camera.y))
    pygame.draw.rect(GAME.surface_map, game_constants.COLOR_BORDER, pygame.Rect(game_constants.BORDER_THICKNESS, game_constants.BORDER_THICKNESS, game_constants.CAMERA_WIDTH*32-game_constants.BORDER_THICKNESS*2, game_constants.CAMERA_HEIGHT*32-game_constants.BORDER_THICKNESS*2), game_constants.BORDER_THICKNESS*2)
def draw_entities():
    GAME.update_rects.append(GAME.surface_entities.fill(game_constants.COLOR_COLORKEY))
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
        game_util.draw_text_bg(GAME.surface_log, GAME.log[x][0], 10, x*14 + 4, game_constants.FONT_PERFECTDOS_SMALL, GAME.log[x][1], game_constants.COLOR_DARKGRAY)
def draw_status():
    GAME.surface_status.blit(game_constants.SPRITE_STATUS, (0, 0))

    GAME.surface_status.blit(GAME.player.portrait_list[0], (38, 22))

    GAME.surface_status.blit(game_content.SPRITESHEET_ICONS.image_at((0, 0, 16, 16), colorkey = game_constants.COLOR_COLORKEY), (216, 16)) #DRAW HP
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_DARKESTGRAY, pygame.Rect(248, 16, 200, 13))
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_HP, pygame.Rect(248, 16, 200*GAME.player.currentHitPoints/GAME.player.getMaxHitPoints(), 13))
    text = game_constants.FONT_PERFECTDOS.render(str(GAME.player.currentHitPoints), False, game_constants.COLOR_WHITE)
    GAME.surface_status.blit(text, (462, 16))
    text = game_constants.FONT_PERFECTDOS.render(str(GAME.player.getMaxHitPoints()), False, game_constants.COLOR_WHITE)
    GAME.surface_status.blit(text, (546 - text.get_width(), 16))

    GAME.surface_status.blit(game_content.SPRITESHEET_ICONS.image_at((0, 16, 16, 16), colorkey = game_constants.COLOR_COLORKEY), (216, 40)) #DRAW MANA
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_DARKESTGRAY, pygame.Rect(248, 40, 200, 13))
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_CYAN, pygame.Rect(248, 40, 200*GAME.player.currentMagicPoints/GAME.player.getMaxMagicPoints(), 13))
    text = game_constants.FONT_PERFECTDOS.render(str(GAME.player.currentMagicPoints), False, game_constants.COLOR_WHITE)
    GAME.surface_status.blit(text, (462, 40))
    text = game_constants.FONT_PERFECTDOS.render(str(GAME.player.getMaxMagicPoints()), False, game_constants.COLOR_WHITE)
    GAME.surface_status.blit(text, (546 - text.get_width(), 40))

    GAME.surface_status.blit(game_content.SPRITESHEET_ICONS.image_at((16, 0, 16, 16), colorkey = game_constants.COLOR_COLORKEY), (216, 64)) #DRAW FOOD
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_DARKESTGRAY, pygame.Rect(248, 64, 80, 13))
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_HUNGER, pygame.Rect(248, 64, 80*GAME.player.currentHunger/game_constants.MAX_HUNGER, 13))

    GAME.surface_status.blit(game_content.SPRITESHEET_ICONS.image_at((32, 0, 16, 16), colorkey = game_constants.COLOR_COLORKEY), (338, 64)) #DRAW CARRY
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_DARKESTGRAY, pygame.Rect(368, 64, 80, 13))
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_YELLOW, pygame.Rect(368, 64, 80*GAME.player.getCurrentCarry()/GAME.player.getMaxCarry(), 13))

    # for textIndex in range(len(GAME.controlsText)): #DRAW CONTROLS
    #     xOffset = (textIndex // 3) *200
    #     game_util.draw_text(GAME.surface_status, GAME.controlsText[textIndex][0], 500 + xOffset, (textIndex%3)*16+4, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
    #     game_util.draw_text(GAME.surface_status, GAME.controlsText[textIndex][1], 550 + xOffset, (textIndex%3)*16+4, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE)
def draw_effects():
    for effect in (GAME.visualeffects + GAME.visualactiveeffects): # UPDATE ALL VISUAL EFFECTS AND DRAW THEM
        GAME.update_rects.append((effect.x - GAME.camera.x, effect.y - GAME.camera.y, effect.width, effect.height))
        effect.execute()
        if game_util.isinscreen(effect.x, effect.y) and effect.visible:
            GAME.update_rects.append(SCREEN.blit(effect.surface, (effect.x - GAME.camera.x, effect.y - GAME.camera.y)))
def draw_windows():
    GAME.update_rects.append(GAME.surface_windows.fill(game_constants.COLOR_COLORKEY))
    for window in GAME.windows: # DRAW ALL VISIBLE IN-GAME WINDOWS
        if window.visible:
            window.draw()

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
            for textIndex in range(len(MENU.optionsText)):
                MENU.surface_options.blit(MENU.optionsText[textIndex], (game_constants.WINDOW_WIDTH/2 - MENU.optionsText[textIndex].get_width()/2, game_constants.WINDOW_HEIGHT*3/4 + textIndex*32))

        for surface in [MENU.surface_logo, MENU.surface_options]: # DRAW ALL SURFACES AT (0, 0)
            SCREEN.blit(surface, (0, 0))


    # FOR DEBUG PURPOSES
    MENU.update_rects.append(game_util.draw_text_bg(SCREEN, 'FPS: ' + str(math.floor(CLOCK.get_fps())), 10, 28, game_constants.FONT_PERFECTDOS, game_constants.COLOR_WHITE, game_constants.COLOR_BLACK))

    pygame.transform.scale(SCREEN, (game_constants.GAME_RESOLUTION_WIDTH, game_constants.GAME_RESOLUTION_HEIGHT), GAMEWINDOW)

    pygame.display.update(MENU.update_rects)
    MENU.update_rects = []
#def draw_charselect():

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


# EXECUTION
if __name__ == '__main__':
    game_init()
    game_loop()
