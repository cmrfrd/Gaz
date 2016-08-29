from Gaz import game_reader

reader = game_reader("semihuman/")
#reader.read_model("semihumanmodel")
#reader.read_games(8)
reader.read_games(10)
reader.feature_scale_data()
reader.create_summaries()
reader.save_model("semihumanmodel")

for key, model in reader.dataset.iter_models(True):
    print "Model Num: %d" % (key)
    for c, classification in model.iter_classes(True):
        print "    Classification: %s" % (str(c))
        print "        Vectors: %d" % (len([v for v in classification.iter_vectors()]))
