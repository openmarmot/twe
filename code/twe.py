
'''
module : twe.py
version : see module_version variable
Language : Python 3.x
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

# module specific variables
module_version='0.1' #module software version
module_last_update_date='June 22 2021' #date of last update

#global variables

SCREEN_SIZE = (1200, 900)
 

#------------------------------------------------------------------------------
def run():

    world=engine.world_builder.initialize_world(SCREEN_SIZE)

    # this has to be here because graphics engine uses player coords in its update
    #  so it needs to be created
    # player will get spawned into the world by its squad
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
