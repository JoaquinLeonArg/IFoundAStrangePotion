# IMPORT
from pyglet import *
import libtcodpy
import math
import game_util
import game_constants
import game_mapping
import game_effects
import game_classes
import game_content
import sys

# GAME
global STATE, MENU, GAME, TILES, SCREEN, GAMEWINDOW, CLOCK, game_classes, game_content
SCREEN = window.Window(game_constants.WINDOW_WIDTH, game_constants.WINDOW_HEIGHT)

fps_display = window.FPSDisplay(SCREEN)

GAME = game_classes.Game()
game_classes.GAME = GAME
game_classes.SCREEN = SCREEN
game_content.GAME = GAME
game_content.SCREEN = SCREEN
game_util.GAME = GAME
game_util.SCREEN = SCREEN
game_mapping.SCREEN = SCREEN
game_effects.GAME = GAME

def game_loop(dt):
    fps_display.update()
    GAME.action = 'none'
    if GAME.movetimer > 0:
        GAME.movetimer -= 1
    GAME.camera.update(GAME.player.x * 32, GAME.player.y * 32)
    for entity in GAME.entities + GAME.items + GAME.creatures + GAME.player.inventory:
        entity.update_frame()
    for gfx in GAME.gfx + GAME.gfx_active:
        gfx.update()
    if GAME.action != 'none':
        GAME.updateOrder()
        GAME.entitiesExecuteTurn()
        GAME.turn_counter += 1

@SCREEN.event
def on_key_press(symbol, _):
    if not GAME.gfx_active and not GAME.movetimer and GAME.player.active:
        if symbol == window.key.UP:
            GAME.player.input('up')
        elif symbol == window.key.DOWN:
            GAME.player.input('down')
        elif symbol == window.key.LEFT:
            GAME.player.input('left')
        elif symbol == window.key.RIGHT:
            GAME.player.input('right')
        elif symbol == game_constants.KEY_PASSTURN:
            GAME.player.input('pass')

        if symbol == game_constants.KEY_MAPUP:
            GAME.camera.update(GAME.camera.x + game_constants.CAMERA_WIDTH*16, GAME.camera.y + game_constants.CAMERA_HEIGHT*16 - 128)
        elif symbol == game_constants.KEY_MAPDOWN:
            GAME.camera.update(GAME.camera.x + game_constants.CAMERA_WIDTH*16, GAME.camera.y + game_constants.CAMERA_HEIGHT*16 + 128)
        elif symbol == game_constants.KEY_MAPLEFT:
            GAME.camera.update(GAME.camera.x + game_constants.CAMERA_WIDTH*16 - 128, GAME.camera.y + game_constants.CAMERA_HEIGHT*16)
        elif symbol == game_constants.KEY_MAPRIGHT:
            GAME.camera.update(GAME.camera.x + game_constants.CAMERA_WIDTH*16 + 128, GAME.camera.y + game_constants.CAMERA_HEIGHT*16)

    if symbol == window.key.ESCAPE:
        app.exit()

        if not GAME.visualactiveeffects:
                if symbol == game_constants.KEY_INVENTORY and not GAME.window:
                    GAME.window = game_content.WindowPlayerInventory()
                elif symbol == game_constants.KEY_SEARCH and not GAME.window:
                    if len([item for item in GAME.items if (item.x == GAME.player.x and item.y == GAME.player.y)]) > 0:
                        GAME.window = game_content.WindowSearchInventory()
                    else:
                        GAME.addLogMessage('Nothing here.', game_constants.COLOR_GRAY)
                elif symbol == game_constants.KEY_STATUS and not GAME.window:
                    GAME.window= game_content.WindowStatus()
                elif symbol == game_constants.KEY_STATS and not GAME.window:
                    GAME.window = game_content.WindowStats()
                elif symbol == game_constants.KEY_EQUIPMENT and not GAME.window:
                    GAME.window = game_content.WindowEquipment()
                elif symbol == game_constants.KEY_SKILLTREE and not GAME.window:
                    GAME.window = game_content.WindowSkillTree()

                if GAME.window:
                    if symbol == window.key.LEFT:
                        GAME.window.input('left')
                    elif symbol == window.key.RIGHT:
                        GAME.window.input('right')
                    elif symbol == window.key.UP:
                        GAME.window.input('up')
                    elif symbol == window.key.DOWN:
                        GAME.window.input('down')
                    elif symbol == game_constants.KEY_USE:
                        GAME.window.input('use')
                    elif symbol == game_constants.KEY_CANCEL:
                        GAME.window.input('cancel')

                if symbol == game_constants.KEY_LOG:
                    GAME.long_log = not GAME.long_log
                if symbol == game_constants.KEY_MINIMAP:
                    GAME.show_minimap = (GAME.show_minimap + 1) % 3

# DRAW
def in_camera(x, y):
    return (GAME.camera.x // 32) < x < (GAME.camera.x // 32) + game_constants.CAMERA_WIDTH and (GAME.camera.y // 32) < y < (GAME.camera.y // 32) + game_constants.CAMERA_HEIGHT
def grid_to_camera(x, y):
    return x*32 - GAME.camera.x, game_constants.MAP_HEIGHT[GAME.level]*32 - y*32 - GAME.camera.y
def absolute_to_camera(x, y):
    return x - GAME.camera.x, game_constants.MAP_HEIGHT[GAME.level] * 32 - y - GAME.camera.y

@SCREEN.event
def on_draw():
    SCREEN.clear()
    if not GAME.level:
        return

    # Draw Tiles
    for i in range(len(GAME.map)):
        for j in range(len(GAME.map[0])):
            if libtcodpy.map_is_in_fov(GAME.light_map, i, j):
                GAME.map[i][j].sprite.position = grid_to_camera(GAME.map[i][j].x, GAME.map[i][j].y)
                GAME.map[i][j].sprite.batch = GAME.btiles
            else:
                GAME.map[i][j].sprite.batch = None
    # Draw Entities + Creatures
    for e in GAME.entities + GAME.creatures:
        if libtcodpy.map_is_in_fov(GAME.light_map, e.x, e.y) and e.visible:
            e.sprite.position = grid_to_camera(e.x, e.y)
            e.sprite.batch = GAME.bentities
        else:
            e.sprite.batch = None

    # Draw
    GAME.btiles.draw()
    GAME.bentities.draw()
    for gfx in GAME.gfx + GAME.gfx_active:
        gfx.sprite.position = absolute_to_camera(gfx.x, gfx.y)
        gfx.sprite.draw()
    fps_display.draw()

    '''draw_log()
    draw_status()
    draw_map()
    draw_entities()
    draw_windows()
    draw_effects()
    draw_minimap()'''

def draw_map():
    GAME.update_rects.append(GAME.surface_map.fill(game_constants.COLOR_BLACK))
    for x in range(math.floor(GAME.camera.x/32), math.ceil(GAME.camera.x/32) + game_constants.CAMERA_WIDTH):
        for y in range(math.floor(GAME.camera.y/32), math.ceil(GAME.camera.y/32) + game_constants.CAMERA_HEIGHT):
            if libtcodpy.map_is_in_fov(GAME.light_map, x, y) or GAME.debug:
                GAME.surface_map.blit(GAME.map[x][y].sprite, (x*32 - GAME.camera.x, y*32 - GAME.camera.y))
                GAME.map[x][y].discovered = True
            elif GAME.map[x][y].discovered:
                GAME.surface_map.blit(GAME.map[x][y].sprite_shadow, (x*32 - GAME.camera.x, y*32 - GAME.camera.y))
def draw_minimap():
    if not GAME.window:
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
                            pygame.draw.rect(SCREEN, game_constants.COLOR_GRAY, pygame.Rect(minimap_x+1, minimap_y+1, 1, 1))
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
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_HP, (91, 8 + 128, 77*(GAME.player.currentHitPoints // GAME.player.getStat('HitPoints')), 13))
    pygame.draw.rect(GAME.surface_status, game_constants.COLOR_YELLOW, (91, 8 + 128 + 18, 77 * (GAME.player.currentMagicPoints // GAME.player.getStat('MagicPoints')), 13))
    #pygame.draw.rect(GAME.surface_status, game_constants.COLOR_BROWN, (91, 8 + 128 + 18*2, 77 * (GAME.player.getCurrentCarry() // GAME.player.getStat('MaxCarry)), 13)) # TODO: Fix this
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

    pygame.display.flip()

    #pygame.display.update(MENU.update_rects)
    #MENU.update_rects = []
#def draw_charselect():



# EXECUTION

if __name__ == '__main__':
    GAME.start(game_content.p_normal(game_constants.MAP_WIDTH[0] // 2, game_constants.MAP_HEIGHT[0] // 2), game_mapping.mapgen_woods)
    clock.schedule_interval(game_loop, 1 / 120.0)
    app.run()
