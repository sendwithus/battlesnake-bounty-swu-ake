import settings

def redis_connection():
	try:
		(scheme, url, port) = settings.REDIS_URL.split(":")
		redis_server = redis.Redis(url, port)
		return redis_server
	except Exception as e:
		print e


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