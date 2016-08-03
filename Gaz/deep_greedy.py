from tetris_infastructure import get_piece_rotation, get_all_moves, tetris_shapes

from time import sleep
from math import e

#a bunch of scoring functions I tried...
#in order are the ones that worked best

def score_space(board):
    return (float(board.full_rows) / (board.total_spaces + board.max + 1)) + board.mode

def no_spaces(board):
    return 1.0/(board.max + board.total_spaces + 1)

def score_1(board):
    return float(board.full_rows) / (board.max + board.total_spaces)

class deep_greedy(object):
    '''deep greedy implements a greedy algorithm with multiple layers
    '''
    def __init__(self, depth=2, time_const=0.01):
        self.score_func = score_1
        self.time_const = time_const
        self.depth = depth

    def get_branch_scores(self, layer, total_score, board):
        '''get all possible moves, score them, get the max
        '''
        if layer <= 0:
            return self.score_func(board)
        else:
            pass#total_score += self.score_func(board)

        for future_piece in tetris_shapes:
            for move in get_all_moves(board, future_piece):
                total_score += self.get_branch_scores(
                                   layer - 1,
                                   total_score,
                                   move["board"].calc_data()
                               )
        return total_score

    def get_next_move(self, board, piece):
        '''Given a depth greedy search a tree
        '''

        branch_scores = {}
        for move in get_all_moves(board, piece):
            score = self.get_branch_scores(
                          self.depth, 
                          0,
                          move["board"].calc_data(), 
                     )
            branch_scores[score] = (move["slice"]["index"], 
                                   get_piece_rotation(move["rotation"]["piece"]))
        
        sleep(self.time_const)
        return branch_scores[max(branch_scores.keys())]

        

