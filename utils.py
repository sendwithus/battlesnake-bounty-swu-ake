import json
import redis
import settings
import os

_redis_server = None


def redis_server():
	global _redis_server
	if _redis_server:
		return _redis_server

	# url, port = settings.REDIS_URL.rsplit(':', 1)
	# port = int(port)
	# print "%s, %s" % (url, port)
	# _redis_server = redis.from_url(url, port)

	_redis_server = redis.from_url(os.environ.get("REDIS_URL"))
	return _redis_server

def redis_key(payload):
	return json.dumps(payload)

def add_vectors(v1, v2):
	(x1, y1) = v1
	(x2, y2) = v2
	return x1+x2, y1+y2

def subtract_vectors(v1, v2):
	(x1, y1) = v1
	(x2, y2) = v2
	return x1-x2, y1-y2


	# # consistent order snakes
	# snakes = {}
	# for snake in payload.get("snakes", {}):
	# 	snakes[snake.get("name")] = snake
	# snake_ids = snakes.keys()
	# snake_ids.sort()
	# snakes = [snakes[key] for key in snake_ids]

	# key = payload.get("game")
	# for snake in snakes:
	# 	key += "_"
	# 	for x, y in snake.get("coords", []):
	# 		key += "%d%d" % (x, y)
	# return key