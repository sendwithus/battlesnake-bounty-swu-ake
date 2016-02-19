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
	# if not payload:
	# 	return
	board = RedisBoard(payload)	

	# visit self
	quality_key = "%s_quality" % redis_key
	quality = board.quality()
	current_quality = redis_server().get(quality_key)
	if not current_quality or quality > current_quality:
		redis_server().set(quality)
	best_move(game)

	# # visit children
	children = board.worstcase_children_dict()
	for direction in children.keys():
		payload = children[direction]
		redis_server().sadd(redis_key, json.dumps(payload))

print "Worker up and monitoring"
while True:
	for game in redis_server().smembers("active_games"):
		for redis_key in ["%s_north" % game, "%s_south" % game, "%s_east" % game,"%s_west" % game]:

			board_key = redis_server().spop(redis_key)
			if game and board_key:
				visit(game, board_key, redis_key)
			time.sleep(0)
		time.sleep(0.1)
	time.sleep(0.1)