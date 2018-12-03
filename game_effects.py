import game_constants
import game_classes
from abc import ABC

global GAME

class Effect(ABC):
    def __init__(self, priority):
        self.priority = priority




# STAT MODS #
class linearStat(Effect):
    def __init__(self, priority, stat_name, amount):
        super().__init__(priority)
        self.stat_name = stat_name
        self.amount = amount
    def execute(self, target, stat, current):
        if self.stat_name == stat:
            return self.amount + current
        else:
            return current
    def getDescription(self):
        if self.amount > 0:
            return ('+{} {}'.format(self.amount, self.stat_name), game_constants.COLOR_POSITIVESTAT)
        else:
            return ('{} {}'.format(self.amount, self.stat_name), game_constants.COLOR_NEGATIVESTAT)

class nullifyStat(Effect):
    def __init__(self, priority, stat_name):
        super().__init__(priority)
        self.stat_name = stat_name
    def execute(self, target, stat_name, current):
        if self.stat_name == stat_name:
            return -target.stats[stat_name]
        else:
            return current
    def getDescription(self):
        return ('Nullify {}'.format(self.stat_name), game_constants.COLOR_NEGATIVESTAT)

# BEHAVIOR MODS #
class drillMod(Effect):
    def __init__(self, priority):
        super().__init__(priority)
    def execute(self, event, parent, args):
        if event == 'move':
            x_to, y_to = parent.x + args[0], parent.y + args[1]
            GAME.map[x_to][y_to].event('destroy', [])
    def getDescription(self):
        return ('Destroy walls on contact', game_constants.COLOR_POSITIVESTAT)

# SPELL EFFECTS #
class healFlatEffect(Effect):
    def __init__(self, priority, amount):
        super().__init__(priority)
        self.amount = amount
    def execute(self, parent):
        parent.event('heal', (self.amount))
    def getDescription(self):
        return ('Heal player for {}'.format(self.amount), game_constants.COLOR_POSITIVESTAT)

class healPercentageEffect(Effect):
    def __init__(self, priority, amount):
        super().__init__(priority)
        self.amount = amount
    def execute(self, parent):
        parent.event('heal', (int(parent.getMaxHitPoints()*self.amount)))
    def getDescription(self):
        return ('Heal player for {}% of his max HP ({})'.format(self.amount, int(GAME.player.getMaxHitPoints()*self.amount)), game_constants.COLOR_POSITIVESTAT)

# REQUIREMENTS #
class minimumStat():
    def __init__(self, stat_name, amount):
        self.stat_name = stat_name
        self.amount = amount
    def execute(self, parent):
        return parent.getStat(self.stat_name) >= self.amount
    def getDescription(self, parent):
        if self.execute(parent):
            return ('{}+ {}'.format(self.amount, self.stat_name), game_constants.COLOR_POSITIVESTAT)
        else:
            return ('{}+ {}'.format(self.amount, self.stat_name), game_constants.COLOR_NEGATIVESTAT)

# TERRAIN BEHAVIOR #
class StoneOnDestroy(Effect):
    def execute(self, event_name, parent, _):
        if event_name == 'destroy':
            GAME.map[parent.x][parent.y] = game_classes.Tile(parent.x, parent.y, True, True, game_constants.TILE_SPRITES['cave_dirt'])