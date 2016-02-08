#!/usr/bin/python
from flask import Flask, render_template, jsonify, request
import redis
import json

import settings


application = Flask(__name__, static_url_path='/static')
redis_server = redis.Redis('localhost')


@application.route('/')
def home():
	return jsonify(ME)


@application.route('/start', methods=['POST'])
def start():
	data = json.loads(request.data)
	game = data.get("game")

	redis_server.sadd("active_games", game)
	redis_server.set("%s_current_board" % game, data)
	redis_server.delete("%s_to_visit" % game)
	redis_server.sadd("%s_to_visit" % game, request.data)

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
	key = redis_key(data)
	game = data.get("game")

	# traverse from here
	redis_server.set("%s_current_board" % game, key)
	redis_server.delete("%s_to_visit" % game)
	redis_server.sadd("%s_to_visit" % game, json.dumps(request.data))

	time.sleep(0.5) # TODO: wait till 0.99 after this request came in

	return jsonify({
		"move": redis_server.get("%s_best_move" % game),
		"taunt": ""
	})


if __name__ == '__main__':
	application.debug = True
	application.run()