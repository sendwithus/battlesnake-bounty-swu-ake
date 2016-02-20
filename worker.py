#!/usr/bin/python
import redis
import time
import json

from board.redisBoard import RedisBoard
import settings
from test import test
from utils import redis_server, best_move


def update_quality(board):
	quality_key = "%s_quality" % redis_key
	quality_dict = board.quality()
	quality = sum(quality_dict.values())
	current_quality = redis_server().get(quality_key)
	try:
		current_quality = int(current_quality)

		if redis_server().llen(redis_key) > 0:
			if not current_quality or quality < current_quality:
				print "quality: %s" % quality_dict
				redis_server().set(quality_key, quality)

	except Exception as e:
		print e


def update_visits(board):
	# visit counter
	visit_key = "%s_v" % redis_key
	visits = redis_server().get(visit_key)
	current_count = int(visits) if redis_server().get(visit_key) else 0
	redis_server().set(visit_key, current_count+1)


def visit(game, payload, redis_key):
	try:
		payload = json.loads(payload)
		board = RedisBoard(payload)	
		update_quality(board)
		update_visits(board)
		visit_children(board, redis_key)
	except Exception as e:
		import traceback
		traceback.print_exc()
		print e

def visit_children(board, redis_key):
	# # visit children
	children = board.worstcase_children_dict()
	for direction in children.keys():
		payload = children[direction]
		redis_server().lpush(redis_key, json.dumps(payload))


print "Worker up and monitoring"
while True:
	try:
		for game in redis_server().smembers("active_games"):
			for redis_key in ["%s_north" % game, "%s_south" % game, "%s_east" % game,"%s_west" % game]:
				if redis_server().llen(redis_key) > 0:
					payload = redis_server().rpop(redis_key)
					visit(game, payload, redis_key)
				time.sleep(0)
			time.sleep(0)
		time.sleep(0)
	except Exception as e:
		print e


