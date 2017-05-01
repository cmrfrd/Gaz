from tetris_infastructure import get_all_moves, get_piece_index, get_piece_rotation
from game_reader import game_reader

from math import sqrt, exp, pi, log
from time import sleep

def dot(A, B):
    '''Provided 2 lists, return the dot product
    '''
    if len(A) != len(B):
        return 0
    return sum(float(i[0]) * i[1] for i in zip(A, B))

def Q(weights, state):
    '''
    Provided the vectors weights, and state
    return the dot product
    '''
    return dot(weights, state)

def grad_Q(weights, state):
    '''
    Returs the gradient of quality of a state
    '''
    return state

def l(weights, future_state):
    '''
    Provided the vector weights, and state
    return the exp of Q(weights, future)
    '''
    return exp(Q(weights, future_state))

def grad_l(weights, future_state):
    '''
    return the gradient l 
    '''
    grad_l = future_state
    scalar = l(weights, future_state)
    for i in range(len(grad_l)):
        grad_l[i] *= scalar
    return grad_l

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

def grad_Z(weights, state, piece):
    '''
    sum all l values into one vector given the state and the piece
    '''
    gradZ = [0 for i in range(len(weights))]
    for future_move in get_all_moves(state, piece):
        future_vector = future_move["board"].get_feature_dict().values()
        gradlj = grad_l(weights, future_vector)
        
        # sum components together
        for i in range(len(gradlj)):
            gradZ[i] += gradlj[i]

    return gradZ

def q(weights, current_state, future_state, piece):
    '''
    given vector weights, the current board, and a piece,
    get the percent quality of the future move
    '''
    num = l(weights, future_state)
    denom = Z(weights, current_state, piece)
    print "quality..."
    print num
    print denom
    print num/denom

    print future_state
    for future_move in get_all_moves(current_state, piece):
        future_vector = future_move["board"].get_feature_dict().values()
        if future_vector == future_state:
            print future_vector

    assert((num/denom)>=0)
    assert((num/denom)<=1)
    return num / denom

def grad_q(weights, current_state, future_state, piece):
    '''
    '''
    print "Calling grad_q..."
    #print "WEIGHTS..."
    #print weights
    #print "FUTURE VECTOR..."
    #future_state = [float(i)/sum(future_state) for i in future_state]
    #print future_state
    
    a = (-1.0)*l(weights, future_state)
    b = Z(weights, current_state, piece) ** 2
    c = (a/b)
    first = [c*i for i in grad_Z(weights, current_state, piece)]

    d = Z(weights, current_state, piece)
    last = [i/float(d) for i in grad_l(weights, future_state)]

    print "grad_q..."
    print [sum(c) for c in zip(first, last)]

    return [sum(c) for c in zip(first, last)]


def score_ratio(weights, current_state, future_state, piece):
    '''
    given vector weights, the current board, future board,
    and the piece get the score ratio. Score ratio is the
    future state, minus the 
    '''
    #print "Calling the Score Ratio..."

    #print "q..."
    a = q(weights, current_state, future_state, piece)
    #print a

    #print "grad_q..."
    g_q = grad_q(weights, current_state, future_state, piece)
    #print "grad_q", g_q

    return [i/float(a) for i in g_q]

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
        a = [i*beta for i in self.z]
        b = score_ratio(weights, current_state, chosen_future_state, piece)
        self.z = [sum(c) for c in zip(a, b)]
        print "z..."
        print self.z

        return self.z

    def update_delta(self, beta, piece_number, weights, current_state, piece, chosen_future_state):
        z_args = (beta, weights, current_state, piece, chosen_future_state.values())

        print "Rows destroyed"
        #print chosen_future_state
        #print current_state.full_rows
        #reward = chosen_future_state["rows"] - current_state.full_rows        
        reward = current_state.max - chosen_future_state["max"]
        reward = reward if reward > 0 else 1

        print reward

        z = self.update_z(*z_args)

        zr = [i*reward for i in z]
        #print "ZR..."
        #print zr

        zrdelta = [v-self.delta[i] for i, v in enumerate(zr)]
        #print "zrdelta..."
        #print zrdelta

        time_const = float(piece_number) / (piece_number + 1)
        #print time_const
        zrdeltat = [time_const * i for i in zrdelta]
        #print "time delta..."
        #print zrdeltat

        left_term = self.delta
        self.delta = [left_term[i] + zrdeltat[i] for i,j in enumerate(zrdeltat)]
        return self.delta

    def update_weights(self, alpha, beta, piece_number, weights, current_state, piece, chosen_future_state):
        '''
        Provided an 'nth piece', and appropriate arguments, update
        the vector weights by theta = theta + alpha*delta
        '''
        delta = self.update_delta(beta, piece_number, weights, current_state, piece, chosen_future_state)
        print "Delta..."
        print delta
        
        delta_alpha = [alpha * i for i in delta]
        self.weights = [self.weights[i] + delta_alpha[i] for i,j in enumerate(delta_alpha)]
        return self.weights

    def init_vectors(self, board):
        if not self.var_init:
            if self.z == None:
                self.z = [0 for i in range(len(board.get_feature_dict().values()))]
            if self.delta == None:
                self.delta = [0 for i in range(len(board.get_feature_dict().values()))]
            if self.weights == None:
                #from random import random
                self.weights = [-6.972988005626286, -0.020006240467911964, -0.01043888166236461, -0.1542055196093272, -0.9691387470733887, -1.41186411342795, -1.0251165642981068, -1.3243355833487855, -1.0972287489572317, -1.887972513711374, -1.0009040006185181, 0.19012803587242647, -0.4964566199636361, -2.2045536787683284, -2.479350024636267, -2.305543293214648, -1.7516964814585965, -1.6565620876636407, -2.5447265673123916, -2.1056599083056464, -2.2526206869502867, -1.9441180621960652]
                #self.weights = [random() for i in range(len(board.get_feature_dict().values()))]

    def get_next_move(self, board, piece, piece_number):
        '''
        Using a boltzman distribution, and gradient descent, update
        a set of weights
        '''    
        self.init_vectors(board)

        moves = list(get_all_moves(board, piece))

        best_move = moves[0]
        for m in moves[1:]:
            if Q(self.weights, best_move["board"].calc_data(True).get_feature_dict().values()) < Q(self.weights, m["board"].calc_data(True).get_feature_dict().values()):
                best_move = m

        print "Quality"
        print [Q(self.weights, m["board"].calc_data(True)) for m in moves]

        self.update_weights(0.01, 0.5, piece_number, self.weights, board, piece, best_move["board"].get_feature_dict())
        print "Updating Weights..."
        print self.weights
        sleep(self.time)

        best_move = (best_move["slice"]["index"], 
                      get_piece_rotation(best_move["rotation"]["piece"]))

        return best_move

    def train(self, cboard, cpiece, cpiece_number, fboard, fpiece):
        '''
        Pass in a state, piece, and piece number to train boltz
        '''
        self.init_vectors(cboard)
        self.update_weights(0.1, 0.5, cpiece_number, self.weights, cboard, cpiece, fboard.get_feature_dict())
