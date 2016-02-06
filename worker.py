#!/usr/bin/python
import redis
import time

from board import Board
import settings

redis_server = redis.Redis('localhost')


def visit(game, board_key):
	print "visiting %s" % board_key
	board = Board(redis_key=board_key)
	print board
	print board.territory_control

while True:
	for game in redis_server.smembers("active_games"):
		board_key = redis_server.spop("%s_to_visit" % game)
		if game and board_key:
			visit(game, board_key)
	time.sleep(1)

