
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
- create world objects (can be called by anything)

the idea is this static class holds the standard way for creating objects
- anything that creates objects should do it here

# ref

'''


#import built in modules
import math
import random
import copy 

#import custom packages
from engine.world import World
#from engine.graphics_2d_pygame import Graphics_2D_Pygame

from engine.world_object import WorldObject

#from world_objects.wo_man import WOMan
#from world_objects.wo_crate import WOCrate
#from world_objects.wo_gun import WOGun
#from world_objects.wo_vehicle import WOVehicle


from ai.ai_zombie import AIZombie
from ai.ai_player import AIPlayer
from ai.ai_gun import AIGun
from ai.ai_none import AINone
from ai.ai_building import AIBuilding
# module specific variables
module_version='0.0' #module software version
module_last_update_date='march 28 2021' #date of last update

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
    world.graphic_engine.loadImage('zombie_soldier','images/zombie_soldier.png')

    # weapons
    world.graphic_engine.loadImage('1911','images/1911.png')
    world.graphic_engine.loadImage('dp28','images/dp28.png')
    world.graphic_engine.loadImage('mp40','images/mp40.png')
    world.graphic_engine.loadImage('panzerfaust','images/panzerfaust.png')
    world.graphic_engine.loadImage('ppk','images/ppk.png')
    world.graphic_engine.loadImage('stg44','images/stg44.png')
    world.graphic_engine.loadImage('tt33','images/tt33.png')

    # buildings
    world.graphic_engine.loadImage('warehouse-inside','images/warehouse-inside.png')
    world.graphic_engine.loadImage('warehouse-outside','images/warehouse-outside.png')

    # vehicle
    world.graphic_engine.loadImage('kubelwagen','images/kubelwagen.png')

    #terrain
    world.graphic_engine.loadImage('catgrass','images/catgrass.png')

    #crates?
    world.graphic_engine.loadImage('crate','images/crate.png')

#------------------------------------------------------------------------------
def load_test_environment(world):
    ''' test environment. not a normal map load '''

    #add a player
    spawn_player(world, [50.,50.])

    # zombie generator 
    #spawn_zombie_horde(world, [10,10], 50)

    # add mp40
    spawn_gun(world,[float(random.randint(0,500)),float(random.randint(0,500))],'mp40')

    # add warehouse
    spawn_warehouse(world,[float(random.randint(0,500)),float(random.randint(0,500))])
    

#------------------------------------------------------------------------------
def spawn_crate(world,world_coords, crate_type):
    # crate_type -- string denoting crate type 
    z=WorldObject(world,['crate'],AINone)
    z.world_coords=copy.copy(world_coords)
    z.is_crate=True
    z.render_level=2
        
    z.wo_start()


#------------------------------------------------------------------------------
def spawn_gun(world,world_coords,GUN_TYPE):

    if GUN_TYPE=='mp40':
        z=WorldObject(world,['mp40'],AIGun)
        z.name='Klaus Hammer'
        z.world_coords=world_coords
        z.is_gun=True
        z.render_level=2
        z.wo_start()


#------------------------------------------------------------------------------
def spawn_kubelwagen(world,world_coords):
    z=WorldObject(world,['kubelwagen'],AINone)
    z.world_coords=copy.copy(world_coords)
    z.is_vehicle=True
    z.render_level=3
    z.wo_start()



#------------------------------------------------------------------------------
def spawn_player(world,world_coords):
    z=WorldObject(world,['man'],AIPlayer)
    z.name='Klaus Hammer'
    z.world_coords=world_coords
    z.speed=50.
    z.is_player=True
    z.render_level=3
    z.wo_start()
    world.player=z

#------------------------------------------------------------------------------
def spawn_warehouse(world,world_coords):
    z=WorldObject(world,['warehouse-outside','warehouse-inside'],AIBuilding)
    z.name='Klaus Hammer'
    z.world_coords=world_coords
    z.speed=0
    z.render_level=1
    z.wo_start()

#------------------------------------------------------------------------------
def spawn_zombie(world,world_coords):
    z=WorldObject(world,['zombie_soldier'],AIZombie)
    z.name='Klaus Hammer'
    z.world_coords=world_coords
    z.speed=float(random.randint(10,40))
    z.render_level=3
    z.wo_start()

#------------------------------------------------------------------------------
def spawn_zombie_horde(world, world_coords, amount):
    for x in range(amount):
        spawn_zombie(world,[float(random.randint(0,500))+world_coords[0],float(random.randint(0,500))+world_coords[1]])