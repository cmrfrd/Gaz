from time import sleep
from multiprocessing import Process

class player(object):
	def __init__(self, board, piece, auto, dirs, lc, op, rh, nor, pause):
		Process.__init__(self)
		self.board = board
		self.piece = piece
		self.auto = auto
		self.dirs = dirs
		self.lc = lc
		self.op = op
		self.rh = rh
		self.nor = nor
		self.pause = pause

	def run(self):#manipulate board and such to automatically play tetris!!!!
		lc = self.lc
		op = self.op
		rh = self.rh
		nor = self.nor

		print "First fun"

		time_const = 0.2
		movement_list = ["L","L","S"]
		while 1:
			self.pause.wait()
			print self.board
			for move in movement_list:
				if move == "L":op=[self.piece[:],lc[:]];lc[0]-=1
    	        		if move == "R":op=[self.piece[:],lc[:]];lc[0]+=1
    				if move == "D":op=[self.piece[:],lc[:]];lc[1]+=1;t=1
    				if move == "U" and self.piece:op=[self.piece[:],lc[:]];self.piece=[[self.piece[x][-y-1] for x in range(len(self.piece))] for y in range(len(self.piece[0]))];nor=1
    				if move == "S":rh=1
				sleep(time_const)

	def sliced_board(self, n):#generator to get board slices based on piece length
		for i in range(len(self.board)-n):
			yield self.board[i:i+n]
