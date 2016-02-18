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


@application.route('/start', methods=['POST'])
def start():
	try:
		data = request.get_json(force=True)
		game = data.get("game")
		board = RedisBoard(data)

		redis_server().sadd("active_games", game)
		redis_server().delete("%s_N" % game)
		redis_server().delete("%s_S" % game)
		redis_server().delete("%s_E" % game)
		redis_server().delete("%s_W" % game)

		for next_pos in board.children_dict():
			curr_pos = board.head()
			direction = DIRECTION_STRINGS[subtract_vectors(next_pos, curr_pos)]
			for next_board in board.children_dict()[direction]:
				board_direction_key = "%s_%s" % (game, direction)
				print board_direction_key 
				redis_server().sadd(board_direction_key, next_board)

	except Exception as e:
		print e 

	return jsonify({
		"taunt": "red october standing by",
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
	game = "unknown"
	move = "north"

	try:
		data = json.loads(request.data)
		key = redis_key(data)
		game = data.get("game")
		# traverse from here
		redis_server().set("%s_current_board" % game, key)
		redis_server().delete("%s_to_visit" % game)
		redis_server().sadd("%s_to_visit" % game, json.dumps(request.data))

		time.sleep(0.5) # TODO: wait till 0.99 after this request came in

		redis_server().get("%s_best_move" % game)
	except Exception as e:
		print e

	return jsonify({
		"move": move,
		"taunt": ""
	})

if __name__ == '__main__':
	application.debug = True
	application.run()