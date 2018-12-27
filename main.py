import pygame
import random
import math
import tilemaps
from collections import defaultdict
from statusbar import StatusBar
from statussquare import StatusSquare
from scrollwindow import ScrollWindow

pygame.init()
pygame.display.set_caption('Tile Clicker')

clock = pygame.time.Clock()
GAME_TICK = pygame.USEREVENT + 1  # 25
TICKS_PER_SEC = 20
ONE_SEC = TICKS_PER_SEC
TEN_SEC = 10*TICKS_PER_SEC

DISPLAY_WIDTH = 1200
DISPLAY_HEIGHT = 700

gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))

MAP_SIZE = 9

TILE_WIDTH = 50
TILE_HEIGHT = 50

PERK_WIDTH = 100
PERK_HEIGHT = 50
PERK_OFFSET = 50
PERK_DIST = 25

GAME_OFFSETS = {'x': 50, 'y': 50}
GAME_OFFSET = (GAME_OFFSETS['x'], GAME_OFFSETS['y'])

GAME_WIDTH = 600
GAME_HEIGHT = 600

CHART_WIDTH = 240
CHART_HEIGHT = 240

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
RED = pygame.Color('red')
LIGHTGREEN = pygame.Color('lightgreen')
DARKGREEN = pygame.Color('darkgreen')
GREEN = pygame.Color('green')
GREY = pygame.Color('grey')
BLUE = pygame.Color('blue')
LIGHTBLUE = pygame.Color('lightblue')
YELLOW = pygame.Color('yellow')
PURPLE = pygame.Color('purple')
CYAN = pygame.Color('cyan')

WATER = (82, 146, 255)
GRASS = (95, 131, 33)
ROCK = (215, 255, 158)
SAND = (255, 235, 115)
ICE = (219, 243, 255)

# Coin cost of maps at different radii
MAP_COSTS = {0: 0,
             1: 100,
             2: 200,
             3: 400,
             4: 800}

TILE_INFO = {
             'r': {'name': 'Stone',
                   'color': GREY,
                   'can_spawn': {'rock': 10,
                                 'boulder': 5,
                                 'irondeposit': 2,
                                 'golddeposit': 2}},
             'w': {'name': 'Water',
                   'color': WATER,
                   'can_spawn': {'fish': 1}},
             'g': {'name': 'Grass',
                   'color': GRASS,
                   'can_spawn': {'tree': 1,
                                 'bush': 1}},
             's': {'name': 'Sand',
                   'color': SAND,
                   'can_spawn': {'sand': 10,
                                 'coinpile': 1}},
             'i': {'name': 'Ice',
                   'color': ICE,
                   'can_spawn': {'none': 15,
                                 'loosegem': 1}}
             }

RESOURCES = {
             'rock': {'image': pygame.image.load('Rocks.png').convert_alpha(),
                      'minetime': 5*ONE_SEC,
                      'minegives': {'stone': 1},
                      'minecosts': {'energy': 5}},
             'boulder': {'image': pygame.image.load('Boulder.png').convert_alpha(),
                         'minetime': 10*ONE_SEC,
                         'minegives': {'stone': 5},
                         'minecosts': {'energy': 20}},
             'irondeposit': {'image': pygame.image.load('Iron.png').convert_alpha(),
                             'minetime': 10*ONE_SEC,
                             'minegives': {'ironore': 2},
                             'minecosts': {'energy': 20}},
             'golddeposit': {'image': pygame.image.load('Gold.png').convert_alpha(),
                             'minetime': 10*ONE_SEC,
                             'minegives': {'goldore': 2},
                             'minecosts': {'energy': 20}},
             'fish': {'image': pygame.image.load('Fish2a.png').convert_alpha(),
                      'minetime': 5*ONE_SEC,
                      'minegives': {'food': 1},
                      'minecosts': {'energy': 5}},
             'tree': {'image': pygame.image.load('Tree1.png').convert_alpha(),
                      'minetime': 5*ONE_SEC,
                      'minegives': {'wood': 2},
                      'minecosts': {'energy': 5}},
             'bush': {'image': pygame.image.load('Bush2.png').convert_alpha(),
                      'minetime': 5*ONE_SEC,
                      'minegives': {'food': 1},
                      'minecosts': {'energy': 5}},
             'sand': {'image': pygame.image.load('Sandpile.png').convert_alpha(),
                      'minetime': ONE_SEC,
                      'minegives': {'sand': 1},
                      'minecosts': {'energy': 5}},
             'coinpile': {'image': pygame.image.load('Goldcoins.png').convert_alpha(),
                          'minetime': ONE_SEC,
                          'minegives': {'coins': 20},
                          'minecosts': {'energy': 5}},
             'loosegem': {'image': pygame.image.load('Gem.png').convert_alpha(),
                          'minetime': ONE_SEC,
                          'minegives': {'gem': 1},
                          'minecosts': {'energy': 5}},
             'animal trap': {'symbol': "AT",
                             'minetime': ONE_SEC,
                             'minegives': {'food': 4},
                             'minecosts': {'energy': 5}},
             'house': {'symbol': "Ho",
                       'minetime': TEN_SEC,
                       'minegives': {'stone': 10,
                                     'wood': 20},
                       'minecosts': {'energy': 20},
                       'beds': 4,
                       'recruitcost': 20,
                       'confirmdestroy': True,
                       'upkeep': {'food': 1},
                       'frequency': TEN_SEC},
             'fishing shack': {'symbol': "FS",
                               'minetime': 5*ONE_SEC,
                               'minegives': {'stick': 5,
                                             'wood': 10},
                               'minecosts': {'energy': 20},
                               'confirmdestroy': True,
                               'gathers': ['fish'],
                               'workradius': 2,
                               'upkeep': {'workers': 1},
                               'frequency': 5*ONE_SEC},
             'forager hut': {'symbol': "FH",
                             'minetime': 5*ONE_SEC,
                             'minegives': {'stick': 5,
                                           'wood': 10},
                             'minecosts': {'energy': 20},
                             'confirmdestroy': True,
                             'gathers': ['bush', 'rock', 'gem', 'sand'],
                             'workradius': 3,
                             'upkeep': {'workers': 1},
                             'frequency': 5*ONE_SEC},
             'lumberjack hut': {'symbol': "LH",
                                'minetime': 5*ONE_SEC,
                                'minegives': {'stone': 10,
                                              'wood': 20},
                                'minecosts': {'energy': 20},
                                'confirmdestroy': True,
                                'gathers': ['tree'],
                                'workradius': 3,
                                'upkeep': {'workers': 1},
                                'frequency': 5*ONE_SEC},
             'miner': {'symbol': "Mn",
                       'minetime': 5*ONE_SEC,
                       'minegives': {'iron': 5,
                                     'stone': 10,
                                     'wood': 10},
                       'minecosts': {'energy': 20},
                       'confirmdestroy': True,
                       'gathers': ['boulder', 'irondeposit', 'golddeposit'],
                       'workradius': 2,
                       'upkeep': {'workers': 1},
                       'frequency': 5*ONE_SEC},
             'wood generator': {'symbol': "WG",
                                'minetime': 5*ONE_SEC,
                                'minegives': {'iron': 5,
                                              'stone': 10,
                                              'wood': 10},
                                'minecosts': {'energy': 20},
                                'confirmdestroy': True,
                                'powerproduced': 2,
                                'upkeep': {'wood': 1},
                                'frequency': 5*ONE_SEC},
             'electric miner': {'symbol': "EM",
                                'minetime': 5*ONE_SEC,
                                'minegives': {'iron': 5,
                                              'stone': 10,
                                              'wood': 10},
                                'minecosts': {'energy': 20},
                                'confirmdestroy': True,
                                'gathers': ['boulder', 'irondeposit', 'golddeposit'],
                                'workradius': 3,
                                'upkeep': {'power': 1},
                                'frequency': 5*ONE_SEC}
             }

ALL_RECIPES = {
               'stick': {'gives': {'stick': 2},
                         'costs': {'wood': 1,
                                   'energy': 2}},
               'glass': {'gives': {'glass': 1},
                         'costs': {'sand': 2,
                                   'energy': 10}},
               'iron': {'gives': {'iron': 1},
                        'costs': {'ironore': 2,
                                  'energy': 10}},
               'gold': {'gives': {'gold': 1},
                        'costs': {'goldore': 2,
                                  'energy': 10}}
               }

BUILDABLES = {
              'animal trap': {'description': ['Produces 4 food.',
                                              'Consumed on use.'],
                              'canbuild': ['g', 'w'],
                              'buildcosts': {'food': 1,
                                             'stone': 1,
                                             'stick': 5,
                                             'energy': 5},
                              'buildtime': TEN_SEC},
              'house': {'description': ['Increases capacity by 4.',
                                        'Upkeep: 1 food / 10 sec.'],
                        'canbuild': ['g', 'r', 's', 'i'],
                        'buildcosts': {'stone': 30,
                                       'wood': 40,
                                       'energy': 50},
                        'buildtime': 5*ONE_SEC},
              'fishing shack': {'description': ['Automatically collects ',
                                                'nearby fish.'],
                                'canbuild': ['g', 'r', 's', 'i'],
                                'buildcosts': {'stick': 10,
                                               'wood': 20,
                                               'energy': 30},
                                'buildtime': 5*ONE_SEC},
              'forager hut': {'description': ['Automatically collects ',
                                              'nearby berries and stone.'],
                              'canbuild': ['g', 'r', 's', 'i'],
                              'buildcosts': {'stick': 10,
                                             'wood': 20,
                                             'energy': 30},
                              'buildtime': 5*ONE_SEC},
              'lumberjack hut': {'description': ['Automatically chops ',
                                                 'down trees.'],
                                 'canbuild': ['g', 'r', 's', 'i'],
                                 'buildcosts': {'stone': 30,
                                                'wood': 40,
                                                'energy': 30},
                                 'buildtime': 5 * ONE_SEC},
              'miner': {'description': ['Automatically mines ',
                                        'boulders and ores.'],
                        'canbuild': ['g', 'r', 's', 'i'],
                        'buildcosts': {'iron': 10,
                                       'stone': 20,
                                       'wood': 20,
                                       'energy': 30},
                        'buildtime': 5 * ONE_SEC},
              'wood generator': {'description': ['Consumes 1 wood and , ',
                                                 'generates 2 power. '],
                                 'canbuild': ['g', 'r', 's', 'i'],
                                 'buildcosts': {'iron': 10,
                                                'stone': 20,
                                                'wood': 20,
                                                'energy': 30},
                                 'buildtime': 5 * ONE_SEC},
              'electric miner': {'description': ['Automatically mines ',
                                                 'boulders and ores. ',
                                                 'Uses 1 power. '],
                                 'canbuild': ['g', 'r', 's', 'i'],
                                 'buildcosts': {'iron': 10,
                                                'stone': 20,
                                                'wood': 20,
                                                'energy': 30},
                                 'buildtime': 5 * ONE_SEC}
              }

ITEMS = {
         'energy': {'i_cap': 'Energy',
                    'lower': 'energy',
                    'plural': 'energy',
                    'plural_i_cap': 'Energy',
                    'sell_value': 0},
         'coins': {'i_cap': 'Coin',
                   'lower': 'coin',
                   'plural': 'coins',
                   'plural_i_cap': 'Coins',
                   'sell_value': 0},
         'workers': {'i_cap': 'Worker',
                     'lower': 'worker',
                     'plural': 'workers',
                     'plural_i_cap': 'Workers',
                     'sell_value': 0},
         'wood': {'i_cap': 'Wood',
                  'lower': 'wood',
                  'plural': 'pieces of wood',
                  'plural_i_cap': 'Pieces of wood',
                  'sell_value': 2},
         'stick': {'i_cap': 'Stick',
                   'lower': 'stick',
                   'plural': 'sticks',
                   'plural_i_cap': 'Sticks',
                   'sell_value': 1},
         'stone': {'i_cap': 'Stone',
                   'lower': 'stone',
                   'plural': 'stones',
                   'plural_i_cap': 'Stones',
                   'sell_value': 1},
         'food': {'i_cap': 'Food',
                  'lower': 'portion of food',
                  'plural': 'portions of food',
                  'plural_i_cap': 'Portions of food',
                  'sell_value': 2},
         'ironore': {'i_cap': 'Iron ore',
                     'lower': 'iron ore',
                     'plural': 'iron ore',
                     'plural_i_cap': 'Iron ore',
                     'sell_value': 2},
         'iron': {'i_cap': 'Iron',
                  'lower': 'iron ingot',
                  'plural': 'iron ingots',
                  'plural_i_cap': 'Iron Ingots',
                  'sell_value': 10},
         'goldore': {'i_cap': 'Gold ore',
                     'lower': 'gold ore',
                     'plural': 'gold ore',
                     'plural_i_cap': 'Gold ore',
                     'sell_value': 3},
         'gold': {'i_cap': 'Gold',
                  'lower': 'gold ingot',
                  'plural': 'gold ingots',
                  'plural_i_cap': 'Gold ingots',
                  'sell_value': 20},
         'sand': {'i_cap': 'Sand',
                  'lower': 'pile of sand',
                  'plural': 'piles of sand',
                  'plural_i_cap': 'Piles of sand',
                  'sell_value': 1},
         'glass': {'i_cap': 'Glass',
                   'lower': 'pane of glass',
                   'plural': 'panes of glass',
                   'plural_i_cap': 'Panes of glass',
                   'sell_value': 5},
         'gem': {'i_cap': 'Gem',
                 'lower': 'gem',
                 'plural': 'gems',
                 'plural_i_cap': 'Gems',
                 'sell_value': 100},
         'fish': {'i_cap': 'Fish',
                  'lower': 'fish',
                  'plural': 'fishing spots',
                  'plural_i_cap': 'Fishing spots'},
         'rock': {'i_cap': 'Rock',
                  'lower': 'rock',
                  'plural': 'rocks',
                  'plural_i_cap': 'Rocks'},
         'boulder': {'i_cap': 'Boulder',
                     'lower': 'boulder',
                     'plural': 'boulders',
                     'plural_i_cap': 'Boulders'},
         'irondeposit': {'i_cap': 'Iron deposit',
                         'lower': 'iron deposit',
                         'plural': 'iron deposits',
                         'plural_i_cap': 'iron deposits'},
         'golddeposit': {'i_cap': 'Gold deposit',
                         'lower': 'gold deposit',
                         'plural': 'gold deposits',
                         'plural_i_cap': 'Gold deposits'},
         'tree': {'i_cap': 'Tree',
                  'lower': 'tree',
                  'plural': 'trees',
                  'plural_i_cap': 'Trees'},
         'bush': {'i_cap': 'Bush',
                  'lower': 'bush',
                  'plural': 'bushes',
                  'plural_i_cap': 'Bushes'},
         'coinpile': {'i_cap': 'Coin pile',
                      'lower': 'coin pile',
                      'plural': 'coin piles',
                      'plural_i_cap': 'Coin piles'},
         'loosegem': {'i_cap': 'Gem',
                      'lower': 'gem',
                      'plural': 'gems',
                      'plural_i_cap': 'Gems'},
         'house': {'i_cap': 'House',
                   'lower': 'house',
                   'plural': 'houses',
                   'plural_i_cap': 'Houses'},
         'fishing shack': {'i_cap': 'Fishing shack',
                           'lower': 'fishing shack',
                           'plural': 'fishing shacks',
                           'plural_i_cap': 'Fishing shacks'},
         'animal trap': {'i_cap': 'Animal Trap',
                         'lower': 'animal trap',
                         'plural': 'animal traps',
                         'plural_i_cap': 'Animal traps'},
         'forager hut': {'i_cap': 'Forager hut',
                         'lower': 'forager hut',
                         'plural': 'forager huts',
                         'plural_i_cap': 'Forager huts'},
         'lumberjack hut': {'i_cap': 'Lumberjack hut',
                            'lower': 'lumberjack hut',
                            'plural': 'lumberjack huts',
                            'plural_i_cap': 'Lumberjack huts'},
         'miner': {'i_cap': 'Miner',
                   'lower': 'miner',
                   'plural': 'miners',
                   'plural_i_cap': 'Miners'},
         'wood generator': {'i_cap': 'Wood generator',
                            'lower': 'wood generator',
                            'plural': 'wood generators',
                            'plural_i_cap': 'Wood generators'},
         'electric miner': {'i_cap': 'Electric miner',
                            'lower': 'electric miner',
                            'plural': 'electric miners',
                            'plural_i_cap': 'Electric miners'}
         }

PERKS = {
         '000': {'name': 'Bonus Stone',
                 'cost': 50,
                 'description': ['Get 50% more stone ',
                                 'from boulders'],
                 'dependencies': None,
                 'bonuses': {'minegives': {'boulder': {'stone': 0.5}}}},
         '001': {'name': 'Bonuser Stone',
                 'cost': 100,
                 'description': ['Get 100% more stone from ',
                                 'rocks and boulders'],
                 'dependencies': ['000'],
                 'bonuses': {'minegives': {'rock': {'stone': 1.0},
                                           'boulder': {'stone': 1.0}}}},
         '011': {'name': 'Melting',
                 'cost': 50,
                 'description': ['Learn how to make glass ',
                                 'and how to smelt iron and gold.'],
                 'dependencies': ['000'],
                 'knowledge': {'recipes': ['glass', 'iron', 'gold']}},
         '012': {'name': 'Mining',
                 'cost': 50,
                 'description': ['Learn how to build miners ',
                                 'who can mine Boulders and ore.'],
                 'dependencies': ['011'],
                 'knowledge': {'buildings': ['miner']}},
         '013': {'name': 'Better mining',
                 'cost': 100,
                 'description': ['Get 50% more stone from ',
                                 'boulders and ore when mining.'],
                 'dependencies': ['012'],
                 'bonuses': {'minegives': {'boulder': {'stone': 0.5},
                                           'irondeposit': {'ironore': 0.5},
                                           'golddeposit': {'goldore': 0.5}}}},
         '021': {'name': 'Power!',
                 'cost': 50,
                 'description': ['Learn how to build a ',
                                 'generator that burns wood. '],
                 'dependencies': ['011'],
                 'knowledge': {'buildings': ['wood generator']}},
         '100': {'name': 'Bonus Wood',
                 'cost': 50,
                 'description': ['Get 50% more wood from trees.'],
                 'dependencies': ['000'],
                 'bonuses': {'minegives': {'tree': {'wood': 0.5}}}},
         '102': {'name': 'Electric Mining',
                 'cost': 50,
                 'description': ['Learn how to build ',
                                 'electric miners. '],
                 'dependencies': ['021', '101'],
                 'knowledge': {'buildings': ['electric miner']}},
         '101': {'name': 'People!',
                 'cost': 50,
                 'description': ['Learn how to build houses. '],
                 'dependencies': ['100'],
                 'knowledge': {'buildings': ['house']}},
         '112': {'name': 'Forager Hut',
                 'cost': 50,
                 'description': ['Learn how to ',
                                 'build forager huts.'],
                 'dependencies': ['101'],
                 'knowledge': {'buildings': ['forager hut']}},
         '113': {'name': 'Lumberjack Hut',
                 'cost': 50,
                 'description': ['Learn how to ',
                                 'build lumberjack huts.'],
                 'dependencies': ['101'],
                 'knowledge': {'buildings': ['lumberjack hut']}},
         '114': {'name': 'Fishing Shack',
                 'cost': 50,
                 'description': ['Learn how to ',
                                 'build fishing shacks.'],
                 'dependencies': ['101'],
                 'knowledge': {'buildings': ['fishing shack']}},
         '121': {'name': 'Bonuser Wood',
                 'cost': 100,
                 'description': ['Get 50% more wood from trees.'],
                 'dependencies': ['100'],
                 'bonuses': {'minegives': {'tree': {'wood': 0.5}}}},
         '131': {'name': 'Faster Wood',
                 'cost': 50,
                 'description': ['Chop trees 50% faster.'],
                 'dependencies': ['100'],
                 'bonuses': {'minetime': {'tree': 0.5}}},
         '132': {'name': 'Fasterer Wood',
                 'cost': 100,
                 'description': ['Chop trees 50% faster.'],
                 'dependencies': ['131'],
                 'bonuses': {'minetime': {'tree': 0.5}}},
         }

GAME_AREA_RECT = (GAME_OFFSETS['x'], GAME_OFFSETS['y'], GAME_WIDTH, GAME_HEIGHT)
gameArea = gameDisplay.subsurface(GAME_AREA_RECT)
MAP_OFFSET = ((GAME_WIDTH - (MAP_SIZE*TILE_WIDTH)) / 2,
              (GAME_HEIGHT - (MAP_SIZE*TILE_HEIGHT)) / 2)
maprect = (MAP_OFFSET[0], MAP_OFFSET[1], (MAP_SIZE*TILE_WIDTH), (MAP_SIZE*TILE_HEIGHT))
mapArea = gameArea.subsurface(maprect)
perkrect = (700, 75, 450, 450)
perkArea = gameDisplay.subsurface(perkrect)

mapviewbutton = pygame.Surface((40, 40))
mapviewbuttonpos = (GAME_WIDTH - 58, 18)
mapviewrect = mapviewbutton.get_rect(topleft=mapviewbuttonpos)
mapviewbutton.fill(GREY)
for x in range(3):
    for y in range(3):
        pygame.draw.rect(mapviewbutton, BLACK, (x*15, y*15, 10, 10))

FONTS = {'small': pygame.font.SysFont(None, 15),
         'medium': pygame.font.SysFont(None, 25),
         '20': pygame.font.SysFont(None, 20),
         'mediumbold': pygame.font.SysFont(None, 25, True),
         '45': pygame.font.SysFont(None, 45),
         'large': pygame.font.SysFont(None, 50)}

rand_row = [0, 1, 2, 3, 4, 5, 6, 7, 8]
rand_col = [0, 1, 2, 3, 4, 5, 6, 7, 8]
random.shuffle(rand_row)
random.shuffle(rand_col)


def text_objects(text, font, color=BLACK, bg=None):
    text_surface = font.render(text, True, color, bg)
    return text_surface, text_surface.get_rect()


class Log(object):
    def __init__(self):
        self.text_lines = []
        self.surf = None

    def add_line(self, textline):
        self.text_lines.append(textline)
        if len(self.text_lines) > 5:
            del self.text_lines[0]
        self.make_surf()

    def make_surf(self):
        self.surf = ToolTip(self.text_lines)


log = Log()


class Player(object):
    def __init__(self):
        self.max_energy = 100
        self.inventory = {'energy': 0,
                          'coins': 0,
                          'wood': 0,
                          'stick': 0,
                          'sand': 0,
                          'stone': 0,
                          'food': 0,
                          'ironore': 0,
                          'iron': 0,
                          'glass': 0,
                          'goldore': 0,
                          'gold': 0,
                          'gem': 0}
        self.population = 0
        self.known_items = []
        self.recipes = {}
        self.buildables = {}
        self.perks = []
        self.usables = {'food': {'gives': {'energy': 20},
                                 'costs': {'food': 1}}}
        self.rates = {}

    def get_perk(self, id, game):
        if 'knowledge' in PERKS[id]:
            if 'recipes' in PERKS[id]['knowledge']:
                for recipe in PERKS[id]['knowledge']['recipes']:
                    self.learn_recipe(recipe)
            if 'buildings' in PERKS[id]['knowledge']:
                for building in PERKS[id]['knowledge']['buildings']:
                    self.learn_building(building)
        if 'bonuses' in PERKS[id]:
            mine_gives = PERKS[id]['bonuses'].get('minegives', None)
            mine_time = PERKS[id]['bonuses'].get('minetime', None)
            if mine_gives is not None:
                for bonus in mine_gives:
                    for thing in mine_gives[bonus]:
                        game.dropbuffs[bonus]['minegives'][thing] += mine_gives[bonus][thing]

            if mine_time is not None:
                for bonus in mine_time:
                    if bonus not in self.rates:
                        self.rates[bonus] = mine_time[bonus]
                    else:
                        self.rates[bonus] = self.rates[bonus]*mine_time[bonus]

    def learn_recipe(self, thing):
        self.recipes[thing] = ALL_RECIPES[thing]

    def learn_building(self, thing):
        self.buildables[thing] = BUILDABLES[thing]

    def adjust_inventory(self, item, amt):
        if item == 'energy':
            new_amt = min(self.max_energy, self.inventory['energy'] + amt)
            self.inventory['energy'] = new_amt
        else:
            if item not in self.known_items:
                self.known_items.append(item)
            self.inventory[item] += amt
            if self.inventory[item] < 0:
                self.inventory[item] = 0
                return 'failed'

    def craftable(self, item, number=1):
        is_craftable = True
        for key, value in self.recipes[item]['costs'].items():
            if self.inventory[key] < value*number:
                is_craftable = False
        return is_craftable

    def buildable(self, item):
        is_buildable = True
        for key, value in self.buildables[item]['buildcosts'].items():
            if self.inventory[key] < value:
                is_buildable = False
        return is_buildable

    def usable(self, item, number=1):
        is_usable = True
        for key, value in self.usables[item]['costs'].items():
            if self.inventory[key] < value*number:
                is_usable = False
        return is_usable

    def craft(self, item, number=1):
        if self.craftable(item, number):
            for key, value in self.recipes[item]['costs'].items():
                self.adjust_inventory(key, -value*number)
            for key, value in self.recipes[item]['gives'].items():
                self.adjust_inventory(key, value*number)
                text = '{:,}'.format(value*number)+' '+get_name(key, value*number, False)+' crafted'
                log.add_line(TextLine(text))

    def use(self, item, number=1):
        if self.usable(item, number):
            for key, value in self.usables[item]['costs'].items():
                self.adjust_inventory(key, -value*number)
            for key, value in self.usables[item]['gives'].items():
                self.adjust_inventory(key, value*number)
                text = '{:,}'.format(number)+' '+get_name(item, number, False)+' used'
                log.add_line(TextLine(text))


player = Player()

item_history = {key: [None] for key in player.inventory}
for i in range(59):
    for key in item_history:
        if i == 58:
            item_history[key].append(0)
        else:
            item_history[key].append(None)


def update_item_history():
    for item in player.inventory:
        item_history[item].append(player.inventory[item])
        del item_history[item][0]


class TextLine(object):
    def __init__(self, string, color=BLACK, font='medium', bg=None, return_val=None):
        self.font = FONTS[font]
        self.surf, self.rect = text_objects(string, self.font, color, bg)
        self.string = string
        self.color = color
        self.tooltip = None
        self.return_val = return_val

    def check_mouseover(self, relmouse):
        if ((self.rect.x + self.rect.w > relmouse[0] > self.rect.x
             and self.rect.y + self.rect.h > relmouse[1] > self.rect.y)):
            return True


class ToolTip(pygame.Surface):
    def __init__(self, text_list, o_color=None):
        self.text_list = text_list
        self.o_color = o_color
        self.w = 0
        self.h = 0
        for line in text_list:
            self.w = max(self.w, line.rect.w+2*2)  # pixel buffer of 2 on each side
            self.h += line.rect.h
        super().__init__((self.w, self.h))
        self.fill(WHITE)
        self.set_alpha(220)
        self.make()

    def make(self):
        y = 0
        for line in self.text_list:
            self.blit(line.surf, (2, y, line.rect.w, line.rect.h))  # pixel buffer of 2
            y += line.rect.h
        if self.o_color:
            pygame.draw.rect(self, self.o_color, self.get_rect(), 1)

    def draw(self, surface, pos):
        new_pos = (min(pos[0]+10, surface.get_width()-self.w-1), max(1, pos[1]-self.h-10))
        surface.blit(self, new_pos)


class Tile(pygame.Rect):
    def __init__(self, x, y, map, type='g'):
        super().__init__(x*TILE_WIDTH, y*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
        self.grid_x = x
        self.grid_y = y
        self.map: Map = map
        self.type = type
        self.color = TILE_INFO[type]['color']
        self.surf = pygame.Surface((TILE_WIDTH, TILE_HEIGHT))
        self.resource = None
        self.resource_dict = None
        self.mine_costs = None
        self.beds = 0
        self.population = 0
        self.max_power = 0
        self.recruit_cost = 0
        self.produces = None
        self.gathers = None
        self.frequency = None
        self.upkeep = None
        self.work_radius = None
        self.text_rect = None
        self.text_surf = None
        self.symbol = None
        self.image = None
        self.status = None
        self.status_square = None
        self.timer = None
        self.tooltip = None
        self.redraw()

    def tick(self):
        if self.timer:
            num = 100-100*self.timer.value/float(self.timer.ticks)
            if self.status == 'mined':
                self.status_square.set(num)
            elif self.status == 'building':
                self.status_square.set(100-num)
            self.timer.tick()
            if self.timer and self.timer.value <= 0:
                self.status = None
                self.status_square = None
                self.timer = None
            self.redraw()

    def spawn(self, game, force=False):
        if len(TILE_INFO[self.type]['can_spawn'].items()) > 0 or force:
            res_list = []
            for key, value in TILE_INFO[self.type]['can_spawn'].items():
                for i in range(value):
                    res_list.append(key)
            res = random.choice(res_list)
            if res != 'none':
                self.resource = res
                self.resource_dict = RESOURCES[res]
                self.mine_costs = self.resource_dict['minecosts']
                if 'symbol' in self.resource_dict:
                    self.symbol = self.resource_dict['symbol']
                else:
                    self.image = self.resource_dict['image']
                self.redraw()
                self.set_tooltip(game)

    def begin_build(self, res, game):
        self.resource = res
        self.resource_dict = RESOURCES[res]
        self.mine_costs = self.resource_dict['minecosts']
        self.produces = self.resource_dict.get('produces', None)
        self.gathers = self.resource_dict.get('gathers', None)
        self.frequency = self.resource_dict.get('frequency', None)
        self.upkeep = self.resource_dict.get('upkeep', None)
        self.work_radius = self.resource_dict.get('workradius', None)
        if 'symbol' in self.resource_dict:
            self.symbol = self.resource_dict['symbol']
        else:
            self.image = self.resource_dict['image']
        for key, value in BUILDABLES[res]['buildcosts'].items():
            player.adjust_inventory(key, -value)
        action = self.finish_build
        action_dict = {'game': game}
        self.timer = Timer(BUILDABLES[res]['buildtime'], action, action_dict)
        self.status = 'building'
        self.status_square = StatusSquare(self.w, self.h, WHITE)
        self.redraw()

    def finish_build(self, game):
        beds = self.resource_dict.get('beds', 0)
        self.map.beds += beds
        self.beds += beds
        if 'powerproduced' in self.resource_dict:
            self.max_power = self.resource_dict['powerproduced']
            self.map.max_power += self.max_power

        self.recruit_cost = self.resource_dict.get('recruitcost', 0)
        if self.produces or self.gathers or self.upkeep:
            action = self.begin_work
            action_dict = {'game': game}
            self.timer = Timer(ONE_SEC, action, action_dict)
            self.status = 'starting production'
        else:
            self.status = None
        self.status_square = None
        self.redraw()
        self.set_tooltip(game)

    def begin_work(self, game):
        if self.upkeep is None or self.can_work():
            if self.status in ['not producing', 'disabled', 'starting production']:
                if self.population > 0:
                    self.map.available_workers += self.population
                if self.max_power > 0:
                    self.map.available_power += self.max_power

            if self.upkeep:
                for key, value in self.upkeep.items():
                    if key == 'workers':
                        self.map.available_workers -= value
                    elif key == 'power':
                        self.map.available_power -= value
                    else:
                        player.adjust_inventory(key, -value)
            action = self.finish_work
            action_dict = {'game': game}
            self.timer = Timer(self.frequency, action, action_dict)
            self.status = 'producing'
        else:
            if self.status == 'producing':
                self.map.available_workers -= self.population
                self.map.available_power -= self.max_power
            action = self.begin_work
            action_dict = {'game': game}
            self.timer = Timer(self.frequency, action, action_dict)
            self.status = 'not producing'
        self.redraw()
        self.set_tooltip(game)

    def finish_work(self, game):
        if self.upkeep:
            if 'workers' in self.upkeep:
                self.map.available_workers += self.upkeep['workers']
            if 'power' in self.upkeep:
                self.map.available_power += self.upkeep['power']
        if self.upkeep is None or self.can_work():
            self.status = 'producing'
            if self.produces:
                for key, value in self.produces.items():
                    player.adjust_inventory(key, value)

            worked = False
            if self.gathers:
                for y in range(self.work_radius*2+1):
                    for x in range(self.work_radius*2+1):
                        grid_y = self.grid_y + y - self.work_radius
                        grid_x = self.grid_x + x - self.work_radius
                        if 8 >= grid_y >= 0 and 8 >= grid_x >= 0:
                            if ((self.map.tiles[grid_y][grid_x].resource in self.gathers
                                 and self.map.tiles[grid_y][grid_x].status != 'mined')):
                                worked = self.map.tiles[grid_y][grid_x].resource
                                self.map.tiles[grid_y][grid_x].begin_mine(game, manual=False)
                                break
                    if worked:
                        break

            if self.upkeep:
                for key, value in self.upkeep.items():
                    if key == 'workers':
                        self.map.available_workers -= self.upkeep['workers']
                    elif key == 'power':
                        self.map.available_power -= self.upkeep['power']
                    else:
                        player.adjust_inventory(key, -value)
            ticks = self.frequency
            if worked:
                if worked in player.rates:
                    rate = player.rates[worked]
                else:
                    rate = 1
                ticks = int(RESOURCES[worked]['minetime']*rate)
            action = self.finish_work
            action_dict = {'game': game}
            self.timer = Timer(ticks, action, action_dict)
        else:
            if self.status == 'producing':
                self.map.available_workers -= self.population
                self.map.available_power -= self.max_power
            action = self.begin_work
            action_dict = {'game': game}
            self.timer = Timer(self.frequency, action, action_dict)
            self.status = 'not producing'
        self.redraw()
        self.set_tooltip(game)

    def can_work(self):
        will_work = True
        if self.upkeep:
            for key, value in self.upkeep.items():
                if key == 'workers':
                    if self.map.available_workers < value:
                        will_work = False
                elif key == 'power':
                    if self.map.available_power < value:
                        will_work = False
                else:
                    if player.inventory[key] < value:
                        will_work = False
        return will_work

    def minable(self):
        is_minable = True
        if self.mine_costs:
            for key, value in self.mine_costs.items():
                if player.inventory[key] < value:
                    is_minable = False
        return is_minable

    def begin_mine(self, game, manual=True):
        if self.beds > 0:
            self.map.beds -= self.beds
            self.beds = 0
            self.recruit_cost = 0
        if self.status == 'producing':
            if self.upkeep:
                self.map.available_workers += self.upkeep.get('workers', 0)
                self.map.available_power += self.upkeep.get('power', 0)
            self.map.available_workers -= self.population
            if self.max_power > 0:
                self.map.max_power -= self.max_power
                self.map.available_power -= self.max_power
                self.max_power = 0

        if self.population > 0:
            self.map.population -= self.population
            self.population = 0
        if not manual or self.minable():
            self.status = 'mined'
            if manual:
                for key, value in self.mine_costs.items():
                    player.adjust_inventory(key, -value)
            action = self.finish_mine
            action_dict = {'game': game}
            if self.resource in player.rates:
                rate = player.rates[self.resource]
            else:
                rate = 1
            ticks = int(RESOURCES[self.resource]['minetime']*rate)
            self.timer = Timer(ticks, action, action_dict)
            self.status_square = StatusSquare(self.w, self.h, WHITE)
            self.redraw()

    def finish_mine(self, game):
        for key, value in game.buffedgives(self.resource).items():
            player.adjust_inventory(key, value)
            text = '{:,}'.format(value)+' '+get_name(key, value, False)+' added'
            log.add_line(TextLine(text))
        self.resource = None
        self.resource_dict = None
        self.mine_costs = None
        self.produces = None
        self.gathers = None
        self.frequency = None
        self.upkeep = None
        self.work_radius = None
        self.symbol = None
        self.image = None
        self.status = None
        self.status_square = None
        self.timer = None
        self.redraw()
        self.set_tooltip(game)

    def disable(self, game):
        if self.status == 'producing':
            if self.upkeep:
                self.map.available_workers += self.upkeep.get('workers', 0)
                self.map.available_power += self.upkeep.get('power', 0)
            self.map.available_workers -= self.population
            self.map.available_power -= self.max_power

        self.status = 'disabled'
        self.status_square = None
        self.timer = None
        self.redraw()
        self.set_tooltip(game)

    def enable(self, game):
        action = self.begin_work
        action_dict = {'game': game}
        self.timer = Timer(self.frequency, action, action_dict)
        self.status = 'not producing'
        self.redraw()
        self.set_tooltip(game)

    def set_tooltip(self, game):
        text_list = [TextLine(TILE_INFO[self.type]['name'] + ' tile')]
        if self.resource is not None:
            text_list.append(TextLine(''))
            text_list.append(TextLine('Has ' + ITEMS[self.resource]['lower']))
            text_list.append(TextLine(''))
            text_list.append(TextLine('Gives:'))
            for key, value in game.buffedgives(self.resource).items():
                text = '  ' + ITEMS[key]['i_cap'] + ' (' + '{:,}'.format(value) + ')'
                text_list.append(TextLine(text))
            if self.mine_costs is not None:
                text_list.append(TextLine(''))
                text_list.append(TextLine('Costs (to mine):'))
                for key, value in self.mine_costs.items():
                    text = ('  '+'{:,}'.format(value)+' '+ITEMS[key]['lower']+
                            ' ('+'{:,}'.format(player.inventory[key])+')')
                    if self.mine_costs[key] <= player.inventory[key]:
                        text_list.append(TextLine(text))
                    else:
                        text_list.append(TextLine(text, GREY))
            if self.timer is not None:
                text_list.append(TextLine(''))
                text_list.append(TextLine('Done in:'))
                time_str = str(int(self.timer.value/ONE_SEC))
                text = '  '+time_str+' seconds'
                text_list.append(TextLine(text))
        if self.status is not None:
            text_list.append(TextLine(''))
            text_list.append(TextLine('status: '+self.status))
        text_list.append(TextLine('max_power: '+str(self.max_power)))
        self.tooltip = ToolTip(text_list, BLACK)

    def doclick(self, event, game):
        if event.button == 1:
            if self.mine_costs:
                for key, value in self.mine_costs.items():
                    if key == 'energy' and player.inventory[key] < value:
                        if game.energy_bar_flash:
                            game.energy_bar_flash = False
                        else:
                            game.energy_bar_flash = True
                            game.timers.append(Timer(5, game.unflash_energy_bar, {}))
            if self.resource and self.status not in ['mined', 'building'] and self.minable():
                if RESOURCES[self.resource].get('confirmdestroy', False):
                    if do_confirm_popup(['Are you sure you want', 'to destroy this '+self.resource+'?']):
                        self.begin_mine(game)
                else:
                    self.begin_mine(game)
        elif event.button == 3:
            if self.resource and self.resource in BUILDABLES:
                menu_items = []
                can_recruit = False
                can_destroy = False
                if self.resource == 'house':
                    if (self.beds > self.population
                        and RESOURCES[self.resource].get('recruitcost', 0) <= player.inventory['coins']):
                        color1 = BLACK
                        can_recruit = True
                    else:
                        color1 = GREY
                    if self.resource and self.status not in ['mined', 'building'] and self.minable():
                        color2 = BLACK
                        can_destroy = True
                    else:
                        color2 = GREY
                    menu_items.append(TextLine('Recruit worker ('+str(self.recruit_cost)+' Coins)',
                                               color1, return_val='recruit'))
                    menu_items.append(TextLine('Destroy ', color2, return_val='destroy'))
                if self.status != 'disabled':
                    menu_items.append(TextLine('Disable ', return_val='disable'))
                else:
                    menu_items.append(TextLine('Enable ', return_val='enable'))
                # Make all choice rects extend to end of menu so you don't have to click the text
                max_width = max(item.rect.w for item in menu_items)
                for item in menu_items:
                    item.rect.w = max_width
                selection = None
                menuw = 0
                menuh = 0
                for item in menu_items:
                    item.rect.topleft = (1, menuh)
                    menuw = max(menuw, item.rect.w + 2)  # pixel buffer of 1 on each side
                    menuh += item.rect.h
                greyout = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
                greyout.fill(WHITE)
                greyout.set_alpha(150)
                gameDisplay.blit(greyout, (0, 0))
                mouse = pygame.mouse.get_pos()
                game_mouse = get_rel_mouse(mouse, gameDisplay)
                menu = gameDisplay.subsurface((game_mouse[0], game_mouse[1], menuw, menuh))
                menu.fill(WHITE)
                pygame.draw.rect(menu, BLACK, menu.get_rect(), 1)
                for item in menu_items:
                    menu.blit(item.surf, item.rect)
                pygame.display.flip()
                in_menu = True
                while in_menu:
                    mouse = pygame.mouse.get_pos()
                    menu_mouse = get_rel_mouse(mouse, menu)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            quit()
                        if event.type == pygame.MOUSEBUTTONUP:
                            for item in menu_items:
                                if item.rect.collidepoint(menu_mouse):
                                    selection = item.return_val
                            in_menu = False
                if selection == 'recruit' and can_recruit:
                    self.map.population += 1
                    if self.status == 'producing':
                        self.map.available_workers += 1
                    self.population += 1
                    player.adjust_inventory('coins', -RESOURCES[self.resource].get('recruitcost', 0))
                elif selection == 'destroy' and can_destroy:
                    if self.resource and self.status not in ['mined', 'building'] and self.minable():
                        if RESOURCES[self.resource].get('confirmdestroy', False):
                            if do_confirm_popup(
                                    ['Are you sure you want', 'to destroy this ' + self.resource + '?']):
                                self.begin_mine(game)
                        else:
                            self.begin_mine(game)
                elif selection == 'enable':
                    self.enable(game)
                elif selection == 'disable':
                    self.disable(game)
            elif not self.resource:
                self.spawn(game, force=True)
            self.redraw()
            self.set_tooltip(game)

    def check_mouseover(self, mouse):
        if ((self.x + self.w > mouse[0] > self.x
             and self.y + self.h > mouse[1] > self.y)):
            return True

    def get_rect(self):
        return [self.x, self.y, self.w, self.h]

    def redraw(self):
        bg_color = self.color
        if self.status == 'disabled':
            bg_color = RED
        pygame.draw.rect(self.surf, bg_color, (self.surf.get_rect()))
        if self.resource:
            if self.symbol:
                self.text_surf, self.text_rect = text_objects(self.symbol, FONTS['45'])
                self.text_rect.center = self.surf.get_rect().center
                self.surf.blit(self.text_surf, self.text_rect)
            elif self.image:
                self.surf.blit(self.image, (0, 0))
            if self.beds == 4:
                pygame.draw.circle(self.surf, BLACK, (8, TILE_HEIGHT-7), 5, min(1, max(0, 1-self.population)))
                pygame.draw.circle(self.surf, BLACK, (19, TILE_HEIGHT-7), 5, min(1, max(0, 2-self.population)))
                pygame.draw.circle(self.surf, BLACK, (31, TILE_HEIGHT-7), 5, min(1, max(0, 3-self.population)))
                pygame.draw.circle(self.surf, BLACK, (42, TILE_HEIGHT-7), 5, min(1, max(0, 4-self.population)))
        if self.status_square is not None:
            self.surf.blit(self.status_square.surf, self.surf.get_rect())
        pygame.draw.rect(self.surf, BLACK, self.surf.get_rect(), 1)

    def draw(self, surface):
        surface.blit(self.surf, self.get_rect())


class Map(object):
    def __init__(self, tilemap, game):
        self.tiles = [[None]*MAP_SIZE for _ in range(MAP_SIZE)]
        self.res_count = 0
        self.beds = 0
        self.population = 0
        self.available_workers = 0
        self.max_power = 0
        self.available_power = 0
        for y, row in enumerate(tilemap):
            for x, col in enumerate(row):
                if col != '0':
                    self.tiles[y][x] = Tile(x, y, self, col)
        for i in range(10):
            self.rand_spawn(game)
        self.surf = pygame.Surface((MAP_SIZE*TILE_WIDTH, MAP_SIZE*TILE_WIDTH))
        self.make_surf()
        self.make_thumb()
        self.make_tooltip()

    def rand_spawn(self, game):
        i = 0
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.tiles[y][x].resource:
                    i += 1
        self.res_count = i
        if self.res_count < 40:
            spawned = False
            while not spawned:
                y = random.randint(0, MAP_SIZE-1)
                x = random.randint(0, MAP_SIZE-1)
                if self.tiles[y][x].resource is None:
                    spawned = True
                    self.tiles[y][x].spawn(game)

    def make_surf(self):
        self.surf.fill(WHITE)
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                self.tiles[y][x].draw(self.surf)

    def make_thumb(self):
        self.thumb = pygame.transform.smoothscale(self.surf, (TILE_WIDTH, TILE_HEIGHT))

    def make_tooltip(self):
        pop_str = '/'.join(('{:,}'.format(self.available_workers),
                            '{:,}'.format(self.population),
                            '{:,}'.format(self.beds)))
        pow_str = '/'.join(('{:,}'.format(self.available_power),
                            '{:,}'.format(self.max_power)))
        tool_list = []
        tool_list.append(TextLine('Population: '+pop_str))
        tool_list.append(TextLine('  (avail./total/max)'))
        tool_list.append(TextLine(''))
        tool_list.append(TextLine('Power: '+pow_str))
        tool_list.append(TextLine('  (avail./max)'))
        tool_list.append(TextLine(''))
        tool_list.append(TextLine('contains: '))
        tool_list.append(TextLine(''))
        resource_count = defaultdict(int)
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.tiles[y][x].resource:
                    resource_count[self.tiles[y][x].resource] += 1
        for res in RESOURCES:
            if res in resource_count:
                tool_list.append(TextLine(ITEMS[res]['i_cap']+': '+str(resource_count[res])))

        self.tooltip = ToolTip(tool_list, BLACK)


class Timer(object):
    def __init__(self, ticks, action, kwargs, repeat=False):
        self.ticks = ticks
        self.value = ticks
        self.action = action
        self.kwargs = kwargs
        self.repeat = repeat
        self.done = False

    def tick(self):
        self.value -= 1
        if self.value == 0:
            self.action(**self.kwargs)
            if self.repeat:
                self.value = self.ticks
            else:
                self.done = True
                return 'done'


class Button(object):
    def __init__(self, w, h, string=None, font_color=BLACK, font='medium', bg_color=WHITE):
        self.surf = pygame.Surface((w, h))
        self.string = string
        self.font_color = font_color
        self.font = FONTS[font]
        self.bg_color = bg_color
        self.rect = self.surf.get_rect()
        self.tooltip = None
        self.make()
        self.tags = []

    def make(self):
        self.surf.fill(self.bg_color)
        pygame.draw.rect(self.surf, BLACK, self.rect, 1)
        text_surf, text_rect = text_objects(self.string, self.font, self.font_color)
        text_rect.center = (self.surf.get_rect().centerx, self.surf.get_rect().centery+2)
        self.surf.blit(text_surf, text_rect)


class BuyMap(object):
    def __init__(self, cost):
        self.cost = cost
        self.make_surf()

    def make_surf(self):
        self.surf = pygame.Surface((TILE_WIDTH, TILE_HEIGHT))
        self.surf.fill(GREY)
        lines = [((1, 1), (TILE_WIDTH/4, 1)),
                 ((3*TILE_WIDTH/4, 1), (TILE_WIDTH-2, 1)),
                 ((TILE_WIDTH-2, 1), (TILE_WIDTH-2, TILE_HEIGHT/4)),
                 ((TILE_WIDTH-2, 3*TILE_HEIGHT/4), (TILE_WIDTH-2, TILE_HEIGHT-2)),
                 ((TILE_WIDTH-2, TILE_HEIGHT-2), (3*TILE_WIDTH/4, TILE_HEIGHT-2)),
                 ((TILE_WIDTH/4, TILE_HEIGHT-2), (1, TILE_HEIGHT-2)),
                 ((1, TILE_HEIGHT-2), (1, 3*TILE_HEIGHT/4)),
                 ((1, TILE_HEIGHT/4), (1, 1))]
        for pair in lines:
            pygame.draw.line(self.surf, BLACK, pair[0], pair[1], 1)

        text_surface = FONTS['20'].render('BUY', True, BLACK)
        text_rect = text_surface.get_rect(center=self.surf.get_rect().center)
        text_rect.bottom = (TILE_HEIGHT/2)-2
        self.surf.blit(text_surface, text_rect)

    def draw(self, surf, pos, cash_available):
        surf.blit(self.surf, pos)
        if cash_available >= self.cost:
            text_surface = FONTS['20'].render('{:,}'.format(self.cost)+' C', True, BLACK)
        else:
            text_surface = FONTS['20'].render('{:,}'.format(self.cost)+' C', True, WHITE)
        text_rect = text_surface.get_rect(center=self.surf.get_rect().center)
        text_rect.top = (TILE_HEIGHT/2)+2
        relpos = (text_rect.left + pos[0], text_rect.top + pos[1])
        surf.blit(text_surface, relpos)


class Perk(object):
    def __init__(self, id, game, **kwargs):
        self.id = id
        self.name = kwargs.get('name', None)
        self.cost = kwargs.get('cost', None)
        self.description = kwargs.get('description', None)
        self.dependencies = kwargs.get('dependencies', None)
        self.pos = kwargs.get('pos', None)
        self.bonuses = kwargs.get('bonuses', None)
        self.status = 'unavailable'
        self.update_status()
        self.make_surf()
        self.rect = self.surf.get_rect(topleft=(PERK_OFFSET+self.pos[0]*(PERK_DIST+PERK_WIDTH),
                                                PERK_OFFSET+self.pos[1]*(PERK_DIST+PERK_HEIGHT)))
        self.set_tooltip(game)

    def update_status(self):
        if self.status != 'purchased':
            if self.id in player.perks:
                self.status = 'purchased'
            elif self.dependencies is None or set(self.dependencies).issubset(player.perks):
                self.status = 'available'

    def do_click(self, game):
        if self.status == 'available' and player.inventory['coins'] >= self.cost:
            self.status = 'purchased'
            player.adjust_inventory('coins', -self.cost)
            player.perks.append(self.id)
            player.get_perk(self.id, game)
            self.update_status()

    def make_surf(self):
        self.surf = pygame.Surface((PERK_WIDTH, PERK_HEIGHT))
        self.surf.fill(WHITE)

        if self.status == 'purchased':
            self.surf.fill(LIGHTGREEN)
            bold_rect = self.surf.get_rect()
            bold_rect.w -= 1
            bold_rect.h -= 1
            pygame.draw.rect(self.surf, BLACK, bold_rect, 2)
            text_surface = FONTS['20'].render(self.name, True, BLACK)
        elif self.status == 'available':
            pygame.draw.rect(self.surf, BLACK, self.surf.get_rect(), 1)
            text_surface = FONTS['20'].render(self.name, True, BLACK)
        else:
            pygame.draw.rect(self.surf, GREY, self.surf.get_rect(), 1)
            text_surface = FONTS['20'].render(self.name, True, GREY)
        text_rect = text_surface.get_rect(center=self.surf.get_rect().center)
        text_rect.bottom = (PERK_HEIGHT/2)-2
        self.surf.blit(text_surface, text_rect)

    def draw(self, surface):
        surface.blit(self.surf, self.rect)

    def set_tooltip(self, game):
        self.tooltip = None
        text_list = []
        for text in self.description:
            text_list.append(TextLine(text))
        if self.status != 'purchased':
            text_list.append(TextLine(''))
            text_list.append(TextLine('Costs:'))
            cost_str = '  '+'{:,}'.format(self.cost)+' '+'coins'
            if player.inventory['coins'] >= self.cost:
                text_list.append(TextLine(cost_str))
            else:
                text_list.append(TextLine(cost_str, GREY))
        text_list.append(TextLine(''))
        if self.status == 'purchased':
            text_color = DARKGREEN
        elif self.status == 'available':
            text_color = BLACK
        else:
            text_color = RED
        text_list.append(TextLine(self.status, text_color))

        self.tooltip = ToolTip(text_list, BLACK)


def get_name(item, num, cap):
    if num == 1 or num == -1:
        if cap:
            return ITEMS[item]['i_cap']
        else:
            return ITEMS[item]['lower']
    else:
        if cap:
            return ITEMS[item]['plural_i_cap']
        else:
            return ITEMS[item]['plural']


def get_sell_val(item):
    return ITEMS[item]['sell_value']


def get_map_cost(grid_pos):
    if 0 <= grid_pos[0] <= 8 and 0 <= grid_pos[1] <= 8:
        x = abs(grid_pos[0]-4)
        y = abs(grid_pos[1]-4)
        radius = max(x, y)
        cost = MAP_COSTS[radius]
        return cost
    else:
        return 0


def do_confirm_popup(texts):
    question_texts = [TextLine(text) for text in texts]
    menuw = 200
    menuh = 50
    for qtext in question_texts:
        menuw = max(menuw, qtext.rect.w+(2*25))  # pixel buffer of 25 on each side
        menuh += qtext.rect.h
    greyout = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    greyout.fill(WHITE)
    greyout.set_alpha(150)
    gameDisplay.blit(greyout, (0, 0))
    confirm_button = Button(75, 25, 'Confirm')
    cancel_button = Button(75, 25, 'Cancel')
    buttony = menuh - 25 - 10
    confirm_button.rect.centerx = int(menuw//4)
    confirm_button.rect.top = buttony
    cancel_button.rect.centerx = int(menuw*3//4)
    cancel_button.rect.top = buttony
    menu = gameArea.subsurface(((GAME_WIDTH-menuw)/2, (GAME_HEIGHT-menuh)/2, menuw, menuh))
    menu.fill(WHITE)
    pygame.draw.rect(menu, BLACK, menu.get_rect(), 1)
    i = 0
    for qtext in question_texts:
        menu.blit(qtext.surf, (25, 10+i))
        i += qtext.rect.h
    menu.blit(confirm_button.surf, confirm_button.rect)
    menu.blit(cancel_button.surf, cancel_button.rect)
    pygame.display.flip()
    while True:
        mouse = pygame.mouse.get_pos()
        game_mouse = get_rel_mouse(mouse, menu)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONUP:
                if confirm_button.rect.collidepoint(game_mouse):
                    return True
                if cancel_button.rect.collidepoint(game_mouse):
                    return False


def all_maps_spawn(maps, game):
    for row in maps:
        for map in row:
            if type(map) is Map:
                map.rand_spawn(game)


def draw_line(surf, pos1, pos2):
    pygame.draw.line(surf, BLACK, pos1, pos2, 2)


def page_select_surf(pages, cur_page, text_surfaces, page_select_rect):
    page_index = pages.index(cur_page)
    w_extra = DISPLAY_WIDTH-GAME_OFFSET[0]-GAME_WIDTH-10-page_select_rect.w-10
    pages_surf = pygame.Surface((page_select_rect.w + w_extra, page_select_rect.h + 7))
    pages_surf.fill(WHITE)
    for txtsurf in text_surfaces:
        pages_surf.blit(txtsurf.surf, (txtsurf.rect.x, txtsurf.rect.y + 4))
    t = text_surfaces
    btm = t[0].rect.bottom + 5
    top = t[0].rect.top
    y = (btm + top) / 2
    last = len(pages) - 1

    draw_line(pages_surf, (t[0].rect.left - 30, btm), (t[0].rect.left, top))
    for i in range(last):
        draw_line(pages_surf, (t[i].rect.left, top), (t[i].rect.right, top))
        draw_line(pages_surf, (t[i].rect.right, top), (t[i].rect.right + 15, y))
        draw_line(pages_surf, (t[i].rect.right + 15, y), (t[i].rect.right + 30, top))
    draw_line(pages_surf, (t[last].rect.left, top), (t[last].rect.right, top))
    draw_line(pages_surf, (t[last].rect.right, top), (t[last].rect.right + 30, btm))

    for i in range(len(pages)):
        if page_index == i:
            draw_line(pages_surf, (t[0].rect.left - 45, btm), (t[i].rect.left - 30, btm))
            draw_line(pages_surf, (t[i].rect.right + 30, btm), (t[last].rect.right + w_extra, btm))

    for i in range(last):
        if page_index == i + 1:
            draw_line(pages_surf, (t[i].rect.right, btm), (t[i].rect.right + 15, y))
        else:
            draw_line(pages_surf, (t[i].rect.right + 15, y), (t[i+1].rect.left, btm))

    return pages_surf


def do_crafting_popup(item):
    greyout = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    greyout.fill(WHITE)
    greyout.set_alpha(150)
    gameDisplay.blit(greyout, (0, 0))
    menu = gameDisplay.subsurface((700, 100, 450, 450))
    max_craftable = 0
    first = True
    for key, value in player.recipes[item]['costs'].items():
        if first:
            max_craftable = player.inventory[key]//value
            first = False
        else:
            max_craftable = min(max_craftable, player.inventory[key]//value)

    bar = StatusBar(menu, 50, 50, 350, 50, GREEN, WHITE, BLACK, max_craftable)
    in_menu = True
    while in_menu:
        menu.fill(WHITE)
        xrect = pygame.Rect(425, 5, 20, 20)
        pygame.draw.rect(menu, BLACK, menu.get_rect(), 1)

        # draw X for closing menu
        pygame.draw.line(menu, BLACK, (425, 5), (445, 25), 2)
        pygame.draw.line(menu, BLACK, (425, 25), (445, 5), 2)

        mouse = pygame.mouse.get_pos()
        relmouse = get_rel_mouse(mouse, menu)
        craft_portion = min(max(0, (relmouse[0] - 50)/350), 1)
        craft_num = int(round(bar.maximum * craft_portion, 0))
        bar.val = craft_num
        bar.draw()
        craft_result_num = craft_num*player.recipes[item]['gives'][item]
        craft_text = 'Gives: '+'{:,}'.format(craft_result_num)+' '+get_name(item, craft_result_num, False)
        menu.blit(FONTS['medium'].render(craft_text, True, BLACK), (25, 10))
        menu.blit(FONTS['medium'].render('Cost:', True, BLACK), (25, 125))
        i = 0
        for key, value in player.recipes[item]['costs'].items():
            craft_num_str = '{:,}'.format(value*craft_num)
            inv_num_str = '{:,}'.format(player.inventory[key])
            tmp_str = ITEMS[key]['i_cap']+': '+craft_num_str+' ('+inv_num_str+')'
            tmp_text = FONTS['medium'].render(tmp_str, True, BLACK)
            menu.blit(tmp_text, (50, 150 + i))
            i += tmp_text.get_height()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONUP:
                if bar.collidepoint(relmouse):
                    player.craft(item, craft_num)
                    in_menu = False
                if xrect.collidepoint(relmouse):
                    in_menu = False

        pygame.display.flip()


def do_build_popup(item, cur_map, game):
    gamecopy = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    gamecopy.blit(gameDisplay, (0, 0))
    greyout = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    greyout.fill(WHITE)
    greyout.set_alpha(150)
    menu = gameDisplay.subsurface((700, 100, 450, 450))
    target_tile = pygame.Surface((TILE_WIDTH, TILE_HEIGHT))
    target_tile.set_alpha(150)
    in_menu = True
    while in_menu:
        gameDisplay.blit(gamecopy, (0, 0))
        gameDisplay.blit(greyout, (0, 0))
        menu.fill(WHITE)
        xrect = pygame.Rect(425, 5, 20, 20)
        pygame.draw.rect(menu, BLACK, menu.get_rect(), 1)

        # draw X for closing menu
        pygame.draw.line(menu, BLACK, (425, 5), (445, 25), 2)
        pygame.draw.line(menu, BLACK, (425, 25), (445, 5), 2)

        mouse = pygame.mouse.get_pos()
        map_mouse = get_rel_mouse(mouse, mapArea)
        menu_mouse = get_rel_mouse(mouse, menu)
        menu.blit(FONTS['medium'].render('Choose where to build a '+item, True, BLACK), (25, 10))
        menu.blit(FONTS['medium'].render('by clicking on the tile on the left.', True, BLACK), (25, 30))
        menu.blit(FONTS['medium'].render('Build: '+ITEMS[item]['lower'], True, BLACK), (50, 85))
        menu.blit(FONTS['medium'].render('Cost:', True, BLACK), (50, 115))
        i = 0
        for key, value in player.buildables[item]['buildcosts'].items():
            bld_num_str = '{:,}'.format(value)
            inv_num_str = '{:,}'.format(player.inventory[key])
            tmp_str = ITEMS[key]['i_cap']+': '+bld_num_str+' ('+inv_num_str+')'
            tmp_text = FONTS['medium'].render(tmp_str, True, BLACK)
            menu.blit(tmp_text, (100, 140 + i))
            i += tmp_text.get_height()
        xgrid = int(map_mouse[0]//TILE_WIDTH)
        ygrid = int(map_mouse[1]//TILE_HEIGHT)
        can_build = False
        if 0 <= xgrid < MAP_SIZE and 0 <= ygrid < MAP_SIZE:
            tile = cur_map.tiles[ygrid][xgrid]
            if tile.type in player.buildables[item]['canbuild'] and tile.resource is None:
                target_tile.fill(GREEN)
                can_build = True
            else:
                target_tile.fill(RED)
            if RESOURCES[item].get('workradius', 0) > 0:
                draw_radius_surface((xgrid, ygrid), RESOURCES[item]['workradius'])
            mapArea.blit(target_tile, tile.topleft)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONUP:
                if can_build:
                    tile.begin_build(item, game)
                    in_menu = False
                if xrect.collidepoint(menu_mouse):
                    in_menu = False

        pygame.display.flip()


def do_using_popup(item):
    greyout = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    greyout.fill(WHITE)
    greyout.set_alpha(150)
    gameDisplay.blit(greyout, (0, 0))
    menu = gameDisplay.subsurface((700, 100, 450, 450))
    maxusable = 0
    if 'energy' in player.usables[item]['gives']:
        maxusable = int(math.ceil(((player.max_energy-player.inventory['energy']) /
                                   player.usables[item]['gives']['energy'])))
    for key, value in player.usables[item]['costs'].items():
        if maxusable == 0:
            maxusable = player.inventory[key]//value
        else:
            maxusable = min(maxusable, player.inventory[key]//value)

    bar = StatusBar(menu, 50, 50, 350, 50, GREEN, WHITE, BLACK, maxusable)
    in_menu = True
    while in_menu:
        menu.fill(WHITE)
        xrect = pygame.Rect(425, 5, 20, 20)
        pygame.draw.rect(menu, BLACK, menu.get_rect(), 1)

        # draw X for closing menu
        pygame.draw.line(menu, BLACK, (425, 5), (445, 25), 2)
        pygame.draw.line(menu, BLACK, (425, 25), (445, 5), 2)

        mouse = pygame.mouse.get_pos()
        relmouse = get_rel_mouse(mouse, menu)
        use_portion = min(max(0, (relmouse[0] - 50)/350), 1)
        use_number = int(round(bar.maximum * use_portion, 0))
        bar.val = use_number
        bar.draw()
        menu.blit(FONTS['medium'].render('Use: '+'{:,}'.format(use_number)+' '+get_name(item, use_number, False),
                                         True, BLACK), (25, 10))
        menu.blit(FONTS['medium'].render('Gives:', True, BLACK), (25, 125))
        i = 0
        for key, value in player.usables[item]['gives'].items():
            tmpstr = ITEMS[key]['i_cap']+': '+'{:,}'.format(value*use_number)
            tmptext = FONTS['medium'].render(tmpstr, True, BLACK)
            menu.blit(tmptext, (50, 150 + i))
            i += tmptext.get_height()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONUP:
                if bar.collidepoint(relmouse):
                    player.use(item, use_number)
                    in_menu = False
                if xrect.collidepoint(relmouse):
                    in_menu = False

        pygame.display.flip()


def get_recipe_surfs():
    i = 100
    recipe_surfaces = []
    for key, value in player.recipes.items():
        color = BLACK
        if not player.craftable(key):
            color = GREY
        textline = TextLine(ITEMS[key]['i_cap'], color)
        tooltip_textlines = []
        tooltip_textlines.append(TextLine('Makes:'))
        for thing, amt in player.recipes[key]['gives'].items():
            tooltip_textlines.append(TextLine('  '+ITEMS[thing]['i_cap']+' ('+'{:,}'.format(amt)+')'))
        tooltip_textlines.append(TextLine(''))
        tooltip_textlines.append(TextLine('Costs:'))
        for thing, amt in player.recipes[key]['costs'].items():
            text = '  '+ITEMS[thing]['i_cap']+': '+'{:,}'.format(amt)+' ('+'{:,}'.format(player.inventory[thing])+')'
            if player.inventory[thing] < amt:
                tooltip_textlines.append(TextLine(text, GREY))
            else:
                tooltip_textlines.append(TextLine(text))
        textline.tooltip = ToolTip(tooltip_textlines, BLACK)
        recipe_surfaces.append(textline)
        textline.string = key
        textline.rect.x = GAME_WIDTH + 100
        textline.rect.y = i
        i += textline.rect.h + 5
    return recipe_surfaces


def get_build_surfs():
    i = 100
    build_surfaces = []
    for key, value in player.buildables.items():
        color = BLACK
        if not player.buildable(key):
            color = GREY
        textline = TextLine(ITEMS[key]['i_cap'], color)
        tooltip_textlines = []
        tooltip_textlines.append(TextLine('Description:'))
        for desc_line in player.buildables[key]['description']:
            tooltip_textlines.append(TextLine('  '+desc_line))
        tooltip_textlines.append(TextLine(''))
        tooltip_textlines.append(TextLine('Costs:'))
        for thing, amt in player.buildables[key]['buildcosts'].items():
            text = '  '+ITEMS[thing]['i_cap']+': '+'{:,}'.format(amt)+' ('+'{:,}'.format(player.inventory[thing])+')'
            if player.inventory[thing] < amt:
                tooltip_textlines.append(TextLine(text, GREY))
            else:
                tooltip_textlines.append(TextLine(text))
        tooltip = ToolTip(tooltip_textlines, BLACK)
        textline.tooltip = tooltip
        build_surfaces.append(textline)
        textline.string = key
        textline.rect.x = GAME_WIDTH + 100
        textline.rect.y = i
        i += textline.rect.h + 5
    return build_surfaces


def get_usables_surfs():
    i = 100
    usables_surfaces = []
    for key, value in player.usables.items():
        if key in player.known_items:
            color = BLACK
            if not player.usable(key):
                color = GREY
            count = '{:,}'.format(player.inventory[key])
            textline = TextLine(ITEMS[key]['i_cap']+' ('+count+')', color)
            tooltip_textlines = []
            tooltip_textlines.append(TextLine('Gives:'))
            for thing1, amt in player.usables[key]['gives'].items():
                tooltip_textlines.append(TextLine('  '+ITEMS[thing1]['i_cap']+' ('+'{:,}'.format(amt)+')'))
            tooltip_textlines.append(TextLine('Costs:'))
            for thing2, amt in player.usables[key]['costs'].items():
                text = ('  '+ITEMS[thing2]['i_cap']+': '+'{:,}'.format(amt)+' ('+
                        '{:,}'.format(player.inventory[thing2])+')')
                if player.inventory[thing2] < amt:
                    tooltip_textlines.append(TextLine(text, GREY))
                else:
                    tooltip_textlines.append(TextLine(text))
            tooltip = ToolTip(tooltip_textlines, BLACK)
            textline.tooltip = tooltip
            usables_surfaces.append(textline)
            textline.string = key
            textline.rect.x = GAME_WIDTH + 100
            textline.rect.y = i
            i += textline.rect.h + 5
    return usables_surfaces


def get_sell_buttons(game):
    sell_buttons = []
    height = FONTS['medium'].render('10', True, BLACK).get_height()
    i = 100
    for key, value in player.inventory.items():
        if key not in game.exclude and key in player.known_items:
            if value > 0:
                button1 = Button(11, height-1, '1')
                button1.tags.append(key)
                button1.rect = button1.surf.get_rect(topleft=(GAME_WIDTH + 475, i))
                sell_buttons.append(button1)
            if value > 9:
                button2 = Button(21, height-1, '10')
                button2.tags.append(key)
                button2.rect = button2.surf.get_rect(topleft=(GAME_WIDTH + 496, i))
                sell_buttons.append(button2)
            if value > 99:
                button3 = Button(31, height-1, '100')
                button3.tags.append(key)
                button3.rect = button3.surf.get_rect(topleft=(GAME_WIDTH + 527, i))
                sell_buttons.append(button3)
            i += height
    return sell_buttons


def make_perk_surf(surface, game_perks):
    surface.fill(WHITE)
    '''Draw lines to show dependencies'''
    for perk in game_perks:
        if perk.dependencies is not None:
            x1 = (PERK_OFFSET+PERK_WIDTH/2)+perk.pos[0]*(PERK_WIDTH+PERK_DIST)
            y1 = (PERK_OFFSET+PERK_HEIGHT/2)+perk.pos[1]*(PERK_HEIGHT+PERK_DIST)
            perk_pos = (x1, y1)
            for target in perk.dependencies:
                x2 = (PERK_OFFSET+PERK_WIDTH/2)+PERKS[target]['pos'][0]*(PERK_WIDTH+PERK_DIST)
                y2 = (PERK_OFFSET+PERK_HEIGHT/2)+PERKS[target]['pos'][1]*(PERK_HEIGHT+PERK_DIST)
                target_pos = (x2, y2)
                pygame.draw.line(surface, BLACK, perk_pos, target_pos, 1)
    for perk in game_perks:
        perk.make_surf()
        perk.draw(surface)


def get_rel_mouse(mouse, surface):
    return tuple(map(lambda x, y: x - y, mouse, surface.get_abs_offset()))


def draw_radius_surface(pos, radius):
    if radius != 0:
        xmin = max(0, pos[0]-radius)
        xmax = min(8, pos[0]+radius)
        ymin = max(0, pos[1]-radius)
        ymax = min(8, pos[1]+radius)
        radius_surface = pygame.Surface(((xmax-xmin+1)*TILE_WIDTH, (ymax-ymin+1)*TILE_HEIGHT))
        radius_surface.fill(BLUE)
        radius_surface.set_alpha(50)
        blit_pos = (MAP_OFFSET[0]+GAME_OFFSET[0]+xmin*TILE_WIDTH,
                    MAP_OFFSET[1]+GAME_OFFSET[1]+ymin*TILE_HEIGHT)
        gameDisplay.blit(radius_surface, blit_pos)


one_of_four = pygame.Surface((45, 10))
one_of_four.fill(WHITE)
pygame.draw.circle(one_of_four, BLACK, (9, 5), 4, 0)
pygame.draw.circle(one_of_four, BLACK, (18, 5), 4, 1)
pygame.draw.circle(one_of_four, BLACK, (27, 5), 4, 1)
pygame.draw.circle(one_of_four, BLACK, (36, 5), 4, 1)


class Game(object):
    def __init__(self):
        self.mouse = pygame.mouse.get_pos()
        self.game_mouse = get_rel_mouse(self.mouse, gameArea)
        self.map_mouse = get_rel_mouse(self.mouse, mapArea)
        self.perk_mouse = get_rel_mouse(self.mouse, perkArea)

        self.map_view = False

        self.energy_bar_flash = False
        self.energy_bar = StatusBar(gameDisplay, 200, 15, 100, 20, GREEN, WHITE, BLACK)
        self.energy_bar.maximum = player.max_energy
        self.energy_bar.val = player.inventory['energy']
        self.energy_text = TextLine('Energy:', font='large')
        self.energy_text.rect.x, self.energy_text.rect.y = 50, 6

        self.pages = ['Inventory', 'Use', 'Craft', 'Build', 'Perks']
        self.cur_page = self.pages[0]

        self.exclude = ['energy', 'coins']

        i = 45
        self.page_surfaces = []
        self.page_select_rect = pygame.Rect(0, 0, 1, 1)
        for page in self.pages:
            textline = TextLine(page)
            self.page_surfaces.append(textline)
            textline.rect.x = i
            self.page_select_rect = self.page_select_rect.union(textline)
            i += textline.rect.w + 30

        self.recipe_surfaces = get_recipe_surfs()
        self.usables_surfaces = get_usables_surfs()
        self.build_surfaces = get_build_surfs()
        self.sell_buttons = get_sell_buttons(self)

        self.perks = []
        perk_max_x = 0
        perk_max_y = 0
        perk_grid_y = -1
        last_j = 0
        for perk in PERKS:
            j = int(perk[1])
            k = int(perk[2])
            if j+k != 0 and j == last_j:
                PERKS[perk]['pos'] = (k, perk_grid_y)
            else:
                perk_grid_y += 1
                PERKS[perk]['pos'] = (k, perk_grid_y)
            last_j = j

            self.perks.append(Perk(perk, self, **PERKS[perk]))
            perk_max_x = max(perk_max_x, PERK_OFFSET+(PERKS[perk]['pos'][0]+1)*(PERK_DIST+PERK_WIDTH))
            perk_max_y = max(perk_max_y, PERK_OFFSET+(PERKS[perk]['pos'][1]+1)*(PERK_DIST+PERK_HEIGHT))

        self.perk_window = ScrollWindow((perk_max_x, perk_max_y), (450, 450), WHITE)

        make_perk_surf(self.perk_window.full_surf, self.perks)

        self.page_select_surfs = {}
        for page in self.pages:
            self.page_select_surfs[page] = page_select_surf(self.pages, page, self.page_surfaces, self.page_select_rect)
        self.page_select_surf = self.page_select_surfs[self.pages[0]]

        self.tooltip = None

        player.learn_recipe('stick')
        player.learn_building('animal trap')
        player.adjust_inventory('energy', 100)
        # player.adjust_inventory('wood', 100000)
        # player.adjust_inventory('stick', 100000)
        # player.adjust_inventory('stone', 100000)
        # player.adjust_inventory('ironore', 100000)
        # player.adjust_inventory('goldore', 100000)
        # player.adjust_inventory('iron', 100000)
        # player.adjust_inventory('gold', 100000)
        # player.adjust_inventory('food', 100000)
        # player.adjust_inventory('coins', 100000)

        # dropbuffs = {'res': {'gives':{'thing': 0}...,'minecosts': {'thing': 0}}...}
        self.dropbuffs = {}
        for key1 in RESOURCES:
            self.dropbuffs[key1] = {'minegives': {}, 'minecosts': {}}
            for key2 in RESOURCES[key1]['minegives']:
                self.dropbuffs[key1]['minegives'][key2] = 0
            for key2 in RESOURCES[key1]['minecosts']:
                self.dropbuffs[key1]['minecosts'][key2] = 0

        self.maps = [[None]*MAP_SIZE for _ in range(MAP_SIZE)]
        self.maps[4][4] = BuyMap(0)
        self.buy_map((4, 4))
        self.cur_map = self.maps[4][4]
        self.last_map = {1: None, 2: None}

        self.tracker = 0

        pygame.time.set_timer(GAME_TICK, int(1000//TICKS_PER_SEC))
        self.timers = [
                       Timer(5*ONE_SEC, player.adjust_inventory, {'item': 'energy', 'amt': 1}, True),
                       # Timer(ONE_SEC, player.adjust_inventory, {'item': 'energy', 'amt': 100}, True),
                       Timer(5*ONE_SEC, all_maps_spawn, {'maps': self.maps, 'game': self}, True),
                       Timer(int(ONE_SEC/20), self.update_map_surf, {}, True),
                       Timer(int(ONE_SEC/10), self.update_map_thumbs, {}, True),
                       Timer(ONE_SEC, update_item_history, {}, True)
        ]

    def unflash_energy_bar(self):
        self.energy_bar_flash = False

    def buffedgives(self, res):
        gives = {}
        for key, value in RESOURCES[res]['minegives'].items():
            gives[key] = int(value*(1+self.dropbuffs[res]['minegives'][key]))
        return gives

    def update_map_surf(self):
        self.cur_map.make_surf()

    def update_map_thumbs(self):
        if self.map_view:
            for y, row in enumerate(self.maps):
                for x, map in enumerate(row):
                    if type(map) is Map and x == self.tracker:
                        map.make_surf()
                        map.make_thumb()
                        map.make_tooltip()
            self.tracker += 1
            if self.tracker == 9:
                self.tracker = 0

    def force_update_map_thumbs(self):
        for y, row in enumerate(self.maps):
                for x, map in enumerate(row):
                    if type(map) is Map:
                        map.make_surf()
                        map.make_thumb()
                        map.make_tooltip()

    def buy_map(self, grid_pos):
        map = self.maps[grid_pos[1]][grid_pos[0]]
        x = abs(grid_pos[0] - 4)
        y = abs(grid_pos[1] - 4)
        radius = max(x, y)
        adjacent_maps = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        if type(map) is BuyMap:
            player.adjust_inventory('coins', -map.cost)
            if radius == 0:
                tilemap = tilemaps.tilemap1
            elif radius == 1:
                while True:
                    tilemap = random.choice([tilemaps.tilemap2, tilemaps.tilemap3, tilemaps.tilemap4])
                    if self.last_map[1] != tilemap:
                        self.last_map[1] = tilemap
                        break
            elif radius == 2:
                while True:
                    tilemap = random.choice([tilemaps.tilemap5, tilemaps.tilemap6, tilemaps.tilemap7])
                    if self.last_map[2] != tilemap:
                        self.last_map[2] = tilemap
                        break
            elif radius == 3:
                if grid_pos[0] == 1:
                    if grid_pos[1] == 1:
                        tilemap = tilemaps.tilemap15
                    elif grid_pos[1] == 7:
                        tilemap = tilemaps.tilemap14
                    else:
                        tilemap = tilemaps.tilemap11
                elif grid_pos[0] == 7:
                    if grid_pos[1] == 1:
                        tilemap = tilemaps.tilemap12
                    elif grid_pos[1] == 7:
                        tilemap = tilemaps.tilemap13
                    else:
                        tilemap = tilemaps.tilemap9
                else:
                    if grid_pos[1] == 1:
                        tilemap = tilemaps.tilemap8
                    elif grid_pos[1] == 7:
                        tilemap = tilemaps.tilemap10
            else:
                tilemap = tilemaps.tilemap16

            self.maps[grid_pos[1]][grid_pos[0]] = Map(tilemap, self)
            for rel_pos in adjacent_maps:
                pos = (grid_pos[0]+rel_pos[0], grid_pos[1]+rel_pos[1])
                if 0 <= pos[0] <= 8 and 0 <= pos[1] <= 8 and self.maps[pos[1]][pos[0]] is None:
                    self.maps[pos[1]][pos[0]] = BuyMap(get_map_cost(pos))

    def scroll_window(self, win, rel_mouse):
        if win.moving_h:
            win.h_sb.left = min(win.view_size[0]-win.h_sb.w,
                                max(0, win.start_x-(win.start_mouse[0]-rel_mouse[0])))
            win.xpos = win.h_sb.left/(win.view_size[0]-win.h_sb_size)*(win.full_size[0]-win.view_size[0])
        if win.moving_v:
            win.v_sb.top = min(win.view_size[1]-win.v_sb.h,
                               max(0, win.start_y-(win.start_mouse[1]-rel_mouse[1])))
            win.ypos = win.v_sb.top/(win.view_size[1]-win.v_sb_size)*(win.full_size[1]-win.view_size[1])

    def drawgame(self):
        coins_str = '{:,}'.format(player.inventory['coins'])
        coins_text = TextLine('Coins: '+coins_str, font='large')
        coins_text.rect.topright = (GAME_WIDTH+GAME_OFFSETS['x'], 6)
        pop_str = '/'.join(('{:,}'.format(self.cur_map.available_workers),
                            '{:,}'.format(self.cur_map.population),
                            '{:,}'.format(self.cur_map.beds)))
        pow_str = '/'.join(('{:,}'.format(self.cur_map.available_power),
                            '{:,}'.format(self.cur_map.max_power)))
        pop_text = TextLine('Island Pop.: '+pop_str+'   Power: '+pow_str, font='large')
        pop_text.tooltip = ToolTip([TextLine('avail./total/max, avail./max')], BLACK)
        poptextx = gameArea.get_rect(topleft=GAME_OFFSET).centerx
        poptexty = DISPLAY_HEIGHT-(DISPLAY_HEIGHT-GAME_HEIGHT)/4
        pop_text.rect.center = (poptextx, poptexty)
        self.mouse = pygame.mouse.get_pos()
        self.game_mouse = get_rel_mouse(self.mouse, gameArea)
        self.map_mouse = get_rel_mouse(self.mouse, mapArea)
        self.perk_mouse = get_rel_mouse(self.mouse, perkArea)

        self.energy_bar.val = player.inventory['energy']
        gameDisplay.fill(WHITE)
        gameArea.fill(GREY)
        gameArea.blit(mapviewbutton, mapviewbuttonpos)
        tooltip = None
        draw_radius_pos = None
        if not self.map_view:
            for y in range(MAP_SIZE):
                for x in range(MAP_SIZE):
                    if self.cur_map.tiles[y][x].collidepoint(self.map_mouse):
                        self.cur_map.tiles[y][x].set_tooltip(self)
                        tooltip = self.cur_map.tiles[y][x].tooltip
                        if self.cur_map.tiles[y][x].work_radius is not None:
                            draw_radius_pos = (x, y)

            mapArea.blit(self.cur_map.surf, (0, 0))
            gameDisplay.blit(pop_text.surf, pop_text)
            if pop_text.rect.collidepoint(self.mouse):
                tooltip = pop_text.tooltip
        else:
            for y, row in enumerate(self.maps):
                for x, map in enumerate(row):
                    if type(map) is Map:
                        mapArea.blit(map.thumb, (x*TILE_WIDTH, y*TILE_HEIGHT))
                        if self.cur_map.tiles[y][x].collidepoint(self.map_mouse):
                            map.make_tooltip()
                            tooltip = map.tooltip
                    elif type(map) is BuyMap:
                        map.draw(mapArea, (x*TILE_WIDTH, y*TILE_HEIGHT), player.inventory['coins'])
        if draw_radius_pos is not None:
            draw_radius_surface(draw_radius_pos, self.cur_map.tiles[draw_radius_pos[1]][draw_radius_pos[0]].work_radius)
        if len(log.text_lines) > 0:
            logpos = (GAME_WIDTH + 100, DISPLAY_HEIGHT - 25 - log.surf.get_height())
            gameDisplay.blit(log.surf, logpos)

        pygame.draw.rect(gameDisplay, BLACK, GAME_AREA_RECT, 1)
        pygame.draw.rect(gameDisplay, BLACK, gameDisplay.get_rect(), 1)
        gameDisplay.blit(self.page_select_surf, (GAME_WIDTH + 50 + 10,
                                                 GAME_OFFSET[1] - self.page_select_surf.get_rect().h))
        y_start = GAME_OFFSET[1]
        pygame.draw.line(gameDisplay, BLACK, (GAME_WIDTH + 50 + 10, y_start),
                         (GAME_WIDTH + 50 + 10, y_start + 500), 2)
        pygame.draw.line(gameDisplay, BLACK, (GAME_WIDTH + 50 + 10, y_start + 500),
                         (DISPLAY_WIDTH - 10, y_start + 500), 2)
        pygame.draw.line(gameDisplay, BLACK, (DISPLAY_WIDTH - 10, y_start + 500),
                         (DISPLAY_WIDTH - 10, y_start - 2), 2)
        gameDisplay.blit(self.energy_text.surf, self.energy_text)
        gameDisplay.blit(coins_text.surf, coins_text)
        self.energy_bar.draw()
        if self.energy_bar_flash:
            pygame.draw.rect(gameDisplay, RED, self.energy_bar.get_rect())
        if self.cur_page == 'Inventory':
            self.sell_buttons = get_sell_buttons(self)
            for button in self.sell_buttons:
                gameDisplay.blit(button.surf, button.rect.topleft)

            header_text1 = FONTS['medium'].render('Number', True, BLACK)
            header_text2 = FONTS['medium'].render('Sell value (All)', True, BLACK)
            header_text3 = FONTS['medium'].render('Sell', True, BLACK)
            gameDisplay.blit(header_text1, (GAME_WIDTH + 275 - header_text1.get_width(), 75))
            gameDisplay.blit(header_text2, (GAME_WIDTH + 440 - header_text2.get_width(), 75))
            gameDisplay.blit(header_text3, (GAME_WIDTH + 475, 75))
            i = 0
            text_surfs = {}
            for key, value in player.inventory.items():
                if key not in self.exclude and key in player.known_items:
                    tmptext1 = FONTS['medium'].render(ITEMS[key]['i_cap']+':', True, BLACK)
                    tmptext2 = FONTS['medium'].render('{:,}'.format(value), True, BLACK)
                    tmptext2x = GAME_WIDTH + 275 - tmptext2.get_width()
                    tmpstr3 = '{:,}'.format(get_sell_val(key))+' ('+'{:,}'.format(value*get_sell_val(key))+')'
                    tmptext3 = FONTS['medium'].render(tmpstr3, True, BLACK)
                    tmptext3x = GAME_WIDTH + 440 - tmptext3.get_width()
                    gameDisplay.blit(tmptext1, (GAME_WIDTH + 100, 100 + i))
                    gameDisplay.blit(tmptext2, (tmptext2x, 100 + i))
                    gameDisplay.blit(tmptext3, (tmptext3x, 100 + i))

                    text_surfs[key] = {'surf': tmptext1,
                                       'pos': (GAME_WIDTH + 100, 100 + i)}

                    i += tmptext1.get_height()
            for item, info in text_surfs.items():
                if info['surf'].get_rect(topleft=info['pos']).collidepoint(self.mouse):
                    ymax = max(num for num in item_history[item] if num is not None)
                    ymin = min(num for num in item_history[item] if num is not None)
                    ymax += 1
                    if ymin > 0:
                        ymin -= 1
                    if (ymax - ymin) % 2 != 0:
                        ymax += 1

                    max_text = FONTS['medium'].render('{:,}'.format(ymax), True, BLACK)
                    chart_offset = max(20, max_text.get_width() + 6)

                    mouseover_chart = pygame.Surface((chart_offset+CHART_WIDTH+20, CHART_HEIGHT+60))
                    mouseover_chart.fill(WHITE)
                    chart_area = mouseover_chart.subsurface((chart_offset, 20, CHART_WIDTH, CHART_HEIGHT))

                    pygame.draw.rect(mouseover_chart, BLACK, mouseover_chart.get_rect(), 1)

                    title_text = FONTS['medium'].render(ITEMS[item]['plural_i_cap']+':', True, BLACK)
                    mouseover_chart.blit(title_text, title_text.get_rect(center=(chart_offset+CHART_WIDTH/2, 10)))
                    bottom_text = FONTS['medium'].render('(Seconds ago)', True, BLACK)
                    mouseover_chart.blit(bottom_text, bottom_text.get_rect(center=(chart_offset+CHART_WIDTH/2,
                                                                                   CHART_HEIGHT+50)))

                    zero_secs = FONTS['medium'].render('0', True, BLACK)
                    mouseover_chart.blit(zero_secs, zero_secs.get_rect(center=(chart_offset+CHART_WIDTH,
                                                                               CHART_HEIGHT+33)))
                    thirty_secs = FONTS['medium'].render('30', True, BLACK)
                    mouseover_chart.blit(thirty_secs, thirty_secs.get_rect(center=(chart_offset+CHART_WIDTH/2,
                                                                                   CHART_HEIGHT+33)))
                    sixty_secs = FONTS['medium'].render('60', True, BLACK)
                    mouseover_chart.blit(sixty_secs, sixty_secs.get_rect(center=(chart_offset, CHART_HEIGHT+33)))

                    mouseover_chart.blit(max_text, max_text.get_rect(midright=(chart_offset-5, 20)))
                    mid_text = FONTS['medium'].render('{:,}'.format(int((ymax+ymin)/2)), True, BLACK)
                    mouseover_chart.blit(mid_text, mid_text.get_rect(midright=(chart_offset-5, 20+CHART_HEIGHT/2)))
                    min_text = FONTS['medium'].render('{:,}'.format(ymin), True, BLACK)
                    mouseover_chart.blit(min_text, min_text.get_rect(midright=(chart_offset-5, 20+CHART_HEIGHT)))

                    pygame.draw.rect(chart_area, BLACK, chart_area.get_rect(), 1)
                    prev_point = None
                    for i, val in enumerate(item_history[item]):
                        if val is not None:
                            if prev_point is not None:
                                pygame.draw.line(chart_area, GREEN, prev_point,
                                                 (i*int(CHART_WIDTH/60)+2,
                                                  int(CHART_HEIGHT-CHART_HEIGHT*((val-ymin)/(ymax-ymin)))-3), 2)
                            prev_point = (i*int(CHART_WIDTH/60)+2,
                                          int(CHART_HEIGHT-CHART_HEIGHT*((val-ymin)/(ymax-ymin)))-3)
                    chart_pos = (self.mouse[0]+20, self.mouse[1]+20)
                    gameDisplay.blit(mouseover_chart, chart_pos)

        elif self.cur_page == 'Use':
            self.usables_surfaces = get_usables_surfs()
            for usesurf in self.usables_surfaces:
                gameDisplay.blit(usesurf.surf, (usesurf.rect.x, usesurf.rect.y))
                if usesurf.rect.collidepoint(self.mouse):
                    tooltip = usesurf.tooltip
        elif self.cur_page == 'Craft':
            self.recipe_surfaces = get_recipe_surfs()
            for resurf in self.recipe_surfaces:
                gameDisplay.blit(resurf.surf, (resurf.rect.x, resurf.rect.y))
                if resurf.rect.collidepoint(self.mouse):
                    tooltip = resurf.tooltip
        elif self.cur_page == 'Build':
            self.build_surfaces = get_build_surfs()
            for bsurf in self.build_surfaces:
                gameDisplay.blit(bsurf.surf, (bsurf.rect.x, bsurf.rect.y))
                if bsurf.rect.collidepoint(self.mouse):
                    tooltip = bsurf.tooltip
        elif self.cur_page == 'Perks':
            make_perk_surf(self.perk_window.full_surf, self.perks)
            self.perk_window.draw(perkArea, (0, 0))
            rel_mouse = (self.perk_mouse[0]+self.perk_window.xpos, self.perk_mouse[1]+self.perk_window.ypos)
            if self.perk_window.view_surf.get_rect(topleft=perkArea.get_abs_offset()).collidepoint(self.mouse):
                for perk in self.perks:
                    if perk.rect.collidepoint(rel_mouse):
                        perk.set_tooltip(self)
                        tooltip = perk.tooltip

        if tooltip:
            tooltip.draw(gameDisplay, self.mouse)
        curfps = int(clock.get_fps())
        fpssurf, fpsrect = text_objects(str(curfps), FONTS['medium'])
        gameDisplay.blit(fpssurf, fpsrect)
        pygame.display.flip()
        clock.tick()

    def main(self):
        while True:
            mouse = self.mouse
            game_mouse = self.game_mouse
            map_mouse = self.map_mouse
            perk_mouse = self.perk_mouse
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == GAME_TICK:
                    for i, timer in enumerate(self.timers):
                        if timer.tick() == 'done':
                            del self.timers[i]
                    for y1 in rand_row:
                        for x1 in rand_col:
                            if type(self.maps[y1][x1]) is Map:
                                for y2 in rand_row:
                                    for x2 in rand_col:
                                        self.maps[y1][x1].tiles[y2][x2].tick()
                    random.shuffle(rand_row)
                    random.shuffle(rand_col)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.cur_page == 'Perks':
                        perk_mouse = get_rel_mouse(mouse, perkArea)
                        if event.button == 1:
                            if self.perk_window.has_h_sb:
                                if self.perk_window.h_sb.collidepoint(perk_mouse):
                                    self.perk_window.moving_h = True
                                    self.perk_window.start_mouse = perk_mouse
                                    self.perk_window.start_x = self.perk_window.h_sb.left
                            if self.perk_window.has_v_sb:
                                if self.perk_window.v_sb.collidepoint(perk_mouse):
                                    self.perk_window.moving_v = True
                                    self.perk_window.start_mouse = perk_mouse
                                    self.perk_window.start_y = self.perk_window.v_sb.top
                        elif event.button == 4:
                            self.perk_window.scroll(-10)
                        elif event.button == 5:
                            self.perk_window.scroll(10)

                if event.type == pygame.MOUSEBUTTONUP:
                    if self.map_view:
                        xgrid = int(map_mouse[0]//TILE_WIDTH)
                        ygrid = int(map_mouse[1]//TILE_HEIGHT)
                        if 0 <= xgrid < MAP_SIZE and 0 <= ygrid < MAP_SIZE:
                            if type(self.maps[ygrid][xgrid]) is Map:
                                self.cur_map = self.maps[ygrid][xgrid]
                                self.map_view = False
                            elif (type(self.maps[ygrid][xgrid]) is BuyMap
                                  and player.inventory['coins'] >= self.maps[ygrid][xgrid].cost):
                                self.buy_map((xgrid, ygrid))
                    else:
                        for y in range(MAP_SIZE):
                            for x in range(MAP_SIZE):
                                if self.cur_map.tiles[y][x].check_mouseover(map_mouse):
                                    self.cur_map.tiles[y][x].doclick(event, self)

                    if mapviewrect.collidepoint(game_mouse):
                        self.map_view = not self.map_view
                        self.force_update_map_thumbs()

                    if self.cur_page == 'Inventory':
                        for button in self.sell_buttons:
                            if button.rect.collidepoint(mouse):
                                player.adjust_inventory(button.tags[0], - int(button.string))
                                player.adjust_inventory('coins', ITEMS[button.tags[0]]['sell_value']*int(button.string))

                    elif self.cur_page == 'Craft':
                        for recipe in self.recipe_surfaces:
                            if recipe.check_mouseover(mouse):
                                if player.craftable(recipe.string):
                                    self.drawgame()
                                    do_crafting_popup(recipe.string)

                    elif self.cur_page == 'Use':
                        for usable in self.usables_surfaces:
                            if usable.check_mouseover(mouse):
                                if player.usable(usable.string):
                                    self.drawgame()
                                    do_using_popup(usable.string)

                    elif self.cur_page == 'Build':
                        for buildsurf in self.build_surfaces:
                            if buildsurf.check_mouseover(mouse) and player.buildable(buildsurf.string):
                                self.map_view = False
                                self.drawgame()
                                do_build_popup(buildsurf.string, self.cur_map, self)

                    elif self.cur_page == 'Perks':
                        self.perk_window.moving_h = False
                        self.perk_window.moving_v = False
                        if self.perk_window.view_surf.get_rect(topleft=perkArea.get_abs_offset()).collidepoint(mouse):
                            rel_mouse = (perk_mouse[0]+self.perk_window.xpos, perk_mouse[1]+self.perk_window.ypos)
                            for perk in self.perks:
                                if perk.rect.collidepoint(rel_mouse):
                                    perk.do_click(self)

                    for i, page in enumerate(self.page_surfaces):
                        pagemouse = (mouse[0] - GAME_WIDTH - 60,
                                     mouse[1] - GAME_OFFSET[1] + self.page_select_surf.get_rect().h)
                        if page.check_mouseover(pagemouse):
                            self.cur_page = self.pages[i]
                            self.page_select_surf = self.page_select_surfs[self.cur_page]

            for thing in self.perks:
                thing.update_status()

            if self.cur_page == 'Perks':
                perk_mouse = get_rel_mouse(mouse, perkArea)
                self.scroll_window(self.perk_window, perk_mouse)
            self.drawgame()


game = Game()

if __name__ == '__main__':
    game.main()
