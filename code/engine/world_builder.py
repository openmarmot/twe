
'''
module : world_builder.py
version : see module_version variable
Language : Python 3.x
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
from ai.ai_human import AIHuman
import math
import random
import copy 

#import custom packages
from engine.world import World
import engine.math_2d

from engine.world_object import WorldObject



# load AI 
from ai.ai_human import AIHuman
from ai.ai_gun import AIGun
from ai.ai_none import AINone
from ai.ai_building import AIBuilding
from ai.ai_projectile import AIProjectile
from ai.ai_grenade import AIGrenade
from ai.ai_squad import AISquad
# module specific variables
module_version='0.0' #module software version
module_last_update_date='april 27 2021' #date of last update

#global variables

#------------------------------------------------------------------------------
def create_squads(WORLD,SOLDIERS,FACTION):
    assault_rifles=[]
    rifles=[]
    semiauto_rifles=[]
    subguns=[]
    machineguns=[]
    antitank=[]
    unarmed_vehicle=[]
    armed_vehicle=[]
    tank=[]
    airplane=[]

    # categorize 
    for b in SOLDIERS:
        if b.ai.primary_weapon.name=='kar98k':
            rifles.append(b)
        elif b.ai.primary_weapon.name=='stg44':
            assault_rifles.append(b)
        elif b.ai.primary_weapon.name=='mp40':
            subguns.append(b)
        elif b.ai.primary_weapon.name=='mg34':
            machineguns.append(b)
        elif b.ai.primary_weapon.name=='mosin_nagant':
            rifles.append(b)
        elif b.ai.primary_weapon.name=='ppsh43':
            subguns.append(b)
        elif b.ai.primary_weapon.name=='dp28':
            machineguns.append(b)

    squad_list=[]

    buildsquads=True 

    while buildsquads:
        if len(assault_rifles+rifles+semiauto_rifles+subguns+machineguns+antitank)<1:
            buildsquads=False
        else :
            s=AISquad(WORLD)
            s.faction=FACTION

            # -- build a rifle squad --
            if len(rifles)>7 :
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())

                # mg ?
                if len(machineguns)>0:
                    s.members.append(machineguns.pop())

                # squad lead subgun or assault rifle
                if len(subguns)>0:
                    s.members.append(subguns.pop())
                elif len(assault_rifles)>0:
                    s.members.append(assault_rifles.pop())
            # -- assault squad --
            elif len(assault_rifles)>4 :
                s.members.append(assault_rifles.pop())
                s.members.append(assault_rifles.pop())
                s.members.append(assault_rifles.pop())
                s.members.append(assault_rifles.pop())
                s.members.append(assault_rifles.pop())
            # -- erstaz groups --
            else :
                if len(rifles)>0:
                    s.members.append(rifles.pop())
                if len(semiauto_rifles)>0:
                    s.members.append(semiauto_rifles.pop())
                if len(subguns)>0:
                    s.members.append(subguns.pop())
                if len(assault_rifles)>0:
                    s.members.append(assault_rifles.pop())
                if len(machineguns)>0:
                    s.members.append(machineguns.pop())
                if len(antitank)>0:
                    s.members.append(antitank.pop())

                # lets do it again

                if len(rifles)>0:
                    s.members.append(rifles.pop())
                if len(semiauto_rifles)>0:
                    s.members.append(semiauto_rifles.pop())
                if len(subguns)>0:
                    s.members.append(subguns.pop())
                if len(assault_rifles)>0:
                    s.members.append(assault_rifles.pop())
                if len(machineguns)>0:
                    s.members.append(machineguns.pop())
                if len(antitank)>0:
                    s.members.append(antitank.pop())

            squad_list.append(s)

    return squad_list
            





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
    world.graphic_engine.loadImage('man','images/humans/man.png')
    world.graphic_engine.loadImage('german_soldier','images/humans/german_soldier.png')
    world.graphic_engine.loadImage('german_ss_fall_helm_soldier','images/humans/german_ss_fall_helm_soldier.png')
    world.graphic_engine.loadImage('soviet_soldier','images/humans/russian_soldier.png')
    world.graphic_engine.loadImage('zombie_soldier','images/humans/zombie_soldier.png')
    world.graphic_engine.loadImage('civilian_man','images/humans/civilian_man.png')

    # guns
    world.graphic_engine.loadImage('1911','images/weapons/1911.png')
    world.graphic_engine.loadImage('dp28','images/weapons/dp28.png')
    world.graphic_engine.loadImage('mp40','images/weapons/mp40.png')
    world.graphic_engine.loadImage('panzerfaust','images/weapons/panzerfaust.png')
    world.graphic_engine.loadImage('ppk','images/weapons/ppk.png')
    world.graphic_engine.loadImage('stg44','images/weapons/stg44.png')
    world.graphic_engine.loadImage('tt33','images/weapons/tt33.png')
    world.graphic_engine.loadImage('kar98k','images/weapons/kar98k.png')
    world.graphic_engine.loadImage('mg34','images/weapons/mg34.png')
    world.graphic_engine.loadImage('mosin_nagant','images/weapons/mosin_nagant.png')
    world.graphic_engine.loadImage('ppsh43','images/weapons/ppsh43.png')

    # airplanes
    world.graphic_engine.loadImage('ju88-winter-weathered','images/airplanes/ju88-winter-weathered.png')

    # grenades
    world.graphic_engine.loadImage('model24','images/weapons/model24.png')

    # projectiles
    world.graphic_engine.loadImage('projectile','images/projectile.png')
    world.graphic_engine.loadImage('shrapnel','images/shrapnel.png')

    # buildings
    world.graphic_engine.loadImage('warehouse-inside','images/warehouse-inside.png')
    world.graphic_engine.loadImage('warehouse-outside','images/warehouse-outside.png')

    # vehicle
    world.graphic_engine.loadImage('kubelwagen','images/vehicles/kubelwagen.png')

    #terrain
    world.graphic_engine.loadImage('catgrass','images/catgrass.png')

    #crates?
    world.graphic_engine.loadImage('crate','images/crate.png')

    # effects 
    world.graphic_engine.loadImage('blood_splatter','images/blood_splatter.png')

    # consumables
    world.graphic_engine.loadImage('adler-cheese','images/consumables/adler-cheese.png')
    world.graphic_engine.loadImage('camembert-cheese','images/consumables/camembert-cheese.png')
    world.graphic_engine.loadImage('champignon-cheese','images/consumables/champignon-cheese.png')
    world.graphic_engine.loadImage('karwendel-cheese','images/consumables/karwendel-cheese.png')

#------------------------------------------------------------------------------
def load_test_environment(world):
    ''' test environment. not a normal map load '''

    # this is done by world menu now
    #add a player
    #p=spawn_human(world, [50.,50.],'player',True)
    #p.add_inventory(spawn_gun(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'stg44',False))
    #p.add_inventory(spawn_grenade(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'model24',False))

    # add civilians 
    spawn_human(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'civilian_man',True)
    spawn_human(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'civilian_man',True)
    spawn_human(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'civilian_man',True)
    spawn_human(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'civilian_man',True)

    # zombie generator 
    #spawn_zombie_horde(world, [10,10], 50)

    # add a couple guns 
    spawn_gun(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'mp40',True)
    spawn_gun(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'stg44',True)
    spawn_gun(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'mosin_nagant',True)


    # and some grenades! 
    spawn_grenade(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'model24',True)
    spawn_grenade(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'model24',True)
    spawn_grenade(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'model24',True)
    spawn_grenade(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'model24',True)

    # add ju88
    spawn_ju88(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],True)

    # add warehouse
    #spawn_warehouse(world,[float(random.randint(-1500,1500)),float(random.randint(-1500,1500))])

    #cheese 
    spawn_consumable(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],'karwendel-cheese')
    spawn_consumable(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],'adler-cheese')
    spawn_consumable(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],'camembert-cheese')
    spawn_consumable(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],'champignon-cheese')

    # add ze germans
    s=[]
    s.append(spawn_soldiers(world,'german_kar98k'))
    s.append(spawn_soldiers(world,'german_kar98k'))
    s.append(spawn_soldiers(world,'german_kar98k'))
    s.append(spawn_soldiers(world,'german_kar98k'))
    s.append(spawn_soldiers(world,'german_kar98k'))
    s.append(spawn_soldiers(world,'german_kar98k'))
    s.append(spawn_soldiers(world,'german_kar98k'))
    s.append(spawn_soldiers(world,'german_kar98k'))
    s.append(spawn_soldiers(world,'german_kar98k'))
    s.append(spawn_soldiers(world,'german_kar98k'))
    s.append(spawn_soldiers(world,'german_mp40'))
    s.append(spawn_soldiers(world,'german_mp40'))
    s.append(spawn_soldiers(world,'german_stg44'))
    s.append(spawn_soldiers(world,'german_mg34'))
    s.append(spawn_soldiers(world,'german_mg34'))

    
    # create german squads
    world.german_ai.squads=create_squads(world,s,'german')

    # add ze russians
    s=[]
    s.append(spawn_soldiers(world,'soviet_mosin_nagant'))
    s.append(spawn_soldiers(world,'soviet_mosin_nagant'))
    s.append(spawn_soldiers(world,'soviet_mosin_nagant'))
    s.append(spawn_soldiers(world,'soviet_mosin_nagant'))
    s.append(spawn_soldiers(world,'soviet_mosin_nagant'))
    s.append(spawn_soldiers(world,'soviet_mosin_nagant'))
    s.append(spawn_soldiers(world,'soviet_mosin_nagant'))
    s.append(spawn_soldiers(world,'soviet_mosin_nagant'))
    s.append(spawn_soldiers(world,'soviet_mosin_nagant'))
    s.append(spawn_soldiers(world,'soviet_mosin_nagant'))
    s.append(spawn_soldiers(world,'soviet_mosin_nagant'))
    s.append(spawn_soldiers(world,'soviet_mosin_nagant'))
    s.append(spawn_soldiers(world,'soviet_dp28'))
    s.append(spawn_soldiers(world,'soviet_ppsh43'))
    s.append(spawn_soldiers(world,'soviet_ppsh43'))
    s.append(spawn_soldiers(world,'soviet_ppsh43'))

    # create soviet squads 
    world.soviet_ai.squads=create_squads(world,s,'soviet')

    # spawn
    world.german_ai.spawn_on_map()
    world.soviet_ai.spawn_on_map()

#------------------------------------------------------------------------------    
def spawn_consumable(world,world_coords,CONSUMABLE_TYPE):
    if CONSUMABLE_TYPE=='adler-cheese':
        z=WorldObject(world,['adler-cheese'],AINone)
        z.world_coords=copy.copy(world_coords)
        z.render_level=2
        z.name='Adler cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True 
        z.wo_start() 

    if CONSUMABLE_TYPE=='camembert-cheese':
        z=WorldObject(world,['camembert-cheese'],AINone)
        z.world_coords=copy.copy(world_coords)
        z.render_level=2
        z.name='Camembert cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True 
        z.wo_start() 

    if CONSUMABLE_TYPE=='champignon-cheese':
        z=WorldObject(world,['champignon-cheese'],AINone)
        z.world_coords=copy.copy(world_coords)
        z.render_level=2
        z.name='Champignon cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True 
        z.wo_start() 

    if CONSUMABLE_TYPE=='karwendel-cheese':
        z=WorldObject(world,['karwendel-cheese'],AINone)
        z.world_coords=copy.copy(world_coords)
        z.render_level=2
        z.name='Karwendel cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True 
        z.wo_start() 

#------------------------------------------------------------------------------
def spawn_blood_splatter(world,world_coords):
    z=WorldObject(world,['blood_splatter'],AINone)
    z.world_coords=copy.copy(world_coords)
    z.render_level=2
    z.name='blood_splatter'
    z.rotation_angle=float(random.randint(0,359))  
    z.wo_start()   

#------------------------------------------------------------------------------
def spawn_crate(world,world_coords, crate_type,SPAWN):
    # crate_type -- string denoting crate type 
    z=WorldObject(world,['crate'],AINone)
    z.world_coords=copy.copy(world_coords)
    z.is_crate=True
    z.render_level=2
    z.name='crate'
        
    if SPAWN :
        z.wo_start()
    return z


#------------------------------------------------------------------------------
def spawn_grenade(WORLD,WORLD_COORDS,GRENADE_TYPE,SPAWN):

    if GRENADE_TYPE=='model24':
        z=WorldObject(WORLD,['model24'],AIGrenade)
        z.name='model24'
        z.is_grenade=True
        z.world_coords=copy.copy(WORLD_COORDS)
        z.speed=140.
        z.ai.maxTime=2.
        z.render_level=2

    if SPAWN :
        z.wo_start()
    return z


#------------------------------------------------------------------------------
def spawn_gun(world,world_coords,GUN_TYPE, SPAWN):

    if GUN_TYPE=='mp40':
        z=WorldObject(world,['mp40'],AIGun)
        z.name='mp40'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=32
        z.ai.mag_capacity=32
        z.ai.rate_of_fire=0.12
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    if GUN_TYPE=='ppsh43':
        z=WorldObject(world,['ppsh43'],AIGun)
        z.name='ppsh43'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=35
        z.ai.mag_capacity=35
        z.ai.rate_of_fire=0.12
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    if GUN_TYPE=='stg44':
        z=WorldObject(world,['stg44'],AIGun)
        z.name='stg44'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=30
        z.ai.mag_capacity=30
        z.ai.rate_of_fire=0.1
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    if GUN_TYPE=='dp28':
        z=WorldObject(world,['dp28'],AIGun)
        z.name='dp28'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=47
        z.ai.mag_capacity=47
        z.ai.rate_of_fire=0.12
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    if GUN_TYPE=='ppk':
        z=WorldObject(world,['ppk'],AIGun)
        z.name='ppk'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=7
        z.ai.mag_capacity=7
        z.ai.rate_of_fire=0.6
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    if GUN_TYPE=='tt33':
        z=WorldObject(world,['tt33'],AIGun)
        z.name='tt33'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=8
        z.ai.mag_capacity=8
        z.ai.rate_of_fire=0.8
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    if GUN_TYPE=='1911':
        z=WorldObject(world,['1911'],AIGun)
        z.name='1911'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=7
        z.ai.mag_capacity=7
        z.ai.rate_of_fire=0.7
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    if GUN_TYPE=='mg34':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='mg34'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=75
        z.ai.mag_capacity=75
        z.ai.rate_of_fire=0.05
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    if GUN_TYPE=='kar98k':
        z=WorldObject(world,['kar98k'],AIGun)
        z.name='kar98k'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=5
        z.ai.mag_capacity=5
        z.ai.rate_of_fire=0.7
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    if GUN_TYPE=='mosin_nagant':
        z=WorldObject(world,['mosin_nagant'],AIGun)
        z.name='mosin_nagant'
        z.world_coords=copy.copy(world_coords)
        z.is_gun=True
        z.ai.magazine=2
        z.ai.mag_capacity=2
        z.ai.rate_of_fire=0.7
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    if SPAWN :
        z.wo_start()
    return z

#------------------------------------------------------------------------------
def spawn_human(WORLD,WORLD_COORDS,HUMAN_TYPE,SPAWN):
    # SPAWN -bool, whether to spawn in the world or not 
    
    z=None
    if HUMAN_TYPE=='zombie':
        z=WorldObject(WORLD,['zombie_soldier'],AIHuman)
        z.name='Zombie Klaus Hammer'
        z.world_coords=WORLD_COORDS
        z.speed=float(random.randint(5,20))
        z.render_level=3
        z.collision_radius=10
        z.is_human=True
        z.is_zombie=True
    if HUMAN_TYPE=='player':
        z=WorldObject(WORLD,['man'],AIHuman)
        z.name='Klaus Hammer'
        z.world_coords=copy.copy(WORLD_COORDS)
        z.speed=50.
        z.is_player=True
        z.render_level=3
        z.is_human=True
        WORLD.player=z
    if HUMAN_TYPE=='civilian_man':
        z=WorldObject(WORLD,['civilian_man'],AIHuman)
        z.name='Reginald Thimblebottom'
        z.world_coords=WORLD_COORDS
        z.speed=float(random.randint(18,25))
        z.render_level=3
        z.collision_radius=10
        z.is_human=True
        z.is_civilian=True
    if HUMAN_TYPE=='german_soldier':
        z=WorldObject(WORLD,['german_soldier'],AIHuman)
        z.name='Klaus Hammer'
        z.world_coords=WORLD_COORDS
        z.speed=float(random.randint(18,25))
        z.render_level=3
        z.collision_radius=10
        z.is_human=True
        z.is_soldier=True
        z.is_german=True
    if HUMAN_TYPE=='soviet_soldier':
        z=WorldObject(WORLD,['soviet_soldier'],AIHuman)
        z.name='Boris Volvakov'
        z.world_coords=WORLD_COORDS
        z.speed=float(random.randint(18,25))
        z.render_level=3
        z.collision_radius=10
        z.is_human=True
        z.is_soldier=True
        z.is_soviet=True
    if SPAWN :
        z.wo_start()
    return z


#------------------------------------------------------------------------------
def spawn_ju88(world,world_coords,SPAWN):
    z=WorldObject(world,['ju88-winter-weathered'],AINone)
    z.world_coords=copy.copy(world_coords)
    z.render_level=3
    if SPAWN :
        z.wo_start()
    return z


#------------------------------------------------------------------------------
def spawn_projectile(WORLD,WORLD_COORDS,TARGET_COORDS,SPREAD,IGNORE_LIST,MOUSE_AIM):
    # MOUSE_AIM bool as to whether to use mouse aim for calculations
    z=WorldObject(WORLD,['projectile'],AIProjectile)
    z.name='projectile'
    z.world_coords=copy.copy(WORLD_COORDS)
    z.speed=300.
    z.ai.maxTime=5.
    z.is_projectile=True
    z.render_level=3
    z.ai.ignore_list=IGNORE_LIST

    if MOUSE_AIM :
        # do computations based off of where the mouse is. TARGET_COORDS is ignored
        dst=WORLD.graphic_engine.get_mouse_screen_coords()
        dst=[dst[0]+SPREAD[0],dst[1]+SPREAD[1]]
        z.rotation_angle=engine.math_2d.get_rotation(WORLD.graphic_engine.get_player_screen_coords(),dst)
        z.heading=engine.math_2d.get_heading_vector(WORLD.graphic_engine.get_player_screen_coords(),dst)
    else :
        dst=[TARGET_COORDS[0]+SPREAD[0],TARGET_COORDS[1]+SPREAD[1]]
        z.rotation_angle=engine.math_2d.get_rotation(WORLD_COORDS,dst)
        z.heading=engine.math_2d.get_heading_vector(WORLD_COORDS,dst)

    z.wo_start()

#------------------------------------------------------------------------------
# basically just a different kind of projectile
def spawn_shrapnel(WORLD,WORLD_COORDS,TARGET_COORDS,IGNORE_LIST):
    # MOUSE_AIM bool as to whether to use mouse aim for calculations
    z=WorldObject(WORLD,['shrapnel'],AIProjectile)
    z.name='shrapnel'
    z.world_coords=copy.copy(WORLD_COORDS)
    z.speed=200.
    z.ai.maxTime=random.uniform(0.3, 0.9)
    z.is_projectile=True
    z.render_level=3
    z.ai.ignore_list=IGNORE_LIST
    z.rotation_angle=engine.math_2d.get_rotation(WORLD_COORDS,TARGET_COORDS)
    z.heading=engine.math_2d.get_heading_vector(WORLD_COORDS,TARGET_COORDS)
    # increase the collision radius to make sure we get hits
    z.collision_radius=10
    z.wo_start()

#------------------------------------------------------------------------------
def spawn_shrapnel_cloud(WORLD,WORLD_COORDS,AMOUNT):
    for x in range(AMOUNT):
        target_coords=[float(random.randint(-150,150))+WORLD_COORDS[0],float(random.randint(-150,150))+WORLD_COORDS[1]]
        spawn_shrapnel(WORLD,WORLD_COORDS,target_coords,[])


#------------------------------------------------------------------------------
def spawn_soldiers(WORLD,SOLDIER_TYPE):
    ''' return a soldier with full kit '''
    # --------- german types ---------------------------------
    if SOLDIER_TYPE=='german_kar98k':
        z=spawn_human(WORLD,[0.0],'german_soldier',False)
        z.add_inventory(spawn_gun(WORLD,[0,0],'kar98k',False))
        z.add_inventory(spawn_grenade(WORLD,[0,0],'model24',False))
        return z
    if SOLDIER_TYPE=='german_mp40':
        z=spawn_human(WORLD,[0.0],'german_soldier',False)
        z.add_inventory(spawn_gun(WORLD,[0,0],'mp40',False))
        z.add_inventory(spawn_grenade(WORLD,[0,0],'model24',False))
        return z
    if SOLDIER_TYPE=='german_mg34':
        z=spawn_human(WORLD,[0.0],'german_soldier',False)
        z.add_inventory(spawn_gun(WORLD,[0,0],'mg34',False))
        z.add_inventory(spawn_grenade(WORLD,[0,0],'model24',False))
        return z
    if SOLDIER_TYPE=='german_stg44':
        z=spawn_human(WORLD,[0.0],'german_soldier',False)
        z.add_inventory(spawn_gun(WORLD,[0,0],'stg44',False))
        z.add_inventory(spawn_grenade(WORLD,[0,0],'model24',False))
        return z

    # --------- soviet types ----------------------------------------
    if SOLDIER_TYPE=='soviet_mosin_nagant':
        z=spawn_human(WORLD,[0.0],'soviet_soldier',False)
        z.add_inventory(spawn_gun(WORLD,[0,0],'mosin_nagant',False))
        z.add_inventory(spawn_grenade(WORLD,[0,0],'model24',False))
        return z
    if SOLDIER_TYPE=='soviet_ppsh43':
        z=spawn_human(WORLD,[0.0],'soviet_soldier',False)
        z.add_inventory(spawn_gun(WORLD,[0,0],'ppsh43',False))
        z.add_inventory(spawn_grenade(WORLD,[0,0],'model24',False))
        return z 
    if SOLDIER_TYPE=='soviet_dp28':
        z=spawn_human(WORLD,[0.0],'soviet_soldier',False)
        z.add_inventory(spawn_gun(WORLD,[0,0],'dp28',False))
        z.add_inventory(spawn_grenade(WORLD,[0,0],'model24',False))
        return z 
    if SOLDIER_TYPE=='soviet_tt33':
        z=spawn_human(WORLD,[0.0],'soviet_soldier',False)
        z.add_inventory(spawn_gun(WORLD,[0,0],'tt33',False))
        z.add_inventory(spawn_grenade(WORLD,[0,0],'model24',False)) 
        return z   

#------------------------------------------------------------------------------
def spawn_vehicle(WORLD,WORLD_COORDS,VEHICLE_TYPE,SPAWN):

    if VEHICLE_TYPE=='kubelwagen':
        z=WorldObject(WORLD,['kubelwagen'],AINone)
        z.world_coords=copy.copy(WORLD_COORDS)
        z.is_vehicle=True
        z.render_level=3
        if SPAWN :
            z.wo_start()
        return z

#------------------------------------------------------------------------------
def spawn_warehouse(world,world_coords,SPAWN):
    z=WorldObject(world,['warehouse-outside','warehouse-inside'],AIBuilding)
    z.name='warehouse'
    z.world_coords=copy.copy(world_coords)
    z.speed=0
    z.render_level=1
    if SPAWN :
        z.wo_start()
    return z

#------------------------------------------------------------------------------
def spawn_zombie_horde(world, world_coords, amount):
    for x in range(amount):
        spawn_human(world,[float(random.randint(0,500))+world_coords[0],float(random.randint(0,500))+world_coords[1]],'zombie',True)