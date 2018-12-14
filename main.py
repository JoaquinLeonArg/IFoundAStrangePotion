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
    GAME.update_inputs()
    for gfx in GAME.gfx + GAME.gfx_active:
        gfx.update()
    if GAME.action != 'none':
        GAME.update_order()
        GAME.entities_execute()
        GAME.turn_counter += 1

@SCREEN.event
def on_key_press(symbol, _):
    if symbol == window.key.UP:
        GAME.input('up', True)
    elif symbol == window.key.DOWN:
        GAME.input('down', True)
    elif symbol == window.key.LEFT:
        GAME.input('left', True)
    elif symbol == window.key.RIGHT:
        GAME.input('right', True)
    elif symbol == game_constants.KEY_PASSTURN:
        GAME.input('pass', True)

    if symbol == window.key.ESCAPE:
        app.exit()

    if not GAME.gfx_active and not GAME.window:
            if symbol == game_constants.KEY_INVENTORY:
                GAME.window = game_content.WindowPlayerInventory()
            elif symbol == game_constants.KEY_SEARCH:
                if len([item for item in GAME.items if (item.x == GAME.player.x and item.y == GAME.player.y)]) > 0:
                    GAME.window = game_content.WindowSearchInventory()
                else:
                    GAME.addLogMessage('Nothing here.', game_constants.COLOR_GRAY)
            elif symbol == game_constants.KEY_STATUS:
                GAME.window= game_content.WindowStatus()
            elif symbol == game_constants.KEY_STATS:
                GAME.window = game_content.WindowStats()
            elif symbol == game_constants.KEY_EQUIPMENT:
                GAME.window = game_content.WindowEquipment()
            elif symbol == game_constants.KEY_SKILLTREE:
                GAME.window = game_content.WindowSkillTree()
            if symbol == game_constants.KEY_LOG:
                GAME.long_log = not GAME.long_log
            if symbol == game_constants.KEY_MINIMAP:
                GAME.show_minimap = (GAME.show_minimap + 1) % 3
@SCREEN.event
def on_key_release(symbol, _):
    if symbol == window.key.UP:
        GAME.input('up', False)
    elif symbol == window.key.DOWN:
        GAME.input('down', False)
    elif symbol == window.key.LEFT:
        GAME.input('left', False)
    elif symbol == window.key.RIGHT:
        GAME.input('right', False)
    elif symbol == game_constants.KEY_PASSTURN:
        GAME.input('pass', False)

# DRAW
def in_camera(x, y):
    return int(GAME.camera.x / 32) < x < int(GAME.camera.x / 32) + game_constants.CAMERA_WIDTH and int(GAME.camera.y / 32) < y < int(GAME.camera.y / 32) + game_constants.CAMERA_HEIGHT
def grid_to_camera(x, y):
    return x*32 - GAME.camera.x, game_constants.MAP_HEIGHT[0]*32 - y*32 - GAME.camera.y
def absolute_to_camera(x, y):
    return x - GAME.camera.x, game_constants.MAP_HEIGHT[0]*32 - y - GAME.camera.y

@SCREEN.event
def on_draw():
    SCREEN.clear()
    if not GAME.level:
        return

    # Process Tiles
    for i in range(int(GAME.camera.x / 32) - 2, int(GAME.camera.x / 32) + game_constants.CAMERA_WIDTH + 2):
        for j in range(int(game_constants.MAP_HEIGHT[0] - GAME.camera.y / 32) - int(game_constants.CAMERA_WIDTH/2) - 2, int(game_constants.MAP_HEIGHT[0] - GAME.camera.y / 32) + 4):
            try:
                if libtcodpy.map_is_in_fov(GAME.light_map, i, j) or GAME.debug:
                    GAME.map[i][j].sprite.position = grid_to_camera(GAME.map[i][j].x, GAME.map[i][j].y)
                    GAME.map[i][j].sprite.batch = GAME.btiles
                    GAME.map[i][j].sprite_shadow.batch = None
                    GAME.map[i][j].discovered = True
                elif GAME.map[i][j].discovered:
                    GAME.map[i][j].sprite_shadow.position = grid_to_camera(GAME.map[i][j].x, GAME.map[i][j].y)
                    GAME.map[i][j].sprite.batch = None
                    GAME.map[i][j].sprite_shadow.batch = GAME.btiles
                else:
                    GAME.map[i][j].sprite.batch = None
                    GAME.map[i][j].sprite_shadow.batch = None
            except:
                pass
    # Process Entities + Creatures
    for e in GAME.entities + GAME.creatures:
        if libtcodpy.map_is_in_fov(GAME.light_map, e.x, e.y) and e.visible:
            e.sprite.position = grid_to_camera(e.x, e.y)
            e.sprite.batch = GAME.bentities
        else:
            e.sprite.batch = None
    # Process VisualEffects
    for gfx in GAME.gfx + GAME.gfx_active:
            gfx.sprite.position = absolute_to_camera(gfx.x, gfx.y)
            gfx.sprite.batch = GAME.bgfx
    # Process StatusWindow
    GAME.update_status_window()


    # Draw everything
    GAME.btiles.draw()
    GAME.bentities.draw()
    GAME.bgfx.draw()
    GAME.sstatus.draw()
    game_util.draw_bar(int(GAME.ui_positions['status_x']) + 90,
                                    int(GAME.ui_positions['status_y']) + 64,
                                    78 * int(GAME.player.currentHitPoints/GAME.player.get_stat('HitPoints')), 14, game_constants.COLORS['health_bar'])
    game_util.draw_bar(int(GAME.ui_positions['status_x']) + 90,
                       int(GAME.ui_positions['status_y']) + 46,
                       78 * int(GAME.player.currentMagicPoints / GAME.player.get_stat('MagicPoints')), 14, game_constants.COLORS['magic_bar'])

    fps_display.draw()

    '''draw_log()
    draw_status()
    draw_windows()
    draw_minimap()'''
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


# EXECUTION

if __name__ == '__main__':
    GAME.start(game_content.p_normal(game_constants.MAP_WIDTH[0] // 2, game_constants.MAP_HEIGHT[0] // 2), game_mapping.mapgen_dungeon)
    clock.schedule_interval(game_loop, 1 / 60.0)
    app.run()
