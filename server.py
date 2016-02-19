#!/usr/bin/python
from flask import Flask, render_template, jsonify, request
import json
import pprint

import settings
from utils import redis_server, redis_key, subtract_vectors
from board.redisBoard import RedisBoard

application = Flask(__name__, static_url_path='/static')

@application.route('/')
def home():
	return jsonify(settings.ME)


def set_head_board():
	data = request.get_json(force=True)
	game = data.get("game")
	board = RedisBoard(data)

	redis_server().sadd("active_games", game)
	redis_server().delete("%s_N" % game)
	redis_server().delete("%s_S" % game)
	redis_server().delete("%s_E" % game)
	redis_server().delete("%s_W" % game)

	children = board.children_dict()
	for direction in children.keys():
		for next_board in children[direction]:
			board_direction_key = "%s_%s" % (game, direction)
			print "child for: %s" % board_direction_key
			import pprint
			pprint.pprint(next_board)
			redis_server().sadd(board_direction_key, next_board)


@application.route('/start', methods=['POST'])
def start():
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
	move = redis_server().get("%s_best_move" % game, "north")

	return jsonify({
		"move": move,
		"taunt": ""
	})

if __name__ == '__main__':
	application.debug = True
	application.run()