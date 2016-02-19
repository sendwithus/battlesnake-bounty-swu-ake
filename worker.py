#!/usr/bin/python
import redis
import time
import json

from board.redisBoard import RedisBoard
import settings
from test import test
from utils import redis_server



def visit(game, data, redis_key):
	payload = json.loads(data)
	board = RedisBoard(payload=payload)	

	# visit self
	quality_key = "%s_quality" % redis_key
	quality = board.quality()
	current_quality = redis_server().get(quality_key)
	if not current_quality or quality > current_quality:
		redis_server().set(quality)
	print "%s: %s" % (quality_key, board.quality())

	# # visit children
	# for child_payload in board.children_payloads():
	# 	child_payload = json.dumps(child_payload)
	# 	if not redis_server().exists(child_payload):
	# 		redis_server().sadd(redis_key, child_payload)

try:
	print "Worker up and monitoring"
	while True:
		for game in redis_server().smembers("active_games"):
			for redis_key in ["%s_north" % game, "%s_south" % game, "%s_east" % game,"%s_west" % game]:
				board_key = redis_server().spop(redis_key)
				if game and board_key:
					visit(game, board_key, redis_key)
				time.sleep(0)
			time.sleep(0)
		time.sleep(0.1)
except Exception as e:
	print e