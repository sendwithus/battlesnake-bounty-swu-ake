#!/usr/bin/python
import redis
import time
import json

from board.redisBoard import RedisBoard
import settings
from test import test

redis_server = redis.Redis(settings.REDIS_URL)


def clear_redis():
    for key in  redis_server.keys('*'):
    	print "nuking: %s" % key
    	redis_server.delete(key)

def visit(game, data):
	print "visiting %s" % data
	board = RedisBoard(payload=json.loads(data))
	for child_payload in board.children_payloads():
		child_payload = json.dumps(child_payload)
		if not redis_server.exists(child_payload):
			redis_server.sadd("%s_to_visit" % game, child_payload)
			print child_payload


def application(environ, start_response):
	clear_redis()
	test()
	while True:
		for game in redis_server.smembers("active_games"):
			board_key = redis_server.spop("%s_to_visit" % game)
			if game and board_key:
				visit(game, board_key)
			time.sleep(1)
