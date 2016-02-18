import redis
import json

import settings
from board.computeBoard import ComputeBoard
from utils import redis_server


class RedisBoard(ComputeBoard):

	def __init__(self, payload=None):
		self.redis_server = redis_server()

		# load from redis
		if self.redis_server.exists(payload):
			print "loading from redis"
			data = self.redis_server.get(payload)
			data = json.loads(data)
			self._territory_control = data['territory_control']
			self._food_details = data['food_details']
			self._closest_food_directions = data['closest_food_directions']
			self._children_payloads = data['children_payloads']
			return

		# cache to redis
		print "building A"
		super(RedisBoard, self).__init__(payload)
		print "building B"
		self.territory_control()
		print "building C"
		self.food_details()
		print "building D"
		self.closest_food_directions()
		print "building E"
		self.children_payloads()
		print "building F"
		self.board_quality()
		print "building G"

		data = {
			'territory_control': self.territory_control(),
			'food_details': self.food_details(),
			'closest_food_directions': self.closest_food_directions(),
			'children_payloads': self.children_payloads(),
			'board_quality': self.board_quality(),
		}
		self.redis_server.set(self.payload, json.dumps(data))
		print "building D"

	def territory_control(self):
		if not hasattr(self, '_territory_control'):
			self._territory_control = super(RedisBoard, self).territory_control()
		return self._territory_control

	def food_details(self):
		if not hasattr(self, '_food_details'):
			self._food_details = super(RedisBoard, self).food_details()
		return self._food_details

	def closest_food_directions(self):
		if not hasattr(self, '_closest_food_directions'):
			self._closest_food_directions = super(RedisBoard, self).closest_food_directions()
		return self._closest_food_directions

	def children_payloads(self):
		if not hasattr(self, '_children_payloads'):
			self._children_payloads = super(RedisBoard, self).children_payloads()
		return self._children_payloads