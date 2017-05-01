import glob
from os.path import abspath, dirname, realpath
import csv
import json
import ast
import gc
import cPickle
import pickle
import base64
import datetime
from itertools import izip
from math import sqrt, exp, pi
from collections import Counter, OrderedDict

from tetris_infastructure import Board, tetris_shapes

current_filepath = dirname(realpath(__file__))
gameplay_dir = "/gameplays/"
model_dir = "/models/"

def avg(list_num):
	return sum(list_num) / float(len(list_num))

def std(list_num):
	average = avg(list_num)
	variance = sum( [(x-average) ** 2 for x in list_num] ) / float(len(list_num))
	return sqrt(variance)

def probobility(num, mean, stdev):
	exponent = exp(-( ((x-mean) **2) / (2*(stdev ** 2))))
	return (1 / (sqrt(2*pi) * stdev)) * exponent

def feature_scale(feature, f_max=None, f_min=None):
	'''feature scale a single value given a max and min
	'''
	assert f_max != None or f_min != None
	if f_max - f_min == 0:
		return float(feature)
	return (float(feature) - f_min)/(f_max - f_min)

def feature_scale_list(features, f_max=None, f_min=None):
	'''This func will normalize a list of features to fin in [0,1]
	'''
	if f_max==None:f_max = max(features)
	if f_min==None:f_min = min(features)

	return [feature_scale(f, f_max, f_min) for f in features]

class DataSet(OrderedDict):
	'''
	Special dictionary that contains models with 
	classifications that contain feature vectors
	
	Designated Structure:
	{
	  'model_1':{
	    'classification_1':{
	      'summary':{
	        'avg':[69],
		'std':[6.9]
	      },
	      'feature_vectors':[
	        {feature_vector_1},
	        ...
	      ]
	    }
	    ...
	  },
	  ...
	}
	'''
	def __init__(self, *args, **kwargs):
		super(DataSet, self).__init__(*args, **kwargs)

	def _get_label(self):
		return self["label"]

        def _get_list(self, key):
		'''
		provided a key, try to access a value with
		that key. If the value for the key doesn't
		exist, create a list for that key
		'''
		try:
			return self[key]
		except KeyError, AttributeError:
		       	self[key] = []
		return self[key]

	def _get_dict(self, key, label=None):
		'''
		provided a key and a label try to access a
		value with that key. If they value doesn't
		exist, create a new dataset with that label
		'''
		try:
			return self[key]
		except KeyError, AttributeError:
		       	self[key] = DataSet(label=label)
		return self[key]

	def get_classification_summary(self, summary_key):
		'''
		given self is a classification, and
		provided a summary key, return that
		summary
		'''
		assert self._get_label() == "classification", "self is not a classification"
		return self._get_dict("summary", "summary")[summary_key]

	def get_model(self, model):
		'''given self is a dataset, get a model
		'''
		return self._get_dict(model, "model")

	def iter_models(self, with_key=False):
		'''given self is a Dataset, iterate models
		'''
		if with_key:
			for model_key, model in self.iteritems():
				yield model_key, model
		else:
			for model_key, model in self.iteritems():
				yield model

	def iter_classes(self, with_key=False):
		'''
		given self is a model, iterate through all
		the classifications
		'''
		assert self._get_label() == "model", "self is not a model"
		if with_key:
			for classification_key, classification in self.iteritems():
				if classification_key == "label":
					continue
				yield classification_key, classification
		else:
			for classification_key, classification in self.iteritems():
				if classification_key == "label":
					continue
				yield classification

	def iter_vectors(self):
		'''
		given self is a classification, iterate
		through all the vectors
		'''
		assert self._get_label() == "classification", "self is not a classification"
		for dict_vect in self["feature_vectors"]:
			yield dict_vect

	def iter_all_class_vectors(self):
		'''
		given that self is a model, iterate through 
		all the classifications and their vectors 
		'''
		assert self._get_label() == "model", "self is not a model"
		for classification in self.iter_classes():
			for dict_vect in classification.iter_vectors():
				yield dict_vect

	def iter_all_vectors(self):
		'''
		given self is a dataset, iterate through all 
		the vectors of all the classes of all the models
		'''
		for model_key, model in self.iteritems():
			for dict_vect in model.iter_all_class_vectors():
				yield dict_vect

	def add_summary(self, summary):
		'''
		given self is a classification, and provided a 
		classification and an info, add the info
		extending into the "summary" dict 
		'''
		assert self._get_label() == "classification", "self is not a classification"
		self._get_dict("summary") \
		    .update(summary)

	def add_classification_vector_dict(self, classification, vector):
		'''
		given self is a model, and provided
		a classification and a vector, add 
		the vector to the "feature_vectors" 
		classification list
		'''
		assert self._get_label() == "model", "self is not a model"
		self._get_dict(classification, "classification") \
		    ._get_list("feature_vectors") \
		    .append(vector)

	def add_classification_vector_dicts(self, classification, vectors):
		'''
		given self is a model, and provided
		a classification and vectors, add the
		vectors to the "feature_vectors"
		classification list
		'''
		assert self._get_label() == "model", "self is not a model"
		for vector in vectors:
			self.add_classification_vector_dict(classification, vector)

	def add_vector_dict(self, vector):
		'''
		given self is a classification and provided
		a vector add the vector to "feature_vectors"
		'''
		assert self._get_label() == "classification", "self is not a classification"
		self._get_list("feature_vectors").append(vector)
		

	def remove_vector_dicts(self):
		'''given self is a classification remove all vectors of a classification
		'''
		assert self._get_label() == "classification", "self is not a classification"
		self["feature_vectors"] = []

class game_reader(object):
	def __init__(self, path=""):
            self.get_gameplay_files(path)
	    self.dataset = DataSet()
	    self.csv_reader_settings = {
		    "delimiter":":",
		    "quoting":csv.QUOTE_NONE
		 }

	def get_gameplay_files(self, dir_path):
            '''provided a path, get the gameplay csv files 
	    '''
            self.gameplay_files = []
	    
	    path = current_filepath + gameplay_dir + dir_path + "*.csv"
	    for g_file in glob.glob(path):
		    self.gameplay_files.append(g_file)

	    return self.gameplay_files

	def read_model(self, file_path):
            '''provided a modelname, load the pickled file into a dataset
            '''
	    path = current_filepath + model_dir + file_path  + ".pickle"
            with open(path, "rb+") as model_file:
		    self.dataset = cPickle.load(model_file)
	    return self.dataset

	def save_model(self, file_path=None):
            '''
	    provided a model_name, save dataset to a pickle 
	    file for reloading, else use a generated filename
	    by date
            '''
            if file_path == None:
                file_path = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
		file_path += '-'
		file_path += str(len(self.dataset))

	    path = current_filepath + model_dir + file_path + ".pickle"
	    with open(path, "wb+") as model_file:
                cPickle.dump(self.dataset, model_file)

	def evaluate_game_line(self, line):
            '''provided a line, extract the move information
	    '''
            model = ast.literal_eval(line[1])[1]
            classification = (ast.literal_eval(line[0]), ast.literal_eval(line[2]))
	    features = Board(zip(*ast.literal_eval(line[3]))).get_feature_dict()
	    return model, classification, features
		
	def read_games(self, num_games=1, trim=5):
            '''
	    provided the number of games and a trim, create
	    a dataset with those games, but in each game trim
	    the last 'trim' moves
	    '''
	    assert 1 <= num_games <= len(self.gameplay_files)

	    for index, game_file in enumerate(self.gameplay_files[:num_games]):

                game = open(game_file,'rb').readlines()[:-trim]
		moves = csv.reader(game, **self.csv_reader_settings)

		for index, move in enumerate(moves):
                    model, classification, features = self.evaluate_game_line(move)
		    self.dataset.get_model(model) \
		                .add_classification_vector_dict(classification, features)
	    return self.dataset

	def create_summaries(self):
		'''
		given a dataset, iterate through the classes of
		each model and get the row of the vectors and
		add the std and avg to the dataset summary
		'''
		std_list = []
		avg_list = []

		for model in self.dataset.iter_models():
			for classification in model.iter_classes():
				feature_rows = iter(zip(*[v.values() for v in classification.iter_vectors()]))
				for feature_row in feature_rows:
					std_list.append(std(feature_row))
					avg_list.append(avg(feature_row))

				classification.add_summary({"std":std_list})
				classification.add_summary({"avg":avg_list})		
		return self.dataset

	def feature_scale_data(self):
		'''
		given a dataset, iterate through all the vectors
		of each class of each model and scale each value 
		to fit between [0,1]. Do this by getting a 'row' 
		of a feature in a class and using the max and min 
		to feature scale each value. Then convert the rows 
		to vectors and replace the existing vectors
		'''
		for model in self.dataset.iter_models():
			for classification in model.iter_classes():
				feature_keys = classification.iter_vectors().next().keys()

				feature_list_vectors = [v.values() for v in classification.iter_vectors()]
				feature_rows = iter(zip(*feature_list_vectors))
				
				scaled_rows = [feature_scale_list(feature_row) for feature_row in feature_rows]
				scaled_vectors = zip(*scaled_rows)
				
				classification.remove_vector_dicts()
				for scaled_vector in scaled_vectors:
					scaled_vector_dict = dict(zip(feature_keys, scaled_vector))
					classification.add_vector_dict(scaled_vector_dict)		
		return self.dataset

	def train_weight_vector(self, num_games=1, trim=5):
	    assert 1 <= num_games <= len(self.gameplay_files)

	    from boltz import boltz
	    bol = boltz("test")

	    for index, game_file in enumerate(self.gameplay_files[:num_games]):

                game = open(game_file,'rb').readlines()[:-trim]
		moves = csv.reader(game, **self.csv_reader_settings)

		cpiece, cboard = self.get_board_piece(moves.next())
		for index, move in enumerate(moves):
			fpiece, fboard = self.get_board_piece(move)
			bol.train(cboard, cpiece, index, fboard, fpiece)

			print "Height diff"
			print cboard.max - fboard.max
			
			print "Current"
			for r in cboard:print r
			print "Future"
			for r in fboard:print r

			cpiece, cboard = fpiece, fboard

			print bol.weights

	    return self.dataset

	def get_board_piece(self, move):
            '''Provided a move from a csv, return the piece and the board
	    '''
	    piece = ast.literal_eval(move[1])[0]
	    board = Board(zip(*ast.literal_eval(move[3])))

	    return piece, board
