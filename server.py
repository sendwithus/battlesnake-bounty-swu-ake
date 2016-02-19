#!/usr/bin/python
from flask import Flask, render_template, jsonify, request
import json
import pprint
import time

import settings
from utils import redis_server, redis_key, subtract_vectors, best_move
from board.redisBoard import RedisBoard

application = Flask(__name__, static_url_path='/static')


@application.route('/')
def home():
	return jsonify(settings.ME)


@application.route('/4swu/redis/nuke')
def nuke_redis():
	for key in redis_server().keys('*'):
		redis_server().delete(key)
	return jsonify({'nuked': 'all the things'})


@application.route('/4swu/redis/debug')
def debug_redis():
	data = {}
	for key in redis_server().keys('*'):
		try:
			data[key] = redis_server().get(key)
		except:
			try:
				data[key] = list(redis_server().smembers("active_games"))
			except Exception as e:
				data[key] = str(e)
				print e
	return jsonify(data)


def set_head_board():
	data = request.get_json(force=True)
	game = data.get("game")

	redis_server().sadd("active_games", str(game))
	redis_server().delete("%s_north" % game)
	redis_server().delete("%s_south" % game)
	redis_server().delete("%s_east" % game)
	redis_server().delete("%s_west" % game)
	redis_server().set("%s_north_quality" % game, 0)
	redis_server().set("%s_south_quality" % game, 0)
	redis_server().set("%s_east_quality" % game, 0)
	redis_server().set("%s_west_quality" % game, 0)

	redis_server().set("%s_north_v" % game, 0)
	redis_server().set("%s_south_v" % game, 0)
	redis_server().set("%s_east_v" % game, 0)
	redis_server().set("%s_west_v" % game, 0)


	board = RedisBoard(data)
	children = board.worstcase_children_dict()
	for direction in children.keys():
		payload = children[direction]
		if type(payload) != dict:
			print "payload is not json!: %s" % payload
		board_direction_key = "%s_%s" % (game, direction)
		redis_server().sadd(board_direction_key, json.dumps(payload))
	return board

def clear_game():
	data = request.get_json(force=True)
	game = data.get("game")

	redis_server().delete("%s_north" % game)
	redis_server().delete("%s_south" % game)
	redis_server().delete("%s_east" % game)
	redis_server().delete("%s_west" % game)
	redis_server().set("%s_north_quality" % game, 0)
	redis_server().set("%s_south_quality" % game, 0)
	redis_server().set("%s_east_quality" % game, 0)
	redis_server().set("%s_west_quality" % game, 0)


@application.route('/start', methods=['POST'])
def start():
	set_head_board()
	return jsonify({
		"taunt": '',
	})


@application.route('/end', methods=['POST'])
def end():
	data = json.loads(request.data)
	redis_server().srem("active_games", data.get("game"))
	return jsonify(settings.ME)


def debug():
	data = json.loads(request.data)
	game = data.get("game")
	n = redis_server().get("%s_north_v" % game)
	s = redis_server().get("%s_south_v" % game)
	e = redis_server().get("%s_east_v" % game)
	w = redis_server().get("%s_west_v" % game)
	print "visits: %s" % {"n":n, "s":s, "e":e, "w":w}

@application.route('/move', methods=['POST'])
def move():
	board = set_head_board()
	time.sleep(0.5)
	data = json.loads(request.data)
	move = best_move(data.get("game"))
	if move not in board.valid_moves():
		move = random.choice(board.valid_moves())
	clear_game()
	debug()
	response = {
		"move": move,
		"taunt": ""
	}
	return jsonify(response)

if __name__ == '__main__':
	application.debug = True
	application.run()