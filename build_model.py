from Gaz import game_reader

reader = game_reader()
#reader.read_model("test_model")
reader.read_games(19)
#reader.feature_scale_data()
reader.save_model("colmodel")

for model, val in reader.dataset.iteritems():
    print "Model Num: %d, Classifications: %d" % (model, len(val))
    #for cl, moves in val.iteritems():
    #    print "Classification: %s, Num Moves %d" % (str(cl), len(moves))

