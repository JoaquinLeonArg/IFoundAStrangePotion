import pygame
import game_constants
import game_util
import libtcodpy
from game_util import Singleton
from game_mapping import mapgen_dungeon
from sys import exit

pygame.init()


class MainMenu:
    def __init__(self):
        self.timer = 0

        self.option = 0
        self.characterNumber = 0

        self.surface_logo = pygame.Surface((game_constants.WINDOW_WIDTH, game_constants.WINDOW_HEIGHT))
        self.surface_options = pygame.Surface((game_constants.WINDOW_WIDTH, game_constants.WINDOW_HEIGHT))

        self.surface_options.set_colorkey(game_constants.COLOR_COLORKEY)

        self.optionsText = [game_constants.FONT_PERFECTDOS_LARGE.render('Start game', False, game_constants.COLOR_WHITE),
                        game_constants.FONT_PERFECTDOS_LARGE.render('Options', False, game_constants.COLOR_WHITE),
                        game_constants.FONT_PERFECTDOS_LARGE.render('Exit', False, game_constants.COLOR_WHITE)]

        self.rd_img = True
        self.rd_opt = True
        self.update_rects = []

class AbstractApplicationManager(metaclass = Singleton):
    def update(self):
        pass
    def draw(self):
        pass
    def lateUpdate(self):
        pass

class GameManager(AbstractApplicationManager):
    def __init__(self):
        self.gameStatus = GameStatus()
        self.gameCamera = GameCamera()
        self.action = None
    def update(self):
        self.gameStatus.update()
        self.updateCamera()
        self.action = None
        VisualEffectsManager.updateMoveTimer()
        self.input()
    def draw(self):
        self.gameStatus.draw()
    def lateUpdate(self):
        pass
    def updateCamera(self):
        self.gameCamera.update(self.gameStatus.player.x, self.gameStatus.player.y)
    def input(self):
        events = pygame.event.get()
        keystates = pygame.key.get_pressed()
        if not VisualEffectsManager().getActiveEffects() and VisualEffectsManager().moveTimer is 0 and GameStatus().player.active:
            if keystates[pygame.K_UP]:
                GameStatus().player.input('up')
            if keystates[pygame.K_DOWN]:
                GameStatus().player.input('down')
            if keystates[pygame.K_LEFT]:
                GameStatus().player.input('left')
            if keystates[pygame.K_RIGHT]:
                GameStatus().player.input('right')
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN and not GAME.visualactiveeffects:

                if event.key == game_constants.KEY_INVENTORY and not GAME.windows:
                    GAME.windows.append(game_content.Window_PlayerInventory())
                if event.key == game_constants.KEY_SEARCH and not GAME.windows:
                    if len([item for item in GAME.items if (item.x == GAME.player.x and item.y == GAME.player.y)]) > 0:
                        GAME.windows.append(game_content.Window_SearchInventory())
                    else:
                        GAME.addLogMessage('Nothing here.', game_constants.COLOR_GRAY)
                if event.key == game_constants.KEY_STATUS and not GAME.windows:
                    GAME.windows.append(game_content.Window_Status())
                if event.key == game_constants.KEY_STATS and not GAME.windows:
                    GAME.windows.append(game_content.Window_Stats())
                if event.key == game_constants.KEY_EQUIPMENT and not GAME.windows:
                    GAME.windows.append(game_content.Window_Equipment())
                if event.key == game_constants.KEY_SKILLTREE and not GAME.windows:
                    GAME.windows.append(game_content.Window_SkillTree())

                for window in [w for w in GAME.windows if w.active]:
                    if event.key == pygame.K_LEFT:
                        window.input('left')
                    if event.key == pygame.K_RIGHT:
                        window.input('right')
                    if event.key == pygame.K_UP:
                        window.input('up')
                    if event.key == pygame.K_DOWN:
                        window.input('down')
                    if event.key == pygame.K_USE:
                        window.input('use')
                    if event.key == pygame.K_CANCEL:
                        window.input('cancel')

                if event.key == game_constants.KEY_LOG:
                    GAME.long_log = not GAME.long_log
                if event.key == game_constants.KEY_MINIMAP:
                    GAME.show_minimap = (GAME.show_minimap + 1) % 3

class GameStatus(metaclass = Singleton):
    def __init__(self):
        self.mapManager = MapManager()
        self.windowManager = WindowManager()
        self.visualEffectsManager = VisualEffectsManager()
        self.logManager = LogManager()
        self.uiManager = UIManager()


        self.player = None
        self.level = 0
        self.showMinimap = 0
        self.turn_count = 0
        self.controls = {
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'down': pygame.K_DOWN,
            'up': pygame.K_UP,
            'select': pygame.K_s,
            'cancel': pygame.K_c
        }
    def reset(self):
        pass
    def update(self):
        self.mapManager.update()
    def execute_turn(self):
        self.turn_count += 1
        self.mapManager.executeTurn()
    def draw(self):
        self.mapManager.draw()
        self.windowManager.draw()
        self.visualEffectsManager.draw()
        self.logManager.draw()
        self.uiManager.draw()

class MapManager(metaclass = Singleton):
    def __init__(self):
        self.tiles = []
        self.creatures = []
        self.entities = []
        self.items = []
        self.lightMap = None
        self.player = GameStatus().player
    def generateLevel(self):
        level = GameStatus().level
        player = GameStatus().player
        self.map, self.items, self.entities, self.creatures, player.x, player.y = mapgen_dungeon(game_constants.MAP_WIDTH[level], game_constants.MAP_HEIGHT[level])
        self.creatures.append(player)
        self.initializeLight()
        self.updateLight()
    def update(self):
        for e in self.tiles + self.creatures + self.entities + self.items + [self.player]:
            e.update()
    def executeTurn(self):
        for e in self.tiles + self.creatures + self.entities + self.items + [self.player]:
            e.execute_turn()
    def initializeLight(self):
        level = GameStatus().level
        self.lightMap = libtcodpy.map_new(game_constants.MAP_WIDTH[level], game_constants.MAP_HEIGHT[level])
        for x in range(game_constants.MAP_WIDTH[level]):
            for y in range(game_constants.MAP_HEIGHT[level]):
                libtcodpy.map_set_properties(self.lightMap, x, y, self.map[x][y].transparent, self.map[x][y].passable)
    def updateLight(self):
        libtcodpy.map_compute_fov(self.lightMap, self.player.x, self.player.y, game_constants.LIGHT_RADIUS, True, libtcodpy.FOV_BASIC)
    def draw(self):
        for e in self.map + self.items + self.entities + self.creatures + [self.player]:
            e.draw()

class WindowManager():
    def __init__(self):
        self.activeWindow = None

        # Popup window
        self.popup_target_y = 0
        self.popup_time = -1
        self.popup_lines = []

        # Surfaces positions
        self.status_position_x, self.status_position_y = (game_constants.STATUS_IDLE_X, game_constants.STATUS_IDLE_Y)
        self.popup_position_x, self.popup_position_y = (game_constants.POPUP_IDLE_X, game_constants.POPUP_IDLE_Y)
        self.log_position_x, self.log_position_y = (game_constants.LOG_IDLE_X, game_constants.LOG_IDLE_Y)
    def update(self):
        # Update popup
        if self.popup_time > 0: #TODO: FOR FUCKS SAKE THIS CODE LOOKS LIKE A TEN YEAR OLD WROTE IT
            self.popup_time -= 1
        elif self.popup_time == 0:
            self.setPopup(None, 0)
            self.popup_time = -1
        if self.popup_time == -1 and self.popup_position_y == 0:
            self.popup_lines = []
    def setPopup(self, message_lines, max_time):
        if not message_lines:
            self.popup_target_y = 0
            self.popup_time = -1
        else:
            self.popup_target_y = len(message_lines)*12 + 20
            self.popup_time = max_time
            self.popup_lines = message_lines

class VisualEffectsManager():
    def __init__(self):
        self.effects = [] # (VisualEffect effect, Bool active)
        self.moveTimer = 10
    def getPassiveEffects(self):
        return [e for e in self.effects if e[1]]
    def getActiveEffects(self):
        return [e for e in self.effects if not e[1]]
    def drawEffects(self):
        for e in self.effects:
            e.update()
            e.draw()
    def updateMoveTimer(self):
        self.movetimer = max(self.moveTimer - 1, 0)

class LogManager():
    def __init__(self):
        self.log = []
    def addMessage(self, message, color):
        self.log.insert(0, (message, color))
        self.rd_log = True

class UIManager():
    def __init__(self):
        self.UIElements = []
    def draw(self):
        for e in self.UIElements:
            e.update()
            e.draw()

class MenuManager(AbstractApplicationManager):
    pass

class Application(metaclass = Singleton):
    def __init__(self):
        self.debug_mode = True
        self.windowResolution = (1280, 720) # TODO: IMPLEMENT A WAY TO CHANGE IT
        self.applicationManager = GameManager()
        self.window = pygame.display.set_mode((game_constants.GAME_RESOLUTION_WIDTH, game_constants.GAME_RESOLUTION_HEIGHT), 0, 16)
        self.screen = pygame.Surface((game_constants.WINDOW_WIDTH, game_constants.WINDOW_HEIGHT))
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
        pygame.display.set_caption('I found a strange potion')
        self.debug('Application initialized.')
    def debug(self, msg):
        if self.debug_mode:
            print(msg)
    def onFrame(self):
        self.applicationManager.update()
        self.applicationManager.draw()
        self.applicationManager.lateUpdate()
    def draw(self):
        self.window.fill(game_constants.COLOR_BLACK)
        self.applicationManager.draw()
        pygame.transform.scale(self.window, self.windowResolution, self.screen)

class UIElement:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.target_x, self.target_y = x, y
    def update(self):
        self.x += self.target_x - self.x
        self.y += self.target_y - self.y
    def smoothTranslate(self, to_x, to_y):
        self.target_x, self.target_y = to_x, to_y
    def draw(self):
        pass

class Tile:
    def __init__(self, x, y, passable, transparent, sprite):
        self.x = x
        self.y = y
        self.passable = passable
        self.transparent = transparent
        self.sprite = sprite.convert()
        self.sprite_shadow = self.sprite.convert()
        self.discovered = False
        libtcodpy.map_set_properties(MapManager().lightMap, self.x, self.y, self.passable, self.transparent)
        dark = pygame.Surface((self.sprite.get_width(), self.sprite.get_height()), flags=pygame.SRCALPHA)
        dark.fill((50, 50, 50, 0))
        self.sprite_shadow.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    def onDestroy(self):
        pass
    def onWalk(self):
        pass

class GameCamera():
    def __init__(self):
        self.x = 0
        self.y = 0
    def update(self, x, y):
        self.x += (x-self.x-game_constants.CAMERA_WIDTH*16)*0.05
        self.y += (y-self.y-game_constants.CAMERA_HEIGHT*16)*0.05
        self.x = int(game_util.clamp(self.x, 0, game_constants.MAP_WIDTH[GameStatus().level]*32 - game_constants.CAMERA_WIDTH*32))
        self.y = int(game_util.clamp(self.y, 0, game_constants.MAP_HEIGHT[GameStatus().level]*32 - game_constants.CAMERA_HEIGHT*32))

class VisualEffect:
    def __init__(self, x, y, visible, images):
        self.x = x
        self.y = y
        self.visible = visible
        self.images = images
        self.image = images[0]
    def update(self):
        pass
    def draw(self):
        if game_util.isinscreen(self.x*32, self.y*32) and self.visible:
            Application().window.blit(self.image, (self.x*32 - GameManager().gameCamera.x, self.y*32 - GameManager().gameCamera.y + 8))
    def destroy(self):
        if self in VisualEffectsManager().getActiveEffects():
            VisualEffectsManager().getActiveEffects().remove(self)
        if self in VisualEffectsManager().getPassiveEffects():
            VisualEffectsManager().getPassiveEffects().remove(self)

class AnimationOnce(VisualEffect):
    def __init__(self, x, y, images, frame_wait):
        super().__init__(x, y, True, images)
        self.counter_next = 0
        self.frame = 0
        self.frame_wait = frame_wait
    def update(self):
        self.counter_next += 1
        if self.counter_next == self.frame_wait:
            self.frame += 1
            if self.frame == len(self.images):
                self.destroy()
                return
            self.counter_next = 0
            self.image = self.images[self.frame]

class LoopVisualEffect(VisualEffect):
    def __init__(self, x, y, visible, images, frame_wait):
        super().__init__(x, y, visible, images)
        self.frame_wait = frame_wait
        self.counter_next = 0
        self.frame = 0
    def update(self):
        self.counter_next += 1
        if self.counter_next == self.frame_wait:
            self.counter_next = 0
            self.frame = (self.frame + 1) % len(self.images)
            self.image = self.images[self.frame]

class CreatureMoveVisualEffect(LoopVisualEffect):
    def __init__(self, creature, from_pos, to_pos, duration):
        super().__init__(creature.x, creature.y, True, creature.sprite_list[creature.frame:] + creature.sprite_list[:creature.frame], game_constants.ANIMATION_WAIT * 8)
        self.creature = creature
        self.dx, self.dy = to_pos[0], to_pos[1]
        self.duration = duration
        self.current = 0
        self.creature.visible = False
    def update(self):
        self.current += 1
        self.x += self.dx / self.duration
        self.y += self.dy / self.duration
        super().update()
        if self.current == self.duration:
            self.destroy()
    def destroy(self):
        super().destroy()
        self.creature.visible = True

class Window:
    def __init__(self, x, y, sprite):
        self.x, self.y = (x, y)
        self.sprite = sprite.convert()
        self.surface = pygame.Surface((self.sprite.get_width(), self.sprite.get_height()))
        self.parent = None
        self.redraw = True
        self.visible = True
        self.active = True
        self.popup = None
        GameStatus().rd_win = True
        GameStatus().player.active = False
    def draw(self):
        if not self.visible:
            return
        if self.redraw:
            self.update()
        Application().window.blit(self.surface, (self.x, self.y))
    def update(self):
        self.surface.blit(self.sprite, (0, 0))
    def destroy(self):
        if self is WindowManager().activeWindow:
            WindowManager().activeWindow = None
        if self.parent == None:
            GameStatus().player.active = True
        GameStatus().rd_win = True
    def input(self, key):
        if not self.active:
            return
        if self.popup == None:
            self.getItems()
            self.basicControls(key)
            self.redraw = True
        else:
            self.popup.input(key)
            self.popup.redraw = True
        GameStatus().rd_win = True
    def popupInput(self, key):
        if self.popup == None:
            return
    def destroyPopup(self):
        self.popup.destroy()
        self.popup = None
        self.active = True
        GameStatus().rd_win = True
    def basicControls(self, key):
        pass
    def getItems(self):
        pass

class WindowList(Window):
    def __init__(self, x, y, sprite, descriptable):
        super().__init__(x, y, sprite)
        self.index = 0
        self.getItems()
    def basicControls(self, key):
        if key == 'up':
            self.index = (self.index - 1) % len(self.items)
        elif key == 'down':
            self.index = (self.index + 1) % len(self.items)
        elif key == 'cancel':
            self.destroy()
    def getItems(self):
        self.items = []
    def update(self):
        super().update()
    # def updateDescription(self):
    #     if self.needDesc:
    #         GameStatus().descriptionWindow.x = self.x - game_constants.DESCWINDOW_WIDTH
    #         GameStatus().descriptionWindow.y = min(self.index*16+self.yoffset + 32, game_constants.CAMERA_HEIGHT*32 - game_constants.DESCWINDOW_HEIGHT)

class WindowPopupList(WindowList):
    def __init__(self, parent_window, window_name, x, y, sprite, options_list):
        super().__init__(x, y, sprite, False)
        self.parent_window = parent_window
        self.window_name = window_name
        self.items = options_list
    def input(self, key):
        self.basicControls(key)
        self.redraw = True
        GameStatus().rd_win = True
    def update(self):
        super().update()
        self.surface.fill(game_constants.COLOR_DARKRED, pygame.Rect(4, self.index*16 + 8, self.surface.get_width() - 8, 16)) # Highlight selected item
        for itemIndex in range(len(self.items)): # Draw item names
            game_util.draw_text_bg(self.surface, self.items[itemIndex][0], game_constants.POPUP_OFFSET_X, itemIndex*16 + 8, game_constants.FONT_PERFECTDOS, self.items[itemIndex][1], game_constants.COLOR_SHADOW)
    def basicControls(self, key):
        if key == 'up':
            self.index = (self.index - 1) % len(self.items)
        elif key == 'down':
            self.index = (self.index + 1) % len(self.items)
        elif key == 'cancel':
            self.parent_window.popupInput('cancel')
        elif key == 'use':
            self.parent_window.popupInput('use')
    def getItems(self):
        pass
    def destroy(self):
        WindowManager().activeWindow.remove(self)

class SelectTarget:
    def __init__(self, parent_window, window_name, item, marker_sprite):
        self.previousCamera = (GameManager().gameCamera.x, GameManager().gameCamera.y)
        self.max_range = item.maxRange
        self.valid_tiles = [(x, y) for x in range(-self.max_range, self.max_range + 1) for y in range(-self.max_range, self.max_range + 1) if item.targetCondition(x, y)]
        self.updatePosition()
        self.surface = pygame.Surface(((self.max_range + 1)*64, (self.max_range + 1)*64))
        self.surface.set_colorkey(game_constants.COLOR_COLORKEY)
        self.parent = parent_window
        self.marker_sprite = marker_sprite
        self.marker_x, self.marker_y = item.getInitialTarget()
        self.visible = True
        self.active = True
        self.redraw = True
        self.redraw_all = True
    def updatePosition(self):
        if (GameManager().gameCamera.x, GameManager().gameCamera.y) != self.previousCamera:
            self.previousCamera = (GameManager().gameCamera.x, GameManager().gameCamera.y)
        self.x = (GameStatus().player.x - self.max_range)*32 - GameManager().gameCamera.x
        self.y = (GameStatus().player.y - self.max_range)*32 - GameManager().gameCamera.y
    def draw(self):
        if self.redraw_all:
            self.redraw_all = False
            self.surface.set_alpha()
            self.surface.fill(game_constants.COLOR_COLORKEY)
            self.updatePosition()
            self.update()
            self.surface.set_alpha(150)
    def update(self):
        self.updatePosition()
        for x in range(-self.max_range, self.max_range + 1):
            for y in range(-self.max_range, self.max_range + 1):
                if (x, y) in self.valid_tiles and game_util.simpledistance((x, y), (0, 0)) <= self.max_range:
                    self.surface.fill(game_constants.COLOR_GREEN, ((self.max_range + x)*32, (self.max_range + y)*32, 32, 32))
    def destroy(self):
        if self in WindowManager().activeWindow:
            WindowManager().activeWindow.remove(self)
        if self.parent == None:
            GameStatus().player.active = True
        GameStatus().rd_win = True
    def input(self, key):
        self.basicControls(key)
        self.redraw_all = True
        GameStatus().rd_win = True
    def basicControls(self, key):
        pass

class Entity:
    def __init__(self, x, y, tags, sprite_list, behaviors = []):
        self.x = x
        self.y = y
        self.behaviors = behaviors
        self.tags = tags
        self.visible = True
        self.priority = 0
        self.sprite_list = sprite_list
        self.sprite = self.sprite_list[0]
        self.frame = 0
        self.counter_next = 0
    def draw(self):
        if self.visible:
            Application().window.blit(self.sprite, (self.x*32 - GameManager().gameCamera.x, self.y*32 - GameManager().gameCamera.y))
    def update(self):
        self.updateFrame()

    def updateFrame(self):
        self.counter_next += 1
        if self.counter_next == game_constants.ANIMATION_WAIT * 8:
            self.counter_next = 0
            self.frame = (self.frame + 1) % len(self.sprite_list)
            self.sprite = self.sprite_list[self.frame]
    def destroy(self):
        MapManager().entities.remove(self)
    def event(self, event_name, args = ()):
        for e in sorted(self.behaviors, key = lambda x: x[1]):
            e[0](event_name, self, args)

class Creature(Entity):
    def __init__(self, x, y, tags, sprite_list, behaviors, stats, statmods = []):
        super().__init__(x, y, tags, sprite_list, behaviors)
        self.priority = 1
        self.behaviors = behaviors
        self.stats = stats
        self.statmods = statmods
        self.currentHitPoints = self.getMaxHitPoints()
        self.currentMagicPoints = self.getMaxMagicPoints()
    def isEnemy(self):
        return 'enemy' in self.tags
    def draw(self):
        super().draw()
        if self.visible:
            pygame.draw.rect(Application().window, game_constants.COLOR_GREEN, ((self.x*32 - GameManager().gameCamera.x)+1, (self.y*32 - GameManager().gameCamera.y)+30, self.currentHitPoints/self.getMaxHitPoints()*(self.sprite.get_width()-1), 1))

    def getStatMod(self, stat_name):
        statmods = sorted(self.statmods, key = lambda x: x.priority)
        amount = 0
        for mod in statmods:
            amount = mod.execute(self, stat_name, amount)
        return amount
    def getMaxHitPoints(self):
        return max(int((self.stats['HitPointsFlat'])*self.stats['HitPointsMult']/100) + self.getStatMod('HitPointsFlat'), 1)
    def getMaxMagicPoints(self):
        return max(int((self.stats['MagicPointsFlat'])*self.stats['MagicPointsMult']/100) + self.getStatMod('MagicPointsFlat'), 1)
    def getPhyAttack(self):
        return max(int(self.stats['PhyAttackFlat']*self.stats['PhyAttackMult']/100) + self.getStatMod('PhyAttackFlat'), 0)
    def getMagAttack(self):
        return max(int((self.stats['MagAttackFlat'])*self.stats['MagAttackMult']/100) + self.getStatMod('MagAttackFlat'), 0)
    def getPhyArmor(self):
        return max(int((self.stats['PhyArmorFlat'])*self.stats['PhyArmorMult']/100) + self.getStatMod('PhyArmorFlat'), 1)
    def getMagArmor(self):
        return max(int((self.stats['MagArmorFlat'])*self.stats['MagArmorMult']/100) + self.getStatMod('MagArmorFlat'), 1)

class Player(Creature):
    def __init__(self, x, y, sprite_list, portrait_list, stats, equipment, inventory, modifiers, status, skilltree, behaviors, statmods = []):
        super().__init__(x, y, ['player'], sprite_list, behaviors, stats, statmods)
        self.inventory = inventory
        self.name = 'Player'
        self.portrait_list = portrait_list
        self.xp = 0
        self.level = 1
        self.equipment = equipment
        self.currentHunger = game_constants.MAX_HUNGER
        self.active = True
        self.priority = 2

        self.potion = None

        self.modifiers = modifiers
        self.status = status
        self.skilltree = skilltree
        self.behaviors = behaviors
    def input(self, key):
        if self.active:
            if key == 'up':
                self.event('move', (0, -1))
                game_util.map_light_update(MapManager().lightMap)
            elif key == 'down':
                self.event('move', (0, 1))
                game_util.map_light_update(MapManager().lightMap)
            elif key == 'left':
                self.event('move', (-1, 0))
                game_util.map_light_update(MapManager().lightMap)
            elif key == 'right':
                self.event('move', (1, 0))
                game_util.map_light_update(MapManager().lightMap)
    def canAttack(self, relativePosition):
        if self.equipment[0] is None: # No weapon equipped
            return [creature for creature in MapManager().creatures if creature is not self and (creature.x, creature.y) == (self.x + relativePosition[0], self.y + relativePosition[1]) and 'monster' in creature.tags]
        return self.equipment[0].attackTargets(relativePosition) # Weapon range
    def tilesAttack(self, relativePosition):
        if self.equipment[0] is None: # No weapon equipped
            return [(self.x + relativePosition[0], self.y + relativePosition[1])]
        return self.equipment[0].attackTiles(relativePosition) # Weapon range


    def getMaxCarry(self):
        return 10 + self.stats['MaxCarry']
    def getHungerDepletion(self):
        return max(1, 4 + self.stats['HungerFlat'])
    def getCurrentCarry(self):
        return sum([item.size for item in self.inventory] + [item.size for item in self.equipment if item is not None])

class Monster(Creature):
    def __init__(self, x, y, tags, sprite_list, name, drops, behaviors, stats, statmods = []):
        super().__init__(x, y, tags, sprite_list, behaviors, stats, statmods)
        self.name = name
        self.drops = drops
        self.tags = ['monster'] + tags

class Item(Entity):
    def __init__(self, x, y, tags, sprite_list, name, rarity, size, description):
        super().__init__(x, y, tags, sprite_list)
        self.name = name
        self.size = size
        self.rarity = rarity
        if self.rarity == 'Common':
            self.color = game_constants.COLOR_WHITE
        elif self.rarity == 'Rare':
            self.color = game_constants.COLOR_BLUE
        elif self.rarity == 'Mythic':
            self.color = game_constants.COLOR_CYAN
        elif self.rarity == 'Antique':
            self.color = game_constants.COLOR_ORANGE
        if self.rarity == 'Divine':
            self.color = game_constants.COLOR_DARKRED
        else:
            self.color = game_constants.COLOR_GRAY
        self.description = description

class Equipment(Item):
    def __init__(self, x, y, name, rarity, size, description, slot, stats, mods, requirements, tags, sprite_list):
        super().__init__(x, y, tags, sprite_list, name, rarity, size, description)
        self.slot = slot
        self.itemType = 'equipment'
        self.stats = stats
        self.mods = mods
        self.requirements = [requirement(self) for requirement in requirements]
    def equip(self):
        for stat, value in self.stats:
            GameStatus().player.stats[stat] += value
        for mod in self.mods:
            GameStatus().player.statmods.append(mod)
    def unequip(self):
        for stat, value in self.stats:
            GameStatus().player.stats[stat] -= value
        for mod in self.mods:
            GameStatus().player.statmods.remove(mod)
    def canEquip(self):
        return all(requirement() for requirement in self.requirements)

class Weapon(Equipment):
    def __init__(self, x, y, name, rarity, size, description, stats, mods, requirements, tags, sprite_list, spriteattack_list):
        super().__init__(x, y, name, rarity, size, description, 0, stats, mods, requirements, tags, sprite_list)
        self.spriteattack_list = spriteattack_list
    def attackTargets(self, relativePosition):
        pass
    def attackTiles(self, relativePosition):
        pass

class Consumable(Item):
    def __init__(self, x, y, tags, sprite_list, name, color, size, description, effects, useCondition = [], charges = 1):
        super().__init__(x, y, tags, sprite_list, name, color, size, description)
        self.tags += ['target_self']
        self.onUse = effects
        self.useCondition = useCondition
        self.charges = charges
        self.displayCharges = self.charges == 1
        self.itemType = 'consumable'
        self.used = False
    def use(self, *args):
        for action in self.onUse:
            action.execute()
        if self.used:
            GameStatus().player.inventory.remove(self)
    def condition(self):
        for condition in self.useCondition:
            if not condition.execute():
                return False
        return True
    def gotUsed(self):
        return self.used

class ConsumableMap(Consumable):
    def __init__(self, x, y, tags, sprite_list, name, color, size, description, effects, initialTarget, maxRange, useCondition = [], charges = [], targetCondition = []):
        super().__init__(x, y,tags, sprite_list, name, color, size, description, effects, useCondition, charges)
        self.tags.remove('target_self')
        self.tags += ['target_map']
        self.initialTarget = initialTarget(self)
        self.maxRange = maxRange
        self.conditions = targetCondition
    def getInitialTarget(self):
        return self.initialTarget.execute()
    def targetCondition(self, x, y):
        for condition in self.conditions:
            if not condition.execute(x, y):
                return False
        return True
    def use(self, x, y):
        for action in self.onUse:
            action.execute(x, y)
        if self.used:
            GameStatus().player.inventory.remove(self)

class ShortSword(Weapon):
    def attackTargets(self, relativePosition):
        return [creature for creature in MapManager().creatures if creature is not self and (creature.x, creature.y) == (GameStatus().player.x, GameStatus().player.y) + relativePosition and 'monster' in creature.tags]
    def attackTiles(self, relativePosition):
        return [(GameStatus().player.x + relativePosition[0], GameStatus().player.y + relativePosition[1])]

class LongSword(Weapon):
    def attackTargets(self, relativePosition): # TODO: Fix this behavior
        if relativePosition[0] == 0:
            return [creature for creature in MapManager().creatures if creature is not self and creature.x in [GameStatus().player.x + 1, GameStatus().player.x, GameStatus().player.x - 1] and creature.y == GameStatus().player.y + relativePosition[1] and 'monster' in creature.tags]
        elif relativePosition[1] == 0:
            return [creature for creature in MapManager().creatures if creature is not self and creature.x == GameStatus().player.x + relativePosition[0] and creature.y in [GameStatus().player.y + 1, GameStatus().player.y, GameStatus().player.y - 1] and 'monster' in creature.tags]
    def attackTiles(self, relativePosition):
        if relativePosition[0] == 0:
            return [(GameStatus().player.x - 1, GameStatus().player.y + relativePosition[1]), (GameStatus().player.x, GameStatus().player.y + relativePosition[1]), (GameStatus().player.x + 1, GameStatus().player.y + relativePosition[1])]
        elif relativePosition[1] == 0:
            return [(GameStatus().player.x + relativePosition[0], GameStatus().player.y - 1), (GameStatus().player.x + relativePosition[0], GameStatus().player.y), (GameStatus().player.x + relativePosition[0], GameStatus().player.y + 1)]

class Spear(Weapon):
    def attackTargets(self, relativePosition): # TODO: Check if this is working as intended
        return [creature for creature in MapManager().creatures if creature is not self and ((creature.x, creature.y) == (GameStatus().player.x, GameStatus().player.y) + relativePosition or (creature.x, creature.y) == (GameStatus().player.x, GameStatus().player.y) + relativePosition*2) and 'monster' in creature.tags]

class Potion:
    def __init__(self, name, sprite_list, actions, conditions, startCharges, maxCharges, description):
        self.name = name
        self.sprite_list = sprite_list
        self.actions = actions
        self.conditions = conditions
        self.charges = startCharges
        self.maxCharges = maxCharges
        self.description = description
    def drink(self):
        if self.charges > 0 and all([condition.execute() for condition in self.conditions]):
            for action in self.actions:
                action.execute()
            self.charges -= 1

class Spell:
    def __init__(self, name, description, sprite_list, effects, costs, cd):
        self.name = name
        self.description = description
        self.sprite_list = sprite_list
        self.effects = effects
        self.costs = costs
        self.cd = cd


class Skill:
    def __init__(self, index, pos, name, description, sprite, move, req, maxRank):
        self.index = index
        self.x , self.y = pos
        self.name = name
        self.description = description
        self.sprite = sprite
        self.move = move
        self.req = req
        self.maxRank = maxRank
        self.rank = 0
    def onBuy(self):
        if self.maxRank != -1:
            self.rank += 1
    def isMaxed(self):
        return self.rank == self.maxRank
    def isNotMaxed(self):
        return not self.isMaxed()