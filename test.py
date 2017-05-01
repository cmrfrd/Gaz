import argparse
import tetris

parser = argparse.ArgumentParser(description='Plays tetris')

parser.add_argument('-gaz', action="store_true", default=False, dest="start_auto", help='Add -gaz for Gaz to take over')
parser.add_argument('-inv', action="store_false", default=True, dest="screen", help='Add -inv for screen to be invisible')
parser.add_argument('-r', default=False, const="", dest="record", nargs="?",  help='Add -r and the name of the name of the filename to record your gameplay. If no name provided a name will be generated based on the current datetime')
parser.add_argument('-knn', default=False, const="defaultmodel", dest="knn_modelname", nargs="?", help='Add this flag and a modelname to use KNN. If no model is provided "defaultmodel" will be used ')
parser.add_argument('-greedy', action="store_true", default=False, dest="greedy", help='Add this flag to use a greedy algorithm')
parser.add_argument('-dgreedy', action="store", dest="dgreedy", nargs=2, type=int, help="Add this flag to use a deep tree search greedy algorithm. The first argument is the layers or 'depth' the greedy algorithm will search, and the second argument is the 'skim' or the top n branch moves the algorithm should search further")
parser.add_argument('-naive', default=False, const="defaultmodel", dest="naive_modelname", nargs="?", help='This flag uses the naive bayes classifier to play tetris')
parser.add_argument('')

args = parser.parse_args()

while True:
    App = tetris.TetrisApp(**dict(args._get_kwargs()))
    App.run()
