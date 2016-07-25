from tetris_infastructure import Board, tetris_shapes
from game_reader import game_reader

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
	for classification, feature_val_list in dataset[model_choice].iteritems():
		if index == 1:print feature_val_list[0]
		for feature_dict in feature_val_list:
			distances.append( (classification, euclidian_distance( feature_dict.values(), new_vect ) ) )
		index += 1
	#get the shortest 'k' distances for classification
	top_k_distances = [d[0] for d in sorted(distances, key=by_dist)[:k]]
	
	#get the most common classification and return to user
	most_common = Counter(top_k_distances).most_common(1)[0][0]

	return most_common

def best_move_by_KNN(self, pieces, board, games=10, k=5):
	reader = Game_Reader(pieces, board)
	reader.read_model("10gamemodel")

	while not self.exit.is_set() and self.app.auto.wait() and not self.app.gameover:
		current_state_vector = reader.feature_dict_from_board( zip(*self.app.board) ).values()
		move = k_nearest_neighbors(k, reader.dataset, self.get_piece_index(self.app.piece[:]), current_state_vector)
		yield move

class KNN(object):
	def __init__(self, modelname, k=5):
		self.reader = game_reader()
		self.model = self.reader.read_model(modelname)
		self.k = k
	
	def get_next_move(self, board, piece):
		'''classify a new move based on kNN in dataset. Assume all data normalized
		'''

		current_state_vector = self.reader.feature_dict_from_board( board ).values()

		by_dist = lambda item:item[1]
		
	        #get all the distances away from a given new_vect
		distances = []
		index = 0
		for classification, feature_val_list in dataset[model_choice].iteritems():
			if index == 1:print feature_val_list[0]
			for feature_dict in feature_val_list:
				distances.append( (classification, euclidian_distance( feature_dict.values(), new_vect ) ) )
				index += 1
	        #get the shortest 'k' distances for classification
	        top_k_distances = [d[0] for d in sorted(distances, key=by_dist)[:k]]
	
	        #get the most common classification and return to user
	        most_common = Counter(top_k_distances).most_common(1)[0][0]

        	return most_common
		
		     
