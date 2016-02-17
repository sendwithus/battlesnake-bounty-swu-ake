import json
import redis
import settings

_redis_server = None


def redis_server():
	global _redis_server
	if _redis_server:
		return _redis_server

	url = "h:p3e5ialsr72o65caic95m4icq3b@ec2-54-235-152-160.compute-1.amazonaws.com"
	port = 23619
	_redis_server = redis.Redis(host=url, port=port)
	return _redis_server

def redis_key(payload):
	return json.dumps(payload)

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