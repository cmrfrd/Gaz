from tetris_infastructure import get_all_moves, get_piece_index, get_piece_rotation
from game_reader import boltz_model_reader
from mathelp import invert, matsub, matadd, matmultconst, matmult, print_matrix

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
    qfuture = Q(weights, future_state)
    denominator = 0.0
    for m in get_all_moves(current_state, piece):
        qpossible = m['board'].get_feature_dict().values()
        denominator += exp(Q(weights, qpossible) - qfuture)
    quality = 1 / denominator

    #print "quality..."
    #print quality
    return quality

def grad_q(weights, current_state, future_state, piece):
    '''
    Return gradient vector of quality
    '''
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

    #print "grad_q: ", [round(sum(c),3) for c in zip(first, last)]

    return [sum(c) for c in zip(first, last)]

def score_ratio(weights, current_state, future_state, piece):
    '''
    given vector weights, the current board, future board,
    and the piece get the score ratio. Score ratio is the
    future state, minus the 
    '''
    a = q(weights, current_state, future_state, piece)
    #print "Quality:", a

    g_q = grad_q(weights, current_state, future_state, piece)
    #print "grad_q", g_q

    return [i/float(a) for i in g_q]

class boltz(object):
    '''implementation of boltzman distribution with gradient descent
    '''
    def __init__(self, model_name, train, time_const=0.001):
        self.reader = boltz_model_reader(model_name)
        self.model_name = model_name

        self.time = time_const

        self.train = train
        self.var_init = False
        self.z = None
        self.delta = None
        self.weights = None
        self.G = None

    def set_model(self):
        self.weights, self.G = self.reader.get_model()

    def update_z(self, beta, weights, current_state, piece, chosen_future_state):
        a = [i*beta for i in self.z]
        b = score_ratio(weights, current_state, chosen_future_state, piece)
        self.z = [sum(c) for c in zip(a, b)]
        
        #print "z: ", [round(zv, 3) for zv in self.z]

        return self.z

    def update_delta(self, beta, piece_number, weights, current_state, piece, chosen_future_state):
        z_args = (beta, weights, current_state, piece, chosen_future_state.values())

        c = chosen_future_state
        reward = float(chosen_future_state['rows'])
        #print reward

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

    def update_G(self, piece_number):
        '''
        Update covariance matrix. Used to relate variables of vectors with eachother
        '''
        zzT = matmult([[i] for i in self.z], [self.z])        

        #print 'zzT...'
        #print_matrix(zzT, 4)

        right = matsub(zzT, self.G)
        
        #print 'New G...'
        #print_matrix(right, 4)

        time_const = (float(piece_number) / (piece_number+1))
        right = matmultconst(time_const, right)
        self.G = matadd(self.G, right)
        return self.G        

    def update_weights(self, alpha, beta, piece_number, weights, current_state, piece, chosen_future_state):
        '''
        Provided an 'nth piece', and appropriate arguments, update
        the vector weights by theta = theta + alpha*delta
        '''
        delta = self.update_delta(beta, piece_number, weights, current_state, piece, chosen_future_state)
        G = self.update_G(piece_number)
        invG = invert(G)

        #print "G..."
        #print_matrix(G, 3)

        #import numpy as np
        #print "inv G numpy..."
        #print np.linalg.inv(np.array(G))

        #print "invG..."
        #print_matrix(invG, 3)

        #print "Delta..."
        #print [round(d, 3) for d in delta]
        
        delta_alpha = [[alpha * i] for i in delta]
        delta_alpha_G = matmult(G, delta_alpha)

        #print "new weight,  weights"
        #for i,j in zip(delta_alpha_G, self.weights):print i,j
        #print

        delta_alpha_G = [i[0] for i in delta_alpha_G]

        self.weights = [self.weights[i] + delta_alpha_G[i] for i,j in enumerate(delta_alpha_G)]
        return self.weights

    def init_vectors(self, board):
        if not self.var_init:

            if self.reader.read_model(self.model_name):
                self.set_model()
                return True

            vector_len = len(board.get_feature_dict().values())

            self.G = [[0 if j!=i else 0.0000000001 for j in range(vector_len)] for i in range(vector_len)]

            self.z = [0 for i in range(vector_len)]

            self.delta = [0 for i in range(vector_len)]

            if self.weights == None:
                #self.weights = [-31.474400482179206, -2.765251934919666, -6.45010808811692, -5.174819108467723, -6.352852323360011, -8.596575631124415, -7.694439615896075, -8.453052061900113, -8.384371197299263, -9.032709514237311, -6.236766327149332, -4.119020606670995, -2.6667563326503583, -8.714638441159519, -10.229306987705513, -9.82413594493289, -9.508396276324415, -9.31706261721174, -10.285895202897308, -9.807081883576066, -8.250081938684906, -4.1944260367624056]
                #self.weights = [1 for i in range(len(board.get_feature_dict().values()))]
                #self.weights = [-14.839790247800275, -1.1054666528894936, -2.619702106178382, -0.8090526252311214, -1.7182916058443494, -2.02270919624264, -1.9775384191232255, -1.9684488462345067, -1.9658626200627551, -2.1830908740668957, -1.6035147772812925, -0.8608439506318958, -5.149022161837402, -7.933630748741152, -8.3463542975696, -8.072708905144632, -8.09377039434841, -8.07005034049447, -8.009677753209843, -8.030598391677472, -7.405565587259762, -5.147981809312341]
                #self.weights = [-23.36839692395347, -2.051050934470755, 13.599679210353676, -3.1094228880097767, -4.0678989684340605, -5.227268274095173, -4.817260257103382, -4.8682833061783635, -4.926284948833308, -5.204037287272446, -4.231520476053787, -3.2166154755851397, -3.968247158785896, -8.53118491843704, -9.946271097151564, -9.7197183275633, -10.27270237983387, -9.902641333189655, -9.382960163709203, -9.665648777244208, -8.122085867547462, -4.214027858176722]
                #self.weights = [-28.581947880347037, -2.7687185228188116, 11.75516873745802, -4.066424670276082, -5.27308162243105, -6.870294045985815, -6.254132575585693, -5.914531834959484, -5.927509438609294, -7.017046831332446, -5.720519880528214, -4.181216287213059, -4.364456502768255, -10.052858051778598, -11.968216460292089, -12.052702418841939, -12.802237257917575, -12.224378180358924, -10.807403999840965, -11.042837939977272, -9.496080815125728, -5.003640209471587]
                
                #self.weights = [-30.159, -7.499, 14.708, -5.836, -5.027, -7.53, -7.47, -6.789, -6.8, -8.546, -6.756, -5.212, -1.298, -8.898, -11.994, -13.867, -14.023, -13.736, -11.446, -11.419, -9.144, -4.558]

                #self.weights = [-30.428, -7.937, 14.939, -5.932, -5.094, -7.675, -7.648, -7.025, -6.867, -8.594, -6.98, -5.299, -1.008, -8.88, -12.108, -14.017, -14.153, -13.7, -11.344, -11.384, -9.187, -4.621]
                
                # default weights
                self.weights = [-32.29178297824714, -6.7140081229853905, 18.200657138226614, -6.778002574772368, -5.790389683159439, -8.68421375060278, -8.346073572713749, -7.861747023091065, -8.0660906925999, -9.24834472057468, -8.195854690673256, -6.349681663752939, -0.32702750199408276, -8.807394190879467, -12.489099960565342, -14.393060554942453, -14.712533844808732, -14.10165010877199, -11.562207976242341, -11.313917533207434, -8.827313840895929, -3.801900711144742]
            
            self.reader.set_model(self.weights, self.G)
            self.reader.save_model()                
            self.var_init = True

    def input_train(self, cboard, cpiece, cpiece_number, fboard, fpiece):
        '''
        Pass in a state, piece, and piece number to train boltz
        '''
        self.init_vectors(cboard)
        self.update_weights(0.2, 0.5, cpiece_number, self.weights, cboard, cpiece, fboard.get_feature_dict())
        self.reader.save_model()
            
    def get_next_move(self, board, piece, piece_number):
        '''
        Using a boltzman distribution, and gradient descent, update
        a set of weights
        '''    
        self.init_vectors(board)
        if piece_number == 0:
            self.z = [0.0 for i in range(len(board.get_feature_dict().values()))]
            self.delta = [0.0 for i in range(len(board.get_feature_dict().values()))]


        # select best move based on quality score with weights
        moves = list(get_all_moves(board, piece))
        best_move = max(moves, key=lambda m:Q(self.weights, m["board"].get_feature_dict().values()))

        # Update the weights and biases
        if self.train:
            try:
                if piece_number % 20 == 0:
                    self.update_weights(0.9, 0.9, piece_number, self.weights, board, piece, best_move["board"].get_feature_dict())

                    print "Updating Weights..."
                    print [w for w in self.weights]

                    self.reader.set_model(self.weights, self.G)
                    self.reader.save_model(read=True)
                else:
                    self.update_delta(0.9, piece_number, self.weights, board, piece, best_move["board"].get_feature_dict())
            except Exception, e:
                print e
                pass

        sleep(self.time)

        # Reshape the best move data into usable
        best_move = (best_move["slice"]["index"], 
                      get_piece_rotation(best_move["rotation"]["piece"]))

        return best_move
