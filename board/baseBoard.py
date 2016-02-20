import settings
from utils import subtract_vectors
import copy

class BaseBoard(object):

	def __init__(self, payload):
		self.payload = payload
		self._cells = {}
		self.game_name = self.payload.get("game") if self.payload else ""
		self.load_payload(payload)

	def load_payload(self, payload):
		print "loading payload"

		# add food
		for coord in self.food:
			self.set(tuple(coord), "food", True)

		# add snakes
		self.other_snakes = []
		self.other_snake_names = []
		self._snakes = self.payload.get("snakes", [])
		print list(self.all_snakes)
		for snake in self.all_snakes:
			snake_status = snake.get("status", "dead")
			snake_length = len(snake.get("coords", []))
			snake_name = snake.get("name", "")
			if snake_status == "alive" and snake_length > 0:
				ttl = 1
				snake_coords = copy.deepcopy(snake.get("coords", []))
				snake_coords.reverse()
				print "looking at: %s" % snake_coords
				for coord in snake_coords:
					coord = tuple(coord)
					self.set(coord, "empty", False)
					self.set(coord, "controlled_by", snake_name)  # get snake UUID
					self.set(coord, "ttl", ttl)
					print "%s: %s" % (coord, self._cells[coord])
					ttl += 1
				head = tuple(snake_coords[-1])
				self.set(head, "head", True)
				self.set(head, "distance", 0)

			# store each snake
			if snake_name == settings.SNAKE_NAME:
				self._me = snake
			else:
				self.other_snake_names.append(snake.get("name", ""))

		for coord in payload.get("walls", []):
			self.set(coord, "empty", False)

	def set(self, coord, attr, val):
		if coord not in self._cells.keys():
			self._cells[coord] = {}
		self._cells[coord][attr] = val

	def get(self, coord, attr):
		cell = self._cells.get(coord)
		if cell:
			val = cell.get(attr)
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
	def width(self):
		return self.payload.get("width", [])

	@property
	def height(self):
		return self.payload.get("height", [])

	@property
	def food(self):
		return self.payload.get("food", [])

	@property
	def all_snakes(self):
		for s in self._snakes:
			yield s

	@property
	def all_snake_names(self):
		for s in self.all_snakes:
			yield s.get('name')

	@property
	def all_snake_ids(self):
		for s in self.all_snakes:
			yield s.get('id')

	def head(self, name=None):
		if name:
			for s in self.all_snakes:
				if s.get("name") == name:
					return s.get("coords", [])[0]
		for s in self.all_snakes:
			if s.get("id") == settings.SNAKE_ID:
				return s.get("coords", [])[0]

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
			if 0 <= x < self.width and 0 <= y < self.height:
				yield (x, y)

	def adjacent_empty_cells(self, v):
		for coord in self.adjacent_cells(v):
			empty = self.get(coord, 'empty')
			print "%s empty? %s" % (coord, empty)
			if self.get(coord, 'empty'):
				yield coord

	def valid_moves(self):
		moves = []
		for coord in list(self.adjacent_empty_cells(self.head())):
			delta = subtract_vectors(coord, self.head())
			direction = settings.DIRECTION_STRINGS.get(delta)
			if direction:
				moves.append(direction)

		print "heads: %s" % self.head()
		print "adjacent_cells: %s" % list(self.adjacent_empty_cells(self.head()))
		print "valid moves: %s" % moves
		if len(list(self.adjacent_empty_cells(self.head()))):
			print "%s: %s" % (coord, self._cells.get(coord))

		# print "payload:"
		# import pprint
		# pprint.pprint(self.payload)

		return moves


	def snake(self, snake_id):
		for snake in self._snakes:
			if snake.get("id", "") == snake_id:
				return snake

	def snake_choices(self, snake_id=None):
		if not snake_id:
			snake_id = settings.SNAKE_ID

		head = self.snake(snake_id).get('coords')[0]
		return self.adjacent_empty_cells(head)

	def add_vectors(self, v1, v2):
		(x1, y1) = v1
		(x2, y2) = v2
		return x1+x2, y1+y2

