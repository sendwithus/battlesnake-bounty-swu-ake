N = (-1, 0)
S = (1, 0)
E = (0, 1)
W = (0, -1)

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
ME = {
    'name': SNAKE_NAME,
    "color": "#f7931d",  # guybrush green
    "head": "/static/cat-snake.svg",
}

import os
REDIS_URL = os.environ.get("REDIS_URL", 'localhost')