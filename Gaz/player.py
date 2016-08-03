from time import sleep
from threading import Thread, Event
from tetris_infastructure import Board

from KNN import KNN
from greedy import greedy
from deep_greedy import deep_greedy

class no_brain(object):
	def __init__(self):
		pass
	def get_next_move(self, board, piece):
		raise NotImplementedError("No brain has been provided to Gaz")

class player(Thread):
	def __init__(self, app, **kwargs):
		Thread.__init__(self)
		self.exit = Event()
		self.app = app
		self.player_brain = no_brain()

		if kwargs["knn_modelname"]:
			self.player_brain = KNN(kwargs["knn_modelname"])
		elif kwargs["greedy"]:
			self.player_brain = greedy()
		elif isinstance(kwargs["dgreedy"], int):
			self.player_brain = deep_greedy(kwargs["dgreedy"])

	def execute_move(self, move, time=0.01):
		'''executes move based on tuple (x_coord, rotations)
		'''
		assert move[0] in range(len(self.app.board)),"X coord not in range of board"

		try:
		    #execute the number of rotations
                    for i in range(move[1]):
                        self.app.rotate_piece()

		    #move to the appropriate coordinate
		    move_int = move[0] - self.app.piece_x
		    self.app.move(move_int)
		
		    self.app.insta_drop()

		except Exception, e:
                    return False

		sleep(time)
		return True

	def run(self):
		debug = True
		player_pieces_processed = 0

		while self.app.auto.wait() and not self.exit.is_set() and  not self.app.gameover:

			#make sure player and game are in sync with pieces processed
			if self.app.pieces_processed > player_pieces_processed:
				player_pieces_processed += 1
				continue

			#Create new board and piece object for player to injest
			board = Board(zip(*self.app.board))
			piece = self.app.piece

			move = self.player_brain.get_next_move(board, piece)

			if self.execute_move(move):
				player_pieces_processed += 1
			
		print "process has ended"

	def shutdown(self):
		print "executing shutdown"
		self.app.auto.set()
		self.exit.set()
