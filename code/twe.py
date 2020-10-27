
'''
module : twe.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :

the main python file for the project. 
contains the main loop.

'''


#import built in modules
import random

#import custom packages

import engine.world_builder


# module specific variables
module_version='0.1' #module software version
module_last_update_date='Sept 07 2020' #date of last update

#global variables

SCREEN_SIZE = (800, 800)
 

#------------------------------------------------------------------------------
def run():

    world=engine.world_builder.initialize_world(SCREEN_SIZE)
    engine.world_builder.load_test_environment(world)

    while world.graphic_engine.quit==False:

        world.update()
        world.render()
#------------------------------------------------------------------------------

if __name__ == "__main__":
    run()
