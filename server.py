#!/usr/bin/python
from flask import Flask, render_template, jsonify, request
import redis
import json

from board import Board
import settings

application = Flask(__name__, static_url_path='/static')
redis_server = redis.Redis('localhost')


@application.route('/')
def home():
	return jsonify(ME)


@application.route('/start', methods=['POST'])
def start():
	data = json.loads(request.data)
	board = Board(data)

	current_board_key = "%s_current_board" % board.game_name
	best_move_key = "%s_best_move" % board.game_name
	to_visit_key = "%s_to_visit" % board.game_name

	redis_server.sadd("active_games", board.game_name)
	redis_server.set(current_board_key, board.redis_key)
	redis_server.delete(to_visit_key)
	redis_server.sadd(to_visit_key, board.redis_key)

	return jsonify({
		'taunt': "red october standing by",
	})


@application.route('/end', methods=['POST'])
def end():
	data = json.loads(request.data)
	redis_server.srem("active_games", data.get("game"))
	# TODO: remove all redis keys to do with this game
	return jsonify(ME)


@application.route('/move', methods=['POST'])
def move():
	data = json.loads(request.data)
	game_name = data.get("game")
	board = Board(data)

	current_board_key = "%s_current_board" % game_name
	best_move_key = "%s_best_move" % game_name
	to_visit_key = "%s_to_visit" % game_name

	# traverse from here
	redis_server.set(current_board_key, board.redis_key)
	redis_server.delete(to_visit_key)
	redis_server.sadd(to_visit_key, board.redis_key)

	time.sleep(0.9) # TODO: wait till 0.99 after this request came in

	return jsonify({
		"move": redis_server.get(best_move_key),
		"taunt": ""
	})


if __name__ == '__main__':
	application.debug = True
	application.run()