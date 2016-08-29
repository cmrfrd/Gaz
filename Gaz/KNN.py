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
	'''
	provided 'k', a dataset, and a new vector, get the top
	'k' distances by euclidian distance. Then classify the
	vector by the most 'votes' by top 'k' distances and the
	points
	'''
	model = dataset.get_model(model_choice)

	distances = []
	for class_key, classification in model.iter_classes(with_key=True):
		for feature_vector in classification.iter_vectors():
			distance = euclidian_distance(feature_vector.values(), new_vect)
			distances.append((class_key, distance))

	top_k_distances = [d[0] for d in sorted(distances, key=lambda item:item[1])[:k]]
	most_common = Counter(top_k_distances).most_common(1)[0][0]

	return most_common

class KNN(object):
	def __init__(self, modelname, k=20, time_const=0.01):
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
		
		
		     
