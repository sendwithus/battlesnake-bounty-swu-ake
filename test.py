#!/usr/bin/python
import json
import requests

from board import Board
import settings


snake_1 = {
    "name": settings.SNAKE_NAME,
    "status": "alive",
    "message": "Moved north",
    "taunt": "Let's rock!",
    "age": 56,
    "health": 83,
    "coords": [ [1, 1], [1, 2], [2, 2], [2, 2], [2, 2] ],
    "kills": 4,
    "food": 12
}

snake_2 = {
    "name": "Z",
    "status": "alive",
    "message": "Moved north",
    "taunt": "Let's rock!",
    "age": 56,
    "health": 83,
    "coords": [ [28, 18], [28, 17], [29, 17] ],
    "kills": 4,
    "food": 12
}


move_payload = {
    "game": "hairy-cheese",
    "mode": "advanced",
    "turn": 4,
    "board": {
        "height": 20,
        "width": 30
    },
    "snakes": [
    	snake_1,
    	snake_2,
    ],
    "food": [
        [1, 2], [9, 3]
    ]
}

import redis
redis_server = redis.Redis('localhost')
for key in  redis_server.keys('*'):
	print "nuking: %s" % key
	redis_server.delete(key)

start_url = "http://localhost:5000/start"
r = requests.post(start_url, json.dumps(move_payload))
print r

# move_url = "http://localhost:5000/move"
# r = requests.post(move_url, json.dumps(move_payload))
# print r

# for distance in range(0, 10):
#     head = Node(move_payload, "A")
#     (move, score, node) = head.best_move(distance)
#     print "looking %s moves ahead, my best score is: %s, %s" % (distance, score, move)