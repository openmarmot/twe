
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

#global variables

SCREEN_SIZE = (1200, 900)
 

#------------------------------------------------------------------------------
def run():

    world = World(SCREEN_SIZE)

    # fake player that is only used until the player actually spawns via the menu
    # required because the game engine needs to know the player position
    p=engine.world_builder.spawn_object(world, [50.,50.],'player',False)
    

    #-- launch start menu ---
    world.world_menu.active_menu='start'
    world.world_menu.menu_state='none'
    # fake input to get the text added
    world.world_menu.handle_input('none')



    # main game loop
    while world.graphic_engine.quit==False:

        world.update()
        world.render()
#------------------------------------------------------------------------------

if __name__ == "__main__":
    run()

#import cProfile as profile
#profile.run('run()')
