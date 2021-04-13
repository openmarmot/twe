
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
import engine.math_2d

from engine.world_object import WorldObject



# load AI 
from ai.ai_man import AIMan
from ai.ai_gun import AIGun
from ai.ai_none import AINone
from ai.ai_building import AIBuilding
from ai.ai_projectile import AIProjectile

# module specific variables
module_version='0.0' #module software version
module_last_update_date='april 11 2021' #date of last update

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

    # projectiles
    world.graphic_engine.loadImage('projectile','images/projectile.png')

    # buildings
    world.graphic_engine.loadImage('warehouse-inside','images/warehouse-inside.png')
    world.graphic_engine.loadImage('warehouse-outside','images/warehouse-outside.png')

    # vehicle
    world.graphic_engine.loadImage('kubelwagen','images/kubelwagen.png')

    #terrain
    world.graphic_engine.loadImage('catgrass','images/catgrass.png')

    #crates?
    world.graphic_engine.loadImage('crate','images/crate.png')

    # effects 
    world.graphic_engine.loadImage('blood_splatter','images/blood_splatter.png')

#------------------------------------------------------------------------------
def load_test_environment(world):
    ''' test environment. not a normal map load '''

    #add a player
    spawn_player(world, [50.,50.])

    # zombie generator 
    #spawn_zombie_horde(world, [10,10], 50)

    # add a couple guns 
    spawn_gun(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'mp40')
    spawn_gun(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'ppk')
    spawn_gun(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'tt33')
    spawn_gun(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'1911')

    # add warehouse
    #spawn_warehouse(world,[float(random.randint(0,1500)),float(random.randint(0,1500))])
    

def spawn_blood_splatter(world,world_coords):
    z=WorldObject(world,['blood_splatter'],AINone)
    z.world_coords=copy.copy(world_coords)
    z.render_level=2
    z.name='blood_splatter'
    z.rotation_angle=float(random.randint(0,359))  
    z.wo_start()   

#------------------------------------------------------------------------------
def spawn_crate(world,world_coords, crate_type):
    # crate_type -- string denoting crate type 
    z=WorldObject(world,['crate'],AINone)
    z.world_coords=copy.copy(world_coords)
    z.is_crate=True
    z.render_level=2
    z.name='crate'
        
    z.wo_start()


#------------------------------------------------------------------------------
def spawn_gun(world,world_coords,GUN_TYPE):

    if GUN_TYPE=='mp40':
        z=WorldObject(world,['mp40'],AIGun)
        z.name='mp40'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=30
        z.ai.mag_capacity=30
        z.ai.rate_of_fire=0.05
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        z.wo_start()

    if GUN_TYPE=='ppk':
        z=WorldObject(world,['ppk'],AIGun)
        z.name='ppk'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=7
        z.ai.mag_capacity=7
        z.ai.rate_of_fire=0.7
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        z.wo_start()

    if GUN_TYPE=='tt33':
        z=WorldObject(world,['tt33'],AIGun)
        z.name='tt33'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=8
        z.ai.mag_capacity=8
        z.ai.rate_of_fire=0.9
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        z.wo_start()

    if GUN_TYPE=='1911':
        z=WorldObject(world,['1911'],AIGun)
        z.name='1911'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=7
        z.ai.mag_capacity=7
        z.ai.rate_of_fire=0.8
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        z.wo_start()


#------------------------------------------------------------------------------
def spawn_kubelwagen(world,world_coords):
    z=WorldObject(world,['kubelwagen'],AINone)
    z.world_coords=copy.copy(world_coords)
    z.is_vehicle=True
    z.render_level=3
    z.wo_start()



#------------------------------------------------------------------------------
def spawn_player(world,WORLD_COORDS):
    z=WorldObject(world,['man'],AIMan)
    z.name='Klaus Hammer'
    z.world_coords=copy.copy(WORLD_COORDS)
    z.speed=50.
    z.is_player=True
    z.render_level=3
    z.is_human=True
    z.wo_start()
    world.player=z

#------------------------------------------------------------------------------
def spawn_projectile(WORLD,WORLD_COORDS,TARGET_COORDS,IGNORE_LIST,MOUSE_AIM):
    # MOUSE_AIM bool as to whether to use mouse aim for calculations
    z=WorldObject(WORLD,['projectile'],AIProjectile)
    z.name='projectile'
    z.world_coords=copy.copy(WORLD_COORDS)
    z.speed=175.
    z.render=3
    z.ai.maxTime=6.
    z.is_projectile=True
    z.render_level=3
    z.ai.ignore_list=IGNORE_LIST

    if MOUSE_AIM :
        # do computations based off of where the mouse is. TARGET_COORDS is ignored
        z.rotation_angle=engine.math_2d.get_rotation(WORLD.graphic_engine.get_player_screen_coords(),WORLD.graphic_engine.get_mouse_screen_coords())
        z.heading=engine.math_2d.get_heading_vector(WORLD.graphic_engine.get_player_screen_coords(),WORLD.graphic_engine.get_mouse_screen_coords())
    else :
        z.rotation_angle=engine.math_2d.get_rotation(WORLD_COORDS,TARGET_COORDS)
        z.heading=engine.math_2d.get_heading_vector(WORLD_COORDS,TARGET_COORDS)

    z.wo_start()

 
#------------------------------------------------------------------------------
def spawn_warehouse(world,world_coords):
    z=WorldObject(world,['warehouse-outside','warehouse-inside'],AIBuilding)
    z.name='warehouse'
    z.world_coords=copy.copy(world_coords)
    z.speed=0
    z.render_level=1
    z.wo_start()

#------------------------------------------------------------------------------
def spawn_zombie(world,world_coords):
    z=WorldObject(world,['zombie_soldier'],AIMan)
    z.name='Zombie Klaus Hammer'
    z.world_coords=world_coords
    z.speed=float(random.randint(10,60))
    z.render_level=3
    z.collision_radius=10
    z.is_human=True
    z.is_zombie=True
    z.wo_start()

#------------------------------------------------------------------------------
def spawn_zombie_horde(world, world_coords, amount):
    for x in range(amount):
        spawn_zombie(world,[float(random.randint(0,500))+world_coords[0],float(random.randint(0,500))+world_coords[1]])