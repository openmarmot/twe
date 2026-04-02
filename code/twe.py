
'''
repo : https://github.com/openmarmot/twe

notes :

the main python file for the project. 
contains the main loop.

python twe.py will run the project

test run with : python3 twe.py --quick-battle civilian 2

Project Github : https://github.com/openmarmot/twe 

'''


#import built in modules

#import custom packages

import sys
import argparse
from engine.graphics_2d_pygame import Graphics_2D_Pygame

#global variables

#screen_size = (1200,900)
#screen_size = (1920,1080)
#screen_size = None # this is full screen
screen_size = "auto"

#------------------------------------------------------------------------------
def run():
    '''main function'''

    parser = argparse.ArgumentParser()
    parser.add_argument('--quick-battle', nargs=2, metavar=('FACTION', 'OPTION'),
                        help="Start quick battle immediately: FACTION (civilian, german, soviet), OPTION (number)")
    args = parser.parse_args()

    graphic_engine=Graphics_2D_Pygame(screen_size)
    graphic_engine.switch_mode(0)
    if args.quick_battle:
        faction = args.quick_battle[0]
        option = int(args.quick_battle[1])
        graphic_engine.load_quick_battle(faction, option)
        

    # main game loop
    while graphic_engine.quit is False:

        graphic_engine.update()
        graphic_engine.render()

#------------------------------------------------------------------------------
if __name__ == "__main__":
    run()

#import cProfile as profile
#profile.run('run()')
