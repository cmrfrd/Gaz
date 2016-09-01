from tetris_infastructure import get_piece_rotation, get_all_moves
from time import sleep
import json
from math import e

#a bunch of scoring functions I tried...
#in order are the ones that worked best

def score_space(board):
    return (float(board.full_rows) / (board.total_spaces + board.max + 1)) + board.mode

def no_spaces(board):
    return 1.0/(board.max + board.total_spaces + 1)

def score_1(board):
    return float(board.full_rows) / (board.max + board.total_spaces)

def score_2(board):
    return board.row_completeness / (board.max + board.min + board.total_spaces + 1)

def bad_score(board):
    return board.full_rows * e**-(board.total_spaces + board.max + board.min + board.average + board.mode)

def bad_score_2(board):
    return ((board.max / (board.average + board.mode + board.total_spaces)) / board.min)

def bad_score_3(board):
    return float(board.full_rows) ** -(board.max + board.min + board.average + board.mode + board.total_spaces + 1)

def bad_score_4(board):
    return (board.max + board.min + board.average + board.mode + board.total_spaces + 1) % board.full_rows

def bad_score_5(board):
    return (float(board.min)/board.max) * (board.full_rows/(board.total_spaces+1))

def bad_score_6(board):
    return (board.min/float(board.max)) * (board.mode/board.average) * (board.full_rows/(float(board.total_spaces)+1))

class greedy(object):
    '''greedy implements a greedy algorithm
    '''
    def __init__(self, time_const=0.01):
        self.score_func = score_1
        self.time_const = time_const

    def get_next_move(self, board, piece, piece_number):
        '''get all possible moves, score them, get the max
        '''
        moves = get_all_moves(board, piece)

        best_move = max(moves, key=lambda m:self.score_func(m["board"].calc_data(True)))

        best_move = (best_move["slice"]["index"], 
                      get_piece_rotation(best_move["rotation"]["piece"]))

        sleep(self.time_const)

        return best_move

