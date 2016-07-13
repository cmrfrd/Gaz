import glob
import csv
import json
import ast
import pickle
import datetime
from math import sqrt
from collections import Counter, OrderedDict

gameplay_dir = "gameplays/"

def feature_scale(feature, f_max=None, f_min=None):
	'''feature scale a single value given a max and min
	'''
	assert f_max != None or f_min != None
	return (feature - f_min)/(f_max - f_min)

def feature_scale_list(features, f_max=None, f_min=None):
	'''This func will normalize a list of features to fin in [0,1]
	'''
	if f_max==None:f_max = max(features)
	if f_min==None:f_min = min(features)

	return [feature_scale(f, f_max, f_min) for f in features]	

def euclidian_distance(v1, v2):
	'''distance of 2 vectors
	'''
	distance = 0
	for a, b in zip(v1, v2):
		distance += (a - b) ** 2
	return sqrt(distance)

def k_nearest_neighbors(k, dataset, model_choice, new_vect):
	'''classify a new move based on kNN in dataset. Assume all data normalized
	'''
	by_dist = lambda item:item[1]

	#get all the distances away from a given new_vect
	distances = []
	for classification, feature_val_list in dataset[model_choice].iteritems():
		for feature_dict in feature_val_list:
			distances.append( (classification, euclidian_distance( feature_dict.values(), new_vect ) ) )

	#get the shortest 'k' distances for classification
	top_k_distances = [d[0] for d in sorted(distances, key=by_dist)[:k]]
	
	#get the most common classification and return to user
	most_common = Counter(top_k_distances).most_common(1)[0][0]

	return most_common

class Game_Reader(object):
	def __init__(self, pieces, board, dir=gameplay_dir):
		self.gameplay_files = [file for file in glob.glob(dir + "*.csv")];
		self.sample_board = board;
		self.pieces = pieces;
		self.dataset = {}

        def feature_dict_from_board(self, board_list):
		'''returns a long vector of features from a board
		'''
    	        self.sample_board.__init__(board_list)
		self.sample_board.calc_data()
		cols = self.sample_board[:]
	
		feature_dict = self.sample_board.__dict__

		for index, col in enumerate(self.sample_board):
			feature_dict["col" + str(index)] = col.height

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
			filename = "models/" + datetime.datetime.now().strftime("%Y-%m-%d|%H:%M:%S") + '-' + str(len(self.dataset))
		
		model_file = open(filename + ".pickle", "wb")
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
			for move in moves:

                                #look at csv data to see ordering of information
				model = ast.literal_eval(move[1])[1]
				classification = (ast.literal_eval(move[0]), ast.literal_eval(move[2]))
				features = self.feature_dict_from_board(zip(*ast.literal_eval(move[3])))
				
				try:
					self.dataset[model]
					try:
						self.dataset[model][classification].append(features)
					except KeyError, AttributeError:
						self.dataset[model][classification] = [features]
				except KeyError, AttributeError:
					self.dataset[model] = {}

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

if __name__ == "__main__":
	
	a = Game_Reader(tetris_shapes, Board)
