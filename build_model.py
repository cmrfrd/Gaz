from Gaz import game_reader

reader = game_reader()
#reader.read_model("semihumanmodel")
#reader.read_games(8)
reader.set_game_filepath("semihuman/")
reader.read_games(8)
reader.create_summaries()
print "done reading"
reader.save_model("semihumanmodel")
print "saving"
print reader.dataset.num_vectors()

for model, val in reader.dataset.iteritems():
    print "Model Num: %d" % (model)
    for c, classification in val.iteritems():
        print "    Classification: %s" % (str(c))
        print "        Vectors: %d" % (len(classification["feature_vectors"]))
