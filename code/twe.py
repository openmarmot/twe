
'''
repo : https://github.com/openmarmot/twe

notes :

the main python file for the project.
contains the main loop.

python twe.py will run the project

test run with : python3 twe.py --quick-battle civilian 2

Project Github : https://github.com/openmarmot/twe

This is not meant to be run directly. instead use start.sh

for a timed test do the following
runs quick battle as civilian faction and exits after N seconds:
bash start.sh --ai-test civilian 10

'''


#import built in modules

#import custom packages

import argparse
import time
import pygame
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
    parser.add_argument('--ai-test', nargs=2, metavar=('FACTION', 'SECONDS'),
                        help="AI testing mode: auto-run quick battle and exit after SECONDS")
    args = parser.parse_args()

    graphic_engine=Graphics_2D_Pygame(screen_size)
    graphic_engine.switch_mode(0)
    if args.quick_battle:
        faction = args.quick_battle[0]
        option = int(args.quick_battle[1])
        graphic_engine.load_quick_battle(faction, option)

    ai_test_seconds = None
    ai_test_start_time = None
    ai_test_grace_period = 2.0
    if args.ai_test:
        faction = args.ai_test[0]
        option = int(args.ai_test[1].split('.')[0])
        ai_test_seconds = float(args.ai_test[1])
        graphic_engine.load_quick_battle(faction, option)
        ai_test_start_time = time.time()

    # main game loop
    while graphic_engine.quit is False:

        graphic_engine.update()
        graphic_engine.render()

        if ai_test_seconds is not None and time.time() - ai_test_start_time >= ai_test_seconds:
                graphic_engine.quit = True
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    if args.ai_test:
        time.sleep(ai_test_grace_period)

#------------------------------------------------------------------------------
if __name__ == "__main__":
    run()

#import cProfile as profile
#profile.run('run()')
