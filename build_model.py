from KNN import Game_Reader, k_nearest_neighbors
from tetris_player import Board, tetris_shapes


reader = Game_Reader(tetris_shapes, Board)
reader.read_games(1)
reader.feature_scale_data()



