Gaz
==============
Gaz is a plug and play system where you provide a brain for her to play tetris.She is sery selfish and has no remorse.

##About
Tetris has **always** been an addiction of mine. I decided to eradicate this obsession by "solving" it so I'll never want to play it again. In case no one gets the [reference](http://zim.wikia.com/wiki/Gaz_Membrane). 

###Prerequisites
The only dependency for this repo is ```[pygame](http://www.pygame.org/wiki/GettingStarted)``` and ```[matplotlib](http://matplotlib.org/faq/installing_faq.html)``` if you want to see pretty graphs.

###Installing

If you have pip
```bash
pip install pygame
```

NOTE: matplotlib installations are weird... see this for help ---> [link](http://stackoverflow.com/questions/9829175/pip-install-matplotlib-error-with-virtualenv)

or if you don't
```bash
sudo apt-get install python-pygame
sudo apt-get build-dep python-matplotlib
```

Instructions
------------

Currently there are 2 ways to use Tetris with Gaz.

1. Normal Tetris.
        
    By running ```python tetris.py``` you can play normal tetris as 
    Alexey Pajitnov intended.
    
        Controls:
        LEFT ARROW - moves piece left
        RIGHT ARROW - moves piece right
        DOWN ARROW - moves piece down
        UP ARROW - rotates piece clockwise
        LEFT SHIFT - Gaz takes over
        ESC - ends the game

    If you want to record your games as human data for Gaz to look at or for personal 
    use run ```python tetris.py -r [name or file]``` and it will save them to ```Gaz/gameplays```. 

2. Playing with Gaz

    By running ```python tetris.py -gaz -greedy``` Gaz will automatically starty playing using her simple greedy algorithm. You can always switch out
    of "Auto" mode by pressing ```LEFT SHIFT```.

    By running ```python tetris.py -gaz -degreedy 0 3``` Gaz with use a deep greedy algorithm. '0' is the depth, and '3' is the top_n skimmed moves off of each layer. Keep the depth at either 0,1,2 because the branching factor in tetris is to big and advanced pruning methods need to be used to reduce the number of moves to search through. 

    A good deep greedy setting in ```python tetris.py -gaz -degreedy 2 2```.

    The two other usages are ```python tetris.py -gaz -naive semihumanmodel``` and ```python tetris.py -gaz -knn``` which use naive bayes and K nearest neighbors respectively. They don't work too well but if you ca build a model that will make them work then please give me that model so I can analyze your gameplay to see what magic dust you have
    
    **Advanced Usage:**
    
    By running ```python metric_tetris.py``` you can have Gaz play multiple games at once over many games, build summaries, and eventually will learn and get better at playing tetris.

    To build DataSets and Models edit ```build_model.py``` script to save and build models. Check ```Gaz/game_reader.py``` for the code that builds models. 