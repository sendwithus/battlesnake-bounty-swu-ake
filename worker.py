#!/usr/bin/python
import redis
import time
import json

from board.redisBoard import RedisBoard
import settings
from test import test
from utils import redis_server, best_move



def visit(game, data, redis_key):
	payload = json.loads(data)
	# if not payload:
	# 	return
	board = RedisBoard(payload)	

	# visit self
	quality_key = "%s_quality" % redis_key
	quality = board.quality()
	current_quality = redis_server().get(quality_key)
	current_quality = 0 if current_quality == 'None' else int(current_quality)

	if len(redis_server().smembers(redis_key)) > 0:
		if not current_quality or quality > current_quality:
			redis_server().set(quality_key, quality)

	# visit counter
	visit_key = "%s_v" % redis_key
	current_count = int(redis_server().get(visit_key))
	redis_server().set(visit_key, current_count+1)

	# # visit children
	children = board.worstcase_children_dict()
	for direction in children.keys():
		payload = children[direction]
		redis_server().lpush(redis_key, json.dumps(payload))

print "Worker up and monitoring"
while True:
	for game in redis_server().smembers("active_games"):
		for redis_key in ["%s_north" % game, "%s_south" % game, "%s_east" % game,"%s_west" % game]:
			if redis_server().llen(redis_key) > 0:
				board_key = redis_server().lpop(redis_key)
				visit(game, board_key, redis_key)
			time.sleep(0)
		time.sleep(0)
	time.sleep(0)