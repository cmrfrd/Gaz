Gaz
==============

Tetris has always been an addiction of mine. I decided to eradicate it by "solving" it so I'll never want to play it again.

In case no one gets the [reference](http://zim.wikia.com/wiki/Gaz_Membrane). Gaz keeps playing tetris in order to try and make herself better. Very selfish, and has no remorse.

The only dependency for this repo is ```pygame```. To install,

If you have pip
```bash
pip install pygame
```

or if you don't
```bash
sudo apt-get install python-pygame
```

Instructions
---------------------

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

2. Playing with Gaz

    By running ```python tetris.py -gaz``` Gaz will automatically start playing tetris using her greedy algorithm.
    
    By running ```python tetris.py -gaz -knn``` Gaz will automatically start playing tetris utilizing the k nearest neighbors algorithm with a prebuilt model.
    
    Advanced Usage:
    
    By running ```python metric_tetris.py``` you can have Gaz play multiple games at once over many games.