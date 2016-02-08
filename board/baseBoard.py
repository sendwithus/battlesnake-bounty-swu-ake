import settings


class BaseBoard(object):

	def __init__(self, payload):
		self.payload = payload
		self._cells = {}
		self.game_name = self.payload.get("game")

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
			if 0 <= x < self.width and 0 <= y < self.height:
				yield (x, y)

	def adjacent_empty_cells(self, v):
		for coord in self.adjacent_cells(v):
			x, y = coord
			if not self.get((x, y), 'solid'):
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

