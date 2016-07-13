from time import sleep
from threading import Thread, Event
from KNN import Game_Reader, k_nearest_neighbors
from math import e

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

cols = 10
rows = 22

rotations_by_index = {#number of rotations by index of piece in tetris shapes
	6:1,
	1:2,2:5,5:2,
	0:4,3:4,4:4
}

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
	def __init__(self, row):
		list.__init__(self, row)
		self.is_full = all(row)

class Column(list):
	def __init__(self, col_list):
		list.__init__(self, col_list)
		self.height_gap = False
		self.height = False
		self.spaces = False

	def __eq__(self, other_col_list):
		return self == other_col_list

	def remove_space(self, index):
		if index in range(len(self)):
			del self[index]
			return [0] + self
		return self

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
		if isinstance(board_list, Board):
			self = board_list
		else:
			list.__init__(self, [Column(col).calc_data() for col in board_list])

		self.max = False
		self.min = False
		self.average = False
		self.mode = False
		self.total_spaces = False
		self.full_rows = False
		self.row_completeness = False

	def invert(self):
		return [list(row) for row in zip(*self)]
	
	def calc_data(self, update=False):		
		if not self.full_rows or self.row_completeness or update:
			self.full_rows = 1
			self.row_completeness = 1

			row_board = self.invert()							#get the board in row format
			if len(row_board[0]) == cols:							#when the board isn't a slice
				for index, row in enumerate(row_board[:-1:-1]):				#loop through each row bottom first

					perc_complete = float(len(row) - row.count(0)) / len(row)       #get the percent complete of the row
					row_complete = perc_complete / (index + 1)                      #the lower the row is more complete the higher the score
					self.row_completeness += row_complete
				
				for index, row in enumerate(row_board[:-1:-1]):
					if all(row):							#if the row is complete
						for col in self:col.remove_space(index)			#delete that space in each column
						self.full_rows += 1 					#increment the number of rows

				self.row_completeness /= rows
					
		if not self.max or update:
			self.max = max(col.height for col in self)
		if not self.min or update:
			self.min = min(col.height for col in self)
		if not self.average or update:
			self.average = sum(col.height for col in self)/len(self)
		if not self.mode or update:
			heights = [col.height for col in self]
			self.mode = max(heights, key=heights.count)
		if not self.total_spaces or update:
			self.total_spaces = sum(col.spaces for col in self)
		return self

	def data(self):
		print "Max: %d" % (self.max)
		print "Avg: %f" % (self.average)
		print "Mode: %d" % (self.mode)
		print "Spaces: %d" % (self.total_spaces)
		print "Rows: %d" % (self.full_rows)
		print "Comp: %f" % (self.row_completeness)

	def calc_col_data(self):
		for col in self:
			col.calc_data(True)

	def slice_iter(self, width):#iterator that returns a "board" object

		assert 1 <= width <= len(self)

		for col in range(0, len(self) - width + 1):
			yield (col, Board(self[col:col+width][:]))

	def fake_add(self, x, piece):#takes a piece at an x coordinate and returns a board object with that piece "insta dropped"
		row_board = self.invert()								#get the board in col format
 
		assert x in [0]+range(len(self) - len(zip(*piece)) + 1)					#make x coord is within bounds
		
		for y in range(1, len(row_board)):							#loop through index's of row_board
			if check_collision(row_board, piece, (x, y)):					#if there is a collision at "y"
				row_board_with_piece = join_matrixes(row_board, piece, (x, y))		#add the piece to the board
				return Board(zip(*row_board_with_piece))				#return new Board in original format

class player_process(Thread):
	def __init__(self, app):
		Thread.__init__(self)
		self.exit = Event()
		self.app = app

	def slice_score(self, slice):return 0
	def score(self, board):return (float(board.full_rows)) / (board.max + board.min + board.average + board.mode + board.total_spaces + 1)
	def score_2(self, board):
		return board.row_completeness

	def bad_score(self, board):return board.full_rows * e**-(board.total_spaces + board.max + board.min + board.average + board.mode)
	def bad_score_2(self, board):return ((board.max / (board.average + board.mode + board.total_spaces)) / board.min)
	def bad_score_3(self, board):return float(board.full_rows) ** -(board.max + board.min + board.average + board.mode + board.total_spaces + 1)
	def bad_score_4(self, board):return (board.max + board.min + board.average + board.mode + board.total_spaces + 1) % board.full_rows
	def bad_score_5(self, board):return (float(board.min)/board.max) * (board.full_rows/(board.total_spaces+1))
	def bad_score_6(self, board):return (board.min/float(board.max)) * (board.mode/board.average) * (board.full_rows/(float(board.total_spaces)+1))

	def get_piece_index(self, shape):
		'''Since tetris piece variables are morphed in place, we need to keep rotating them to get their index
		'''
		rotations = 0
		index = -1
		for r in range(3):
			try:
				index = tetris_shapes.index(shape)
			except ValueError:
				shape = rotate_clockwise(shape)
		return index

	def get_rotations(self, shape):#iter through each rotoation of a shape
		#shape = shape
		rotations = 0
		rotations = rotations_by_index[self.get_piece_index(shape)]#gets the number of rotations manually
		
		rotated_shape = shape
		for r in range(rotations):
			rotated_shape = rotate_clockwise(rotated_shape)
			yield rotated_shape

	def find_best_scored_move(self, board, piece, score_func, time=0.5):
		scores = {}
		for rotated_piece in self.get_rotations(piece):#iter through each rotation

			for slice_index, slice in board.slice_iter(len(zip(*rotated_piece))):#iter through each slice				

				slice_without_piece = slice.calc_data()
				board_without_piece = board.calc_data()	
				#renaming for ease of use

				slice_with_piece = slice.fake_add(0, rotated_piece).calc_data()
				board_with_piece = board.fake_add(slice_index, rotated_piece).calc_data()			
				#add the piece to the boards

				total_score = score_func(slice_with_piece) + score_func(board_with_piece)

				#print board_without_piece
				#print '\n'
				'''for i in board_without_piece:print i
				print '\n'
				for i in board_with_piece:print i
				board_with_piece.data()
				print total_score
				print (slice_index, rotated_piece)'''
		
				scores[total_score] = (slice_index, rotated_piece)
			
		best_move = scores[max(scores.keys())]
		sleep(time)
		return best_move

	def best_move_by_KNN(self, pieces, board, games=10, k=5):
		reader = Game_Reader(pieces, board)
		reader.read_games(games)
		reader.feature_scale_data()

		while not self.exit.is_set() and self.app.auto.wait() and not self.app.gameover:
			current_state_vector = reader.feature_dict_from_board( zip(*self.app.board) ).values()
			yield k_nearest_neighbors(k, reader.dataset, self.app.piece_num, current_state_vector)

	def execute_move(self, move, time=0.01):
		'''executes move based on tuple (rotation, x_coord)
		'''
		while self.app.piece != move[1] and not self.app.gameover:
			self.app.rotate_piece()
			
		move_int = move[0] - self.app.piece_x
		self.app.move(move_int)
			
		self.app.insta_drop()

		sleep(time)
		return True

	def run(self):
		debug = True
		player_pieces_processed = 0

		#To implement KNN uncomment line below as well as KNN line in while loop
		KNN_mover = self.best_move_by_KNN(tetris_shapes, Board)

		while not self.exit.is_set() and self.app.auto.wait() and not self.app.gameover:
			
			#this statement is to make sure each piece is only processed once
			#compares the number of pieces processed by the game and by the player
			if self.app.pieces_processed != player_pieces_processed:
				player_pieces_processed += 1
				continue
			
			#to have player think only one move ahead with one simple heuristic uncomment line below
			#move = self.find_best_scored_move(Board(zip(*self.app.board)), self.app.piece, self.score, 0.001)

			#to use KNN uncomment this line as well as instantiation of iterator before while loop
			move = KNN_mover.next()
			print move

			if self.execute_move(move):
				player_pieces_processed += 1
		print "process has ended"

	def debug(self):
		print "======DEBUG MODE======"
		print "BOARD"
		for i in self.app.board:print i		

		print "CURRENT PIECE"
		for i in self.app.piece:print i

		#print "NEXT PIECE"
		#for i in self.app.next_piece:print i

	def shutdown(self):
		print "executing shutdown"
		self.exit.set()
		self.app.auto.set()
