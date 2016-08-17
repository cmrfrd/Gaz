from tetris_infastructure import Board, tetris_shapes, get_piece_index
from game_reader import game_reader

from collections import Counter
from math import sqrt
from time import sleep

def euclidian_distance(v1, v2):
	'''distance of 2 vectors
	'''
	distance = 0
	for a, b in zip(v1, v2):
		distance += float(a - b) ** 2
	return sqrt(distance)

def k_nearest_neighbors(k, dataset, model_choice, new_vect):
	'''classify a new move based on kNN in dataset. Assume all data normalized
	'''
	by_dist = lambda item:item[1]

	#get all the distances away from a given new_vect
	distances = []
	index = 0
	for classification, feature_val_list in dataset[model_choice]["features"].iteritems():
		for feature_dict in feature_val_list:
			distances.append( 
				(classification, 
				 euclidian_distance( 
						feature_dict.values(), 
						new_vect ) ) )
		index += 1
	#get the shortest 'k' distances for classification
	top_k_distances = [d[0] for d in sorted(distances, key=by_dist)[:k]]
	
	#get the most common classification and return to user
	most_common = Counter(top_k_distances).most_common(1)[0][0]

	return most_common

class KNN(object):
	def __init__(self, modelname, k=5, time_const=0.01):
		self.reader = game_reader()
		self.model = self.reader.read_model(modelname)
		self.k = k
		self.time = time_const
	
	def get_next_move(self, board, piece):
		'''classify a new move based on kNN in dataset. Assume all data normalized
		'''
		current_state_vector = board.get_feature_dict().values()
		model_choice = get_piece_index(piece)
		sleep(self.time)
		
		return k_nearest_neighbors(self.k, self.model, model_choice, current_state_vector)
		
		
		     
