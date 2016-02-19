import settings
from utils import subtract_vectors


class BaseBoard(object):

	def __init__(self, payload):
		self.payload = payload
		self._cells = {}
		self.game_name = self.payload.get("game") if self.payload else ""

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
			x, y = coord
			if self.get((x, y), 'empty'):
				yield coord

	def valid_moves(self):
		moves = []
		for coord in self.adjacent_empty_cells(self.head()):
			delta = subtract_vectors(coord, self.head())
			direction = settings.DIRECTION_STRINGS[delta]
			moves.append(direction)

		print "valid moves: %s" % moves
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

