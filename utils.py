import json
import redis
import settings
import os

_redis_server = None


def redis_server():
	global _redis_server
	if _redis_server:
		return _redis_server

	_redis_server = redis.from_url(os.environ.get("REDIS_URL", 'redis://localhost:6379'))
	return _redis_server

def redis_key(payload):
	# consistent order snakes
	snakes = {}
	for snake in payload.get("snakes", {}):
		snakes[snake.get("name")] = snake
	snake_ids = snakes.keys()
	snake_ids.sort()
	snakes = [snakes[key] for key in snake_ids]

	# list of snakes
	key = str(payload.get("game"))
	for snake in snakes:
		key += "_"
		for x, y in snake.get("coords", []):
			key += "%d%d" % (x, y)

	return key

def add_vectors(v1, v2):
	(x1, y1) = v1
	(x2, y2) = v2
	return x1+x2, y1+y2


def subtract_vectors(v1, v2):
	(x1, y1) = v1
	(x2, y2) = v2
	return x1-x2, y1-y2

def best_move(game, board):
	n = redis_server().get("%s_north_quality" % game)
	s = redis_server().get("%s_south_quality" % game)
	e = redis_server().get("%s_east_quality" % game)
	w = redis_server().get("%s_west_quality" % game)
	qualities = []
	if n:
		qualities.append(('north', int(n)))
	if s:
		qualities.append(('south', int(s)))
	if e:
		qualities.append(('east', int(e)))
	if w:
		qualities.append(('west', int(w)))
	qualities = sorted(qualities, key=lambda tup: -tup[1])
	valid_moves = board.valid_moves()

	print "qualities: %s" % qualities
	print "valid directions: %s" % valid_moves
	for (direction, weight) in qualities:
		if direction in valid_moves:
			print "best: %s at %s" % (direction, weight)
			return direction

