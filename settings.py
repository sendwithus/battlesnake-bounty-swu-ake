N = (0, -1)
S = (0, 1)
E = (1, 0)
W = (-1, 0)

DIRECTIONS = [N, S, E, W]

DIRECTION_STRINGS = {
    N: 'north',
    E: 'east',
    S: 'south',
    W: 'west',
}

DIRECTION_TUPLES = {
    'north': N,
    'east': E,
    'south': S,
    'west': W,
}


ARROWS = {
	'north': ":arrow_up:",
	'south': ":arrow_down:",
	'east': ":arrow_right:",
	'west': ":arrow_left:",
}


SNAKE_NAME = "Adder Lovelace...ssssss"
SNAKE_ID = "ee925ec8-01f4-4f08-a05d-617a97cad866"
ME = {
    'name': SNAKE_NAME,
    "color": "#f7931d",  # guybrush green
    "head": 'http://battlesnake-bounty-swu.herokuapp.com/static/cat-snake.svg',
}

import os
REDIS_URL = os.environ.get("REDIS_URL")