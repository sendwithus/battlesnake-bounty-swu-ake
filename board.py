import redis
import settings

redis_server = redis.Redis('localhost')


def cache(fn):
	def wrapped(self):
		cache_key = "%s_%s" % (self.redis_key, fn.__name__)

		# check object
		if hasattr(self, cache_key):
			return getattr(self, cache_key)

		# check redis
		val = redis_server.get(cache_key)
		if val:
			setattr(self, cache_key, value)
		return val

		# do work
		val = fn(self)

		# cache 
		redis_server.set(cache_key, val)
		setattr(self, cache_key, value)

		return val
	return wrapped


class BaseBoard(object):

	def __init__(self, payload):
		self.payload = payload
		self._cells = {}
		self.width = self.payload.get("board", {}).get("width")
		self.height = self.payload.get("board", {}).get("height")
		self.game_name = self.payload.get("game")

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
				self.set(head, "controlled_by", snake)
				self.set(head, "distance", 0)
				snake_coords.reverse()

			# store each snake
			if snake_name == settings.SNAKE_NAME:
				self._me = snake
			else:
				self.other_snake_names.append(snake.get("name", ""))

	def set(self, coord, attr, val):
		if coord not in self._cells.keys():
			self._cells[coord] = {}
		self._cells[coord][attr] = val

	def get(self, coord, attr):
		val = self._cells.get(coord, {}).get(attr)
		if val:
			return val
		return self.default_value(coord, attr)

	def default_value(self, (x, y), attr):

		if attr == "empty":
			if 0 <= x < self.width:
				if 0 <= y < self.height:
					return True
			return False

		return {
			'food': False
		}.get(attr)

	@property
	def food(self):
		return self.payload.get("food", [])

	@property
	def all_snakes(self):
		yield self._me
		for s in self.other_snakes:
			yield s
	
	@property
	def head(self):
		return self._me.get("coords", [])[0]

	@property
	def north(self):
		coord = self.add_vectors(self.head, DIRECTION_TUPLES['north'])
		return self.get_cell(coord)

	@property
	def south(self):
		coord = self.add_vectors(self.head, settings.DIRECTION_TUPLES['south'])
		return self.get_cell(coord)

	@property
	def east(self):
		coord = self.add_vectors(self.head, settings.DIRECTION_TUPLES['east'])
		return self.get_cell(coord)

	@property
	def west(self):
		coord = self.add_vectors(self.head, settings.DIRECTION_TUPLES['west'])
		return self.get_cell(coord)

	def adjacent_cells(self, v):
		for d in settings.DIRECTIONS:
			ox, oy = v
			x, y = self.add_vectors(v, d)
			if 0 <= x < self._width and 0 <= y < self._height:
				yield (x, y)

	def adjacent_empty_cells(self, v):
		for coord in self.adjacent_cells(v):
			x, y = coord
			if not self.get_cell(x, y).solid:
				yield coord

	def snake(self, snake_name):
		for snake in self._snakes:
			if snake.get("name", "") == snake_name:
				return snake

	def snake_choices(self, snake_name=None):
		if not snake_name:
			snake_name = settings.SNAKE_NAME

		head = self.snake(snake_name).get('coords')[0]
		return self.adjacent_empty_cells(head)

	def add_vectors(self, v1, v2):
		(x1, y1) = v1
		(x2, y2) = v2
		return x1+x2, y1+y2


class Board(BaseBoard):

	def __init__(self, payload=None, redis_key=None):
		if payload:
			super(Board, self).__init__(payload)

		if redis_key:
			self._redis_key = redis_key

		# force cache fils
		self.territory_control
		self.food_details
		self.closest_food_directions

	@property
	def redis_key(self):
		if hasattr(self, "_redis_key"):
			return self._redis_key

		# consistent order snakes
		snakes = {}
		for snake in self.payload.get("snakes", {}):
			snakes[snake.get("name")] = snake
		snake_ids = snakes.keys()
		snake_ids.sort()
		snakes = [snakes[key] for key in snake_ids]

		key = self.payload.get("game")
		for snake in snakes:
			key += "_"
			for x, y in snake.get("coords", []):
				key += "%d%d" % (x, y)
		self._redis_key = key
		return self._redis_key

	@cache
	@property
	def territory_control(self):
		territory_edges = [snake.get('coords')[0] for snake in self.all_snakes]
		territory_control = {}
		while len(territory_edges) > 0:
			
			# pop
			t_edge = territory_edges[0]
			del territory_edges[0]
			
			# default
			controlled_by = self.get(t_edge, "controlled_by")
			if controlled_by not in territory_control.keys():
				territory_control[controlled_by] = 0

			# visit
			for coord in self.adjacent_cells(t_edge):
				coord = tuple(coord)
				if not self.get(coord, "controlled_by"):
					self.set(coord, "controlled_by", controlled_by)
					territory_edges.append(coord)
					territory_control[controlled_by] += 1

		return territory_control

	@cache
	@property
	def food_details(self):
		'''
		return list of tuples: [(distance, controlled_by, coordinate), ]
		'''
		food_details = []
		for (x, y) in self._food:
			(hx, hy) = self.head
			distance = abs(x - hx) + abs(y - hy)
			controlled_by = self._cells[(x, y)].controlled_by
			food_details.append((distance, controlled_by, (x,y)))
		return food_details

	@cache
	@property
	def closest_food_directions(self):
		_closest_food_directions = []
		closest_dist = None
		closest_coord = None
		for (distance, controlled_by, (x, y)) in self.food_details:
			if not closest_coord or (distance < closest_dist and controlled_by == settings.SNAKE_NAME):
				closest_dist = distance
				closest_coord = (x, y)

		(hx, hy) = self.head
		delta_x = hx - x
		delta_y = hy - y

		if delta_x > 0:
			closest_food_directions.append("north")
		if delta_x < 0:
			closest_food_directions.append("south")
		if delta_y > 0:
			closest_food_directions.append("west")
		if delta_y < 0:
			closest_food_directions.append("east")
		return _closest_food_directions

	@cache
	@property
	def children_redis_keys(self):
		return [child.redis_key for child in self.children]

	@property
	def children(self):
		children = []
		for my_move in self.children:
			children += self.children[my_move]
		return children

	@property
	def children_dict(self):

		# enumerate possible sensible move combinations for all snakes
		move_options = []
		for name in self.board.all_snake_names:
			choices = self.board.snake_choices(name)
			move_options.append([(name, (x, y)) for (x, y) in choices])
		possible_move_combinations = list(itertools.product(*move_options))

		# generate all children
		children = {}
		for move_set in possible_move_combinations:
			child = self._child_payload(move_set)
			if child.based_on_move not in self._children.keys():
				children[child.based_on_move] = []
			children[child.based_on_move].append(child)

		return children

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
		return new_payload