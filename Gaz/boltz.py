from tetris_infastructure import get_all_moves, get_piece_index
from game_reader import game_reader

from math import sqrt, exp, pi, log
from time import sleep

def dot(A, B):
    '''Provided 2 lists, return the dot product
    '''
    if len(A) != len(B):
        return 0
    return sum(i[0] * i[1] for i in zip(A, B))

def Q(weights, state):
    '''
    Provided the vectors weights, and state
    return the dot product
    '''
    return dot(weights, state)

def l(weights, future_state):
    '''
    Provided the vector weights, and state
    return the exp of Q(weights, future)
    '''
    return exp(Q(weights, future_state))

def Z(weights, state, piece):
    '''
    given vector weights and current board, and piece
    return the sum of all l() iterating over each move
    '''
    total = 0
    for future_move in get_all_moves(state, piece):
        future_vector = future_move["board"].get_feature_dict().values()
        total += l(weights, future_vector)
    return total

def q(weights, current_state, future_state, piece):
    '''
    given vector weights, the current board, and a piece,
    get the percent quality of the future move
    '''
    return l(weights, future_state) / Z(weights, current_state, piece)

def score_ratio(weights, current_state, piece, future_state):
    '''
    given vector weights, the current board, future board,
    and the piece get the score ratio. Score ratio is the
    future state, minus the 
    '''
    total = 0
    for future_move in get_all_moves(current_state, piece):
        future_board = future_move["board"]
        future_vector = future_board.get_feature_dict().values()
        total += Q(weights, future_vector) * q(weights, current_state, future_board, piece)
    return future_state.get_feature_dict().values() - total

class boltz(object):
    '''implementation of boltzman distribution with gradient descent
    '''
    def __init__(self, modelname, time_const=0.01):
        self.reader = game_reader()
        #self.model = self.reader.read_model(modelname)
        self.time = time_const

        self.var_init = False
        self.z = None
        self.delta = None
        self.weights = None

    def update_z(self, beta, weights, current_state, piece, chosen_future_state):
        self.z = (beta * self.z) + score_ratio(weights, current_state, piece, chosen_future_state)
        return self.z

    def update_delta(self, piece_number, weights, current_state, piece, chosen_future_state):
        z_args = (1, weights, current_state, piece, chosen_future_state)

        left_term = self.delta
        right_term = (piece_number / (piece_number + 1)) * ((chosen_future_state.full_rows * self.update_z(*z_args)) - self.delta)

        self.delta = left_term + right_term
        return self.delta

    def update_weights(self, alpha, piece_number, weights, current_state, piece, chosen_future_state):
        '''
        Provided an 'nth piece', and appropriate arguments, update
        the vector weights by theta = theta + alpha*delta
        '''
        delta = self.update_delta(piece_number, weights, current_state, piece, chosen_future_state)
        self.weights = self.weights + (alpha * delta)
        return self.weights

    def init_vectors(self, board):
        if not self.var_init:
            if self.z == None:
                self.z = [0 for i in range(len(board.get_feature_dict().values()))]
            if self.delta == None:
                self.delta = [0 for i in range(len(board.get_feature_dict().values()))]
            if self.weights == None:
                self.weights = [1 for i in range(len(board.get_feature_dict().values()))]

    def get_next_move(self, board, piece, piece_number):
        '''
        Using a boltzman distribution, and gradient descent, update
        a set of weights
        '''    
        self.init_vectors(board)

        
        #for move in get_all_moves(board, piece):
        #    possible_future = move["board"].calc_data(True)
        #    self.update_weights(1, piece_number, self.weights, board, piece, possible_future)
