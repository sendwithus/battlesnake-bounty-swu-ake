import settings
from urllib.parse import urlparse

def redis_connection():
	o = urlparse(settings.REDIS_URL)
	url = o.hostname + o.path
	port = o.port
	redis_server = redis.Redis(url, port)
	return redis_server


def redis_key(payload):
	# consistent order snakes
	snakes = {}
	for snake in payload.get("snakes", {}):
		snakes[snake.get("name")] = snake
	snake_ids = snakes.keys()
	snake_ids.sort()
	snakes = [snakes[key] for key in snake_ids]

	key = payload.get("game")
	for snake in snakes:
		key += "_"
		for x, y in snake.get("coords", []):
			key += "%d%d" % (x, y)
	return key