import game_constants

###### EQUIPMENT #####
class linearStat():
    def __init__(self, priority, stat_name, amount):
        self.priority = priority
        self.stat_name = stat_name
        self.amount = amount
    def execute(self, target, stat_name, current):
        if self.stat_name == stat:
            return self.amount + current
        else:
            return current
    def getDescription(self):
        return [('Increases ____ by __.', game_constants.COLOR_GREEN)]
class nullifyStat():
    def __init__(self, priority, stat_name):
        self.priority = priority
        self.stat_name = stat_name
    def execute(self, target, stat_name, current):
        if self.stat_name == stat_name:
            return -target.stats[stat_name]
        else:
            return current
    def getDescription(self):
        return [('You have no ____ anymore.', game_constants.COLOR_RED)]
