from Gaz import game_reader

reader = game_reader("semihuman/")
#reader.read_games(11)
#reader.feature_scale_data()
#reader.create_summaries()
#reader.save_model("colinfomodel")

reader.train_weight_vector(2)


