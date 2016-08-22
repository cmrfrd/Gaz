import glob
from os.path import abspath, dirname, realpath
import csv
import json
import ast
import cPickle
import base64
import datetime
from math import sqrt, exp, pi
from collections import Counter, OrderedDict

from tetris_infastructure import Board, tetris_shapes

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
	
	def __init__(self, label=None, *args, **kwargs):
		super(DataSet, self).__init__(*args, **kwargs)
		self.label = label

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
		       	self[key] = DataSet(label)
		return self[key]

	@staticmethod
	def add_vector_dict(model, classification, vector):
		'''
		provided a model, classification, and vector
		add the vector to the classification list in
		the model
		'''
		self.get_classification_from_model(model, classification) \
		    .append(vector)

	def iter_all_vectors(self):
		'''
		given self is a dataset, iterate through all 
		the vectors of all the classes of all the models
		'''
		for model_key, model in self.iteritems():
			for dict_vect in model.iter_class_vectors():
				yield dict_vect

	def iter_class_vectors(self):
		'''
		given that self is a model, iterate through 
		the vectors 
		'''
		assert self.label == "model", "self is not a model"

		for classification_key, classification in self.iteritems():
			for dict_vect in classification:
				yield dict_vect

	def add_vector_dict(self, classification, vector):
		'''
		given self is a model, and provided a
		classification and a vector, add the
		vector to the classification list
		'''
		assert self.label == "classification", "self is not a classification"

		self._get_list(classification).append(vector)

	def get_model(self, model):
		'''given self is a dataset, get a model
		'''
		return self._get_dict(model, "model")


class game_reader(object):
	def __init__(self, gameplay_dir=gameplay_dir):
	    self.current_filepath = dirname(realpath(__file__))
            self.gameplay_files = [file for file in glob.glob(self.current_filepath + gameplay_dir + "*.csv")]

	    self.dataset = DataSet()

	def set_game_filepath(self, path):
            self.gameplay_files = [file for file in glob.glob(self.current_filepath + gameplay_dir + path + "*.csv")]

	def read_model(self, model_name):
            '''Read a model from a file
            '''
            with open(self.current_filepath + model_dir + model_name  + ".pickle", "r+") as model_file:
		    self.dataset = cPickle.load(model_file)
		    return self.dataset

	def save_model(self, model_name=None):
            '''save dataset to pickle file for reloading
            '''
            
            if model_name == None:
                filename = datetime.datetime.now().strftime("%Y-%m-%d|%H:%M:%S") \
		           + '-' \
		           + str(len(self.dataset))
		
	    with open(self.current_filepath + model_dir + model_name + ".pickle", "wb+") as model_file:
		    cPickle.dump(self.dataset, model_file)
		    model_file.close()
		
	def read_games(self, num_games=1, trim=5):
		'''Read in 'n' games and build the dataset from those csv games
		'''
		assert 1 <= num_games <= len(self.gameplay_files)

		for index, game_file in enumerate(self.gameplay_files):
			if index >= num_games:
				break

                        #open game for delimitation. Ignore first entry
			moves = csv.reader(open(game_file,'rb').readlines()[:-trim], 
					   delimiter=":", 
					   quoting=csv.QUOTE_NONE)
			moves.next()

			for index, move in enumerate(moves):
                                #look at csv data to see ordering of information
				model = ast.literal_eval(move[1])[1]
				classification = (ast.literal_eval(move[0]), ast.literal_eval(move[2]))
				features = Board(zip(*ast.literal_eval(move[3]))).get_feature_dict()

				self.dataset.get_model(model)
				self.dataset[model].get_dict(classification)
				self.dataset[model][classification].get_list('feature_vectors').append(features)	
		return self.dataset

	def create_summaries(self):
		'''Create std, and avg summeries in "summary" key in model
		'''
		for model_key, model in self.dataset.iteritems():
			for classification, classification_value in model.iteritems():
				for index, feature in enumerate(zip(*[v.values() for v in classification_value['feature_vectors']])):
					classification_value.get_dict("summary").get_list("avg").append(avg(feature))
					classification_value.get_dict("summary").get_list("std").append(std(feature))
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
