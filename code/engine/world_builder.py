
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
from ai.ai_vehicle import AIVehicle
from ai.ai_human import AIHuman
import math
import random
import copy 

#import custom packages
from engine.world import World
import engine.math_2d

from engine.world_object import WorldObject
from engine.world_area import WorldArea


# load AI 
from ai.ai_human import AIHuman
from ai.ai_gun import AIGun
from ai.ai_none import AINone
from ai.ai_building import AIBuilding
from ai.ai_projectile import AIProjectile
from ai.ai_grenade import AIGrenade
from ai.ai_squad import AISquad
from ai.ai_map_pointer import AIMapPointer
from ai.ai_panzerfaust import AIPanzerfaust
from ai.ai_airplane import AIAirplane

# module specific variables
module_version='0.0' #module software version
module_last_update_date='August 02 2021' #date of last update

#global variables

#------------------------------------------------------------------------------
def create_squads(WORLD,HUMANS,FACTION):
    assault_rifles=[]
    rifles=[]
    semiauto_rifles=[]
    subguns=[]
    machineguns=[]
    antitank=[]
    unidentified_human=[]
    unarmed_human=[]
    unarmed_vehicle=[]
    armed_vehicle=[]
    tank=[]
    airplane=[]

    # categorize 
    for b in HUMANS:
        if b.ai.primary_weapon==None:
            unarmed_human.append(b)
        elif b.ai.primary_weapon.name=='kar98k':
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
        else:
            print('error: unknown primary weapon in squad creation')

    squad_list=[]

    buildsquads=True 

    while buildsquads:
        if len(assault_rifles+rifles+semiauto_rifles+subguns+machineguns+antitank+unarmed_human)<1:
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
                if len(unarmed_human)>0:
                    s.members.append(unarmed_human.pop())

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
                if len(unarmed_human)>0:
                    s.members.append(unarmed_human.pop())

            squad_list.append(s)

    return squad_list
            

#------------------------------------------------------------------------------
def generate_world_area(WORLD,WORLD_COORDS,TYPE,NAME):
    ''' generates the world areas on a NEW map. existing maps will pull this from the database '''
    # TYPE town, airport, bunkers, field_depot, train_depot 
    group=[]
    if TYPE=='town':
        count=random.randint(1,5)
        for x in range(count):
            coords=[WORLD_COORDS[0]+float(random.randint(-200,200)),WORLD_COORDS[1]+float(random.randint(-200,200))]
            group.append(spawn_object(WORLD,coords,'warehouse',True))
        count=random.randint(2,15)
        for x in range(count):
            coords=[WORLD_COORDS[0]+float(random.randint(-200,200)),WORLD_COORDS[1]+float(random.randint(-200,200))]
            group.append(spawn_object(WORLD,coords,'square_building',True))
    
    # do some sorting 
    engine.math_2d.collision_sort(600,group)


    # make the corresponding worldArea object
    w=WorldArea(WORLD)
    w.world_coords=copy.copy(WORLD_COORDS)
    w.name=NAME

    # register with world 
    WORLD.world_areas.append(w)

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
    # not used at the moment
    world.graphic_engine.loadImage('zombie_soldier','images/humans/zombie_soldier.png')
    world.graphic_engine.loadImage('civilian_man','images/humans/civilian_man.png')

    # guns
    world.graphic_engine.loadImage('1911','images/weapons/1911.png')
    world.graphic_engine.loadImage('dp28','images/weapons/dp28.png')
    world.graphic_engine.loadImage('mp40','images/weapons/mp40.png')
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

    # at rockets
    world.graphic_engine.loadImage('panzerfaust','images/weapons/panzerfaust.png')
    world.graphic_engine.loadImage('panzerfaust_warhead','images/projectiles/panzerfaust_warhead.png')


    # projectiles
    world.graphic_engine.loadImage('projectile','images/projectiles/projectile.png')
    world.graphic_engine.loadImage('shrapnel','images/projectiles/shrapnel.png')

    # buildings
    world.graphic_engine.loadImage('warehouse-inside','images/buildings/warehouse-inside.png')
    world.graphic_engine.loadImage('warehouse-outside','images/buildings/warehouse-outside.png')
    world.graphic_engine.loadImage('square_building_inside','images/buildings/square_building_inside.png')
    world.graphic_engine.loadImage('square_building_outside','images/buildings/square_building_outside.png')

    # vehicle
    world.graphic_engine.loadImage('kubelwagen','images/vehicles/kubelwagen.png')
    world.graphic_engine.loadImage('kubelwagen_destroyed','images/vehicles/kubelwagen_destroyed.png')

    #terrain
    world.graphic_engine.loadImage('catgrass','images/catgrass.png')

    #containers
    world.graphic_engine.loadImage('crate','images/containers/crate.png')
    world.graphic_engine.loadImage('german_mg_ammo_can','images/containers/german_mg_ammo_can.png')

    # effects (sprites)
    world.graphic_engine.loadImage('blood_splatter','images/sprites/blood_splatter.png')
    world.graphic_engine.loadImage('brass','images/sprites/brass.png')
    # regular dirt was cool but it was huge. may use in future
    world.graphic_engine.loadImage('dirt','images/sprites/small_dirt.png')

    # consumables
    world.graphic_engine.loadImage('adler-cheese','images/consumables/adler-cheese.png')
    world.graphic_engine.loadImage('camembert-cheese','images/consumables/camembert-cheese.png')
    world.graphic_engine.loadImage('champignon-cheese','images/consumables/champignon-cheese.png')
    world.graphic_engine.loadImage('karwendel-cheese','images/consumables/karwendel-cheese.png')

    # random 
    world.graphic_engine.loadImage('map_pointer_green','images/map/map_pointer_green.png')
    world.graphic_engine.loadImage('map_pointer_blue','images/map/map_pointer_blue.png')
    world.graphic_engine.loadImage('map_pointer_orange','images/map/map_pointer_orange.png')

#------------------------------------------------------------------------------
def load_test_environment(world):
    ''' test environment. not a normal map load '''


    # add a couple weapons 
    spawn_object(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'mp40',True)
    spawn_object(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'panzerfaust',True)
    spawn_object(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'panzerfaust',True)
    spawn_object(world,[float(random.randint(-200,200)),float(random.randint(-200,200))],'model24',True)


    # add ju88
    spawn_object(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],'ju88',True)

    # kubelwagens 
    spawn_object(world,[float(random.randint(-1500,1500)),float(random.randint(-1500,1500))],'kubelwagen',True)
    spawn_object(world,[float(random.randint(-1500,1500)),float(random.randint(-1500,1500))],'kubelwagen',True)


    # add warehouse
    #spawn_warehouse(world,[float(random.randint(-1500,1500)),float(random.randint(-1500,1500))])

    #cheese 
    spawn_object(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],'karwendel-cheese',True)
    spawn_object(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],'adler-cheese',True)
    spawn_object(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],'camembert-cheese',True)
    spawn_object(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],'champignon-cheese',True)


    # spawn some ammo cans 
    spawn_object(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],"german_mg_ammo_can",True)
    spawn_object(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],"german_mg_ammo_can",True)
    spawn_object(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],"german_mg_ammo_can",True)

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
    s.append(spawn_soldiers(world,'german_stg44'))
    s.append(spawn_soldiers(world,'german_stg44'))


    
    # create german squads
    world.german_ai.squads+=create_squads(world,s,'german')

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
    world.soviet_ai.squads+=create_squads(world,s,'soviet')

    # add civilians
    s=[]
    s.append(spawn_civilians(world,'default'))
    s.append(spawn_civilians(world,'default'))
    s.append(spawn_civilians(world,'default'))
    s.append(spawn_civilians(world,'default'))
    s.append(spawn_civilians(world,'default'))
    s.append(spawn_civilians(world,'default'))
    s.append(spawn_civilians(world,'default'))
    s.append(spawn_civilians(world,'default'))
    s.append(spawn_civilians(world,'default'))
    s.append(spawn_civilians(world,'pistol'))
    s.append(spawn_civilians(world,'pistol'))
    s.append(spawn_civilians(world,'big_cheese'))


    # create civilian squads 
    world.civilian_ai.squads+=create_squads(world,s,'civilian')



    # spawn
    # locations will eventually be determined by map control
    world.german_ai.spawn_on_map(world.spawn_west)
    world.soviet_ai.spawn_on_map(world.spawn_east)
    world.american_ai.spawn_on_map(world.spawn_north)
    world.civilian_ai.spawn_on_map(world.spawn_center)

    # add some world areas
    generate_world_area(world,[-2000,2000],'town','Alfa')
    generate_world_area(world,[2000,-2000],'town','Bravo')
    generate_world_area(world,[2000,2000],'town','Charlie')

   # generate_world_area(world,[0,0],'town','Danitza')

#------------------------------------------------------------------------------
def spawn_civilians(WORLD,CIVILIAN_TYPE):
    ''' return a civilian with full kit '''
    # --------- german types ---------------------------------
    if CIVILIAN_TYPE=='default':
        z=spawn_object(WORLD,[0.0],'civilian_man',False)
        z.world_builder_identity='civilian_default'
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        return z
    if CIVILIAN_TYPE=='pistol':
        z=spawn_object(WORLD,[0.0],'civilian_man',False)
        z.world_builder_identity='civilian_default'
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'ppk',False))
        return z
    if CIVILIAN_TYPE=='big_cheese':
        '''goofy unique civilain. don't mess with big cheese'''
        z=spawn_object(WORLD,[0.0],'civilian_man',False)
        z.ai.health*=2
        z.world_builder_identity='civilian_default'
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'camembert-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'camembert-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'camembert-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'camembert-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'camembert-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mg34',False))
        return z

#------------------------------------------------------------------------------
def spawn_object(WORLD,WORLD_COORDS,OBJECT_TYPE, SPAWN):
    z=None
    if OBJECT_TYPE=='warehouse':
        z=WorldObject(WORLD,['warehouse-outside','warehouse-inside'],AIBuilding)
        z.name='warehouse'
        z.speed=0
        z.render_level=1
        z.collision_radius=200
        z.is_building=True

    elif OBJECT_TYPE=='square_building':
        z=WorldObject(WORLD,['square_building_outside','square_building_inside'],AIBuilding)
        z.name='square building'
        z.speed=0
        z.render_level=1
        z.collision_radius=60
        z.is_building=True

    elif OBJECT_TYPE=='adler-cheese':
        z=WorldObject(WORLD,['adler-cheese'],AINone)
        z.render_level=2
        z.name='Adler cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True 

    elif OBJECT_TYPE=='camembert-cheese':
        z=WorldObject(WORLD,['camembert-cheese'],AINone)
        z.render_level=2
        z.name='Camembert cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True 

    elif OBJECT_TYPE=='champignon-cheese':
        z=WorldObject(WORLD,['champignon-cheese'],AINone)
        z.render_level=2
        z.name='Champignon cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True 

    elif OBJECT_TYPE=='karwendel-cheese':
        z=WorldObject(WORLD,['karwendel-cheese'],AINone)
        z.render_level=2
        z.name='Karwendel cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True 

    elif OBJECT_TYPE=='crate':
        z=WorldObject(WORLD,['crate'],AINone)
        z.is_container=True
        z.render_level=2
        z.name='crate'
        z.world_builder_identity='crate'

    elif OBJECT_TYPE=='german_mg_ammo_can':
        z=WorldObject(WORLD,['german_mg_ammo_can'],AINone)
        z.is_container=True
        z.render_level=2
        z.name='german_mg_ammo_can'
        z.world_builder_identity='german_mg_ammo_can'

    elif OBJECT_TYPE=='panzerfaust':
        z=WorldObject(WORLD,['panzerfaust','panzerfaust_warhead'],AIPanzerfaust)
        z.name='panzerfaust'
        z.render_level=2
        z.speed=250
        z.is_handheld_antitank=True

    elif OBJECT_TYPE=='model24':
        z=WorldObject(WORLD,['model24'],AIGrenade)
        z.name='model24'
        z.is_grenade=True
        z.speed=180.
        z.ai.maxTime=1.5
        z.render_level=2

    elif OBJECT_TYPE=='mp40':
        z=WorldObject(WORLD,['mp40'],AIGun)
        z.name='mp40'
        z.world_builder_identity='gun_mp40'
        z.is_gun=True
        z.ai.magazine=32
        z.ai.mag_capacity=32
        z.ai.magazine_count=6
        z.ai.max_magazines=6
        z.ai.rate_of_fire=0.12
        z.ai.flight_time=2
        z.ai.range=700
        z.ai.type='submachine gun'
        z.ai.projectile_type='9mm_ME'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='ppsh43':
        z=WorldObject(WORLD,['ppsh43'],AIGun)
        z.name='ppsh43'
        z.is_gun=True
        z.ai.magazine=35
        z.ai.mag_capacity=35
        z.ai.magazine_count=4
        z.ai.max_magazines=4
        z.ai.rate_of_fire=0.12
        z.ai.flight_time=2
        z.ai.range=700
        z.ai.type='submachine gun'
        z.ai.projectile_type='7.62x25'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='stg44':
        z=WorldObject(WORLD,['stg44'],AIGun)
        z.name='stg44'
        z.is_gun=True
        z.ai.magazine=30
        z.ai.mag_capacity=30
        z.ai.magazine_count=6
        z.ai.max_magazines=6
        z.ai.rate_of_fire=0.1
        z.ai.flight_time=2.5
        z.ai.range=800
        z.ai.type='assault rifle'
        z.ai.projectile_type='7.92x33_SME'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='dp28':
        z=WorldObject(WORLD,['dp28'],AIGun)
        z.name='dp28'
        z.is_gun=True
        z.ai.magazine=47
        z.ai.mag_capacity=47
        z.ai.magazine_count=2
        z.ai.max_magazines=2
        z.ai.rate_of_fire=0.12
        z.ai.flight_time=3.5
        z.ai.range=800
        z.ai.type='machine gun'
        z.ai.projectile_type='7.92x57_SSP'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='ppk':
        z=WorldObject(WORLD,['ppk'],AIGun)
        z.name='ppk'
        z.is_gun=True
        z.ai.magazine=7
        z.ai.mag_capacity=7
        z.ai.magazine_count=2
        z.ai.max_magazines=2
        z.ai.rate_of_fire=0.7
        z.ai.flight_time=1
        z.ai.range=380
        z.ai.type='pistol'
        z.ai.projectile_type='9mm_115'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='tt33':
        z=WorldObject(WORLD,['tt33'],AIGun)
        z.name='tt33'
        z.is_gun=True
        z.ai.magazine=8
        z.ai.mag_capacity=8
        z.ai.magazine_count=2
        z.ai.max_magazines=2
        z.ai.rate_of_fire=0.9
        z.ai.flight_time=1
        z.ai.range=380
        z.ai.type='pistol'
        z.ai.projectile_type='7.62x25'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='1911':
        z=WorldObject(WORLD,['1911'],AIGun)
        z.name='1911'
        z.is_gun=True
        z.ai.magazine=7
        z.ai.mag_capacity=7
        z.ai.magazine_count=2
        z.ai.max_magazines=2
        z.ai.rate_of_fire=0.8
        z.ai.flight_time=1
        z.ai.range=380
        z.ai.type='pistol'
        z.ai.projectile_type='45acp'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mg34':
        z=WorldObject(WORLD,['mg34'],AIGun)
        z.name='mg34'
        z.is_gun=True
        z.ai.magazine=75
        z.ai.mag_capacity=75
        z.ai.magazine_count=4
        z.ai.max_magazines=4
        z.ai.rate_of_fire=0.05
        z.ai.flight_time=3.5
        z.ai.range=850
        z.ai.type='machine gun'
        z.ai.projectile_type='7.92x57_SME'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='kar98k':
        z=WorldObject(WORLD,['kar98k'],AIGun)
        z.name='kar98k'
        z.is_gun=True
        z.ai.magazine=5
        z.ai.mag_capacity=5
        z.ai.magazine_count=8
        z.ai.max_magazines=8
        z.ai.rate_of_fire=1.1
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='rifle'
        z.ai.projectile_type='7.92x57_SME'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mosin_nagant':
        z=WorldObject(WORLD,['mosin_nagant'],AIGun)
        z.name='mosin_nagant'
        z.is_gun=True
        z.ai.magazine=5
        z.ai.mag_capacity=5
        z.ai.magazine_count=6
        z.ai.max_magazines=6
        z.ai.rate_of_fire=1.1
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='rifle'
        z.ai.projectile_type='7.92x57_SME'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='kubelwagen':
        z=WorldObject(WORLD,['kubelwagen'],AIVehicle)
        z.name='kubelwagen'
        z.is_vehicle=True
        z.render_level=3
        z.speed=200
        z.rotation_speed=40.
        z.ai.acceleration=100
        z.collision_radius=50
        z.add_inventory(spawn_object(WORLD,[0,0],'mg34',False))

    elif OBJECT_TYPE=='ju88':
        z=WorldObject(WORLD,['ju88-winter-weathered'],AIAirplane)
        z.name='Junkers Ju88'
        z.speed=500
        z.rotation_speed=50
        z.ai.acceleration=100
        z.render_level=3
        z.collision_radius=200
        z.add_inventory(spawn_object(WORLD,[0,0],'mg34',False)) 
        z.ai.fuel_capacity=2900
        z.ai.fuel=2900
        z.is_airplane=True 

    elif OBJECT_TYPE=='player':
        z=WorldObject(WORLD,['man'],AIHuman)
        z.name='Klaus Hammer'
        z.speed=50.
        z.is_player=True
        z.render_level=3
        z.is_human=True
        WORLD.player=z

    elif OBJECT_TYPE=='civilian_man':
        z=WorldObject(WORLD,['civilian_man'],AIHuman)
        z.name='Reginald Thimblebottom'
        z.speed=float(random.randint(10,25))
        z.render_level=3
        z.collision_radius=10
        z.is_human=True
        z.is_civilian=True

    elif OBJECT_TYPE=='german_soldier':
        z=WorldObject(WORLD,['german_soldier'],AIHuman)
        z.name='Klaus Hammer'
        z.speed=float(random.randint(20,25))
        z.render_level=3
        z.collision_radius=10
        z.is_human=True
        z.is_soldier=True
        z.is_german=True

    elif OBJECT_TYPE=='soviet_soldier':
        z=WorldObject(WORLD,['soviet_soldier'],AIHuman)
        z.name='Boris Volvakov'
        z.speed=float(random.randint(20,25))
        z.render_level=3
        z.collision_radius=10
        z.is_human=True
        z.is_soldier=True
        z.is_soviet=True

    elif OBJECT_TYPE=='brass':
        z=WorldObject(WORLD,['brass'],AINone)
        w=[WORLD_COORDS[0]+float(random.randint(-7,7)),WORLD_COORDS[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.render_level=2
        z.name='brass'
        z.rotation_angle=float(random.randint(0,359))  
    
    elif OBJECT_TYPE=='blood_splatter':
        z=WorldObject(WORLD,['blood_splatter'],AINone)
        z.render_level=2
        z.name='blood_splatter'
        z.rotation_angle=float(random.randint(0,359))  
           
    elif OBJECT_TYPE=='dirt':
        z=WorldObject(WORLD,['dirt'],AINone)
        z.render_level=2
        z.name='dirt'
        z.rotation_angle=float(random.randint(0,359))
    else:
        print('!! Spawn Error: '+OBJECT_TYPE+' is not recognized.')  

    # -- generic settings that apply to all --
    z.world_builder_identity=OBJECT_TYPE
    # set world coords if they weren't already set
    if z.world_coords==None:
        z.world_coords=copy.copy(WORLD_COORDS)

    if SPAWN :
        z.wo_start()
    return z


#------------------------------------------------------------------------------
def spawn_map_pointer(WORLD,TARGET_COORDS,TYPE):
    if TYPE=='normal':
        z=WorldObject(WORLD,['map_pointer_green'],AIMapPointer)
        z.ai.target_coords=TARGET_COORDS
        z.render_level=4
        z.is_map_pointer=True
        z.wo_start()


#------------------------------------------------------------------------------
def spawn_projectile(WORLD,WORLD_COORDS,TARGET_COORDS,SPREAD,IGNORE_LIST,MOUSE_AIM,SHOOTER,MAX_TIME,PROJECTILE_TYPE):
    # MOUSE_AIM bool as to whether to use mouse aim for calculations
    # SHOOTER - the world_object that actually pulled the trigger (a human or vehicle, not a gun)
    # MAX_TIME - max flight time around 3.5 seconds is default
    z=WorldObject(WORLD,['projectile'],AIProjectile)
    z.name='projectile'
    z.world_coords=copy.copy(WORLD_COORDS)
    z.speed=350.
    z.ai.maxTime=MAX_TIME + random.uniform(0.01, 0.05)
    z.is_projectile=True
    z.render_level=3
    z.ai.ignore_list=copy.copy(IGNORE_LIST)
    z.ai.shooter=SHOOTER
    z.ai.projectile_type=PROJECTILE_TYPE

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
def spawn_shrapnel(WORLD,WORLD_COORDS,TARGET_COORDS,IGNORE_LIST,PROJECTILE_TYPE,MIN_TIME,MAX_TIME,ORIGINATOR):
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    # MOUSE_AIM bool as to whether to use mouse aim for calculations
    z=WorldObject(WORLD,['shrapnel'],AIProjectile)
    z.name='shrapnel'
    z.world_coords=copy.copy(WORLD_COORDS)
    z.speed=300.
    z.ai.maxTime=random.uniform(MIN_TIME, MAX_TIME)
    z.is_projectile=True
    z.render_level=3
    z.ai.ignore_list=copy.copy(IGNORE_LIST)
    z.ai.projectile_type=PROJECTILE_TYPE
    z.rotation_angle=engine.math_2d.get_rotation(WORLD_COORDS,TARGET_COORDS)
    z.heading=engine.math_2d.get_heading_vector(WORLD_COORDS,TARGET_COORDS)
    # increase the collision radius to make sure we get hits
    z.collision_radius=10
    z.ai.shooter=ORIGINATOR
    z.wo_start()

#------------------------------------------------------------------------------
def spawn_shrapnel_cloud(WORLD,WORLD_COORDS,AMOUNT,ORIGINATOR):
    ''' creates a shrapnel starburst pattern. used for grenades '''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    for x in range(AMOUNT):
        target_coords=[float(random.randint(-150,150))+WORLD_COORDS[0],float(random.randint(-150,150))+WORLD_COORDS[1]]
        spawn_shrapnel(WORLD,WORLD_COORDS,target_coords,[],'shrapnel',0.1,0.4,ORIGINATOR)

#------------------------------------------------------------------------------
def spawn_heat_jet(WORLD,WORLD_COORDS,TARGET_COORDS,AMOUNT,ORIGINATOR):
    ''' creates a cone/line of shrapnel. used for panzerfaust'''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    for x in range(AMOUNT):
        target_coords=[float(random.randint(-5,5))+TARGET_COORDS[0],float(random.randint(-5,5))+TARGET_COORDS[1]]
        spawn_shrapnel(WORLD,WORLD_COORDS,target_coords,[],'HEAT_jet',0.1,0.3,ORIGINATOR)


#------------------------------------------------------------------------------
def spawn_soldiers(WORLD,SOLDIER_TYPE):
    ''' return a soldier with full kit '''
    # --------- german types ---------------------------------
    if SOLDIER_TYPE=='german_kar98k':
        z=spawn_object(WORLD,[0.0],'german_soldier',False)
        z.world_builder_identity='german_kar98k'
        z.add_inventory(spawn_object(WORLD,[0,0],'kar98k',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        return z
    if SOLDIER_TYPE=='german_mp40':
        z=spawn_object(WORLD,[0.0],'german_soldier',False)
        z.world_builder_identity='german_mp40'
        z.add_inventory(spawn_object(WORLD,[0,0],'mp40',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        return z
    if SOLDIER_TYPE=='german_mg34':
        z=spawn_object(WORLD,[0.0],'german_soldier',False)
        z.world_builder_identity='german_mg34'
        z.add_inventory(spawn_object(WORLD,[0,0],'mg34',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        return z
    if SOLDIER_TYPE=='german_stg44':
        z=spawn_object(WORLD,[0.0],'german_soldier',False)
        z.world_builder_identity='german_stg44'
        z.add_inventory(spawn_object(WORLD,[0,0],'stg44',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        return z

    # --------- soviet types ----------------------------------------
    if SOLDIER_TYPE=='soviet_mosin_nagant':
        z=spawn_object(WORLD,[0.0],'soviet_soldier',False)
        z.world_builder_identity='soviet_mosin_nagant'
        z.add_inventory(spawn_object(WORLD,[0,0],'mosin_nagant',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        return z
    if SOLDIER_TYPE=='soviet_ppsh43':
        z=spawn_object(WORLD,[0.0],'soviet_soldier',False)
        z.world_builder_identity='soviet_ppsh43'
        z.add_inventory(spawn_object(WORLD,[0,0],'ppsh43',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        return z 
    if SOLDIER_TYPE=='soviet_dp28':
        z=spawn_object(WORLD,[0.0],'soviet_soldier',False)
        z.world_builder_identity='soviet_dp28'
        z.add_inventory(spawn_object(WORLD,[0,0],'dp28',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        return z 
    if SOLDIER_TYPE=='soviet_tt33':
        z=spawn_object(WORLD,[0.0],'soviet_soldier',False)
        z.world_builder_identity='soviet_tt33'
        z.add_inventory(spawn_object(WORLD,[0,0],'tt33',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False)) 
        return z   
