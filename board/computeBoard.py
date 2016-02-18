import itertools
import copy

import settings
from board.baseBoard import BaseBoard


class ComputeBoard(BaseBoard):

	def __init__(self, payload=None):
		super(ComputeBoard, self).__init__(payload)

		# add food
		for coord in self.food:
			self.set(tuple(coord), "food", True)

		# add snakes
		self.other_snakes = []
		self.other_snake_names = []
		self._snakes = self.payload.get("snakes", [])
		for snake in self._snakes:
			snake_status = snake.get("status", "dead")
			snake_length = len(snake.get("coords", []))
			snake_name = snake.get("name", "")
			if snake_status == "alive" and snake_length > 0:
				ttl = 1
				snake_coords = snake.get("coords", [])
				snake_coords.reverse()
				for coord in snake_coords:
					coord = tuple(coord)
					self.set(coord, "solid", True)
					self.set(coord, "controlled_by", snake_name)  # get snake UUID
					self.set(coord, "ttl", ttl)
					ttl += 1
				head = tuple(snake_coords[-1])
				self.set(head, "head", True)
				self.set(head, "distance", 0)
				snake_coords.reverse()

			# store each snake
			if snake_name == settings.SNAKE_NAME:
				self._me = snake
			else:
				self.other_snake_names.append(snake.get("name", ""))


	def board_quality(self):
		if hasattr(self, "_board_quality"):
			return self._board_quality

		# board control
		ctrl = self.territory_control()
		avg_control = sum(ctrl.values())/len(ctrl.keys())
		my_control = ctrl[self._me.get("name")]
		board_control = my_control/avg_control

		# approaching food
		hunger = (100 - self._me.get("health"))
		distance = self.distance_to_closest_food()
		approach_food = hunder*distance/10

		self._board_quality = board_control + approach_food
		return self._board_quality

	def territory_control(self):
		if hasattr(self, "_territory_control"):
			return self._territory_control

		territory_edges = [tuple(snake.get('coords')[0]) for snake in self.all_snakes]
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
			(hx, hy) = self.head
			distance = abs(x - hx) + abs(y - hy)
			controlled_by = self.get((x, y), 'controlled_by')
			food_details.append((distance, controlled_by, (x,y)))

		self._food_details = food_details
		return food_details

	def distance_to_closest_food(self):
		distances = [dist for (dist, ctrl, coord) in self.food_details() if ctrl == self._me.get("name")]
		return min(distances)

	def closest_food_directions(self):
		if hasattr(self, "_closest_food_directions"):
			return self._closest_food_directions

		closest_dist = None
		closest_coord = None
		print "CFD a"
		for (distance, controlled_by, (x, y)) in self.food_details():
			print "CFD b"
			if not closest_coord or (distance < closest_dist and controlled_by == settings.SNAKE_NAME):
				closest_dist = distance
				closest_coord = (x, y)
		print "CFD c"

		(hx, hy) = self.head()
		delta_x = hx - x
		delta_y = hy - y
		print "CFD d"

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
		for name in self.all_snake_names:
			choices = self.snake_choices(name)
			move_options.append([(name, (x, y)) for (x, y) in choices])
		possible_move_combinations = list(itertools.product(*move_options))
		print "possible combos: %s" % possible_move_combinations

		# generate all children
		children = {}
		for move_set in possible_move_combinations:
			print move_set
			based_on_move, new_payload = self._child_payload(move_set)
			print based_on_move
			print new_payload
			if child.based_on_move not in self._children.keys():
				children[child.based_on_move] = []
			children[child.based_on_move].append(child)

		return children

	def children_payloads(self):

		# enumerate possible sensible move combinations for all snakes
		move_options = []
		for name in self.all_snake_names:
			choices = self.snake_choices(name)
			move_options.append([(name, (x, y)) for (x, y) in choices])
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
		for (name, (x, y)) in move_set:

			# keep track of our move
			if name == settings.SNAKE_NAME:
				based_on_move = (x, y)

			# find snake
			snake = None
			snake_i = 0
			for snake in new_payload.get("snakes", []):
				if snake.get("name") == name:
					break
				snake_i += 1

			# update snake
			snake['age'] += 1
			snake['health'] -= 1
			del snake['coords'][-1]
			snake['coords'].insert(0, (x, y))
			new_payload.get("snakes", [])[snake_i] = snake
		return based_on_move, new_payload
