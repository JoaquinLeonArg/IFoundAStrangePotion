import game_effects

def parse_equipment(file_path):
    items = []
    file = open(file_path, 'r')
    for line in file.read().split('\n')[1:-1]: # Divide by line
        values = line.split(';') # Divide each line by field
        values[2] = int(values[2]) # '15' ---> 15
        values[4] = int(values[4]) # '15' ---> 15
        values[5] = dict(((a.split(': ')[0], int(a.split(': ')[1])) for a in values[5].split(', '))) # ['MaxHealth: 100', ...] ---> {'MaxHealth': 100, ...}
        values[6] = values[6].split(', ') if values[6] else [] # Separate functions
        values[6] = list(eval('game_effects.{}'.format(f).replace('>', ',')) for f in values[6]) if values[6] else [] # "function(a< b< c)" ---> "function(a, b, c)"
        values[7] = values[7].split(', ') if values[7] else []
        values[8] = values[8].split(', ') if values[8] else []
        values[9] = (int(v) for v in values[9].split(', ')) # "0, 0" ---> (0, 0)
        items.append(values)
    return items

print(parse_equipment('resources/ArmorData.csv'))
