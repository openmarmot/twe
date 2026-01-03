
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :

the main python file for the project. 
contains the main loop.

python twe.py will run the project

Project Github : https://github.com/openmarmot/twe 

'''


#import built in modules

#import custom packages

from engine.graphics_2d_pygame import Graphics_2D_Pygame

#global variables

#screen_size = (1200,900)
screen_size = (1920,1080)
#screen_size = None # this is full screen

#------------------------------------------------------------------------------
def run():
    '''main function'''

    graphic_engine=Graphics_2D_Pygame(screen_size)
    graphic_engine.switch_mode(0)

    # main game loop
    while graphic_engine.quit is False:

        graphic_engine.update()
        graphic_engine.render()

#------------------------------------------------------------------------------
if __name__ == "__main__":
    run()

#import cProfile as profile
#profile.run('run()')
