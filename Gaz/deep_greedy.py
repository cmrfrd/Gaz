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
    def __init__(self, depth=1, top_n=2, time_const=0.01):
        self.score_func = score_1
        self.time_const = time_const
        self.depth = depth
        self.top_n = top_n

    def get_move_tuple(self, move):
        '''returns a move tuple from a move dict object
        '''
        return (move["slice"]["index"], 
                get_piece_rotation(move["rotation"]["piece"]))

    def top_n_moves(self, board, piece, n=3):
        '''Get the top n moves given a scoring function
        '''
        scores = {}
        for move in get_all_moves(board, piece):
            end_move = self.get_move_tuple(move)
            score = self.score_func(move["board"].calc_data())
            scores[score] = move
        
        return [m[1] for m in sorted(scores.iteritems(), key=lambda m:m[0])[-n:]]

    def get_branch_scores(self, layers, board, total_score=0, top_n=3):
        '''get all top n scores of moves
        '''
        if layers == 0:
                return self.score_func(board)
        else:
                total_score += self.score_func(board)

        for future_piece in tetris_shapes:
            for move in self.top_n_moves(board, future_piece, self.top_n):
                total_score += self.get_branch_scores(
                                   layers - 1,
                                   move["board"],
                                   total_score,
                                   top_n
                               )
        return total_score

    def get_next_move(self, board, piece):
        '''Given a depth greedy search a tree
        '''
        branch_scores = {}

        for move in self.top_n_moves(board, piece, self.top_n):
            score = self.get_branch_scores(      
                          self.depth,
                          move["board"],
                          top_n=self.top_n
                    )
            branch_scores[score] = (move["slice"]["index"], 
                                   get_piece_rotation(move["rotation"]["piece"]))
        
        sleep(self.time_const)
        return branch_scores[max(branch_scores.keys())]
