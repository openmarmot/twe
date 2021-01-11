
'''
module : world_builder.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes : 

static module with the following responsibilities
- build worlds
- load art assets (?)

should this be a class called by world instead of a static file that creates world??

# ref

'''


#import built in modules
import math
import random

#import custom packages
from engine.world import World
#from engine.graphics_2d_pygame import Graphics_2D_Pygame

from world_objects.wo_man import WOMan
from world_objects.wo_player import WOPlayer

from world_objects.wo_gun import WOGun

# module specific variables
module_version='0.0' #module software version
module_last_update_date='October 26 2020' #date of last update

#global variables

#------------------------------------------------------------------------------
def initialize_world(SCREEN_SIZE):
    '''
    returns a world object that has completed basic init
    '''

    world = World(SCREEN_SIZE)

    load_images(world)

    return world

#------------------------------------------------------------------------------
def load_images(world):
    '''
    load art assets
    '''
    # people
    world.graphic_engine.loadImage('man','images/man.png')
    world.graphic_engine.loadImage('german_soldier','images/german_soldier.png')
    world.graphic_engine.loadImage('german_ss_fall_helm_soldier','images/german_ss_fall_helm_soldier.png')
    world.graphic_engine.loadImage('russian_soldier','images/russian_soldier.png')

    # weapons
    world.graphic_engine.loadImage('1911','images/1911.png')
    world.graphic_engine.loadImage('dp28','images/dp28.png')
    world.graphic_engine.loadImage('mp40','images/mp40.png')
    world.graphic_engine.loadImage('panzerfaust','images/panzerfaust.png')
    world.graphic_engine.loadImage('ppk','images/ppk.png')
    world.graphic_engine.loadImage('stg44','images/stg44.png')
    world.graphic_engine.loadImage('tt33','images/tt33.png')

    #terrain
    world.graphic_engine.loadImage('catgrass','images/catgrass.png')

    #crates?
    world.graphic_engine.loadImage('crate','images/crate.png')

#------------------------------------------------------------------------------
def load_test_environment(world):
    ''' test environment. not a normal map load '''

    #add a player
    player=WOPlayer(world)
    player.is_player=True
    player.world_coords=[50.,50.]
    player.name='player'
    player.wo_start()
    world.player=player

    # bob generator 
    for x in range(50):
        bob=WOMan(world)
        bob.name='bob'
        bob.world_coords=[float(random.randint(0,500)),float(random.randint(0,500))]
        bob.speed=float(random.randint(10,40))
        bob.wo_start()

    # add mp40
    mp40=WOGun(world,'mp40')
    mp40.world_coords=[float(random.randint(0,500)),float(random.randint(0,500))]
    mp40.wo_start()