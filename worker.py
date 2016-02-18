#!/usr/bin/python
import redis
import time
import json

from board.redisBoard import RedisBoard
import settings
from test import test
from utils import redis_server


def visit(game, data, redis_key):
	board = RedisBoard(payload=json.loads(data))
	redis_server().add("%s_quality" % redis_key, board.quality())
	print "visiting %s" % redis_key

	# visit children
	for child_payload in board.children_payloads():
		child_payload = json.dumps(child_payload)
		if not redis_server().exists(child_payload):
			redis_server().sadd(redis_key, child_payload)

while True:
	for game in redis_server().smembers("active_games"):
		for redis_key in ["%s_N" % game, "%s_S" % game, "%s_E" % game,"%s_W" % game]:
			board_key = redis_server().spop(redis_key)
			if game and board_key:
				visit(game, board_key, redis_key)
	time.sleep(0)
