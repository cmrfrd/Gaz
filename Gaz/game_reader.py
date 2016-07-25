import glob
import csv
import json
import ast
import pickle
import datetime
from math import sqrt
from collections import Counter, OrderedDict
from Tetris_Infastructure import Board, tetris_shapes

gameplay_dir = "gameplays/"

'''
Game reader will read games and product "dataset" object
'''

class DataSet(OrderedDict):
	'''Special dictionary that contains models with classifications that contain feature vectors

	Designated Structure:
	{
	  'model_1':{
	    'classification_1':[
	      [feature_vector_1],
	      ...
	    ],
	    ...
	  },
	  ...
	}
	'''

	def __init__(self):
		super(DataSet, self).__init__()

	def get_model(self, model):
		return self.get_dict(model)

	def add_classification_value(self, classification, feature_vector):
		self.get_list(classification).append(feature_vector)

        def get_list(self, key):
		'''get list from key, if list doesn't exist
		'''
		try:
			return self[key]
		except KeyError, AttributeError:
		       	self[key] = []
		return self[key]

	def get_dict(self, key):
		'''get dict from key. if key doesn't exist, return make new DataSet
		'''
		try:
			return self[key]
		except KeyError, AttributeError:
		       	self.dataset[key] = DataSet()
		return self[key]

class game_reader(object):
	def __init__(self, dir=gameplay_dir):
            self.gameplay_files = [file for file in glob.glob(dir + "*.csv")]
	    self.dataset = DataSet()

        def feature_dict_from_board(self, board_list):
            '''returns a long vector of features from a board
            '''
            board = Board(board_list)
            board.calc_data()
            
            feature_dict = OrderedDict(board.__dict__)
            
            return feature_dict


	def read_model(self, model_name):
            '''Read a model from a file
            '''
            model_file = open("models/" + model_name  + ".pickle")

            self.dataset = pickle.load(model_file)

            return self.dataset

	def save_model(self, filename=None):
            '''save dataset to pickle file for reloading
            '''
            
            if filename == None:
                filename = datetime.datetime.now().strftime("%Y-%m-%d|%H:%M:%S") + '-' + str(len(self.dataset))
		
		model_file = open("models/" + filename + ".pickle", "wb")
		pickle.dump(self.dataset, model_file)
		model_file.close()
		
	def read_games(self, num_games=1):#iterator that goes through each game
		'''Read in 'n' games and build the dataset from those csv games
		'''

		assert 1 <= num_games <= len(self.gameplay_files)

		for index, game_file in enumerate(self.gameplay_files):#iter through each game				

			#break if num_games has been read
			if index >= num_games:
				break

                        #open game for delimitation. Ignore first entry
			moves = csv.reader(open(game_file,'rb'), delimiter=":", quoting=csv.QUOTE_NONE)
			moves.next()

			#iterate through each move and create dict dataset based on information
			for index, move in enumerate(moves):

                                #look at csv data to see ordering of information
				model = ast.literal_eval(move[1])[1]
				classification = (ast.literal_eval(move[0]), ast.literal_eval(move[2]))
				features = self.feature_dict_from_board(zip(*ast.literal_eval(move[3])))

				self.dataset[model][classification]
	
		return self.dataset

	def feature_scale_data(self):
		
		#get a list of features from the dataset for keying and normalization
		features = self.dataset.values()[0].values()[0][0].keys()

		#initialize another alternate form of the dataset, a list for every feature
		container = {'data':[]}
		feature_dict = dict((k,container) for k in features)

		#add all feature -> value pairs to feature dict
		for model, classification_feature in self.dataset.iteritems():
			for classification, feature_val_list in classification_feature.iteritems():
				for feature_val in feature_val_list:
					for feature, value in feature_val.iteritems():
						feature_dict[feature]['data'].append(value)

		#get the max and min of each feature
		for feature, val_list in feature_dict.iteritems():
			feature_dict[feature]['max'] = max(val_list['data'])
			feature_dict[feature]['min'] = min(val_list['data'])
			
		#iterate through the main original dataset and adjust each value by the maxmin
		for model, classification_feature in self.dataset.iteritems():
			for classification, feature_val_list in classification_feature.iteritems():
				for feature_val_index, feature_val in enumerate(feature_val_list):
					for feature, value in feature_val.iteritems():
						max_feature = feature_dict[feature]['max']
						min_feature = feature_dict[feature]['min']
						self.dataset[model][classification][feature_val_index][feature] = feature_scale(value, max_feature, min_feature)
		return self.dataset
