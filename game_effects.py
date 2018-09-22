###### EQUIPMENT #####
class linearStat():
    def __init__(self, priority, stat_name, amount):
        self.priority = priority
        self.stat_name = stat_name
        self.amount = amount
    def execute(self, target, stat_name, current):
        if self.stat_name == stat:
            return self.amount

class nullifyStat():
    def __init__(self, priority, stat_name):
        self.priority = priority
        self.stat_name = stat_name
    def execute(self, target, stat_name, current):
        if self.stat_name == stat:
            return 0
