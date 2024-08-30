
'''
module : twe.py
language : Python 3.x
email : andrew@openmarmot.com
notes :

the main python file for the project. 
contains the main loop.

python twe.py will run the project

Project Github : https://github.com/openmarmot/twe 

'''


#import built in modules
import random

#import custom packages
import engine.world_builder
from engine.world import World
from engine.graphics_2d_pygame import Graphics_2D_Pygame

#global variables

SCREEN_SIZE = (1200, 900)
 

#------------------------------------------------------------------------------
def run():

    graphic_engine=Graphics_2D_Pygame(SCREEN_SIZE)

    world = World()

    # fake player that is only used until the player actually spawns via the menu
    # required because the game engine needs to know the player position
    p=engine.world_builder.spawn_object(world, [50.,50.],'player',False)
    

    #-- launch start menu ---
    world.world_menu.active_menu='start'
    world.world_menu.menu_state='none'
    # fake input to get the text added
    world.world_menu.handle_input('none')

    graphic_engine.world=world

    # main game loop
    while graphic_engine.quit==False:

        graphic_engine.update()
        graphic_engine.render()
#------------------------------------------------------------------------------

if __name__ == "__main__":
    run()

#import cProfile as profile
#profile.run('run()')
