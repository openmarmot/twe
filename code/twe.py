
'''
module : twe.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules
import random

#import custom packages

from engine.world import World
from engine.graphics_2d_pygame import Graphics_2D_Pygame

from world_objects.wo_man import WOMan
from world_objects.wo_player import WOPlayer


# module specific variables
module_version='0.1' #module software version
module_last_update_date='Sept 07 2020' #date of last update

#global variables


SCREEN_SIZE = (800, 800)
world=None

#------------------------------------------------------------------------------
def load():
    global world

# note - this all needs to be moved to a dedicated world_load file

    world = World(Graphics_2D_Pygame(SCREEN_SIZE))


    #load images
    world.graphic_engine.loadImage('man','images/man.png')

    #add a couple test objects
    player=WOPlayer(world)
    player.is_player=True
    player.world_coords=[50.,50.]
    player.name='player'
    player.wo_start()
    world.player=player

    # bob generator 
    for x in range(500):
        bob=WOMan(world)
        bob.name='bob'
        bob.world_coords=[float(random.randint(0,500)),float(random.randint(0,500))]
        bob.speed=float(random.randint(10,40))
        bob.wo_start()

 

#------------------------------------------------------------------------------
def run():

    load()

    while world.graphic_engine.quit==False:

        world.update()
        world.render()
#------------------------------------------------------------------------------

if __name__ == "__main__":
    run()
