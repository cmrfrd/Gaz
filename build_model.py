from KNN import Game_Reader, k_nearest_neighbors
from tetris_player import Board, tetris_shapes
import json
from collections import OrderedDict

def get_piece_index(shape):
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

reader = Game_Reader(tetris_shapes, Board)
reader.read_games(13)
reader.feature_scale_data()



b = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [5, 0, 0, 0, 0, 0, 0, 0, 0, 0], [5, 0, 3, 3, 0, 0, 6, 0, 0, 0], [5, 5, 5, 3, 3, 0, 6, 0, 2, 0], [5, 5, 5, 1, 1, 1, 6, 0, 2, 2], [5, 5, 5, 5, 1, 1, 1, 0, 3, 3], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
for i in b:print i

next_piece = tetris_shapes[2]
for i in next_piece:print i

current_state_vector = reader.feature_dict_from_board( zip(*b) ).values()
move = k_nearest_neighbors(10, reader.dataset, get_piece_index(next_piece[:]), current_state_vector)
print move


def rotate_clockwise(shape):
	return [ [ shape[y][x]
			for y in xrange(len(shape)) ]
		for x in xrange(len(shape[0]) - 1, -1, -1) ]

b = Board(zip(*b))

for i in range(move[1]):
    next_piece = rotate_clockwise(next_piece)

b = b.fake_add(move[0], next_piece)
for i in zip(*b):print i
