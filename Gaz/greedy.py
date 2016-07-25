from tetris_infastructure import get_piece_rotation, get_all_moves
from time import sleep
import json

#a bunch of scoring functions I tried...
#in order are the ones that worked best

def score_space(board):
    return float(board.full_rows) / (board.total_spaces + board.max + 1)

def score(board):
    
    numer = float(board.full_rows)
    denom = (board.max + board.min + board.average + board.mode + board.total_spaces + 1)

    return numer / denom

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
    def __init__(self, time_const=0.05):
        self.score_func = score_space
        self.time_const = time_const

    def get_next_move(self, board, piece):
        '''get all possible moves, score them, get the max
        '''
        scores = {}

        for move in get_all_moves(board, piece):

                #add the piece to the board
                board_with_piece = move["board"].calc_data()

                #calculate the score
                total_score = self.score_func(board_with_piece)

                scores[total_score] = (move["slice"]["index"], 
                                       get_piece_rotation(move["rotation"]["piece"]))

        best_move = scores[max(scores.keys())]

        sleep(self.time_const)

        return best_move

