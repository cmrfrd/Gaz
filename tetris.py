#!/usr/bin/env python2
# Control keys:
#       Down - Drop piece faster
# Left/Right - Move piece
#         Up - Rotate piece clockwise
#     Escape - Quit game
#          P - Pause game
#     Return - Instant drfrom random import randrange as rand
import pygame, sys
from threading import Event
import threading
from random import randrange as rand
from copy import deepcopy
import datetime
import csv
import os
from os.path import abspath, dirname, realpath
import argparse

from Gaz import player
from Gaz.tetris_infastructure import Board


game_filepath = "/Gaz/gameplays/" 

# The configuration
cell_size =	19
cols =		10
rows =		20
maxfps = 	30

colors = [
(0,   0,   0  ),
(255, 85,  85),
(100, 200, 115),
(120, 108, 245),
(255, 140, 50 ),
(50,  120, 52 ),
(146, 202, 73 ),
(150, 161, 218 ),
(0,  0,  0)
]

# Define the shapes of the single parts
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

def remove_row(board, row):
	del board[row]
	return [[0 for i in xrange(cols)]] + board
	
def join_matrixes(mat1, mat2, mat2_off):
	off_x, off_y = mat2_off
	for cy, row in enumerate(mat2):
		for cx, val in enumerate(row):
			mat1[cy+off_y-1	][cx+off_x] += val
	return mat1

def new_board():
	board = [ [ 0 for x in xrange(cols) ]
			for y in xrange(rows) ]
	board += [[ 1 for x in xrange(cols)]]
	return board

class TetrisApp(object):

	def __init__(self, start_auto=False, screen=True, record=False, **kwargs):

		if screen:
			self.init_gui()

		self.width = cell_size*(cols+6)
		self.height = cell_size*rows
		self.rlim = cell_size*cols
		self.bground_grid = [[ 8 if x%2==y%2 else 0 for x in xrange(cols)] for y in xrange(rows)]

		#set screen if flag is provided
		self.screen = pygame.display.set_mode((self.width, self.height)) if screen else None

		#record flag, record list that stores moves including pieces processed and the rotation
		self.record = record
     		self.record_list = []
		self.pieces_processed = 0
		self.rotation = 0

		#initialize the game and important values
		self.next_piece = tetris_shapes[rand(len(tetris_shapes))]
		self.init_game()

		#create the 'auto' event triggered by left shift
		self.auto = Event()

		#create the "player" object which will be triggered on left shift or by argument
		self.player = player(self, **kwargs)

		#flips 'auto' event to start in auto mode
		if start_auto:
			self.flip_auto()		

		self.loop = kwargs["loop"]

	def init_gui(self):
		pygame.init()
		pygame.key.set_repeat(250,25)
		self.default_font = pygame.font.Font(pygame.font.get_default_font(), 12)
		pygame.event.set_blocked(pygame.MOUSEMOTION) #we do not need

	def get_piece_index(self, shape):
		'''
		Rotate a shape max 4 times to find it's index
		'''
		rotations = 0
		index = -1
		for r in range(4):
			try:
				index = tetris_shapes.index(shape)
			except ValueError:
				shape = rotate_clockwise(shape)
		return index
	
	def new_piece(self):
		self.piece = self.next_piece[:]
		self.piece_num = rand(len(tetris_shapes))
		self.next_piece = tetris_shapes[self.piece_num]

		self.piece_x = int(cols / 2 - len(self.piece[0])/2)
		self.piece_y = 0
		
		if check_collision(self.board,
		                   self.piece,
		                   (self.piece_x, self.piece_y)):
			self.gameover = True
	
	def init_game(self):
		self.board = new_board()
		self.new_piece()
		self.level = 1
		self.score = 0
		self.lines = 1
		self.pieces_processed = 0
		pygame.time.set_timer(pygame.USEREVENT+1, 1000)
	
	def disp_msg(self, msg, topleft):
		x,y = topleft
		for line in msg.splitlines():
			self.screen.blit(
				self.default_font.render(
					line,
					False,
					(255,255,255),
					(0,0,0)),
				(x,y))
			y+=14
	
	def center_msg(self, msg):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  self.default_font.render(line, False,
				(255,255,255), (0,0,0))
		
			msgim_center_x, msgim_center_y = msg_image.get_size()
			msgim_center_x //= 2
			msgim_center_y //= 2
		
			self.screen.blit(msg_image, (
			  self.width // 2-msgim_center_x,
			  self.height // 2-msgim_center_y+i*22))
	
	def draw_matrix(self, matrix, offset):
		off_x, off_y  = offset
		for y, row in enumerate(matrix):
			for x, val in enumerate(row):
				if val and val in range(len(colors)):
					pygame.draw.rect(
						self.screen,
						colors[val],
						pygame.Rect(
							(off_x+x) *
							  cell_size,
							(off_y+y) *
							  cell_size, 
							cell_size,
							cell_size),0)
	
	def add_cl_lines(self, n):
		linescores = [0, 40, 100, 300, 1200]
		self.lines += n
		self.score += linescores[n] * self.level
		if self.lines >= self.level*6:
			self.level += 1
			newdelay = 1000-50*(self.level-1)
			newdelay = 100 if newdelay < 100 else newdelay
			pygame.time.set_timer(pygame.USEREVENT+1, newdelay)
	
	def move(self, delta_x):
		if not self.gameover and not self.paused:
			new_x = self.piece_x + delta_x
			if new_x < 0:
				new_x = 0
			if new_x > cols - len(self.piece[0]):
				new_x = cols - len(self.piece[0])
			if not check_collision(self.board,
			                       self.piece,
			                       (new_x, self.piece_y)):
				self.piece_x = new_x

	def quit(self):
		#if the record flag is set, record the gameplay
		if self.record or self.record == "":
			filepath = dirname(realpath(__file__)) + game_filepath
			if self.record == "":
				filepath += datetime.datetime.now().strftime("%Y-%m-%d|%H:%M:%S") + \
				            "-" + \
				            str(self.pieces_processed) + \
					    ".csv"
			else:
				filepath += self.record + ".csv"

			#write the output of the record list into a csv file. Easy peasy

			with open(filepath, "wb") as record_file:
				csv_file_writer = csv.writer(record_file, delimiter=":")
				for play in self.record_list:
					csv_file_writer.writerow(play)
				print "WTITING TO FILE"
		
		if self.loop > 0:
			self.loop -= 1
			print "Pieces: %d"%self.pieces_processed
			self.start_game()
			return None
			
		#shut down process when game quits
		self.player.shutdown()

		if self.screen:
			self.center_msg("Exiting...")		
			pygame.display.update()

		
		print "%d" % (self.pieces_processed)
		sys.exit()
	
	def drop(self, manual):
		if not self.gameover and not self.paused:
			self.score += 1 if manual else 0
			self.piece_y += 1
			if check_collision(self.board,
			                   self.piece,
			                   (self.piece_x, self.piece_y)):
				if self.record or self.record == "":
					piece_info = (self.piece, self.get_piece_index(self.piece))
					record = (self.piece_x, piece_info, self.rotation, deepcopy(self.board))

					self.record_list.append(record)

				self.board = join_matrixes(
				  self.board,
				  self.piece,
				  (self.piece_x, self.piece_y))

				self.new_piece()
				cleared_rows = 0
				while True:
					for i, row in enumerate(self.board[:-1]):
						if 0 not in row:
							self.board = remove_row(
							  self.board, i)
							cleared_rows += 1
							break
					else:
						break

				self.add_cl_lines(cleared_rows)
				self.pieces_processed +=1
				self.rotation = 0
				return True
		return False
	
	def insta_drop(self):
		if not self.gameover and not self.paused:
			while(not self.drop(True)):
				pass
	
	def rotate_piece(self):
		if not self.gameover and not self.paused:
			new_piece = rotate_clockwise(self.piece)
			if not check_collision(self.board,
			                       new_piece,
			                       (self.piece_x, self.piece_y)):

				if new_piece in tetris_shapes:self.rotation = 0 
				else: self.rotation += 1

				self.piece = new_piece
	
	def toggle_pause(self):
		self.paused = not self.paused
	
	def start_game(self):
		if self.gameover:
			self.init_game()
			self.gameover = False

	def flip_auto(self):
		if self.auto.is_set():
			self.auto.clear() 
		else:
			self.auto.set()

	def run(self):
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		lambda:self.drop(True),
			'UP':		self.rotate_piece,
			'p':		self.toggle_pause,
			's':	        self.start_game,
			'SPACE':	self.insta_drop,
			'LSHIFT':	self.flip_auto
		}
		
		self.gameover = False
		self.paused = False

		self.player.start()
		print "starting process"
		
		dont_burn_my_cpu = pygame.time.Clock()

		if self.screen:
			while 1:
				self.screen.fill((0,0,0))
				if self.gameover:
					self.center_msg("""Game Over!\nYour score: %d
Press space to continue""" % self.score)
					self.quit()
				else:
					if self.paused:
						self.center_msg("Paused")
					else:
						pygame.draw.line(self.screen,
							(255,255,255),
							(self.rlim+1, 0),
							(self.rlim+1, self.height-1))
						self.disp_msg("Next:", (
							self.rlim+cell_size,
							2))
						self.disp_msg("Score: %d\n\nLevel: %d\
							\nLines: %d" % (self.score, self.level, self.lines),
							(self.rlim+cell_size, cell_size*5))

						if self.auto.is_set():
							self.disp_msg("Press \n'Left Shift'\nfor Manual\nPlay", (self.rlim + cell_size, cell_size * 10))
							self.disp_msg("IN AUTO \nMODE", (self.rlim + cell_size, cell_size * 15))
						else:
							self.disp_msg("'Left Shift'\nfor Auto play", (self.rlim + cell_size, cell_size * 10))
							self.disp_msg("IN PLAYER \nMODE", (self.rlim + cell_size, cell_size * 15))
						

						self.draw_matrix(self.bground_grid, (0,0))
						self.draw_matrix(self.board, (0,0))
						self.draw_matrix(self.piece,
							(self.piece_x, self.piece_y))
						self.draw_matrix(self.next_piece,
							(cols+1,2))
				pygame.display.update()
			
				if not self.auto.is_set():
					for event in pygame.event.get():
						if event.type == pygame.USEREVENT+1:
							self.drop(False)
						elif event.type == pygame.QUIT:
							self.quit()
						elif event.type == pygame.KEYDOWN:
							for key in key_actions:
								if event.key == eval("pygame.K_"
								+key):
									key_actions[key]()
				else:
					for event in pygame.event.get():
						if event.type == pygame.USEREVENT+1:
							self.drop(False)
						elif event.type == pygame.QUIT:
							self.quit()
						elif event.type == pygame.KEYDOWN:
							for key in key_actions:
								if event.key == eval("pygame.K_"
								+key) and (key == "LSHIFT" or key == "p" or key == "ESCAPE"):
									key_actions[key]()
								
				dont_burn_my_cpu.tick(maxfps)

		else:
			self.auto.set()
			while 1:
				if self.gameover:
					#self.quit()					
					return self.pieces_processed			
				#for event in pygame.event.get():
				#	if event.type == pygame.USEREVENT+1:
				#		self.drop(False)
				#	elif event.type == pygame.QUIT:
				#		self.quit()
				#	elif event.type == pygame.KEYDOWN:
				#		for key in key_actions:
				#			if event.key == eval("pygame.K_"
				#			+key) and (key == "ESCAPE"):
				#				key_actions[key]()
				dont_burn_my_cpu.tick(maxfps)

parser = argparse.ArgumentParser(description='Plays tetris')

parser.add_argument('-gaz', action="store_true", default=False, dest="start_auto", help='Add -gaz for Gaz to take over')
parser.add_argument('-inv', action="store_false", default=True, dest="screen", help='Add -inv for screen to be invisible')
parser.add_argument('-r', default=False, const="", dest="record", nargs="?",  help='Add -r and the name of the name of the filename to record your gameplay. If no name provided a name will be generated based on the current datetime')
parser.add_argument('-knn', default=False, const="defaultmodel", dest="knn_modelname", nargs="?", help='Add this flag and a modelname to use KNN. If no model is provided "defaultmodel" will be used ')
parser.add_argument('-greedy', action="store_true", default=False, dest="greedy", help='Add this flag to use a greedy algorithm')
parser.add_argument('-dgreedy', action="store", dest="dgreedy", nargs=2, type=int, help="Add this flag to use a deep tree search greedy algorithm. The first argument is the layers or 'depth' the greedy algorithm will search, and the second argument is the 'skim' or the top n branch moves the algorithm should search further")
parser.add_argument('-naive', default=False, const="defaultmodel", dest="naive_modelname", nargs="?", help='This flag uses the naive bayes classifier to play tetris')
parser.add_argument('-boltz', action="store_true", default=False, dest="boltz", help='boltz is a brain type that will play tetris')
parser.add_argument('-loop', default=0, dest="loop", action="store", type=int, help="How many loops you want the game to run for")
parser.add_argument('-train', action="store_true", default=False, dest="train", help='Use this flag in conjunction with gaz to train models')

if __name__ == '__main__':
	args = parser.parse_args()
	kwargs = dict(args._get_kwargs())

	App = TetrisApp(**kwargs)
	App.run()
	App.quit()
