from time import sleep
from threading import Thread, Event

tetris_shapes = [
        [[1, 1, 1],
         [0, 1, 0]],

        [[0, 2, 2],
         [2, 2, 0]],

        [[3, 3, 0],
         [0, 3, 3]],

        [[4, 0, 0],
         [4, 4, 4]],

        [[0, 0, 5],
         [5, 5, 5]],

        [[6, 6, 6, 6]],

        [[7, 7],
         [7, 7]]
]

rotations_by_index = {#number of rotations manually by piece location above
	6:1,
	1:2,2:5,5:2,
	0:4,3:4,4:4
}

def remove_row(board, row):
        del board[row]
        return [[0 for i in xrange(cols)]] + board

def rotate_clockwise(shape):
        return [ [ shape[y][x]
                        for y in xrange(len(shape)) ]
                for x in xrange(len(shape[0]) - 1, -1, -1) ]

def check_collision(board, shape, offset):
        off_x, off_y = offset
        for cy, row in enumerate(shape):
                for cx, cell in enumerate(row):
                        try:
                                if cell and board[ cy + off_y ][ cx + off_x ]:
                                        return True
                        except IndexError:
                                return True
        return False

def join_matrixes(mat1, mat2, mat2_off):
        off_x, off_y = mat2_off
        for cy, row in enumerate(mat2):
                for cx, val in enumerate(row):
                        mat1[cy+off_y-1 ][cx+off_x] += val
        return mat1

class Row(list):
	def __init__(self, row_list):
		list.__init__(self, row_list)
		self.is_complete = all(row_list)

class Column(list):
	def __init__(self, col_list):
		list.__init__(self, col_list)
		self.height_gap = False
		self.height = False
		self.spaces = False

	def __eq__(self, other_col_list):
		return self == other_col_list

	def calc_data(self, update=False):#calculates or updates data
		if not self.height_gap or update:
			self.calc_height_gap()
		if not self.height or update:
			self.height = len(self) - self.height_gap
		if not self.spaces or update:
			self.spaces = self.count(0) - self.height_gap
		return self

	def calc_height_gap(self):
		for i,j in enumerate(self):
			if j != 0:
				self.height_gap = i
				break

class Board(list):
	def __init__(self, board_list):
		list.__init__(self, [Column(col).calc_data() for col in board_list])
		self.max = False
		self.average = False
		self.mode = False
		self.total_spaces = False
		self.full_rows = False
		self.is_cols = True

	def invert(self, eq=False):
		if eq:
			if self.is_cols:
				self = [Row(row) for row in zip(*self)]
			else:
				self = [Column(col) for col in zip(*self)]
			self.is_cols = not self.is_cols
		else:
			if self.is_cols:
				return [Row(row) for row in zip(*self)]
			else:
				return [Column(col) for col in zip(*self)]				
		return self

	def calc_data(self, update=False):

		if not self.full_rows or update:
			self.full_rows = 1
			if len(zip(*self)[0]) == 10:
				for index, row in enumerate(zip(*self)):
					if all(row):
						self.full_rows += 1
						self.

		if not self.max or update:
			self.max = max(col.height for col in self)

		if not self.average or update:
			self.average = sum(col.height for col in self)/len(self)

		if not self.mode or update:
			heights = [col.height for col in self]
			self.mode = max(heights, key=heights.count)

		if not self.total_spaces or update:
			self.total_spaces = sum(col.calc_data(self.full_rows_locations, True).spaces for col in self)
		return self

	def data(self):
		print "Max: %d" % (self.max)
		print "Avg: %f" % (self.average)
		print "Mode: %d" % (self.mode)
		print "Spaces: %d" % (self.total_spaces)
		print "Rows: %d" % (self.full_rows)

	def calc_col_data(self):
		for col in self:
			col.calc_data(True)

	def slice_iter(self, width):#iterator that returns a "board" object
		for col in range(len(self)-width+1):
			yield (col, Board(self[col:col+width][:]))

	def fake_add(self, x, piece):#takes a piece at an x coordinate and returns a board object with that piece "insta dropped"
		row_board = [list(row) for row in zip(*self)]#make the cols into rows again
		
		for y in range(1, len(row_board)):
			if check_collision(row_board, piece, (x, y)):
				return Board(zip(*join_matrixes(row_board, piece, (x, y))))

	def score(self):
		return float(self.full_rows) / (self.max + self.average + self.mode + self.total_spaces + 1)

class player_process(Thread):
    def __init__(self, app):
        Thread.__init__(self)
	self.exit = Event()
	self.app = app

    def get_rotations(self, shape):#iter through each rotoation of a shape
	shape = shape
	for r in range(3):
	 	try:
			rotations = rotations_by_index[tetris_shapes.index(shape)]#gets the number of rotations manually
		except ValueError:
			shape = rotate_clockwise(shape)

	rotated_shape = shape
	for r in range(rotations):
		rotated_shape = rotate_clockwise(rotated_shape)
		yield rotated_shape

    def simple_play(self):
	board = Board(zip(*self.app.board))
	scores = {}

	for rotated_stone in self.get_rotations(self.app.stone):#iter through each rotation

		for slice_index, slice in board.slice_iter(len(zip(*rotated_stone))):#iter through each slice				

			slice_without_piece = slice.calc_data()
			board_without_piece = board.calc_data()	
			#renaming for ease of use

			slice_with_piece = slice.fake_add(0, rotated_stone).calc_data()
			board_with_piece = board.fake_add(slice_index, rotated_stone).calc_data()			

			#without_score = slice_without_piece.score() + board_without_piece.score()
			with_score = slice_with_piece.score() + board_with_piece.score()
			total_score = with_score

			for i in board_with_piece:print i
			print board.data()
			print total_score
	
			scores[total_score] = (slice_index, rotated_stone)
		
	best_move = scores[max(scores.keys())]

	#for i in board:print i
	#print max(scores.keys()), best_move
	#print '\n'
		
	while self.app.stone != best_move[1] and not self.app.gameover:
		self.app.rotate_stone()
		
	move_int = best_move[0] - self.app.stone_x
	self.app.move(move_int)
		
	self.app.insta_drop()

	sleep(1)

    def run(self):
	debug = True
	player_pieces_processed = 0

	while not self.exit.is_set() and self.app.auto.wait():
		
		#this statement is to make sure each piece is only processed once
		#compares the number of pieces processed by the game and by the player
		if self.app.pieces_processed != player_pieces_processed:
			player_pieces_processed += 1
			continue
		
		self.simple_play()
		
		player_pieces_processed += 1
		#sleep(0.5)
	print "process has ended"

    def debug(self):
	print "======DEBUG MODE======"
	
	print "BOARD"
	for i in self.app.board:print i		

	print "CURRENT PIECE"
	for i in self.app.stone:print i

	#print "NEXT PIECE"
	#for i in self.app.next_stone:print i

    def shutdown(self):
	print "executing shutdown"
        self.exit.set()
	self.app.auto.set()
