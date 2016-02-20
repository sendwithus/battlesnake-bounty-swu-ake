import itertools
import copy

import settings
from utils import subtract_vectors
from board.baseBoard import BaseBoard


class ComputeBoard(BaseBoard):

	def __init__(self, payload=None):
		super(ComputeBoard, self).__init__(payload)

	def territory_control(self):
		if hasattr(self, "_territory_control"):
			if type(self._territory_control) == int:
				return self._territory_control

		territory_edges = [tuple(snake.get('coords')[0]) for snake in self.all_snakes]
		for snake in self.all_snakes:
			coord = tuple(snake.get('coords')[0])
			# print "%s: %s" % (coord, snake.get("id"))
			self.set(coord, "controlled_by", snake.get("id"))

		territory_control = {}
		while len(territory_edges) > 0:
			
			# pop
			t_edge = territory_edges[0]
			del territory_edges[0]
			
			# visit
			controlled_by = self.get(t_edge, "controlled_by")
			for coord in self.adjacent_cells(t_edge):
				coord = tuple(coord)
				if not self.get(coord, "controlled_by"):
					self.set(coord, "controlled_by", controlled_by)
					territory_edges.append(coord)
					if controlled_by not in territory_control.keys():
						territory_control[controlled_by] = 0
					territory_control[controlled_by] += 1

		self._territory_control = territory_control
		# print self._territory_control
		return territory_control

	def food_details(self):
		'''
		return list of tuples: [(distance, controlled_by, coordinate), ]
		'''
		if hasattr(self, "_food_details"):
			return self._food_details

		food_details = []
		for coord in self.food:
			(x, y) = coord
			(hx, hy) = self.head()
			distance = abs(x - hx) + abs(y - hy)
			controlled_by = self.get((x, y), 'controlled_by')
			food_details.append((distance, controlled_by, (x,y)))

		self._food_details = food_details
		return food_details

	def distance_to_closest_food(self):
		distances = [dist for (dist, ctrl, coord) in self.food_details() if ctrl == settings.SNAKE_ID]
		return min(distances) if len(distances) > 0 else 0

	def closest_food_directions(self):
		if hasattr(self, "_closest_food_directions"):
			return self._closest_food_directions

		closest_dist = None
		closest_coord = None
		for (distance, controlled_by, (x, y)) in self.food_details():
			if not closest_coord or (distance < closest_dist and controlled_by == settings.SNAKE_ID):
				closest_dist = distance
				closest_coord = (x, y)

		(hx, hy) = self.head()
		delta_x = hx - x
		delta_y = hy - y

		closest_food_directions = []
		if delta_x > 0:
			closest_food_directions.append("north")
		if delta_x < 0:
			closest_food_directions.append("south")
		if delta_y > 0:
			closest_food_directions.append("west")
		if delta_y < 0:
			closest_food_directions.append("east")

		self._closest_food_directions = closest_food_directions
		return closest_food_directions

	def children(self):
		children = []
		for my_move in self.children:
			children += self.children[my_move]
		return children

	def children_dict(self):

		# enumerate possible sensible move combinations for all snakes
		move_options = []
		for snake_id in self.all_snake_ids:
			choices = list(self.snake_choices(snake_id))
			move_options.append([(snake_id, (x, y)) for (x, y) in choices])
		possible_move_combinations = list(itertools.product(*move_options))

		# generate all children
		children = {
			'north': [],
			'south': [],
			'east': [],
			'west': [],
		}
		for move_set in possible_move_combinations:
			based_on_move, new_payload = self._child_payload(move_set)
			direction = settings.DIRECTION_STRINGS[subtract_vectors(based_on_move, self.head())]
			children[direction].append(new_payload)
		return children

	def worstcase_children_dict(self):
		worst_children = {}
		children = self.children_dict()
		for direction in children.keys():
			worst_value = 0
			worst_payload = None
			for child_payload in children[direction]:
				quality = ComputeBoard(child_payload).quality()
				if not worst_payload or quality < worst_value:
					worst_value = quality
					worst_payload = child_payload
			if worst_payload:
				worst_children[direction] = worst_payload
		return worst_children

	def children_payloads(self):

		# enumerate possible sensible move combinations for all snakes
		move_options = []
		for snake_id in self.all_snake_id:
			choices = self.snake_choices(id=snake_id)
			move_options.append([(snake_id, (x, y)) for (x, y) in choices])
		possible_move_combinations = list(itertools.product(*move_options))

		payloads = []
		for move_set in possible_move_combinations:
			based_on_move, new_payload = self._child_payload(move_set)
			payloads.append(new_payload)
		return payloads

	def _child_payload(self, move_set):
		new_payload = copy.deepcopy(self.payload)
		new_payload['turn'] += 1
		based_on_move = None

		# update each snake
		for (snake_id, (x, y)) in move_set:
			# keep track of our move
			if snake_id == settings.SNAKE_ID:
				based_on_move = (x, y)

			# find snake
			snake = None
			snake_i = 0
			for snake in new_payload.get("snakes", []):
				if snake.get("id") == snake_id:
					break
				snake_i += 1

			# update snake
			snake['age'] += 1
			snake['health'] -= 1
			del snake['coords'][-1]
			snake['coords'].insert(0, (x, y))
			new_payload.get("snakes", [])[snake_i] = snake

		return based_on_move, new_payload

	def quality(self):
		# return self.territory_control().get('Sendwithus')


		ctrl = self.territory_control()
		board_control = ctrl.get(settings.SNAKE_ID)

		# board control
		ctrl = self.territory_control()
		# avg_control = sum(ctrl.values())/max(1, len(ctrl.keys()))
		# my_control = ctrl.get(settings.SNAKE_ID, 0)
		# board_control = my_control/max(avg_control, 1)
		board_control = ctrl.get(settings.SNAKE_ID, 0)

		# approaching food
		hunger = (100 - self._me.get("health", 100))
		distance = self.distance_to_closest_food()
		approach_food = hunger*(20-distance)*2

		return {
			"control": board_control,
			"food": approach_food}
