from tetris_infastructure import get_all_moves, get_piece_index
from game_reader import game_reader

from math import sqrt, exp, pi, log
from time import sleep

def probobility(num, mean, stdev):
    '''gaussian function
    '''
    try:
        exponent = exp(-( ((num-mean) **2) / (2*(stdev ** 2))))
        return log( (1 / (sqrt(2*pi) * stdev)) * exponent )
    except:
        return 0

def probobility_of_move(dataset, model_choice, new_vect):
    '''calculate probobilities of classifications seen in model
    '''
    model = dataset.get_model(model_choice)
    probobilities = {}

    for class_key, classification in model.iter_classes(with_key=True):
        prob = 1
        for feature_index in range(len(new_vect)):
            mean = classification.get_classification_summary("avg")[feature_index]
            std = classification.get_classification_summary("std")[feature_index]
            num = new_vect[feature_index]

            prob *= probobility(num, mean, std)
        probobilities[prob] = class_key
    return probobilities            

class naive(object):
    '''implementation of naive bayes algorithm
    '''

    def __init__(self, modelname, time_const=0.01):
        self.reader = game_reader()
        self.model = self.reader.read_model(modelname)
        self.time = time_const

    def get_next_move(self, board, piece, piece_number):
        '''Use naive bayes algorithm to calculate classification of next move
        '''    
        feature_vector = board.get_feature_dict().values()
        model_index = get_piece_index(piece)
        probobilities = probobility_of_move(self.model, model_index, feature_vector)

        sleep(self.time)

        return probobilities[max(probobilities.keys())]
        
