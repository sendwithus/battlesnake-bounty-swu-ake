#!/usr/bin/python
from flask import Flask, render_template, jsonify, request
import json
import pprint

import settings
from utils import redis_server, redis_key, subtract_vectors
from board.redisBoard import RedisBoard

application = Flask(__name__, static_url_path='/static')

for key in redis_server().keys('*'):
	redis_server().delete(key)


@application.route('/')
def home():
	return jsonify(settings.ME)


def set_head_board():
	data = request.get_json(force=True)
	game = data.get("game")
	board = RedisBoard(data)

	redis_server().delete("%s_north" % game)
	redis_server().delete("%s_south" % game)
	redis_server().delete("%s_east" % game)
	redis_server().delete("%s_west" % game)
	redis_server().set("%s_north_quality" % game, 0)
	redis_server().set("%s_south_quality" % game, 0)
	redis_server().set("%s_east_quality" % game, 0)
	redis_server().set("%s_west_quality" % game, 0)

	children = board.worstcase_children_dict()
	for direction in children.keys():
		payload = children[direction]
		board_direction_key = "%s_%s" % (game, direction)
		redis_server().sadd(board_direction_key, json.dumps(payload))


@application.route('/start', methods=['POST'])
def start():
	data = request.get_json(force=True)
	game = data.get("game")
	redis_server().sadd("active_games", game)
	set_head_board()
	return jsonify({
		"taunt": '',
	})


@application.route('/end', methods=['POST'])
def end():
	data = json.loads(request.data)
	try:
		redis_server().srem("active_games", data.get("game"))
	except Exception as e:
		print e 
	return jsonify(settings.ME)


@application.route('/move', methods=['POST'])
def move():
	set_head_board()
	time.sleep(0.1) # TODO: wait till 0.99 after this request came in

	n = redis_server().get("%s_north_quality" % game)
	s = redis_server().get("%s_south_quality" % game)
	e = redis_server().get("%s_east_quality" % game)
	w = redis_server().get("%s_west_quality" % game)
	best = max([n, s, e, w])
	print "%s, best is: %s" % (str([n, s, e, w]), best)
	move = "north"
	if s == best:
		move = "south"
	if e == best:
		move = "east"
	if w == best:
		move = "west"

	return jsonify({
		"move": move,
		"taunt": ""
	})

if __name__ == '__main__':
	application.debug = True
	application.run()