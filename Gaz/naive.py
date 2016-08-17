from tetris_infastructure import get_all_moves, get_piece_index
from game_reader import game_reader

from math import sqrt, exp, pi, log
from time import sleep

def probobility(num, mean, stdev):
    '''gaussian function
    '''
    exponent = exp(-( ((num-mean) **2) / (2*(stdev ** 2))))
    return log( (1 / (sqrt(2*pi) * stdev)) * exponent )

def probobility_of_move(dataset, model_choice, new_vect):
    '''calculate probobilities of classifications seen in model
    '''
    model = dataset.get_model(model_choice)
    probobilities = {}
    
    for classification, feature_value in model.iteritems():
        prob = 1
        for feature_index in range(len(new_vect)):
            mean = feature_value["summary"]["avg"][feature_index]
            std = feature_value["summary"]["std"][feature_index]
            num = new_vect[feature_index]

            if std == 0:continue
            prob *= probobility(num, mean, std)
        else:
            probobilities[prob] = classification

    return probobilities            

class naive(object):
    '''implementation of naive bayes algorithm
    '''

    def __init__(self, modelname, time_const=2):
        self.reader = game_reader()
        self.model = self.reader.read_model(modelname)
        self.time = time_const

    def get_next_move(self, board, piece):
        '''Use naive bayes algorithm to calculate classification of next move
        '''    
        feature_vector = board.get_feature_dict().values()
        model_index = get_piece_index(piece)

        probobilities = probobility_of_move(self.model, model_index, feature_vector)

        sleep(self.time)

        return probobilities[max(probobilities.keys())]
        
