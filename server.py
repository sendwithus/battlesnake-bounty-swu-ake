#!/usr/bin/python
from flask import Flask, render_template, jsonify, request
import redis
import json
import pprint

import settings
from utils import redis_server


application = Flask(__name__, static_url_path='/static')

@application.route('/')
def home():
	return jsonify(settings.ME)


@application.route('/start', methods=['POST'])
def start():
	data = request.get_json(force=True)
	pprint.pprint(data)
	game = data.get("game")

	try:
		redis_server().sadd("active_games", game)
		redis_server().set("%s_current_board" % game, data)
		redis_server().delete("%s_to_visit" % game)
		redis_server().sadd("%s_to_visit" % game, request.data)
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

	try:
		data = json.loads(request.data)
		key = redis_key(data)
		game = data.get("game")
		# traverse from here
		redis_server().set("%s_current_board" % game, key)
		redis_server().delete("%s_to_visit" % game)
		redis_server().sadd("%s_to_visit" % game, json.dumps(request.data))
	except Exception as e:
		print e 

	time.sleep(0.5) # TODO: wait till 0.99 after this request came in

	move = "north"
	try:
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