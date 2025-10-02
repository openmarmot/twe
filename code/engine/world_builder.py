
'''
repo : https://github.com/openmarmot/twe
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
import os
import sqlite3

#import custom packages
import engine.math_2d
import engine.name_gen
import engine.log
from engine.world_object import WorldObject
from engine.world_area import WorldArea
from engine.map_object import MapObject
import engine.world_radio
import engine.penetration_calculator
from engine.vehicle_role import VehicleRole
import engine.map_generator


# load AI
from ai.ai_human import AIHuman
from ai.ai_vehicle import AIVehicle
from ai.ai_gun import AIGun
from ai.ai_magazine import AIMagazine
from ai.ai_none import AINone
from ai.ai_building import AIBuilding
from ai.ai_projectile import AIProjectile
from ai.ai_throwable import AIThrowable
from ai.ai_squad import AISquad
from ai.ai_map_pointer import AIMapPointer
from ai.ai_container import AIContainer
from ai.ai_consumable import AIConsumable
from ai.ai_medical import AIMedical
from ai.ai_engine import AIEngine
from ai.ai_coffee_grinder import AICoffeeGrinder
from ai.ai_animated_sprite import AIAnimatedSprite
from ai.ai_wearable import AIWearable
from ai.ai_battery import AIBattery
from ai.ai_radio import AIRadio
from ai.ai_turret import AITurret
from ai.ai_rotor import AIRotor
from ai.ai_hit_marker import AIHitMarker
from ai.ai_dani import AIDani
from ai.ai_wheel import AIWheel

#global variables

# ------ object rarity lists -----------------------------------
list_consumables=['green_apple','potato','turnip','cucumber','pickle','adler-cheese','camembert-cheese'
,'champignon-cheese','karwendel-cheese','wine','schokakola']
list_consumables_common=['green_apple','potato','turnip','cucumber','pickle']
list_consumables_rare=['adler-cheese','camembert-cheese','champignon-cheese','karwendel-cheese','wine','beer']
list_consumables_ultra_rare=['schokakola']

list_household_items=['blue_coffee_cup','coffee_tin','coffee_grinder','pickle_jar']

list_guns=['kar98k','stg44','mp40','mg34','mg42','mosin_nagant','ppsh43','ppsh41','dp28','1911','ppk','tt33','g41w','k43',
    'svt40','svt40-sniper','mg15','fg42-type1','fg42-type2','c96','c96_red_9']
list_guns_common=['kar98k','mosin_nagant','ppsh43','ppsh41','tt33','svt40']
list_guns_rare=['mp40','ppk','stg44','mg34','dp28','k43','g41w','c96']
list_guns_ultra_rare=['fg42-type1','fg42-type2','svt40-sniper','1911','mg15','c96_red_9']
list_german_guns=['kar98k','stg44','mp40','mg34','ppk','k43','g41w','fg42-type1','fg42-type2','walther_p38']

list_guns_rifles=['kar98k','mosin_nagant','g41w','k43','svt40','svt40-sniper']
list_guns_smg=['mp40','ppsh43','ppsh41']
list_guns_assault_rifles=['stg44']
list_guns_machine_guns=['mg34','mg42','dp28','mg15','fg42-type1','fg42-type2']
list_guns_pistols=['1911','ppk','tt33','c96','c96_red_9','walther_p38','luger_p08']
list_guns_at_rifles=['ptrs_41']

list_german_military_equipment=['german_folding_shovel','german_field_shovel']


list_medical=['bandage','german_officer_first_aid_kit']
list_medical_common=['bandage']
list_medical_rare=['german_officer_first_aid_kit']
list_medical_ultra_rare=[]
#----------------------------------------------------------------

# ------ variables that get pulled from sqlite -----------------------------------
squad_data={}

#------------------------------------------------------------------------------
def add_random_pistol_to_inventory(wo,world):
    '''adds a random pistol to the inventory'''
    pistol=random.randint(0,6)
    if pistol==0:
        wo.add_inventory(spawn_object(world,wo.world_coords,'ppk',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'ppk_magazine',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'ppk_magazine',False))
    elif pistol==1:
        wo.add_inventory(spawn_object(world,wo.world_coords,'c96',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'c96_magazine',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'c96_magazine',False))
    elif pistol==2:
        wo.add_inventory(spawn_object(world,wo.world_coords,'tt33',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'tt33_magazine',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'tt33_magazine',False))
    elif pistol==3:
        wo.add_inventory(spawn_object(world,wo.world_coords,'1911',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'1911_magazine',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'1911_magazine',False))
    elif pistol==4:
        wo.add_inventory(spawn_object(world,wo.world_coords,'c96_red_9',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'c96_red_9_magazine',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'c96_red_9_magazine',False))
    elif pistol==5:
        wo.add_inventory(spawn_object(world,wo.world_coords,'walther_p38',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'p38_magazine',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'p38_magazine',False))
    elif pistol==6:
        wo.add_inventory(spawn_object(world,wo.world_coords,'luger_p08',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'luger_p08_magazine',False))
        wo.add_inventory(spawn_object(world,wo.world_coords,'luger_p08_magazine',False))

#------------------------------------------------------------------------------
def add_standard_loadout(wo,world,loadout):
    '''adds a standard loadout to the world object'''
    # loadout - list of strings that correspond to the loadout
    # returns the world object with the loadout added

    if loadout=='dp28':
        wo.add_inventory(spawn_object(world,[0,0],'dp28',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'dp28_magazine',False))
    elif loadout=='fg42-type2':
        wo.add_inventory(spawn_object(world,[0,0],'fg42-type2',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'fg42_type2_magazine',False))
    elif loadout=='g41w':
        wo.add_inventory(spawn_object(world,[0,0],'g41w',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'g41w_magazine',False))
    elif loadout=='kar98k':
        wo.add_inventory(spawn_object(world,[0,0],'kar98k',False))
        for _ in range(12):
            wo.add_inventory(spawn_object(world,[0,0],'kar98k_magazine',False))
    elif loadout=='k43':
        wo.add_inventory(spawn_object(world,[0,0],'k43',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'k43_magazine',False))
    elif loadout=='mg15':
        wo.add_inventory(spawn_object(world,[0,0],'mg15',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'mg15_drum_magazine',False))
    elif loadout=='mg34':
        wo.add_inventory(spawn_object(world,[0,0],'mg34',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'mg34_drum_magazine',False))
    elif loadout=='mg42':
        wo.add_inventory(spawn_object(world,[0,0],'mg42',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'mg34_drum_magazine',False))
    elif loadout=='mosin_nagant':
        wo.add_inventory(spawn_object(world,[0,0],'mosin_nagant',False))
        for _ in range(12):
            wo.add_inventory(spawn_object(world,[0,0],'mosin_magazine',False))
    elif loadout=='mp40':
        wo.add_inventory(spawn_object(world,[0,0],'mp40',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'mp40_magazine',False))
    elif loadout=='panzerschreck':
        wo.add_inventory(spawn_object(world,[0,0],'panzerschreck',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'panzerschreck_magazine',False))
    elif loadout=='ppsh43':
        wo.add_inventory(spawn_object(world,[0,0],'ppsh43',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'ppsh43_magazine',False))
    elif loadout=='ppsh41':
        wo.add_inventory(spawn_object(world,[0,0],'ppsh41',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'ppsh41_box_magazine',False))
    elif loadout=='ptrs_41':
        wo.add_inventory(spawn_object(world,[0,0],'ptrs_41',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'ptrs_41_magazine',False))
    elif loadout=='standard_german_gear':
        wo.add_inventory(spawn_object(world,[0,0],'helmet_stahlhelm',False))
        wo.add_inventory(spawn_object(world,[0,0],'model24',False))
        wo.add_inventory(spawn_object(world,[0,0],'bandage',False))
        wo.ai.wallet['German Military Script']=round(random.uniform(0.05,1.5),2)
    elif loadout=='standard_soviet_gear':
        wo.add_inventory(spawn_object(world,[0,0],'helmet_ssh40',False))
        wo.add_inventory(spawn_object(world,[0,0],'rg_42_grenade',False))
        wo.add_inventory(spawn_object(world,[0,0],'bandage',False))
        wo.ai.wallet['Soviet Ruble']=round(random.uniform(0.05,1.5),2)
    elif loadout=='stg44':
        wo.add_inventory(spawn_object(world,[0,0],'stg44',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'stg44_magazine',False))
    elif loadout=='svt40':
        wo.add_inventory(spawn_object(world,[0,0],'svt40',False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world,[0,0],'svt40_magazine',False))
    elif loadout=='tt33':
        wo.add_inventory(spawn_object(world,[0,0],'tt33',False))
        for _ in range(2):
            wo.add_inventory(spawn_object(world,[0,0],'tt33_magazine',False))


#------------------------------------------------------------------------------
def convert_map_objects_to_world_objects(world,map_objects):
    '''handles converting map_objects to world_objects and spawns them'''

    # note - unsure whether it is best to spawn the objects at this time or not.
    # for now i'm going to spawn them here

    for map_object in map_objects:

        # world_area_ is a special case object
        if map_object.world_builder_identity.startswith('world_area'):
            # make the corresponding WorldArea object
            w=WorldArea(world)
            w.world_coords=map_object.world_coords
            w.name=map_object.name
            w.area_type=map_object.world_builder_identity.split('world_area_')[1]

            # register with world 
            world.world_areas.append(w)
        else:

            wo=spawn_object(world,map_object.world_coords,map_object.world_builder_identity,True)
            
            if wo is None:
                # this means the world_builder_identity was not recognized by spawn_object
                engine.log.add_data('error','world_builder.convert_map_objects_to_world_objects could not convert '+map_object.world_builder_identity,True)
            else:
                wo.rotation_angle=map_object.rotation
                
                if map_object.name not in  ('none',''):
                    wo.name=map_object.name
                
                # add in the saved inventory
                # remember that map_object.inventory is a array of world_builder_identity names
                if len(map_object.inventory)>0:
                    #print('inventory',map_object.inventory)
                    # need to prevent duplicates. this could be better
                    for a in map_object.inventory:
                        already_exists=False
                        for b in wo.ai.inventory:
                            if b.name==a:
                                already_exists=True
                                break
                        if already_exists is False:
                            wo.ai.inventory.append(spawn_object(world,[0,0],a,False))

    # this is needed to flush all the new objects out of the queue and into the world
    world.process_add_remove_queue()

#------------------------------------------------------------------------------
def convert_world_objects_to_map_objects(world,map_square):
    '''converts all world objects to map objects'''

    # clear old map objects
    map_square.map_objects=[]

    # convert world areas to map objects
    for b in world.world_areas:
        # we don't save the dynamic ones, they are generated each time
        if b.area_type!='dynamic':
            temp=MapObject('world_area_'+b.area_type,b.name,b.world_coords,0,[])
            map_square.map_objects.append(temp)

    # convert world objects to map objects
    for b in world.grid_manager.get_all_objects():
        # a couple objects we don't want to save
        if b.no_save is False:
            # assemble inventory name list
            inventory=[]
            if hasattr(b.ai,'inventory'):
                for i in b.ai.inventory:
                    inventory.append(i.world_builder_identity)
            temp=MapObject(b.world_builder_identity,b.name,b.world_coords,0,inventory)
            map_square.map_objects.append(temp)



    # TBD - handle objects that exited the map

#------------------------------------------------------------------------------

def create_random_battlegroup(faction, funds):
    '''Create random battlegroup for a faction'''
    
    battlegroup = []
    cost = 0

    # Sort faction-specific data into categories
    squad_options_tanks = {}
    squad_options_infantry = {}
    squad_options_support_infantry = {}
    squad_options_support_vehicle = {}
    squad_options_other = {}
    
    for key, value in squad_data.items():
        if value['faction'] == faction:
            if value['type'] == 'tank':
                squad_options_tanks[key] = value
            elif value['type'] in ['infantry', 'motorized_infantry', 'mechanized_infantry']:
                squad_options_infantry[key] = value
            elif value['type'] in ['medic', 'mechanic', 'sniper', 'infantry radio', 'mg', 'antitank_infantry']:
                squad_options_support_infantry[key] = value
            elif value['type'] in ['antitank_vehicle', 'fire_support_vehicle', 'towed_antiair', 'scout car']:
                squad_options_support_vehicle[key] = value
            else:
                squad_options_other[key] = value
    
    # Define categories with their batch ranges (min, max)
    categories = [
        (squad_options_infantry, 3, 5),
        (squad_options_tanks, 1, 3),
        (squad_options_support_infantry, 0, 2),
        (squad_options_support_vehicle, 0, 2),
        (squad_options_other, 0, 2)
    ]
    
    while cost < funds:
        added = False
        #random.shuffle(categories)  # Randomize order to avoid bias
        
        for cat_dict, min_num, max_num in categories:
            if cat_dict:
                random_key = random.choice(list(cat_dict.keys()))
                unit_cost = cat_dict[random_key]['cost']
                for i in range(random.randint(min_num, max_num)):
                    if cost + unit_cost <= funds:
                        cost += unit_cost
                        battlegroup.append(random_key)
                        added = True
                    else:
                        break  # No need to try more in this batch
        
        if not added:
            break  # Prevent infinite loop if can't afford anything
    
    return battlegroup

#------------------------------------------------------------------------------
def fill_container(world,container,fill_name):
    ''' fill container with an object (liquid)'''
    # CONTAINER - should be empty
    # FILL_NAME - name of object (liquid) to fill the container with 

    fill=spawn_object(world,[0,0],fill_name,False)
    fill.volume=container.volume
    # need something more clever here.. maybe a density value per object
    fill.weight=container.volume
    container.ai.inventory.append(fill)



#------------------------------------------------------------------------------
def generate_dynamic_world_areas(world):
    ''' generates dynamic world areas'''
    # create some world areas after the world loaded
    # combat ai needs arount 5 or so world_areas to be interesting

    # first some directional ones

    w=WorldArea(world)
    w.world_coords=[-5000,0]
    w.name='west'
    w.area_type='dynamic'
    world.world_areas.append(w)

    w=WorldArea(world)
    w.world_coords=[5000,0]
    w.name='east'
    w.area_type='dynamic'
    world.world_areas.append(w)

    w=WorldArea(world)
    w.world_coords=[0,-5000]
    w.name='north'
    w.area_type='dynamic'
    world.world_areas.append(w)

    w=WorldArea(world)
    w.world_coords=[0,5000]
    w.name='south'
    w.area_type='dynamic'
    world.world_areas.append(w)


#------------------------------------------------------------------------------
def get_random_from_list(world,world_coords,OBJECT_LIST,spawn):
    ''' returns a random object from a list'''
    # OBJECT_LIST : a list of strings that correspond to an object_Type for the 
    # spawn_object function
    index=random.randint(0,len(OBJECT_LIST)-1)
    return spawn_object(world,world_coords,OBJECT_LIST[index],spawn)

#------------------------------------------------------------------------------
def get_squad_map_objects(squad_name):
    '''get a list of map objects that make up a squad'''
    global squad_data
    members=[]
    if squad_name in squad_data:
        members=squad_data[squad_name]['members'].split(',')

    else:
        print('squad data',squad_data)
        engine.log.add_data('error','worldbuilder.get_squad_map_objects squad_name '+squad_name+' not recognized',True)

    # convert each member to a map_object
    map_objects=[]
    for b in members:
        map_objects.append(MapObject(b,'none',[0,0],0,[]))
    
    return map_objects

#------------------------------------------------------------------------------
def load_magazine(world,magazine,projectile_type=None):
    '''loads a magazine with bullets'''
    # wipe whatever is in there
    magazine.ai.projectiles=[]
    
    # gives the option to specify the projectile to load
    if projectile_type==None:
        projectile_type=magazine.ai.compatible_projectiles[0]

    if projectile_type in magazine.ai.compatible_projectiles:
        count=len(magazine.ai.projectiles)
        while count<magazine.ai.capacity:
            z=spawn_object(world,[0,0],'projectile',False)
            z.ai.projectile_type=projectile_type

            # change to a bigger projectile image. might make a couple more
            if engine.penetration_calculator.projectile_data[projectile_type]['diameter'] >14:
                z.image_list=['projectile_mid']
            magazine.ai.projectiles.append(z)

            count+=1
    else:
        engine.log.add_data('Error','world_builder.load_magazine incompatible projectile type: '+projectile_type,True)
    
    # set use case. first reset defaults as this function can be called multiple times
    magazine.ai.use_antitank=False
    magazine.ai.use_antipersonnel=False
    if engine.penetration_calculator.projectile_data[projectile_type]['use']=='at':
        magazine.ai.use_antitank=True
    elif engine.penetration_calculator.projectile_data[projectile_type]['use']=='ap':
        magazine.ai.use_antipersonnel=True
    elif engine.penetration_calculator.projectile_data[projectile_type]['use']=='both':
        magazine.ai.use_antipersonnel=True
        magazine.ai.use_antitank=True
    else:
        engine.log.add_data('Error','world_builder.load_magazine unknown use for projectile: '+projectile_type,True)

#------------------------------------------------------------------------------
def load_quick_battle_map_objects(battle_option,result_container):
    ''' load quick battle map objects. called by game menu'''

    # this is called in a thread by graphics_2d_pygame.load_quick_battle

    world_area_options=[]
    world_area_options.append(['town','town','town'])
    world_area_options.append(['airport'])
    map_areas=random.choice(world_area_options)

    map_objects=engine.map_generator.generate_map(map_areas)

    # -- initial troops --
    squads=[]
    
    

    if battle_option=='1':
        points=2500
        soviet_advantage=points*0.3
        print(f'soviet advantage: {soviet_advantage}')
        squads+=create_random_battlegroup('german',points)
        squads+=create_random_battlegroup('soviet',points+soviet_advantage)

    elif battle_option=='2':
        points=5000
        soviet_advantage=points*0.3
        print(f'soviet advantage: {soviet_advantage}')
        squads+=create_random_battlegroup('german',points)
        squads+=create_random_battlegroup('soviet',points+soviet_advantage)

    
    elif battle_option=='3':
        points=10000
        soviet_advantage=points*0.3
        print(f'soviet advantage: {soviet_advantage}')
        squads+=create_random_battlegroup('german',points)
        squads+=create_random_battlegroup('soviet',points+soviet_advantage)

    # testing
    elif battle_option=='4':
        for b in range(50):
            squads.append('Soviet T-70')
        squads.append('German Panzer VI Ausf E camo1')
        squads.append('German Panzer VI Ausf E camo1')
        squads.append('German Panzer VI Ausf E camo1')

        
        #squads.append('Soviet T34-76 Model 1943')

        #squads.append('German Sd.kfz.251/9')

    # bench mark
    elif battle_option=='5':
        for b in range(100):
            squads.append('Soviet T34-76 Model 1943')
            squads.append('German Panzer IV Ausf G')


    for squad in squads:
        map_objects+=get_squad_map_objects(squad)

    result_container[0]=map_objects


#------------------------------------------------------------------------------
def load_sqlite_squad_data():
    '''builds a squad_data dictionary from sqlite data'''
    global squad_data
    squad_data={}

    conn = sqlite3.connect('data/data.sqlite')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM squad_data")
    
    # Fetch all column names
    column_names = [description[0] for description in cursor.description]
    # Fetch all rows from the table
    rows = cursor.fetchall()

    # Convert rows to dictionary, excluding the 'id' field
    for row in rows:
        row_dict = {column_names[i]: row[i] for i in range(len(column_names)) if column_names[i] != 'id'}
        key = row_dict.pop('name')
        squad_data[key] = row_dict

    # Close the database connection
    conn.close()

#------------------------------------------------------------------------------
def load_world(world,map_objects):
    '''coverts map_objects to world_objects and does everything necessary to load the world'''

    # this is called in a thread by graphics_2d_pygame.load_world()

    # convert map_objects to world_objects
    # note - this also spawns them and creates the world_area objects
    convert_map_objects_to_world_objects(world,map_objects)

    # generate some minor world areas for battle flow
    generate_dynamic_world_areas(world)
    
    # perform all world start tasks
    world.start()

#------------------------------------------------------------------------------
def spawn_aligned_pile(world,point_a,point_b,spawn_string,separation_distance,count,second_layer=True):
    ''' spawn an aligned pile like a wood pile'''
    # point_a - initial spawn point
    # point_b - direction in which the pile grows to 
    # spawn_string - name of the object to spawn
    # separation_distance - distance betwween objects

    rotation=engine.math_2d.get_rotation(point_a,point_b)
    heading=engine.math_2d.get_heading_from_rotation(rotation)
    

    # bottom layer
    current_coords=point_a
    for x in range(count):
        current_coords=engine.math_2d.moveAlongVector(separation_distance,current_coords,heading,1)

        x=spawn_object(world,point_a,spawn_string,True)
        x.rotation_angle=rotation
        x.heading=heading
        x.world_coords=current_coords

    if second_layer:
        current_coords=engine.math_2d.moveAlongVector(separation_distance/3,point_a,heading,1)
        for x in range(int(count/2)):
            current_coords=engine.math_2d.moveAlongVector(separation_distance,current_coords,heading,1)

            x=spawn_object(world,point_a,spawn_string,True)
            x.rotation_angle=rotation
            x.heading=heading
            x.world_coords=current_coords

#------------------------------------------------------------------------------
def spawn_container_body(name,world_object,image_index):
    '''spawns a custom container for a body'''
    # name 
    # world_object - the world_object that is being replaced
    # image_index - index of the image to be used - from the world object
    z=WorldObject(world_object.world,[world_object.image_list[image_index]],AIContainer)
    z.is_container=True
    z.name=name
    z.world_coords=world_object.world_coords
    z.rotation_angle=world_object.rotation_angle
    z.ai.inventory=world_object.ai.inventory
    z.world_builder_identity='body'
    z.volume=world_object.volume
    z.weight=world_object.weight
    z.collision_radius=world_object.collision_radius
    z.is_large_human_pickup=True
    z.is_body=True
    # containers normally update to handle leaks - this is no update for performance considerations
    z.no_update=True 
    z.wo_start()

#------------------------------------------------------------------------------
def spawn_drop_canister(world,world_coords,CRATE_TYPE):
    ''' generates different crate types with contents'''

    z=spawn_object(world,world_coords,'german_drop_canister',True)

    if CRATE_TYPE=='mixed_supply':
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_german_guns,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_german_guns,False))
        z.ai.inventory.append(spawn_object(world,world_coords,'panzerfaust_60',False))
        z.ai.inventory.append(spawn_object(world,world_coords,'panzerfaust_100',False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_medical,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_medical,False))

#------------------------------------------------------------------------------
def spawn_explosion_and_fire(world,world_coords,fire_duration,smoke_duration):
    ''' spawn explosion and fire effects '''
    heading=[0,0]

    for x in range(10):
        coords=[world_coords[0]+random.randint(-2,2),world_coords[1]+random.randint(-2,2)]
        z=spawn_object(world,coords,'small_smoke',True)
        z.heading=heading
        z.ai.speed=random.uniform(1,2)
        z.ai.rotation_speed=random.randint(30,40)
        z.ai.rotate_time_max=60
        z.ai.move_time_max=3
        z.ai.alive_time_max=smoke_duration

    for x in range(1):
        coords=[world_coords[0]+random.randint(-2,2),world_coords[1]+random.randint(-2,2)]
        z=spawn_object(world,coords,'small_fire',True)
        z.heading=heading
        z.ai.speed=random.uniform(1,2)
        z.ai.rotation_speed=random.randint(80,90)
        z.ai.rotate_time_max=5
        z.ai.move_time_max=5
        z.ai.alive_time_max=fire_duration

    for x in range(5):
        coords=[world_coords[0]+random.randint(-2,2),world_coords[1]+random.randint(-2,2)]
        z=spawn_object(world,coords,'small_flash',True)
        z.heading=heading
        z.ai.speed=random.uniform(1,2)
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=random.uniform(0.1,0.4)

    for x in range(1):
        coords=[world_coords[0]+random.randint(-2,2),world_coords[1]+random.randint(-2,2)]
        z=spawn_object(world,coords,'small_explosion',True)
        z.heading=heading
        z.ai.speed=random.uniform(1,2)
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=random.uniform(0.09,0.1)

#------------------------------------------------------------------------------
def spawn_flash(world,world_coords,heading,amount=2):
    ''' spawn flash cloud '''

    for x in range(amount):
        coords=[world_coords[0]+random.randint(-2,2),world_coords[1]+random.randint(-2,2)]
        z=spawn_object(world,coords,'small_flash',True)
        z.heading=heading
        z.ai.speed=random.uniform(1,2)
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=random.uniform(0.1,0.4)
  
#------------------------------------------------------------------------------
def spawn_object(world,world_coords,object_type, spawn):
    '''returns new object. optionally spawns it in the world'''
    z=None
    if object_type=='warehouse':
        z=WorldObject(world,['warehouse-outside','warehouse-inside'],AIBuilding)
        z.name='warehouse'
        z.collision_radius=200
        z.weight=10000
        z.is_building=True

    elif object_type=='square_building':
        z=WorldObject(world,['square_building_outside','square_building_inside'],AIBuilding)
        z.name='square building'
        z.collision_radius=60
        z.weight=10000
        z.is_building=True
    
    elif object_type=='hangar':
        z=WorldObject(world,['hangar_outside','hangar_inside'],AIBuilding)
        z.name='hangar'
        z.collision_radius=600
        z.weight=10000
        z.is_building=True

    elif object_type=='green_apple':
        z=WorldObject(world,['green_apple'],AIConsumable)
        z.name='Green Apple'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-10 

    elif object_type=='potato':
        z=WorldObject(world,['potato'],AIConsumable)
        z.name='potato'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-70
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-20  

    elif object_type=='turnip':
        z=WorldObject(world,['turnip'],AIConsumable)
        z.name='turnip'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-60
        z.ai.thirst_effect=-8
        z.ai.fatigue_effect=-10  
    
    elif object_type=='cucumber':
        z=WorldObject(world,['cucumber'],AIConsumable)
        z.name='cucumber'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-60
        z.ai.thirst_effect=-8
        z.ai.fatigue_effect=-10  

    elif object_type=='pickle':
        z=WorldObject(world,['cucumber'],AIConsumable)
        z.name='pickle'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-60
        z.ai.thirst_effect=-8
        z.ai.fatigue_effect=-10 

    elif object_type=='adler-cheese':
        z=WorldObject(world,['adler-cheese'],AIConsumable)
        z.name='Adler cheese'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-200
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif object_type=='camembert-cheese':
        z=WorldObject(world,['camembert-cheese'],AIConsumable)
        z.name='Camembert cheese'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-250
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif object_type=='champignon-cheese':
        z=WorldObject(world,['champignon-cheese'],AIConsumable)
        z.name='Champignon cheese'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-300
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif object_type=='karwendel-cheese':
        z=WorldObject(world,['karwendel-cheese'],AIConsumable)
        z.name='Karwendel cheese'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-500
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif object_type=='wine':
        z=WorldObject(world,['wine_bottle'],AIConsumable)
        z.name='wine'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=-500
        z.ai.fatigue_effect=50

    elif object_type=='beer':
        z=WorldObject(world,['green_bottle'],AIConsumable)
        z.name='beer'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=-500
        z.ai.fatigue_effect=50   

    elif object_type=='schokakola':
        z=WorldObject(world,['schokakola'],AIConsumable)
        z.name='scho-ka-kola'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=15
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=10
        z.ai.fatigue_effect=-250 
    elif object_type=='bandage':
        z=WorldObject(world,['bandage'],AIMedical)
        z.name='bandage'
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_medical=True
        z.ai.health_effect=50
        z.ai.hunger_effect=0
        z.ai.thirst_effect=0
        z.ai.fatigue_effect=0
    elif object_type=='german_officer_first_aid_kit':
        z=WorldObject(world,['german_officer_first_aid_kit'],AIMedical)
        z.name='German Officer First Aid Kit'
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_medical=True
        z.ai.health_effect=150
        z.ai.hunger_effect=0
        z.ai.thirst_effect=0
        z.ai.fatigue_effect=-300  

    elif object_type=='german_fuel_can':
        z=WorldObject(world,['german_fuel_can'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.volume=20
        z.name='german_fuel_can'
        z.rotation_angle=float(random.randint(0,359))
        fill_container(world,z,'gas_80_octane')

    elif object_type=='blue_coffee_cup':
        z=WorldObject(world,['blue_coffee_cup'],AIContainer)
        z.is_container=True
        z.volume=0.3
        z.name='blue_coffee_cup'
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='55_gallon_drum':
        z=WorldObject(world,['55_gallon_drum'],AIContainer)
        z.is_container=True
        z.volume=208
        z.name='55_gallon_drum'
        z.collision_radius=15
        z.rotation_angle=float(random.randint(0,359))
        z.volume=208.2
        fill_container(world,z,'gas_80_octane')

    elif object_type=='barrel':
        z=WorldObject(world,['barrel'],AIContainer)
        z.is_container=True
        z.volume=208
        z.name='barrel'
        z.collision_radius=15
        z.rotation_angle=float(random.randint(0,359))
        z.no_update=True
        if random.randint(0,1)==1:
            fill_container(world,z,'water')

    elif object_type=='german_mg_ammo_can':
        z=WorldObject(world,['german_mg_ammo_can'],AIContainer)
        z.is_ammo_container=True
        z.is_large_human_pickup=True
        z.name='german_mg_ammo_can'
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='german_drop_canister':
        z=WorldObject(world,['german_drop_canister'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.name='german drop canister'
        z.collision_radius=20
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='crate':
        z=WorldObject(world,['crate'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.name='crate'
        z.collision_radius=20
        z.rotation_angle=float(random.randint(0,359))
        z.volume=100
        z.no_update=True
    
    elif object_type=='crate_mp40':
        z=spawn_object(world,world_coords,'crate',False)
        z.add_inventory(spawn_object(world,world_coords,'mp40',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))

    elif object_type=='crate_random_consumables':
        z=spawn_object(world,world_coords,'crate',False)
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))


    elif object_type=='small_crate':
        z=WorldObject(world,['small_crate'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.name='small_crate'
        z.collision_radius=20
        z.rotation_angle=float(random.randint(0,359))
        z.volume=100
        z.no_update=True

    elif object_type=='cupboard':
        z=WorldObject(world,['cupboard'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.name='cupboard'
        z.collision_radius=20
        z.rotation_angle=float(random.randint(0,359))
        z.volume=100
        z.no_update=True

        if random.randint(0,1)==1:
            z.ai.inventory.append(get_random_from_list(world,world_coords,list_household_items,False))
            z.ai.inventory.append(get_random_from_list(world,world_coords,list_household_items,False))
        if random.randint(0,1)==1:  
            z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables,False))


    elif object_type=='coffee_tin':
        z=WorldObject(world,['coffee_tin'],AIContainer)
        z.is_container=True
        z.volume=1
        z.name='coffee_tin'
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359))
        contents='coffee_beans'
        if random.randint(0,1)==1:
            contents='ground_coffee'
        fill_container(world,z,contents)

    elif object_type=='jar':
        z=WorldObject(world,['jar'],AIContainer)
        z.is_container=True
        z.volume=1
        z.name='jar'
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='pickle_jar':
        z=spawn_object(world,world_coords,'jar',False)
        z.name='pickle jar'
        z.minimum_visible_scale=0.4
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))

    elif object_type=='panzerfaust_60':
        z=WorldObject(world,['panzerfaust','panzerfaust_empty'],AIGun)
        z.name='panzerfaust 60'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.ai.mechanical_accuracy=15
        z.ai.speed=300
        z.is_handheld_antitank=True
        z.ai.magazine=spawn_object(world,world_coords,'panzerfaust_60_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=0
        z.ai.range=1209
        z.ai.type='antitank launcher'
        z.ai.use_antitank=True
        z.ai.smoke_on_fire=True
        z.ai.smoke_type='rocket'
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='panzerfaust_60_magazine':
        z=WorldObject(world,['panzerfaust_empty'],AIMagazine)
        z.name='panzerfaust internal magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['panzerfaust_60']
        z.ai.compatible_projectiles=['panzerfaust_60']
        z.ai.capacity=1
        z.ai.removable=False
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='panzerfaust_100':
        z=WorldObject(world,['panzerfaust','panzerfaust_empty'],AIGun)
        z.name='panzerfaust 100'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.ai.mechanical_accuracy=15
        z.ai.speed=300
        z.is_handheld_antitank=True
        z.ai.magazine=spawn_object(world,world_coords,'panzerfaust_100_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=0
        z.ai.range=1813
        z.ai.type='antitank launcher'
        z.ai.use_antitank=True
        z.ai.smoke_on_fire=True
        z.ai.smoke_type='rocket'
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='panzerfaust_100_magazine':
        z=WorldObject(world,['panzerfaust_empty'],AIMagazine)
        z.name='panzerfaust internal magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['panzerfaust_100']
        z.ai.compatible_projectiles=['panzerfaust_100']
        z.ai.capacity=1
        z.ai.removable=False
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='panzerschreck':
        z=WorldObject(world,['panzerschreck','panzerschreck'],AIGun)
        z.name='panzerschreck'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.ai.mechanical_accuracy=10
        z.ai.speed=300
        z.is_handheld_antitank=True
        z.ai.magazine=spawn_object(world,world_coords,'panzerschreck_magazine',False)
        z.ai.rate_of_fire=1
        z.ai.reload_speed=25
        z.ai.range=2000
        z.ai.type='antitank launcher'
        z.ai.use_antitank=True
        z.ai.smoke_on_fire=True
        z.ai.smoke_type='rocket'
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='panzerschreck_magazine':
        z=WorldObject(world,['panzerfaust_warhead'],AIMagazine)
        z.name='panzerschreck magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['panzerschreck']
        z.ai.compatible_projectiles=['panzerschreck']
        z.ai.capacity=1
        z.ai.removable=True
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='model24':
        z=WorldObject(world,['model24'],AIThrowable)
        z.name='model24'
        z.minimum_visible_scale=0.4
        z.is_grenade=True
        z.is_throwable=True
        z.ai.explosive=True
        z.ai.shrapnel_count=5
        z.ai.explosion_radius=35
        z.ai.max_speed=150
        z.ai.max_flight_time=2.0
        z.ai.range=310
        z.ai.has_fuse=True
        z.ai.fuse_max_time=4
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='rpg43':
        z=WorldObject(world,['model24'],AIThrowable)
        z.name='rpg43'
        z.minimum_visible_scale=0.4
        z.is_grenade=True
        z.is_throwable=True
        z.ai.explode_on_contact=True
        z.ai.heat=True
        z.ai.heat_projectile_type='rpg43_HEAT'
        z.ai.unreliable_contact_fuse=True
        z.ai.max_speed=150
        z.ai.max_flight_time=2.0
        z.ai.range=310
        z.ai.has_fuse=False # no time fuse
        z.ai.fuse_max_time=4
        z.ai.use_antitank=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='molotov_cocktail':
        z=WorldObject(world,['green_bottle'],AIThrowable)
        z.name='Molotov Cocktail'
        z.minimum_visible_scale=0.4
        z.is_grenade=True
        z.is_throwable=True
        z.ai.flammable=True
        z.ai.explode_on_contact=True
        z.ai.flame_amount=5
        z.ai.max_speed=150
        z.ai.max_flight_time=2.0
        z.ai.range=310
        z.ai.has_fuse=True
        z.ai.fuse_max_time=4
        z.ai.use_antipersonnel=True
        z.ai.use_antitank=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='rg_42_grenade':
        z=WorldObject(world,['rg_42_grenade'],AIThrowable)
        z.name='RG-42 Grenade'
        z.minimum_visible_scale=0.4
        z.is_grenade=True
        z.is_throwable=True
        z.ai.explosive=True
        z.ai.shrapnel_count=15
        z.ai.explosion_radius=20
        z.ai.max_speed=150
        z.ai.max_flight_time=2.0
        z.ai.range=310
        z.ai.has_fuse=True
        z.ai.fuse_max_time=3
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='mp40':
        z=WorldObject(world,['mp40'],AIGun)
        z.name='mp40'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=3
        z.ai.magazine=spawn_object(world,world_coords,'mp40_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=7
        z.ai.range=1209
        z.ai.type='submachine gun'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='mp40_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='mp40_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mp40']
        z.ai.compatible_projectiles=['9mm_124','9mm_115','9mm_ME']
        z.ai.capacity=32
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='ppsh41':
        z=WorldObject(world,['ppsh41'],AIGun)
        z.name='ppsh41'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=3
        z.ai.magazine=spawn_object(world,world_coords,'ppsh41_drum_magazine',False)
        z.ai.rate_of_fire=0.048
        z.ai.reload_speed=7
        z.ai.range=1209
        z.ai.type='submachine gun'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='ppsh41_drum_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='ppsh41_drum_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['ppsh41']
        z.ai.compatible_projectiles=['7.62x25']
        z.ai.capacity=71
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)
    
    elif object_type=='ppsh41_box_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='ppsh41_drum_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['ppsh41']
        z.ai.compatible_projectiles=['7.62x25']
        z.ai.capacity=35
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='ppsh43':
        z=WorldObject(world,['ppsh43'],AIGun)
        z.name='ppsh43'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=3
        z.ai.magazine=spawn_object(world,world_coords,'ppsh43_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=7
        z.ai.range=1209
        z.ai.type='submachine gun'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='ppsh43_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='ppsh43_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['ppsh43']
        z.ai.compatible_projectiles=['7.62x25']
        z.ai.capacity=35
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='stg44':
        z=WorldObject(world,['stg44'],AIGun)
        z.name='stg44'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'stg44_magazine',False)
        z.ai.rate_of_fire=0.1
        z.ai.reload_speed=7
        z.ai.range=1813
        z.ai.type='assault rifle'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))
    
    elif object_type=='stg44_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='stg44_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['stg44']
        z.ai.compatible_projectiles=['7.92x33_SME']
        z.ai.capacity=30
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='dp28':
        z=WorldObject(world,['dp28'],AIGun)
        z.name='dp28'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=2
        z.ai.magazine=spawn_object(world,world_coords,'dp28_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=30
        z.ai.range=2418
        z.ai.type='machine gun'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='dp28_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='dp28_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['dp28']
        z.ai.compatible_projectiles=['7.62x54_L','7.62x54_D']
        z.ai.capacity=47
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='dtm':
        # ref : https://www.youtube.com/watch?v=goLAR1KdqRw
        # basically a dp28 adapted for tank use
        z=WorldObject(world,['dp28'],AIGun)
        z.name='DTM Machine Gun'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=2
        z.ai.magazine=spawn_object(world,world_coords,'dtm_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=30
        z.ai.range=2418
        z.ai.type='machine gun'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='dtm_magazine':
        # ref : https://www.youtube.com/watch?v=goLAR1KdqRw
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='DTM Pan Magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['dtm']
        z.ai.compatible_projectiles=['7.62x54_L','7.62x54_D']
        z.ai.capacity=60
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='ppk':
        z=WorldObject(world,['ppk'],AIGun)
        z.name='ppk'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=5
        z.ai.magazine=spawn_object(world,world_coords,'ppk_magazine',False)
        z.ai.rate_of_fire=0.7
        z.ai.reload_speed=5
        z.ai.range=604
        z.ai.type='pistol'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='ppk_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='ppk_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['ppk']
        z.ai.compatible_projectiles=['7.65_Browning']
        z.ai.capacity=8
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='walther_p38':
        z=WorldObject(world,['walther_p38'],AIGun)
        z.name='Walther P38'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=4
        z.ai.magazine=spawn_object(world,world_coords,'p38_magazine',False)
        z.ai.rate_of_fire=0.7
        z.ai.reload_speed=5
        z.ai.range=604
        z.ai.type='pistol'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='p38_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='p38_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['walther_p38']
        z.ai.compatible_projectiles=['9mm_124','9mm_115','9mm_ME']
        z.ai.capacity=8
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='luger_p08':
        z=WorldObject(world,['walther_p38'],AIGun)
        z.name='Luger P08'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=4
        z.ai.magazine=spawn_object(world,world_coords,'luger_p08_magazine',False)
        z.ai.rate_of_fire=0.7
        z.ai.reload_speed=5
        z.ai.range=604
        z.ai.type='pistol'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='luger_p08_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='Luger P08 Magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['luger_p08']
        z.ai.compatible_projectiles=['9mm_124','9mm_115','9mm_ME']
        z.ai.capacity=8
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='c96':
        z=WorldObject(world,['c96'],AIGun)
        z.name='C96 Mauser Pistol'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=3
        z.ai.magazine=spawn_object(world,world_coords,'c96_magazine',False)
        z.ai.rate_of_fire=0.7
        z.ai.reload_speed=8
        z.ai.range=700
        z.ai.type='pistol'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='c96_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='c96_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['c96']
        z.ai.compatible_projectiles=['7.63_Mauser']
        z.ai.capacity=10
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='c96_red_9':
        z=WorldObject(world,['c96'],AIGun)
        z.name='C96 Red 9 Mauser Pistol'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=3
        z.ai.magazine=spawn_object(world,world_coords,'c96_red_9_magazine',False)
        z.ai.rate_of_fire=0.7
        z.ai.reload_speed=8
        z.ai.range=700
        z.ai.type='pistol'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='c96_red_9_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='c96_red_9_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['c96_red_9']
        z.ai.compatible_projectiles=['9mm_124','9mm_115','9mm_ME']
        z.ai.capacity=10
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='tt33':
        z=WorldObject(world,['tt33'],AIGun)
        z.name='tt33'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=4
        z.ai.magazine=spawn_object(world,world_coords,'tt33_magazine',False)
        z.ai.rate_of_fire=0.9
        z.ai.reload_speed=5
        z.ai.range=604
        z.ai.type='pistol'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='tt33_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='tt33_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['tt33']
        z.ai.compatible_projectiles=['7.62x25']
        z.ai.capacity=8
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='1911':
        z=WorldObject(world,['1911'],AIGun)
        z.name='1911'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=4
        z.ai.magazine=spawn_object(world,world_coords,'1911_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=5
        z.ai.range=604
        z.ai.type='pistol'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))
    
    elif object_type=='1911_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='1911_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['1911']
        z.ai.compatible_projectiles=['45_ACP']
        z.ai.capacity=7
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)


    elif object_type=='mg34':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='mg34'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'mg34_drum_magazine',False)
        z.ai.rate_of_fire=0.05
        z.ai.reload_speed=15
        z.ai.range=2418
        z.ai.type='machine gun'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='mg42':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='mg42'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'mg34_drum_magazine',False)
        z.ai.rate_of_fire=0.04
        z.ai.reload_speed=15
        z.ai.range=2418
        z.ai.type='machine gun'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='mg34_drum_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='mg34_drum_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mg34','mg42']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=50
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z,'7.92x57_SME')

    elif object_type=='mg34_belt':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='mg34_belt'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mg34','mg42']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=250
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z,'7.92x57_SME')

    elif object_type=='37mm_m1939_k61':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='37mm_m1939_k61'
        z.no_update=True
        z.is_gun=True
        z.ai.mechanical_accuracy=2
        z.ai.magazine=spawn_object(world,world_coords,'37mm_m1939_k61_magazine',False)
        z.ai.rate_of_fire=0.9
        z.ai.reload_speed=15
        z.ai.range=4000
        z.ai.type='automatic cannon'
        z.ai.use_antipersonnel=True
        z.ai.use_antitank=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='37mm_m1939_k61_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='37mm_m1939_k61_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['37mm_m1939_k61']
        z.ai.compatible_projectiles=['37x252_Frag','37x252_AP-T']
        z.ai.capacity=5
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)
    
    elif object_type=='7.5cm_pak39_L48':
        # https://en.wikipedia.org/wiki/7.5_cm_Pak_39
        z=WorldObject(world,['mg34'],AIGun)
        z.name='7.5 cm Pak 39 L48 Cannon'
        z.no_update=True
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'7.5cm_pak39_L48_magazine',False)
        z.ai.rate_of_fire=1
        z.ai.reload_speed=20
        z.ai.range=4000
        z.ai.type='cannon'
        z.ai.use_antitank=True
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='7.5cm_pak39_L48_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='7.5 cm Pak 39 L48 Cannon Magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['7.5cm_pak39_L48']
        z.ai.compatible_projectiles=['PzGr39_75_L48','Sprgr_34_75_L48']
        z.ai.capacity=1
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    # https://en.wikipedia.org/wiki/76_mm_tank_gun_M1940_F-34
    elif object_type=='76mm_m1940_f34':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='76mm_m1940_f34'
        z.no_update=True
        z.is_gun=True
        z.ai.mechanical_accuracy=2
        z.ai.magazine=spawn_object(world,world_coords,'76mm_m1940_f34_magazine',False)
        z.ai.rate_of_fire=1
        z.ai.reload_speed=30
        z.ai.range=4000
        z.ai.type='cannon'
        z.ai.use_antitank=True
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))
    
    elif object_type=='76mm_m1940_f34_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='76mm_m1940_f34_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['76mm_m1940_f34']
        z.ai.compatible_projectiles=['76x385_AP','OF-350M']
        z.ai.capacity=1
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='85mm_zis_s_53':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='85mm ZIS-S-53'
        z.no_update=True
        z.is_gun=True
        z.ai.mechanical_accuracy=2
        z.ai.magazine=spawn_object(world,world_coords,'85mm_zis_s_53_magazine',False)
        z.ai.rate_of_fire=1
        z.ai.reload_speed=26
        z.ai.range=4000
        z.ai.type='cannon'
        z.ai.use_antitank=True
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='85mm_zis_s_53_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='85mm_zis_s_53_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['85mm_zis_s_53','85mm_d_5s']
        z.ai.compatible_projectiles=['BR-365k','O365k']
        z.ai.capacity=1
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    # for the su-85. same ammo as the t34-85 gun, same pen
    elif object_type=='85mm_d_5s':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='85mm D-5S'
        z.no_update=True
        z.is_gun=True
        z.ai.mechanical_accuracy=2
        z.ai.magazine=spawn_object(world,world_coords,'85mm_zis_s_53_magazine',False)
        z.ai.rate_of_fire=1
        z.ai.reload_speed=20
        z.ai.range=4000
        z.ai.type='cannon'
        z.ai.use_antitank=True
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='100mm_d_10':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='100mm D 10'
        z.no_update=True
        z.is_gun=True
        z.ai.mechanical_accuracy=2
        z.ai.magazine=spawn_object(world,world_coords,'100mm_d_10_magazine',False)
        z.ai.rate_of_fire=1
        z.ai.reload_speed=26
        z.ai.range=4000
        z.ai.type='cannon'
        z.ai.use_antitank=True
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='100mm_d_10_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='100mm_d_10_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['100mm_d_10']
        z.ai.compatible_projectiles=['BR-412','OF-412']
        z.ai.capacity=1
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='mg15':
        z=WorldObject(world,['mg15'],AIGun)
        z.name='mg15'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=2
        z.ai.magazine=spawn_object(world,world_coords,'mg15_drum_magazine',False)
        z.ai.rate_of_fire=0.06
        z.ai.reload_speed=16
        z.ai.range=2418
        z.ai.type='machine gun'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='mg15_drum_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='mg15_drum_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mg15']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=75
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='kar98k':
        z=WorldObject(world,['kar98k'],AIGun)
        z.name='kar98k'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'kar98k_magazine',False)
        z.ai.rate_of_fire=1.1
        z.ai.reload_speed=10
        z.ai.range=2418
        z.ai.type='rifle'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='kar98k_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='kar98k_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['kar98k']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=5
        z.ai.removable=False
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='g41w':
        z=WorldObject(world,['k43'],AIGun)
        z.name='g41w'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'g41w_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=7
        z.ai.range=2418
        z.ai.type='semi auto rifle'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='g41w_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='g41w_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['g41w']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=10
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='k43':
        z=WorldObject(world,['k43'],AIGun)
        z.name='k43'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'k43_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=7
        z.ai.range=2418
        z.ai.type='semi auto rifle'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='k43_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='k43_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['k43']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=10
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='fg42-type1':
        z=WorldObject(world,['fg42-type1'],AIGun)
        z.name='fg42-type1'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'fg42_type1_magazine',False)
        z.ai.rate_of_fire=0.06
        z.ai.reload_speed=7
        z.ai.range=2418
        z.ai.type='machine gun'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='fg42_type1_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='fg42_type1_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['fg42-type1']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=20
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='fg42-type2':
        z=WorldObject(world,['fg42-type2'],AIGun)
        z.name='fg42-type2'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'fg42_type2_magazine',False)
        z.ai.rate_of_fire=0.08
        z.ai.reload_speed=7
        z.ai.range=2418
        z.ai.type='machine gun'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='fg42_type2_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='fg42_type2_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['fg42-type2']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=20
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='mosin_nagant':
        z=WorldObject(world,['mosin_nagant'],AIGun)
        z.name='mosin_nagant'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'mosin_magazine',False)
        z.ai.rate_of_fire=1.1
        z.ai.reload_speed=11
        z.ai.range=2418
        z.ai.type='rifle'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='mosin_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='mosin_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mosin_nagant']
        z.ai.compatible_projectiles=['7.62x54_L','7.62x54_D']
        z.ai.capacity=5
        z.ai.removable=False
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='ptrs_41':
        z=WorldObject(world,['ptrs_41'],AIGun)
        z.name='PTRS 41 Anti-Tank Rifle'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=3
        z.ai.magazine=spawn_object(world,world_coords,'ptrs_41_magazine',False)
        z.ai.rate_of_fire=1.9
        z.ai.reload_speed=14
        z.ai.range=2418
        z.ai.type='rifle'
        #z.ai.use_antipersonnel=True
        z.ai.use_antitank=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='ptrs_41_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='ptrs_41_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['ptrs_41']
        z.ai.compatible_projectiles=['14.5x114_B32']
        z.ai.capacity=5
        z.ai.removable=False
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)
    
    elif object_type=='svt40':
        z=WorldObject(world,['svt40'],AIGun)
        z.name='svt40'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'svt40_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=7
        z.ai.range=2418
        z.ai.type='semi auto rifle'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='svt40_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='svt40_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['svt40','svt40-sniper']
        z.ai.compatible_projectiles=['7.62x54_L','7.62x54_D']
        z.ai.capacity=10
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='svt40-sniper':
        z=WorldObject(world,['svt40-sniper'],AIGun)
        z.name='svt40-sniper'
        z.no_update=True
        z.minimum_visible_scale=0.4
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'svt40_magazine',False)
        z.ai.mag_capacity=10
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=10
        z.ai.range=2500
        z.ai.type='semi auto rifle'
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='soviet_dodge_g505_wc':
        # note! at the moment this is meant to represent a 6x6 american truck
        # 
        # ref : https://truck-encyclopedia.com/ww2/us/Dodge-WC-3-4-tons-series.php
        # ref : https://truck-encyclopedia.com/ww2/us/dodge-WC-62-63-6x6.php
        z=WorldObject(world,['dodge_g505_wc','dodge_g505_wc_destroyed'],AIVehicle)
        z.name='Dodge G505 WC Truck'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.is_transport=True

        driver=VehicleRole('driver',z)
        driver.is_driver=True
        z.ai.vehicle_crew.append(driver)

        for x in range(10):
            passenger=VehicleRole('passenger',z)
            passenger.is_passenger=True
            z.ai.vehicle_crew.append(passenger)

        z.ai.max_speed=651.2
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=2380
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"chrysler_flathead_straight_6_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        z.ai.min_wheels_per_side_front=1
        z.ai.min_wheels_per_side_rear=1
        z.ai.max_wheels=6
        z.ai.max_spare_wheels=0
        z.ai.front_left_wheels.append(spawn_object(world,world_coords,"g505_wheel",False))
        z.ai.front_right_wheels.append(spawn_object(world,world_coords,"g505_wheel",False))
        z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"g505_wheel",False))
        z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"g505_wheel",False))
        z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"g505_wheel",False))
        z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"g505_wheel",False))

    elif object_type=='g505_wheel':
        z=WorldObject(world,['volkswagen_wheel'],AIWheel)
        z.name='g505 Wheel'
        z.ai.compatible_vehicles=['soviet_dodge_g505_wc']

    elif object_type=='german_rso':
        # ref : https://en.wikipedia.org/wiki/Raupenschlepper_Ost
        # related ref : https://tanks-encyclopedia.com/ww2/nazi_germany/Raupenschlepper-Ost-Artillery-SPG.php
        z=WorldObject(world,['rso','rso_destroyed'],AIVehicle)
        z.name='Raupenschlepper Ost'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.is_transport=True

        driver=VehicleRole('driver',z)
        driver.is_driver=True
        z.ai.vehicle_crew.append(driver)

        for x in range(10):
            passenger=VehicleRole('passenger',z)
            passenger.is_passenger=True
            z.ai.vehicle_crew.append(passenger)

        z.ai.max_speed=224.96
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=2500
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'diesel')
        z.ai.engines.append(spawn_object(world,world_coords,"deutz_diesel_65hp_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        z.ai.min_wheels_per_side_front=1
        z.ai.min_wheels_per_side_rear=1
        z.ai.max_wheels=8
        z.ai.max_spare_wheels=0
        for b in range(2):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"rso_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"rso_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"rso_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"rso_wheel",False))

    elif object_type=='german_rso_pak':
        # ref : https://en.wikipedia.org/wiki/Raupenschlepper_Ost
        # ref : https://truck-encyclopedia.com/ww2/us/dodge-WC-62-63-6x6.php
        z=WorldObject(world,['rso_pak','rso_destroyed'],AIVehicle)
        z.name='Raupenschlepper Ost PAK'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.vehicle_armor['top']=[5,0,0]
        z.ai.vehicle_armor['bottom']=[5,0,0]
        z.ai.vehicle_armor['left']=[5,0,0]
        z.ai.vehicle_armor['right']=[5,0,0]
        z.ai.vehicle_armor['front']=[5.20,20,0]
        z.ai.vehicle_armor['rear']=[5,0,0]
        turret=spawn_object(world,world_coords,'251_pak40_turret',True)
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z
        turret.ai.position_offset=[11,0]
        turret.ai.rotation_range=[-360,360]

        role=VehicleRole('driver',z)
        role.is_driver=True
        role.seat_visible=True
        role.seat_offset=[-39,-13]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=turret
        role.seat_visible=True
        role.seat_offset=[-29,-3]
        z.ai.vehicle_crew.append(role)

        z.ai.max_speed=224.96
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=2500
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'diesel')
        z.ai.engines.append(spawn_object(world,world_coords,"deutz_diesel_65hp_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.ai.ammo_rack_capacity=24
        for b in range(20):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"75mm_pak40_magazine",False))
        for b in range(4):
            temp=spawn_object(world,world_coords,"75mm_pak40_magazine",False)
            load_magazine(world,temp,'Sprgr_34_75_L48')
            z.ai.ammo_rack.append(temp)
        z.rotation_angle=float(random.randint(0,359))
        z.ai.min_wheels_per_side_front=1
        z.ai.min_wheels_per_side_rear=1
        z.ai.max_wheels=8
        z.ai.max_spare_wheels=0
        for b in range(2):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"rso_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"rso_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"rso_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"rso_wheel",False))

    elif object_type=='rso_wheel':
        z=WorldObject(world,['volkswagen_wheel'],AIWheel)
        z.name='RSO Wheel'
        z.ai.compatible_vehicles=['german_rso_pak','german_rso']
        z.ai.armor=[5,0,0]

    # this is the base object for the sd.kfz.10 variants. It is not meant to be spawned by itself
    elif object_type=='german_sd_kfz_10_base':
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['sd_kfz_10_chassis'],AIVehicle)
        z.name='Sd.Kfz.10'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.is_transport=True

        # driver and assistant driver positions are the same for all variants
        role=VehicleRole('driver',z)
        role.is_driver=True
        role.seat_visible=True
        role.seat_offset=[-18,-13]
        z.ai.vehicle_crew.append(role)
        role=VehicleRole('passenger',z)
        role.is_passenger=True
        role.seat_visible=True
        role.seat_offset=[-18,12]
        z.ai.vehicle_crew.append(role)

        z.ai.vehicle_armor['top']=[1,0,0]
        z.ai.vehicle_armor['bottom']=[1,0,0]
        z.ai.vehicle_armor['left']=[1,0,0]
        z.ai.vehicle_armor['right']=[1,0,0]
        z.ai.vehicle_armor['front']=[1,0,0]
        z.ai.vehicle_armor['rear']=[1,0,0]
        z.ai.passenger_compartment_armor['top']=[0,0,0]
        z.ai.passenger_compartment_armor['bottom']=[0,0,0]
        z.ai.passenger_compartment_armor['left']=[0,0,0]
        z.ai.passenger_compartment_armor['right']=[0,0,0]
        z.ai.passenger_compartment_armor['front']=[0.0,0,0]
        z.ai.passenger_compartment_armor['rear']=[0,0,0]
        z.ai.max_speed=385.9
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=7800
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"maybach_hl42_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        if random.randint(0,1)==1:
            z.add_inventory(spawn_object(world,world_coords,"panzerfaust_60",False))
        z.ai.min_wheels_per_side_front=1
        z.ai.min_wheels_per_side_rear=5
        z.ai.max_wheels=18
        z.ai.max_spare_wheels=0
        z.ai.front_left_wheels.append(spawn_object(world,world_coords,"251_wheel",False))
        z.ai.front_right_wheels.append(spawn_object(world,world_coords,"251_wheel",False))
        for b in range(8):
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"251_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"251_wheel",False))

    # this is the default transport model
    elif object_type=='german_sd_kfz_10':
        z=spawn_object(world,world_coords,'german_sd_kfz_10_base',False)
        z.name='Sd.Kfz.10'

        passenger_positions=[ [15.0, -13.0],[15.0, 0.0],[15.0, 12.0],[43.0, -13.0],[42.0, 0.0],[42.0, 14.0]]
        for x in range(6):
            role=VehicleRole('passenger',z)
            role.is_passenger=True
            role.seat_visible=True
            role.seat_offset=passenger_positions.pop()
            z.ai.vehicle_crew.append(role)

    # this is the default transport model with camo
    elif object_type=='german_sd_kfz_10_camo':
        z=spawn_object(world,world_coords,'german_sd_kfz_10_base',False)
        z.name='Sd.Kfz.10'
        z.image_list=["sd_kfz_10_chassis_camo"]


    # this is the base object for the sd.kfz.234 variants. It is not meant to be spawned by itself
    elif object_type=='german_sd_kfz_234_base':
        # ref : https://en.wikipedia.org/wiki/Sd.Kfz._234
        # ref : https://tank-afv.com/ww2/germany/Sd-Kfz-234.php
        z=WorldObject(world,['sd_kfz_234_chassis_green_camo'],AIVehicle)
        z.name='Sd.Kfz.234'
        z.is_vehicle=True
        z.is_towable=True

        z.ai.vehicle_armor['top']=[5,0,0]
        z.ai.vehicle_armor['bottom']=[5,0,0]
        z.ai.vehicle_armor['left']=[8,19,0]
        z.ai.vehicle_armor['right']=[8,19,0]
        z.ai.vehicle_armor['front']=[30,55,0]
        z.ai.vehicle_armor['rear']=[10,46,0]
        z.ai.passenger_compartment_armor['top']=[5,0,0]
        z.ai.passenger_compartment_armor['bottom']=[5,0,0]
        z.ai.passenger_compartment_armor['left']=[8,35,0]
        z.ai.passenger_compartment_armor['right']=[8,35,0]
        z.ai.passenger_compartment_armor['front']=[30,40,0]
        z.ai.passenger_compartment_armor['rear']=[10,38,0]
        z.ai.max_speed=385.9
        z.ai.max_offroad_speed=177.6
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=7800
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"maybach_hl42_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        z.ai.radio=spawn_object(world,world_coords,'radio_feldfu_b',False)
        if random.randint(0,1)==1:
            z.add_inventory(spawn_object(world,world_coords,"panzerfaust_100",False))
        z.ai.min_wheels_per_side_front=1
        z.ai.min_wheels_per_side_rear=1
        z.ai.max_wheels=8
        z.ai.max_spare_wheels=0
        for b in range(2):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"251_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"251_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"251_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"251_wheel",False))

    elif object_type=='german_sd_kfz_234/1':
        # ref : https://wiki.warthunder.com/unit/germ_sdkfz_251_9
        # https://en.wikipedia.org/wiki/Sd.Kfz._251
        z=spawn_object(world,world_coords,'german_sd_kfz_234_base',False)
        z.name='Sd.Kfz.234/1'
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.requires_afv_training=True
        z.ai.is_transport=False
        turret=spawn_object(world,world_coords,'234_1_turret',True)
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z

        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=turret

        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        z.ai.vehicle_crew.append(role)
        # mg ammo
        for b in range(10):
            z.add_inventory(spawn_object(world,world_coords,"mg34_belt",False))
        # armor piercing belt
        if random.randint(0,1)==1:
            belt=spawn_object(world,world_coords,"mg34_belt",False)
            load_magazine(world,belt,'7.92x57_SMK')
            z.add_inventory(belt)

        z.ai.ammo_rack_capacity=25
        # AP
        for b in range(15):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"2cm_kwk38_l55_magazine",False))
        # HE
        for b in range(10):
            temp=spawn_object(world,world_coords,"2cm_kwk38_l55_magazine",False)
            load_magazine(world,temp,'20x138_HE')
            z.ai.ammo_rack.append(temp)

    elif object_type=='234_1_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['sd_kfz_234_1_turret'],AITurret)
        z.name='Sd.Kfz.234/1 Turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=1
        z.ai.turret_armor['top']=[1,0,0]
        z.ai.turret_armor['bottom']=[13,0,0]
        z.ai.turret_armor['left']=[8,33,0]
        z.ai.turret_armor['right']=[8,33,0]
        z.ai.turret_armor['front']=[30,33,0]
        z.ai.turret_armor['rear']=[8,33,0]
        z.ai.position_offset=[-16,0]
        z.ai.rotation_range=[-360,360]
        z.ai.primary_weapon=spawn_object(world,world_coords,'2cm_kwk38_l55',False)
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-70,0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon_reload_speed=10
        z.ai.primary_turret=True
        z.ai.coaxial_weapon_reload_speed=10
        z.ai.coaxial_weapon=spawn_object(world,world_coords,'mg34',False)
        z.ai.coaxial_weapon.ai.equipper=z
        z.ai.coaxial_weapon.ai.spawn_case=False
        z.no_save=True

    elif object_type=='2cm_kwk38_l55':
        # ref : https://en.wikipedia.org/wiki/2_cm_KwK_30
        z=WorldObject(world,['mg34'],AIGun)
        z.no_update=True
        z.name='2cm KWK 38 L55'
        z.is_gun=True
        z.ai.mechanical_accuracy=10
        z.ai.magazine=spawn_object(world,world_coords,'2cm_kwk38_l55_magazine',False)
        z.ai.rate_of_fire=0.13
        z.ai.range=4000
        z.ai.type='cannon'
        z.ai.use_antitank=True
        z.ai.use_antipersonnel=True
        z.rotation_angle=0

    elif object_type=='2cm_kwk38_l55_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='2cm KWK 38 L55 magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['2cm_kwk38_l55']
        z.ai.compatible_projectiles=['20x138_API-T','20x138_HE']
        z.ai.capacity=10
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    # this is the base object for the sd.kfz.251 variants. It is not meant to be spawned by itself
    elif object_type=='german_sd_kfz_251_base':
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['sd_kfz_251','sd_kfz_251_destroyed'],AIVehicle)
        z.name='Sd.Kfz.251'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.is_transport=True

        z.ai.vehicle_armor['top']=[8,8,0]
        z.ai.vehicle_armor['bottom']=[8,0,0]
        z.ai.vehicle_armor['left']=[8,19,0]
        z.ai.vehicle_armor['right']=[8,19,0]
        z.ai.vehicle_armor['front']=[14.5,20,0]
        z.ai.vehicle_armor['rear']=[8,31,0]
        z.ai.passenger_compartment_armor['top']=[0,0,0]
        z.ai.passenger_compartment_armor['bottom']=[8,0,0]
        z.ai.passenger_compartment_armor['left']=[8,35,0]
        z.ai.passenger_compartment_armor['right']=[8,35,0]
        z.ai.passenger_compartment_armor['front']=[14.5,30,0]
        z.ai.passenger_compartment_armor['rear']=[8,31,0]
        z.ai.max_speed=385.9
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=7800
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"maybach_hl42_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        z.ai.radio=spawn_object(world,world_coords,'radio_feldfu_b',False)
        if random.randint(0,1)==1:
            z.add_inventory(spawn_object(world,world_coords,"panzerfaust_100",False))
        z.ai.min_wheels_per_side_front=1
        z.ai.min_wheels_per_side_rear=5
        z.ai.max_wheels=18
        z.ai.max_spare_wheels=0
        z.ai.front_left_wheels.append(spawn_object(world,world_coords,"251_wheel",False))
        z.ai.front_right_wheels.append(spawn_object(world,world_coords,"251_wheel",False))
        for b in range(8):
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"251_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"251_wheel",False))

    elif object_type=='german_sd_kfz_251/1':
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=spawn_object(world,world_coords,'german_sd_kfz_251_base',False)
        z.name='Sd.Kfz.251/1'
        turret=spawn_object(world,world_coords,'sd_kfz_251_mg34_turret',True)
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z
        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)
        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=turret
        role.seat_visible=True
        role.seat_offset=[-3,0]
        z.ai.vehicle_crew.append(role)
        passenger_positions=[[4,10],[12,10],[21,10],[35,10],[51,10],[4,-10],[12,-10],[21,-10],[35,-10],[51,-10]]
        passenger_rotation=[90,90,90,90,90,270,270,270,270,270]
        for x in range(10):
            role=VehicleRole('passenger',z)
            role.is_passenger=True
            role.seat_visible=True
            role.seat_rotation=passenger_rotation.pop()
            role.seat_offset=passenger_positions.pop()
            z.ai.vehicle_crew.append(role)
        for b in range(11):
            z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        
        # armor piercing belt
        if random.randint(0,1)==1:
            belt=spawn_object(world,world_coords,"mg34_belt",False)
            load_magazine(world,belt,'7.92x57_SMK')
            z.add_inventory(belt)

    elif object_type=='sd_kfz_251_mg34_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['sd_kfz_251_mg34_turret','sd_kfz_251_mg34_turret'],AITurret)
        z.name='Sd.Kfz.251 MG34 Turret'
        z.is_turret=True
        z.ai.small=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=10
        z.ai.turret_armor['top']=[0,0,0]
        z.ai.turret_armor['bottom']=[13,0,0]
        z.ai.turret_armor['left']=[6,22,0]
        z.ai.turret_armor['right']=[6,22,0]
        z.ai.turret_armor['front']=[6,36,0]
        z.ai.turret_armor['rear']=[0,0,0]
        z.ai.position_offset=[-10,0]
        z.ai.rotation_range=[-20,20]
        z.ai.primary_weapon=spawn_object(world,world_coords,'mg34',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon_reload_speed=10
        z.ai.primary_turret=True
        z.no_save=True

    elif object_type=='german_sd_kfz_251/2':
        # the mortar carrier variant
        # https://en.wikipedia.org/wiki/Sd.Kfz._251
        z=spawn_object(world,world_coords,'german_sd_kfz_251_base',False)
        z.name='Sd.Kfz.251/2'
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.requires_afv_training=True
        z.ai.is_transport=False
        turret=spawn_object(world,world_coords,'251_2_turret',True)
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z

        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        # note special indirect fire gunner role
        role=VehicleRole('gunner',z)
        role.is_indirect_fire_gunner=True
        role.turret=turret
        role.seat_visible=True
        role.seat_offset=[17,0]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        role.seat_visible=True
        role.seat_rotation=90
        role.seat_offset=[24,10]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        role.seat_visible=True
        role.seat_rotation=90
        role.seat_offset=[12,10]
        z.ai.vehicle_crew.append(role)

        z.ai.ammo_rack_capacity=66
        # HE
        for b in range(66):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"8cmGrW34",False))


    elif object_type=='251_2_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['251_2_turret'],AITurret)
        z.name='Sd.Kfz.251/2 Turret'
        z.is_turret=True
        # center should mean it is never hit by a projectile.
        # this is what we want because this turret is completely internal
        z.ai.vehicle_mount_side='center'
        z.ai.turret_accuracy=1
        z.ai.turret_armor['top']=[0,0,0]
        z.ai.turret_armor['bottom']=[0,0,0]
        z.ai.turret_armor['left']=[0,0,0]
        z.ai.turret_armor['right']=[0,0,0]
        z.ai.turret_armor['front']=[0,0,0]
        z.ai.turret_armor['rear']=[0,0,0]
        z.ai.position_offset=[-31,0]
        z.ai.rotation_range=[-30,30]
        z.ai.primary_weapon=spawn_object(world,world_coords,'8cmGrW34',False)
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-0,0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon_reload_speed=3
        z.ai.primary_turret=True
        z.no_save=True

    elif object_type=='8cmGrW34':
        # ref : https://en.wikipedia.org/wiki/8_cm_Granatwerfer_34
        z=WorldObject(world,['mg34'],AIGun)
        z.name='8cm Granatwerfer 34'
        z.no_update=True
        z.is_gun=True
        z.ai.mechanical_accuracy=10
        z.ai.magazine=spawn_object(world,world_coords,'GrW34_magazine',False)
        z.ai.rate_of_fire=1
        z.ai.range=4000
        z.ai.type='cannon'
        z.ai.use_antitank=False
        z.ai.use_antipersonnel=True
        z.ai.direct_fire=False
        z.ai.indirect_fire=True
        z.ai.indirect_fire_mode=True
        z.rotation_angle=0

    elif object_type=='GrW34_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='GrW34_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['8cmGrW34']
        z.ai.compatible_projectiles=['Wurfgranate_34']
        z.ai.capacity=1
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)
        
    elif object_type=='251_wheel':
        z=WorldObject(world,['volkswagen_wheel'],AIWheel)
        z.name='251 Wheel'
        z.ai.compatible_vehicles=['german_sd_kfz_251/22','german_sd_kfz_251']
        z.ai.armor=[5,0,0]

    elif object_type=='german_sd_kfz_251/9':
        # ref : https://wiki.warthunder.com/unit/germ_sdkfz_251_9
        # https://en.wikipedia.org/wiki/Sd.Kfz._251
        z=spawn_object(world,world_coords,'german_sd_kfz_251_base',False)
        z.name='Sd.Kfz.251/9 Stummel'
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.requires_afv_training=True
        z.ai.is_transport=False
        turret=spawn_object(world,world_coords,'251_9_turret',True)
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z

        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=turret
        role.seat_visible=True
        role.seat_offset=[17,0]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        role.seat_visible=True
        role.seat_rotation=90
        role.seat_offset=[24,10]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        role.seat_visible=True
        role.seat_rotation=90
        role.seat_offset=[12,10]
        z.ai.vehicle_crew.append(role)

        z.ai.ammo_rack_capacity=52
        # HE
        for b in range(40):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"75mm_kwk37_l24_magazine",False))
        # HEAT
        for b in range(12):
            temp=spawn_object(world,world_coords,"75mm_kwk37_l24_magazine",False)
            load_magazine(world,temp,'HL_Gr_38A_L24')
            z.ai.ammo_rack.append(temp)

    elif object_type=='251_9_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['251_9_turret','251_9_turret'],AITurret)
        z.name='Sd.Kfz.251/9 Turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=1
        z.ai.turret_armor['top']=[0,0,0]
        z.ai.turret_armor['bottom']=[13,0,0]
        z.ai.turret_armor['left']=[6,22,0]
        z.ai.turret_armor['right']=[6,22,0]
        z.ai.turret_armor['front']=[6,36,0]
        z.ai.turret_armor['rear']=[0,0,0]
        z.ai.position_offset=[-10,0]
        z.ai.rotation_range=[-12,12]
        z.ai.primary_weapon=spawn_object(world,world_coords,'75mm_kwk37_l24',False)
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-70,0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon_reload_speed=15
        z.ai.primary_turret=True
        z.no_save=True

    elif object_type=='75mm_kwk37_l24':
        # ref : https://en.wikipedia.org/wiki/7.5_cm_KwK_37
        z=WorldObject(world,['mg34'],AIGun)
        z.name='75mm KWK 37 L24'
        z.no_update=True
        z.is_gun=True
        z.ai.mechanical_accuracy=10
        z.ai.magazine=spawn_object(world,world_coords,'75mm_kwk37_l24_magazine',False)
        z.ai.rate_of_fire=1
        z.ai.range=4000
        z.ai.type='cannon'
        z.ai.use_antitank=True
        z.ai.use_antipersonnel=True
        z.rotation_angle=0

    elif object_type=='75mm_kwk37_l24_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='75mm_kwk40_l48_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['75mm_kwk37_l24']
        z.ai.compatible_projectiles=['Sprgr_34_75_L24','HL_Gr_38A_L24']
        z.ai.capacity=1
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='german_sd_kfz_251/9_late':
        # ref : https://wiki.warthunder.com/unit/germ_sdkfz_251_9
        # https://en.wikipedia.org/wiki/Sd.Kfz._251
        z=spawn_object(world,world_coords,'german_sd_kfz_251_base',False)
        z.name='Sd.Kfz.251/9 (late) Stummel'
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.requires_afv_training=True
        z.ai.is_transport=False
        turret=spawn_object(world,world_coords,'251_9_late_turret',True)
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z

        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=turret
        role.seat_visible=True
        role.seat_offset=[17,0]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        role.seat_visible=True
        role.seat_rotation=90
        role.seat_offset=[24,10]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        role.seat_visible=True
        role.seat_rotation=90
        role.seat_offset=[12,10]
        z.ai.vehicle_crew.append(role)
        for b in range(10):
            z.add_inventory(spawn_object(world,world_coords,"mg34_belt",False))
        # armor piercing belt
        if random.randint(0,1)==1:
            belt=spawn_object(world,world_coords,"mg34_belt",False)
            load_magazine(world,belt,'7.92x57_SMK')
            z.add_inventory(belt)

        z.ai.ammo_rack_capacity=52
        # HE
        for b in range(40):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"75mm_kwk37_l24_magazine",False))
        # HEAT
        for b in range(12):
            temp=spawn_object(world,world_coords,"75mm_kwk37_l24_magazine",False)
            load_magazine(world,temp,'HL_Gr_38A_L24')
            z.ai.ammo_rack.append(temp)

    elif object_type=='251_9_late_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['251_9_late_turret','251_9_late_turret'],AITurret)
        z.name='Sd.Kfz.251/9 Turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=1
        z.ai.turret_armor['top']=[0,0,0]
        z.ai.turret_armor['bottom']=[13,0,0]
        z.ai.turret_armor['left']=[6,22,0]
        z.ai.turret_armor['right']=[6,22,0]
        z.ai.turret_armor['front']=[6,36,0]
        z.ai.turret_armor['rear']=[0,0,0]
        z.ai.position_offset=[-10,0]
        z.ai.rotation_range=[-12,12]
        z.ai.primary_weapon=spawn_object(world,world_coords,'75mm_kwk37_l24',False)
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-70,0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon_reload_speed=15
        z.ai.coaxial_weapon_reload_speed=10
        z.ai.coaxial_weapon=spawn_object(world,world_coords,'mg42',False)
        z.ai.coaxial_weapon.ai.equipper=z
        z.ai.coaxial_weapon.ai.spawn_case=False
        z.ai.primary_turret=True
        z.no_save=True
        
    elif object_type=='german_sd_kfz_251/22':
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=spawn_object(world,world_coords,'german_sd_kfz_251_base',False)
        z.name='Sd.Kfz.251/22'
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.requires_afv_training=True
        z.ai.is_transport=False
        turret=spawn_object(world,world_coords,'251_pak40_turret',True)
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z

        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=turret
        role.seat_visible=True
        role.seat_offset=[0,0]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        role.seat_visible=True
        role.seat_rotation=90
        role.seat_offset=[4,10]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        role.seat_visible=True
        role.seat_rotation=90
        role.seat_offset=[12,10]
        z.ai.vehicle_crew.append(role)

        z.ai.ammo_rack_capacity=24
        for b in range(20):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"75mm_pak40_magazine",False))
        for b in range(4):
            temp=spawn_object(world,world_coords,"75mm_pak40_magazine",False)
            load_magazine(world,temp,'Sprgr_34_75_L48')
            z.ai.ammo_rack.append(temp)

    elif object_type=='251_pak40_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['pak40_vehicle_turret','pak40_vehicle_turret'],AITurret)
        z.name='PAK 40 turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=1
        z.ai.turret_armor['top']=[0,0,0]
        z.ai.turret_armor['bottom']=[13,0,0]
        z.ai.turret_armor['left']=[6,22,0]
        z.ai.turret_armor['right']=[6,22,0]
        z.ai.turret_armor['front']=[6,36,0]
        z.ai.turret_armor['rear']=[0,0,0]
        z.ai.position_offset=[0,0]
        z.ai.rotation_range=[-30,30]
        z.ai.primary_weapon=spawn_object(world,world_coords,'75mm_pak40',False)
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-70,0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon_reload_speed=20
        z.ai.primary_turret=True
        z.no_save=True

    elif object_type=='german_sd_kfz_251/23':
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=spawn_object(world,world_coords,'german_sd_kfz_251_base',False)
        z.name='Sd.Kfz.251/23'
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.requires_afv_training=True
        z.ai.is_transport=False
        turret=spawn_object(world,world_coords,'234_1_turret',True)
        # reset position offset to match this vehicle
        turret.ai.position_offset=[12,0]
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z

        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=turret
        role.seat_visible=False
        role.seat_offset=[0,0]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        role.seat_visible=False
        role.seat_rotation=90
        role.seat_offset=[4,10]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        role.seat_visible=False
        role.seat_rotation=90
        role.seat_offset=[12,10]
        z.ai.vehicle_crew.append(role)

         # mg ammo
        for b in range(10):
            z.add_inventory(spawn_object(world,world_coords,"mg34_belt",False))

        # armor piercing belt
        if random.randint(0,1)==1:
            belt=spawn_object(world,world_coords,"mg34_belt",False)
            load_magazine(world,belt,'7.92x57_SMK')
            z.add_inventory(belt)

        z.ai.ammo_rack_capacity=30
        # AP
        for b in range(15):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"2cm_kwk38_l55_magazine",False))
        # HE
        for b in range(15):
            temp=spawn_object(world,world_coords,"2cm_kwk38_l55_magazine",False)
            load_magazine(world,temp,'20x138_HE')
            z.ai.ammo_rack.append(temp)

    elif object_type=='german_panzer_iv_ausf_g':
        # ref : https://wiki.warthunder.com/unit/germ_pzkpfw_IV_ausf_G
        z=WorldObject(world,['panzer_iv_g_chassis','panzer_iv_g_chassis_destroyed'],AIVehicle)
        z.name='Panzer IV Ausf. G'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.requires_afv_training=True
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.vehicle_armor['top']=[16,0,0]
        z.ai.vehicle_armor['bottom']=[8,0,0]
        z.ai.vehicle_armor['left']=[30,0,0]
        z.ai.vehicle_armor['right']=[30,0,0]
        z.ai.vehicle_armor['front']=[80,64,0]
        z.ai.vehicle_armor['rear']=[30,15,0]
        z.ai.passenger_compartment_armor['top']=[16,0,0]
        z.ai.passenger_compartment_armor['bottom']=[8,0,0]
        z.ai.passenger_compartment_armor['left']=[30,0,0]
        z.ai.passenger_compartment_armor['right']=[30,0,0]
        z.ai.passenger_compartment_armor['front']=[80,11,0]
        z.ai.passenger_compartment_armor['rear']=[30,15,0]
        main_turret=spawn_object(world,world_coords,'panzer_iv_g_turret',True)
        z.ai.turrets.append(main_turret)
        main_turret.ai.vehicle=z
        mg_turret=spawn_object(world,world_coords,'panzer_iv_hull_mg',True)
        z.ai.turrets.append(mg_turret)
        mg_turret.ai.vehicle=z
        z.ai.radio=spawn_object(world,world_coords,'radio_feldfu_b',False)

        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=main_turret
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('radio_operator',z)
        role.is_gunner=True
        role.turret=mg_turret
        role.is_radio_operator=True
        role.radio=z.ai.radio
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        z.ai.vehicle_crew.append(role)

        z.ai.max_speed=367.04
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=26500
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'diesel')
        z.ai.engines.append(spawn_object(world,world_coords,"kharkiv_v2-34_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        for b in range(10):
            z.add_inventory(spawn_object(world,world_coords,"mg34_belt",False))
        z.ai.ammo_rack_capacity=87
        for b in range(60):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"75mm_kwk40_l43_magazine",False))
        for b in range(27):
            temp=spawn_object(world,world_coords,"75mm_kwk40_l43_magazine",False)
            load_magazine(world,temp,'Sprgr_34_75_L43')
            z.ai.ammo_rack.append(temp)
        z.ai.min_wheels_per_side_front=3
        z.ai.min_wheels_per_side_rear=3
        z.ai.max_wheels=16
        z.ai.max_spare_wheels=0
        for b in range(4):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
        
    elif object_type=='panzer_iv_hull_mg':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['panzer_iv_hull_mg','panzer_iv_hull_mg'],AITurret)
        z.name='Panzer IV Hull MG'
        z.is_turret=True
        z.ai.small=True
        z.ai.vehicle_mount_side='front'
        z.ai.turret_accuracy=10
        z.ai.turret_armor['top']=[16,0,0]
        z.ai.turret_armor['bottom']=[8,0,0]
        z.ai.turret_armor['left']=[30,23,0]
        z.ai.turret_armor['right']=[30,23,0]
        z.ai.turret_armor['front']=[50,11,0]
        z.ai.turret_armor['rear']=[30,15,0]
        z.ai.position_offset=[-50,19]
        z.ai.rotation_range=[-20,20]
        z.ai.primary_weapon=spawn_object(world,world_coords,'mg34',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_weapon_reload_speed=10
        z.no_save=True

    elif object_type=='panzer_iv_g_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['panzer_iv_g_turret','panzer_iv_g_turret'],AITurret)
        z.name='Panzer IV Ausf. G Turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=1
        z.ai.turret_armor['top']=[16,0,0]
        z.ai.turret_armor['bottom']=[8,0,0]
        z.ai.turret_armor['left']=[30,23,0]
        z.ai.turret_armor['right']=[30,23,0]
        z.ai.turret_armor['front']=[50,11,0]
        z.ai.turret_armor['rear']=[30,15,0]
        z.ai.position_offset=[-15,0]
        z.ai.rotation_range=[-360,360]
        z.ai.primary_weapon=spawn_object(world,world_coords,'75mm_kwk40_l43',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-93.0, 1.0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.coaxial_weapon=spawn_object(world,world_coords,'mg34',False)
        z.ai.coaxial_weapon.ai.equipper=z
        z.ai.coaxial_weapon.ai.spawn_case=False
        z.ai.primary_turret=True
        z.ai.primary_weapon_reload_speed=20
        z.ai.coaxial_weapon_reload_speed=10
        z.no_save=True

    elif object_type=='german_panzer_iv_ausf_h':
        # ref : https://wiki.warthunder.com/unit/germ_pzkpfw_IV_ausf_G
        z=WorldObject(world,['panzer_iv_h_chassis','panzer_iv_h_chassis_destroyed'],AIVehicle)
        z.name='Panzer IV Ausf. H'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.requires_afv_training=True
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.vehicle_armor['top']=[16,0,0]
        z.ai.vehicle_armor['bottom']=[8,0,0]
        z.ai.vehicle_armor['left']=[30,0,5]
        z.ai.vehicle_armor['right']=[30,0,5]
        z.ai.vehicle_armor['front']=[80,64,0]
        z.ai.vehicle_armor['rear']=[30,15,0]
        z.ai.passenger_compartment_armor['top']=[16,0,0]
        z.ai.passenger_compartment_armor['bottom']=[8,0,0]
        z.ai.passenger_compartment_armor['left']=[30,0,5]
        z.ai.passenger_compartment_armor['right']=[30,0,5]
        z.ai.passenger_compartment_armor['front']=[80,11,0]
        z.ai.passenger_compartment_armor['rear']=[30,15,0]
        main_turret=spawn_object(world,world_coords,'panzer_iv_h_turret',True)
        z.ai.turrets.append(main_turret)
        main_turret.ai.vehicle=z
        mg_turret=spawn_object(world,world_coords,'panzer_iv_hull_mg',True)
        z.ai.turrets.append(mg_turret)
        mg_turret.ai.vehicle=z
        z.ai.radio=spawn_object(world,world_coords,'radio_feldfu_b',False)

        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=main_turret
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('radio_operator',z)
        role.is_gunner=True
        role.turret=mg_turret
        role.is_radio_operator=True
        role.radio=z.ai.radio
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        z.ai.vehicle_crew.append(role)

        z.ai.max_speed=367.04
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=26500
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'diesel')
        z.ai.engines.append(spawn_object(world,world_coords,"kharkiv_v2-34_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        for b in range(10):
            z.add_inventory(spawn_object(world,world_coords,"mg34_belt",False))
        z.ai.ammo_rack_capacity=87
        for b in range(60):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"75mm_kwk40_l48_magazine",False))
        for b in range(27):
            temp=spawn_object(world,world_coords,"75mm_kwk40_l48_magazine",False)
            load_magazine(world,temp,'Sprgr_34_75_L48')
            z.ai.ammo_rack.append(temp)
        z.ai.min_wheels_per_side_front=3
        z.ai.min_wheels_per_side_rear=3
        z.ai.max_wheels=16
        z.ai.max_spare_wheels=0
        for b in range(4):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))

    elif object_type=='panzer_iv_h_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['panzer_iv_h_turret','panzer_iv_h_turret'],AITurret)
        z.name='Panzer IV Ausf. H Turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=1
        z.ai.turret_armor['top']=[16,0,0]
        z.ai.turret_armor['bottom']=[8,0,0]
        z.ai.turret_armor['left']=[30,23,8]
        z.ai.turret_armor['right']=[30,23,8]
        z.ai.turret_armor['front']=[50,11,0]
        z.ai.turret_armor['rear']=[30,15,8]
        z.ai.position_offset=[-15,0]
        z.ai.rotation_range=[-360,360]
        z.ai.primary_weapon=spawn_object(world,world_coords,'75mm_kwk40_l48',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-100.0, 1.0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.coaxial_weapon=spawn_object(world,world_coords,'mg34',False)
        z.ai.coaxial_weapon.ai.equipper=z
        z.ai.coaxial_weapon.ai.spawn_case=False
        z.ai.primary_turret=True
        z.ai.primary_weapon_reload_speed=20
        z.ai.coaxial_weapon_reload_speed=10
        z.no_save=True

    # J is a H with simplicication. schurtzen are replaced with wire schurtzen on the hull (thin)
    elif object_type=='german_panzer_iv_ausf_j':
        # ref : https://wiki.warthunder.com/unit/germ_pzkpfw_IV_ausf_G
        z=WorldObject(world,['panzer_iv_j_chassis','panzer_iv_j_chassis_destroyed'],AIVehicle)
        z.name='Panzer IV Ausf. J'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.requires_afv_training=True
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.vehicle_armor['top']=[16,0,0]
        z.ai.vehicle_armor['bottom']=[8,0,0]
        z.ai.vehicle_armor['left']=[30,0,1]
        z.ai.vehicle_armor['right']=[30,0,1]
        z.ai.vehicle_armor['front']=[80,64,0]
        z.ai.vehicle_armor['rear']=[30,15,0]
        z.ai.passenger_compartment_armor['top']=[16,0,0]
        z.ai.passenger_compartment_armor['bottom']=[8,0,0]
        z.ai.passenger_compartment_armor['left']=[30,0,1]
        z.ai.passenger_compartment_armor['right']=[30,0,1]
        z.ai.passenger_compartment_armor['front']=[80,11,0]
        z.ai.passenger_compartment_armor['rear']=[30,15,0]
        main_turret=spawn_object(world,world_coords,'panzer_iv_j_turret',True)
        z.ai.turrets.append(main_turret)
        main_turret.ai.vehicle=z
        mg_turret=spawn_object(world,world_coords,'panzer_iv_hull_mg',True)
        z.ai.turrets.append(mg_turret)
        mg_turret.ai.vehicle=z
        z.ai.radio=spawn_object(world,world_coords,'radio_feldfu_b',False)

        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=main_turret
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('radio_operator',z)
        role.is_gunner=True
        role.turret=mg_turret
        role.is_radio_operator=True
        role.radio=z.ai.radio
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        z.ai.vehicle_crew.append(role)

        z.ai.max_speed=367.04
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=26500
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'diesel')
        z.ai.engines.append(spawn_object(world,world_coords,"kharkiv_v2-34_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        for b in range(10):
            z.add_inventory(spawn_object(world,world_coords,"mg34_belt",False))
        z.ai.ammo_rack_capacity=87
        for b in range(60):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"75mm_kwk40_l48_magazine",False))
        for b in range(27):
            temp=spawn_object(world,world_coords,"75mm_kwk40_l48_magazine",False)
            load_magazine(world,temp,'Sprgr_34_75_L48')
            z.ai.ammo_rack.append(temp)
        z.ai.min_wheels_per_side_front=3
        z.ai.min_wheels_per_side_rear=3
        z.ai.max_wheels=16
        z.ai.max_spare_wheels=0
        for b in range(4):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))

    elif object_type=='panzeriv_wheel':
        z=WorldObject(world,['volkswagen_wheel'],AIWheel)
        z.name='Panzer IV Wheel'
        z.ai.compatible_vehicles=['german_panzer_iv_ausf_g','german_panzer_iv_ausf_h','german_panzer_iv_ausf_j']
        z.ai.armor=[10,0,0]

    elif object_type=='panzer_iv_j_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['panzer_iv_j_turret','panzer_iv_j_turret'],AITurret)
        z.name='Panzer IV Ausf. J Turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=1
        z.ai.turret_armor['top']=[16,0,0]
        z.ai.turret_armor['bottom']=[8,0,0]
        z.ai.turret_armor['left']=[30,23,8]
        z.ai.turret_armor['right']=[30,23,8]
        z.ai.turret_armor['front']=[50,11,0]
        z.ai.turret_armor['rear']=[30,15,8]
        z.ai.position_offset=[-15,0]
        z.ai.rotation_range=[-360,360]
        z.ai.primary_weapon=spawn_object(world,world_coords,'75mm_kwk40_l48',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-100.0, 1.0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.coaxial_weapon=spawn_object(world,world_coords,'mg34',False)
        z.ai.coaxial_weapon.ai.equipper=z
        z.ai.coaxial_weapon.ai.spawn_case=False
        z.ai.primary_turret=True
        z.ai.primary_weapon_reload_speed=20
        z.ai.coaxial_weapon_reload_speed=10
        z.no_save=True

    elif object_type=='75mm_kwk40_l43':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='75mm_kwk40_l43'
        z.no_update=True
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'75mm_kwk40_l43_magazine',False)
        z.ai.rate_of_fire=1
        z.ai.reload_speed=20
        z.ai.range=4000
        z.ai.type='cannon'
        z.ai.use_antitank=True
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='75mm_kwk40_l43_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='75mm_kwk40_l48_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['75mm_kwk40_l43']
        z.ai.compatible_projectiles=['PzGr39_75_L43','Sprgr_34_75_L43']
        z.ai.capacity=1
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='75mm_kwk40_l48':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='75mm_kwk40_l48'
        z.no_update=True
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'75mm_kwk40_l48_magazine',False)
        z.ai.rate_of_fire=1
        z.ai.reload_speed=20
        z.ai.range=4000
        z.ai.type='cannon'
        z.ai.use_antitank=True
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='75mm_kwk40_l48_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='75mm_kwk40_l48_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['75mm_kwk40_l48']
        z.ai.compatible_projectiles=['PzGr39_75_L48','Sprgr_34_75_L48']
        z.ai.capacity=1
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='german_panzer_vi_ausf_e':
        # ref : https://wiki.warthunder.com/unit/germ_pzkpfw_IV_ausf_G
        z=WorldObject(world,['panzer_vi_ausf_e_chassis'],AIVehicle)
        z.name='Panzer VI Ausf.E Tiger'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.requires_afv_training=True
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.vehicle_armor['top']=[26,0,0]
        z.ai.vehicle_armor['bottom']=[26,0,0]
        z.ai.vehicle_armor['left']=[62,0,0]
        z.ai.vehicle_armor['right']=[62,0,0]
        z.ai.vehicle_armor['front']=[100,25,0]
        z.ai.vehicle_armor['rear']=[82,9,0]
        z.ai.passenger_compartment_armor['top']=[26,0,0]
        z.ai.passenger_compartment_armor['bottom']=[26,0,0]
        z.ai.passenger_compartment_armor['left']=[82,0,0]
        z.ai.passenger_compartment_armor['right']=[82,0,0]
        z.ai.passenger_compartment_armor['front']=[102,9,0]
        z.ai.passenger_compartment_armor['rear']=[82,9,0]
        main_turret=spawn_object(world,world_coords,'panzer_vi_ausf_e_turret',True)
        z.ai.turrets.append(main_turret)
        main_turret.ai.vehicle=z
        mg_turret=spawn_object(world,world_coords,'panzer_vi_ausf_e_hull_mg',True)
        z.ai.turrets.append(mg_turret)
        mg_turret.ai.vehicle=z
        z.ai.radio=spawn_object(world,world_coords,'radio_feldfu_b',False)

        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=main_turret
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('radio_operator',z)
        role.is_gunner=True
        role.turret=mg_turret
        role.is_radio_operator=True
        role.radio=z.ai.radio
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        z.ai.vehicle_crew.append(role)

        z.ai.max_speed=367.04
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=26500
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'diesel')
        z.ai.engines.append(spawn_object(world,world_coords,"kharkiv_v2-34_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        for b in range(10):
            z.add_inventory(spawn_object(world,world_coords,"mg34_belt",False))
        # armor piercing belt
        if random.randint(0,1)==1:
            belt=spawn_object(world,world_coords,"mg34_belt",False)
            load_magazine(world,belt,'7.92x57_SMK')
            z.add_inventory(belt)
        z.ai.ammo_rack_capacity=92
        for b in range(60):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,'8.8cm_kwk36_l56_magazine',False))
        for b in range(32):
            temp=spawn_object(world,world_coords,'8.8cm_kwk36_l56_magazine',False)
            load_magazine(world,temp,'Sprgr_34_88_L56')
            z.ai.ammo_rack.append(temp)
        z.ai.min_wheels_per_side_front=3
        z.ai.min_wheels_per_side_rear=3
        z.ai.max_wheels=16
        z.ai.max_spare_wheels=0
        for b in range(4):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"panzeriv_wheel",False))
        
    elif object_type=='panzer_vi_ausf_e_hull_mg':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['panzer_iv_hull_mg','panzer_iv_hull_mg'],AITurret)
        z.name='Panzer VI Ausf E Hull MG'
        z.is_turret=True
        z.ai.small=True
        z.ai.vehicle_mount_side='front'
        z.ai.turret_accuracy=10
        z.ai.turret_armor['top']=[40,0,0]
        z.ai.turret_armor['bottom']=[26,0,0]
        z.ai.turret_armor['left']=[82,0,0]
        z.ai.turret_armor['right']=[82,0,0]
        z.ai.turret_armor['front']=[100,0,0]
        z.ai.turret_armor['rear']=[82,0,0]
        z.ai.position_offset=[-63,17]
        z.ai.rotation_range=[-20,20]
        z.ai.primary_weapon=spawn_object(world,world_coords,'mg34',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_weapon_reload_speed=10
        z.no_save=True

    elif object_type=='panzer_vi_ausf_e_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['panzer_vi_ausf_e_turret'],AITurret)
        z.name='Panzer VI Ausf. E Turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=1
        z.ai.turret_armor['top']=[40,0,0]
        z.ai.turret_armor['bottom']=[26,0,0]
        z.ai.turret_armor['left']=[82,0,0]
        z.ai.turret_armor['right']=[82,0,0]
        z.ai.turret_armor['front']=[100,0,0]
        z.ai.turret_armor['rear']=[82,0,0]
        z.ai.position_offset=[-14,0]
        z.ai.rotation_range=[-360,360]
        z.ai.primary_weapon=spawn_object(world,world_coords,'8.8cm_kwk36_l56',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-130.0, 1.0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.coaxial_weapon=spawn_object(world,world_coords,'mg34',False)
        z.ai.coaxial_weapon.ai.equipper=z
        z.ai.coaxial_weapon.ai.spawn_case=False
        z.ai.primary_turret=True
        z.ai.primary_weapon_reload_speed=21
        z.ai.coaxial_weapon_reload_speed=10
        z.no_save=True

    elif object_type=='8.8cm_kwk36_l56':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='8.8 cm KWK 36 L56'
        z.no_update=True
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'8.8cm_kwk36_l56_magazine',False)
        z.ai.rate_of_fire=1
        z.ai.reload_speed=20
        z.ai.range=4000
        z.ai.type='cannon'
        z.ai.use_antitank=True
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='8.8cm_kwk36_l56_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='8.8cm_kwk36_l56_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['8.8cm_kwk36_l56']
        z.ai.compatible_projectiles=['PzGr39_88_L56','Sprgr_34_88_L56']
        z.ai.capacity=1
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    # +camo
    elif object_type=='german_panzer_vi_ausf_e_camo1':
        z=spawn_object(world,world_coords,'german_panzer_vi_ausf_e',False)
        z.image_list=["panzer_vi_ausf_e_chassis_camo1"]
        z.ai.turrets[0].image_list=["panzer_vi_ausf_e_turret_camo1"]

    elif object_type=='soviet_t20':
        # ref : https://en.wikipedia.org/wiki/Komsomolets_armored_tractor
        # ref : https://wiki.warthunder.com/ZiS-30
        z=WorldObject(world,['t20','t20_destroyed'],AIVehicle)
        z.name='T20 Komsomolets armored tractor'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.is_transport=True
        z.ai.open_top=True
        z.ai.vehicle_armor['top']=[5,0,0]
        z.ai.vehicle_armor['bottom']=[7,0,0]
        z.ai.vehicle_armor['left']=[7,19,0]
        z.ai.vehicle_armor['right']=[7,19,0]
        z.ai.vehicle_armor['front']=[10,24,0]
        z.ai.vehicle_armor['rear']=[7,42,0]
        z.ai.passenger_compartment_armor['top']=[0,0,0]
        z.ai.passenger_compartment_armor['bottom']=[5,0,0]
        z.ai.passenger_compartment_armor['left']=[0,0,0]
        z.ai.passenger_compartment_armor['right']=[0,0,0]
        z.ai.passenger_compartment_armor['front']=[0,0,0]
        z.ai.passenger_compartment_armor['rear']=[0,0,0]
        turret=spawn_object(world,world_coords,'t20_turret',True)
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z

        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=turret
        z.ai.vehicle_crew.append(role)

        passenger_positions=[[0,-17],[11,-17],[24,-17],[0,17],[11,17],[24,17]]
        passenger_rotation=[90,90,90,270,270,270]
        for x in range(6):
            role=VehicleRole('passenger',z)
            role.is_passenger=True
            role.seat_visible=True
            role.seat_rotation=passenger_rotation.pop()
            role.seat_offset=passenger_positions.pop()
            z.ai.vehicle_crew.append(role)

        z.ai.max_speed=367.04
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=3500
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"maybach_hl42_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        
        # turret ammo
        for b in range(4):
            z.add_inventory(spawn_object(world,world_coords,"dtm_magazine",False))
        z.ai.min_wheels_per_side_front=1
        z.ai.min_wheels_per_side_rear=1
        z.ai.max_wheels=8
        z.ai.max_spare_wheels=0
        for b in range(2):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"t20_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"t20_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"t20_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"t20_wheel",False))

    elif object_type=='t20_wheel':
        z=WorldObject(world,['volkswagen_wheel'],AIWheel)
        z.name='T20 Wheel'
        z.ai.compatible_vehicles=['soviet_t20']
        z.ai.armor=[5,0,0]
        
    elif object_type=='t20_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['t20_turret','t20_turret'],AITurret)
        z.name='T20 Turret Turret'
        z.is_turret=True
        z.ai.small=True
        z.ai.vehicle_mount_side='front'
        z.ai.turret_accuracy=10
        z.ai.turret_armor['top']=[5,31,0]
        z.ai.turret_armor['bottom']=[5,31,0]
        z.ai.turret_armor['left']=[5,31,0]
        z.ai.turret_armor['right']=[5,31,0]
        z.ai.turret_armor['front']=[5,31,0]
        z.ai.turret_armor['rear']=[5,31,0]
        z.ai.position_offset=[-25,9]
        z.ai.rotation_range=[-20,20]
        z.ai.primary_weapon=spawn_object(world,world_coords,'dtm',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_turret=True
        z.ai.primary_weapon_reload_speed=10
        z.no_save=True

    # this is the base object for the sd.kfz.10 variants. It is not meant to be spawned by itself
    elif object_type=='soviet_zis_5':
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['zis_5'],AIVehicle)
        z.name='Zis 5 Truck'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.is_transport=True

        # driver and assistant driver positions are the same for all variants
        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)
        role=VehicleRole('passenger',z)
        z.ai.vehicle_crew.append(role)

        passenger_positions=[[2.0, -22.0],[20.0, -22.0],[40.0, -22.0],[61.0, -22.0],[21.0, 0.0],[40.0, 19.0],[20.0, 19.0],[0.0, 19.0],[1.0, -1.0],[62.0, 0.0],[61.0, 20.0],[40.0, 0.0]]
        for x in range(12):
            role=VehicleRole('passenger',z)
            role.is_passenger=True
            role.seat_visible=True
            role.seat_offset=passenger_positions.pop()
            z.ai.vehicle_crew.append(role)

        z.ai.vehicle_armor['top']=[1,0,0]
        z.ai.vehicle_armor['bottom']=[1,0,0]
        z.ai.vehicle_armor['left']=[1,0,0]
        z.ai.vehicle_armor['right']=[1,0,0]
        z.ai.vehicle_armor['front']=[1,0,0]
        z.ai.vehicle_armor['rear']=[1,0,0]
        z.ai.passenger_compartment_armor['top']=[0,0,0]
        z.ai.passenger_compartment_armor['bottom']=[0,0,0]
        z.ai.passenger_compartment_armor['left']=[0,0,0]
        z.ai.passenger_compartment_armor['right']=[0,0,0]
        z.ai.passenger_compartment_armor['front']=[0.0,0,0]
        z.ai.passenger_compartment_armor['rear']=[0,0,0]
        z.ai.max_speed=385.9
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=7800
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"maybach_hl42_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        if random.randint(0,1)==1:
            z.add_inventory(spawn_object(world,world_coords,"tt33",False))
        z.ai.min_wheels_per_side_front=1
        z.ai.min_wheels_per_side_rear=1
        z.ai.max_wheels=4
        z.ai.max_spare_wheels=0
        z.ai.front_left_wheels.append(spawn_object(world,world_coords,"251_wheel",False))
        z.ai.front_right_wheels.append(spawn_object(world,world_coords,"251_wheel",False))
        z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"251_wheel",False))
        z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"251_wheel",False))

    elif object_type=='soviet_t34_76_model_1943':
        # ref : https://wiki.warthunder.com/T-34_(1942)
        z=WorldObject(world,['t34_chassis','t34_chassis_destroyed'],AIVehicle)
        z.name='T34-76 Model 1943'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.requires_afv_training=True
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.vehicle_armor['top']=[16,0,0]
        z.ai.vehicle_armor['bottom']=[8,0,0]
        z.ai.vehicle_armor['left']=[45,0,0]
        z.ai.vehicle_armor['right']=[45,0,0]
        z.ai.vehicle_armor['front']=[45,61,0]
        z.ai.vehicle_armor['rear']=[40,47,0]
        z.ai.passenger_compartment_armor['top']=[16,0,0]
        z.ai.passenger_compartment_armor['bottom']=[8,0,0]
        z.ai.passenger_compartment_armor['left']=[40,40,0]
        z.ai.passenger_compartment_armor['right']=[40,40,0]
        z.ai.passenger_compartment_armor['front']=[45,61,0]
        z.ai.passenger_compartment_armor['rear']=[40,47,0]
        main_turret=spawn_object(world,world_coords,'t34_76_model_1943_turret',True)
        z.ai.turrets.append(main_turret)
        main_turret.ai.vehicle=z
        mg_turret=spawn_object(world,world_coords,'t34_hull_mg_turret',True)
        z.ai.turrets.append(mg_turret)
        mg_turret.ai.vehicle=z

        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        role.is_gunner=True
        role.turret=main_turret
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('bow_gunner',z)
        role.is_gunner=True
        role.turret=mg_turret
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        z.ai.vehicle_crew.append(role)

        z.ai.max_speed=367.04
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=26500
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'diesel')
        z.ai.engines.append(spawn_object(world,world_coords,"kharkiv_v2-34_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        for b in range(10):
            z.add_inventory(spawn_object(world,world_coords,"dtm_magazine",False))
        z.ai.ammo_rack_capacity=77
        for b in range(60):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"76mm_m1940_f34_magazine",False))
        for b in range(17):
            temp=spawn_object(world,world_coords,"76mm_m1940_f34_magazine",False)
            load_magazine(world,temp,'OF-350M')
            z.ai.ammo_rack.append(temp)
        z.ai.min_wheels_per_side_front=2
        z.ai.min_wheels_per_side_rear=2
        z.ai.max_wheels=12
        z.ai.max_spare_wheels=0
        for b in range(3):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
        
    elif object_type=='t34_hull_mg_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['t34_hull_mg_turret','t34_hull_mg_turret'],AITurret)
        z.name='T34 hull mg turret'
        z.is_turret=True
        z.ai.small=True
        z.ai.vehicle_mount_side='front'
        z.ai.turret_accuracy=10
        z.ai.turret_armor['top']=[15,0,0]
        z.ai.turret_armor['bottom']=[8,0,0]
        z.ai.turret_armor['left']=[53,21,0]
        z.ai.turret_armor['right']=[53,21,0]
        z.ai.turret_armor['front']=[53,20,0]
        z.ai.turret_armor['rear']=[53,20,0]
        z.ai.position_offset=[-65,13]
        z.ai.rotation_range=[-20,20]
        z.ai.primary_weapon=spawn_object(world,world_coords,'dtm',False)
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon_reload_speed=10
        z.no_save=True

    elif object_type=='t34_76_model_1943_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['t34_76_model_1943_turret','t34_76_model_1943_turret'],AITurret)
        z.name='T34-76 Model 1943 turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=2
        z.ai.turret_armor['top']=[15,0,0]
        z.ai.turret_armor['bottom']=[8,0,0]
        z.ai.turret_armor['left']=[53,21,0]
        z.ai.turret_armor['right']=[53,21,0]
        z.ai.turret_armor['front']=[53,20,0]
        z.ai.turret_armor['rear']=[53,20,0]
        z.ai.position_offset=[-15,0]
        z.ai.rotation_range=[-360,360]
        z.ai.primary_weapon=spawn_object(world,world_coords,'76mm_m1940_f34',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-82,0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.coaxial_weapon=spawn_object(world,world_coords,'dtm',False)
        z.ai.coaxial_weapon.ai.spawn_case=False
        z.ai.coaxial_weapon.ai.equipper=z
        z.ai.primary_turret=True
        z.ai.primary_weapon_reload_speed=25
        z.ai.coaxial_weapon_reload_speed=10
        z.no_save=True

    elif object_type=='soviet_t34_85':
        # ref : https://wiki.warthunder.com/T-34-85
        z=WorldObject(world,['t34_chassis','t34_chassis_destroyed'],AIVehicle)
        z.name='T34-85'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.requires_afv_training=True
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.vehicle_armor['top']=[16,0,0]
        z.ai.vehicle_armor['bottom']=[8,0,0]
        z.ai.vehicle_armor['left']=[45,0,0]
        z.ai.vehicle_armor['right']=[45,0,0]
        z.ai.vehicle_armor['front']=[45,61,0]
        z.ai.vehicle_armor['rear']=[40,47,0]
        z.ai.passenger_compartment_armor['top']=[16,0,0]
        z.ai.passenger_compartment_armor['bottom']=[8,0,0]
        z.ai.passenger_compartment_armor['left']=[40,40,0]
        z.ai.passenger_compartment_armor['right']=[40,40,0]
        z.ai.passenger_compartment_armor['front']=[45,61,0]
        z.ai.passenger_compartment_armor['rear']=[40,47,0]
        main_turret=spawn_object(world,world_coords,'t34_85_turret',True)
        z.ai.turrets.append(main_turret)
        main_turret.ai.vehicle=z
        mg_turret=spawn_object(world,world_coords,'t34_hull_mg_turret',True)
        z.ai.turrets.append(mg_turret)
        mg_turret.ai.vehicle=z
        
        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=main_turret
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('bow_gunner',z)
        role.is_gunner=True
        role.turret=mg_turret
        #role.is_radio_operator=True
        #role.radio=radio
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        z.ai.vehicle_crew.append(role)

        z.ai.max_speed=367.04
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=26500
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'diesel')
        z.ai.engines.append(spawn_object(world,world_coords,"kharkiv_v2-34_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        for b in range(10):
            z.add_inventory(spawn_object(world,world_coords,"dtm_magazine",False))
        z.ai.ammo_rack_capacity=57
        for b in range(50):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"85mm_zis_s_53_magazine",False))
        for b in range(7):
            temp=spawn_object(world,world_coords,"85mm_zis_s_53_magazine",False)
            load_magazine(world,temp,'O365k')
            z.ai.ammo_rack.append(temp)
        z.ai.min_wheels_per_side_front=2
        z.ai.min_wheels_per_side_rear=2
        z.ai.max_wheels=12
        z.ai.max_spare_wheels=0
        for b in range(3):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))

    elif object_type=='t34_wheel':
        z=WorldObject(world,['volkswagen_wheel'],AIWheel)
        z.name='T34 Wheel'
        z.ai.compatible_vehicles=['soviet_t34_85','soviet_t34_76']
        z.ai.armor=[10,0,0]

    elif object_type=='t34_85_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['t34_85_turret','t34_85_turret'],AITurret)
        z.name='T34-85 Turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=2
        z.ai.turret_armor['top']=[20,0,0]
        z.ai.turret_armor['bottom']=[8,0,0]
        z.ai.turret_armor['left']=[75,21,0]
        z.ai.turret_armor['right']=[75,21,0]
        z.ai.turret_armor['front']=[90,20,0]
        z.ai.turret_armor['rear']=[52,9,0]
        z.ai.position_offset=[5,0]
        z.ai.rotation_range=[-360,360]
        z.ai.primary_weapon=spawn_object(world,world_coords,'85mm_zis_s_53',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-147,0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.coaxial_weapon=spawn_object(world,world_coords,'dtm',False)
        z.ai.coaxial_weapon.ai.equipper=z
        z.ai.coaxial_weapon.ai.spawn_case=False
        z.ai.primary_turret=True
        z.ai.primary_weapon_reload_speed=23
        z.ai.coaxial_weapon_reload_speed=10
        z.no_save=True
    elif object_type=='soviet_t70':
        # ref : https://old-wiki.warthunder.com/T-70
        z=WorldObject(world,['t70_chassis'],AIVehicle)
        z.name='T70'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.requires_afv_training=True
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.vehicle_armor['top']=[10,0,0]
        z.ai.vehicle_armor['bottom']=[8,0,0]
        z.ai.vehicle_armor['left']=[15,0,0]
        z.ai.vehicle_armor['right']=[15,0,0]
        z.ai.vehicle_armor['front']=[45,31,0]
        z.ai.vehicle_armor['rear']=[25,43,0]
        z.ai.passenger_compartment_armor['top']=[10,0,0]
        z.ai.passenger_compartment_armor['bottom']=[8,0,0]
        z.ai.passenger_compartment_armor['left']=[15,0,0]
        z.ai.passenger_compartment_armor['right']=[15,0,0]
        z.ai.passenger_compartment_armor['front']=[35,62,0]
        z.ai.passenger_compartment_armor['rear']=[10,70,0]
        main_turret=spawn_object(world,world_coords,'t70_turret',True)
        z.ai.turrets.append(main_turret)
        main_turret.ai.vehicle=z
        
        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=main_turret
        z.ai.vehicle_crew.append(role)

        z.ai.max_speed=367.04
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=26500
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'diesel')
        z.ai.engines.append(spawn_object(world,world_coords,"kharkiv_v2-34_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        for b in range(10):
            z.add_inventory(spawn_object(world,world_coords,"dtm_magazine",False))
        z.ai.ammo_rack_capacity=45
        for b in range(45):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"45mm_19k_magazine",False))
        z.ai.min_wheels_per_side_front=2
        z.ai.min_wheels_per_side_rear=2
        z.ai.max_wheels=12
        z.ai.max_spare_wheels=0
        for b in range(3):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))

    elif object_type=='t70_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['t70_turret'],AITurret)
        z.name='T70 Turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=2
        z.ai.turret_armor['top']=[14,0,0]
        z.ai.turret_armor['bottom']=[8,0,0]
        z.ai.turret_armor['left']=[35,22,0]
        z.ai.turret_armor['right']=[35,22,0]
        z.ai.turret_armor['front']=[35,25,0]
        z.ai.turret_armor['rear']=[35,28,0]
        z.ai.position_offset=[0,-7]
        z.ai.rotation_range=[-360,360]
        z.ai.primary_weapon=spawn_object(world,world_coords,'45mm_19k',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-147,0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.coaxial_weapon=spawn_object(world,world_coords,'dtm',False)
        z.ai.coaxial_weapon.ai.equipper=z
        z.ai.coaxial_weapon.ai.spawn_case=False
        z.ai.primary_turret=True
        z.ai.primary_weapon_reload_speed=25
        z.ai.coaxial_weapon_reload_speed=10
        z.no_save=True

    elif object_type=='45mm_19k':
        # ref https://en.wikipedia.org/wiki/45_mm_anti-tank_gun_M1932_(19-K)#Tank_gun_20-K
        z=WorldObject(world,['mg34'],AIGun)
        z.name='45mm 19k'
        z.no_update=True
        z.is_gun=True
        z.ai.mechanical_accuracy=2
        z.ai.magazine=spawn_object(world,world_coords,'45mm_19k_magazine',False)
        z.ai.rate_of_fire=1
        z.ai.reload_speed=26
        z.ai.range=4000
        z.ai.type='cannon'
        z.ai.use_antitank=True
        z.ai.use_antipersonnel=True
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='45mm_19k_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='85mm_zis_s_53_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['45mm_19k']
        z.ai.compatible_projectiles=['BR-240']
        z.ai.capacity=1
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif object_type=='soviet_su_85':
        # ref : https://wiki.warthunder.com/T-34-85
        z=WorldObject(world,['su_85_chassis'],AIVehicle)
        z.name='SU-85'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.requires_afv_training=True
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.vehicle_armor['top']=[16,0,0]
        z.ai.vehicle_armor['bottom']=[8,0,0]
        z.ai.vehicle_armor['left']=[45,0,0]
        z.ai.vehicle_armor['right']=[45,0,0]
        z.ai.vehicle_armor['front']=[45,50,0]
        z.ai.vehicle_armor['rear']=[45,47,0]
        z.ai.passenger_compartment_armor['top']=[16,0,0]
        z.ai.passenger_compartment_armor['bottom']=[8,0,0]
        z.ai.passenger_compartment_armor['left']=[45,40,0]
        z.ai.passenger_compartment_armor['right']=[45,40,0]
        z.ai.passenger_compartment_armor['front']=[45,61,0]
        z.ai.passenger_compartment_armor['rear']=[40,47,0]
        main_turret=spawn_object(world,world_coords,'su_85_turret',True)
        z.ai.turrets.append(main_turret)
        main_turret.ai.vehicle=z
        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=main_turret
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        z.ai.vehicle_crew.append(role)

        z.ai.max_speed=367.04
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=26500
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'diesel')
        z.ai.engines.append(spawn_object(world,world_coords,"kharkiv_v2-34_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        z.ai.ammo_rack_capacity=60
        for b in range(50):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"85mm_zis_s_53_magazine",False))
        for b in range(10):
            temp=spawn_object(world,world_coords,"85mm_zis_s_53_magazine",False)
            load_magazine(world,temp,'O365k')
            z.ai.ammo_rack.append(temp)
        z.ai.min_wheels_per_side_front=2
        z.ai.min_wheels_per_side_rear=2
        z.ai.max_wheels=12
        z.ai.max_spare_wheels=0
        for b in range(3):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))

    elif object_type=='su_85_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['su_85_turret'],AITurret)
        z.name='SU-85 Turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='front'
        z.ai.turret_accuracy=2
        z.ai.turret_armor['top']=[20,0,0]
        z.ai.turret_armor['bottom']=[8,0,0]
        z.ai.turret_armor['left']=[45,21,0]
        z.ai.turret_armor['right']=[45,21,0]
        z.ai.turret_armor['front']=[45,10,0]
        z.ai.turret_armor['rear']=[45,9,0]
        z.ai.position_offset=[-47,8]
        z.ai.rotation_range=[-10,10]
        z.ai.primary_weapon=spawn_object(world,world_coords,'85mm_d_5s',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-147,0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_turret=True
        z.ai.primary_weapon_reload_speed=21
        z.ai.coaxial_weapon_reload_speed=10
        z.no_save=True

    elif object_type=='soviet_su_100':
        # ref : https://wiki.warthunder.com/T-34-85
        z=WorldObject(world,['su_85_chassis'],AIVehicle)
        z.name='SU-100'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.requires_afv_training=True
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.vehicle_armor['top']=[16,0,0]
        z.ai.vehicle_armor['bottom']=[8,0,0]
        z.ai.vehicle_armor['left']=[45,0,0]
        z.ai.vehicle_armor['right']=[45,0,0]
        z.ai.vehicle_armor['front']=[75,50,0]
        z.ai.vehicle_armor['rear']=[45,47,0]
        z.ai.passenger_compartment_armor['top']=[16,0,0]
        z.ai.passenger_compartment_armor['bottom']=[8,0,0]
        z.ai.passenger_compartment_armor['left']=[45,40,0]
        z.ai.passenger_compartment_armor['right']=[45,40,0]
        z.ai.passenger_compartment_armor['front']=[75,50,0]
        z.ai.passenger_compartment_armor['rear']=[40,47,0]
        main_turret=spawn_object(world,world_coords,'su_100_turret',True)
        z.ai.turrets.append(main_turret)
        main_turret.ai.vehicle=z
        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=main_turret
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        z.ai.vehicle_crew.append(role)

        z.ai.max_speed=367.04
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=26500
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'diesel')
        z.ai.engines.append(spawn_object(world,world_coords,"kharkiv_v2-34_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        z.ai.ammo_rack_capacity=60
        for b in range(25):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"100mm_d_10_magazine",False))
        for b in range(5):
            temp=spawn_object(world,world_coords,"100mm_d_10_magazine",False)
            load_magazine(world,temp,'OF-412')
            z.ai.ammo_rack.append(temp)
        z.ai.min_wheels_per_side_front=2
        z.ai.min_wheels_per_side_rear=2
        z.ai.max_wheels=12
        z.ai.max_spare_wheels=0
        for b in range(3):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"t34_wheel",False))

    elif object_type=='su_100_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['su_100_turret'],AITurret)
        z.name='SU-100 Turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='front'
        z.ai.turret_accuracy=2
        z.ai.turret_armor['top']=[20,0,0]
        z.ai.turret_armor['bottom']=[8,0,0]
        z.ai.turret_armor['left']=[45,21,0]
        z.ai.turret_armor['right']=[45,21,0]
        z.ai.turret_armor['front']=[75,10,0]
        z.ai.turret_armor['rear']=[45,9,0]
        z.ai.position_offset=[-67,8]
        z.ai.rotation_range=[-8,8]
        z.ai.primary_weapon=spawn_object(world,world_coords,'100mm_d_10',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-147,0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_turret=True
        z.ai.primary_weapon_reload_speed=29
        z.no_save=True

    elif object_type=='german_jagdpanzer_38t_hetzer':
        # ref : https://wiki.warthunder.com/Jagdpanzer_38(t)
        # ref : https://en.wikipedia.org/wiki/Hetzer
        z=WorldObject(world,['jagdpanzer_38t_hetzer_chassis','jagdpanzer_38t_hetzer_chassis_destroyed'],AIVehicle)
        z.name='Jadgpanzer 38t Hetzer'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.requires_afv_training=True
        z.ai.passenger_compartment_ammo_racks=True
        z.ai.vehicle_armor['top']=[8,90,0]
        z.ai.vehicle_armor['bottom']=[12,90,0]
        z.ai.vehicle_armor['left']=[20,40,5]
        z.ai.vehicle_armor['right']=[20,40,5]
        z.ai.vehicle_armor['front']=[60,60,0]
        z.ai.vehicle_armor['rear']=[20,14,0]
        z.ai.passenger_compartment_armor['top']=[8,90,0]
        z.ai.passenger_compartment_armor['bottom']=[12,90,0]
        z.ai.passenger_compartment_armor['left']=[20,40,0]
        z.ai.passenger_compartment_armor['right']=[20,40,0]
        z.ai.passenger_compartment_armor['front']=[60,60,0]
        z.ai.passenger_compartment_armor['rear']=[8,68,0]
        main_turret=spawn_object(world,world_coords,'jagdpanzer_38t_main_gun',True)
        z.ai.turrets.append(main_turret)
        main_turret.ai.vehicle=z
        mg_turret=spawn_object(world,world_coords,'remote_mg34_turret',True)
        z.ai.turrets.append(mg_turret)
        mg_turret.ai.vehicle=z
        mg_turret.ai.position_offset=[-5,-15]
        z.ai.radio=spawn_object(world,world_coords,'radio_feldfu_b',False)
        
        role=VehicleRole('driver',z)
        role.is_driver=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=main_turret
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('radio_operator',z)
        role.is_gunner=True
        role.turret=mg_turret
        role.is_radio_operator=True
        role.radio=z.ai.radio
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('commander',z)
        role.is_commander=True
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        z.ai.vehicle_crew.append(role)

        z.ai.max_speed=367.04
        z.ai.max_offroad_speed=177.6
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=26500
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'diesel')
        z.ai.engines.append(spawn_object(world,world_coords,"kharkiv_v2-34_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        for b in range(10):
            z.add_inventory(spawn_object(world,world_coords,"mg34_belt",False))
        z.ai.ammo_rack_capacity=41
        for b in range(30):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"7.5cm_pak39_L48_magazine",False))
        for b in range(11):
            temp=spawn_object(world,world_coords,"7.5cm_pak39_L48_magazine",False)
            load_magazine(world,temp,'Sprgr_34_75_L48')
            z.ai.ammo_rack.append(temp)
        z.ai.min_wheels_per_side_front=1
        z.ai.min_wheels_per_side_rear=1
        z.ai.max_wheels=8
        z.ai.max_spare_wheels=0
        for b in range(2):
            z.ai.front_left_wheels.append(spawn_object(world,world_coords,"panzer38t_wheel",False))
            z.ai.front_right_wheels.append(spawn_object(world,world_coords,"panzer38t_wheel",False))
            z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"panzer38t_wheel",False))
            z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"panzer38t_wheel",False))

    elif object_type=='panzer38t_wheel':
        z=WorldObject(world,['volkswagen_wheel'],AIWheel)
        z.name='Gun Carriage Wheel'
        z.ai.compatible_vehicles=['german_jagdpanzer_38t_hetzer']
        z.ai.armor=[10,0,0]
        
    elif object_type=='remote_mg34_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['remote_mg34_turret','remote_mg34_turret'],AITurret)
        z.name='Remote MG34 Turret'
        z.is_turret=True
        z.ai.small=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=12
        z.ai.remote_operated=True
        z.ai.turret_armor['top']=[0,0,0]
        z.ai.turret_armor['bottom']=[0,0,0]
        z.ai.turret_armor['left']=[15,60,0]
        z.ai.turret_armor['right']=[15,60,0]
        z.ai.turret_armor['front']=[15,60,0]
        z.ai.turret_armor['rear']=[0,0,0]
        # this weapon is shared, so set this when you add the turret
        #z.ai.position_offset=[-65,13] # Best to set this when you spawn per vehicle
        z.ai.rotation_range=[-360,360]
        z.ai.primary_weapon=spawn_object(world,world_coords,'mg34',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon_reload_speed=10
        z.no_save=True

    elif object_type=='jagdpanzer_38t_main_gun':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        z=WorldObject(world,['jagdpanzer_38t_main_gun','jagdpanzer_38t_main_gun'],AITurret)
        z.name='Jagdpanzer 38t Main Gun'
        z.is_turret=True
        z.ai.vehicle_mount_side='front'
        z.ai.turret_accuracy=1
        z.ai.turret_armor['top']=[70,60,0]
        z.ai.turret_armor['bottom']=[70,60,0]
        z.ai.turret_armor['left']=[70,60,0]
        z.ai.turret_armor['right']=[70,60,0]
        z.ai.turret_armor['front']=[70,60,0]
        z.ai.turret_armor['rear']=[70,60,0]
        z.ai.position_offset=[-45,10]
        z.ai.rotation_range=[-20,20]
        z.ai.primary_weapon=spawn_object(world,world_coords,'7.5cm_pak39_L48',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-83,-1]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_turret=True
        z.ai.primary_weapon_reload_speed=20
        z.no_save=True

    elif object_type=='soviet_37mm_m1939_61k_aa_gun_carriage':
        z=WorldObject(world,['zu_7_carriage','zu_7_carriage'],AIVehicle)
        z.name='37mm_m1939_61k_aa_gun'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.is_towed_gun=True
        z.ai.requires_afv_training=True
        turret=spawn_object(world,world_coords,'37mm_m1939_61k_turret',True)
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=turret
        role.seat_visible=True
        role.seat_offset=[0,-10]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        role.seat_visible=True
        role.seat_offset=[0,10]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('driver',z)
        role.is_driver=True
        role.seat_visible=True
        role.seat_offset=[10,10]
        z.ai.vehicle_crew.append(role)

        z.ai.engines.append(spawn_object(world,world_coords,"bicycle_pedals",False))
        z.ai.max_speed=100
        z.ai.max_offroad_speed=100
        z.ai.open_top=True
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=1400
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.rotation_angle=float(random.randint(0,359))
        z.ai.ammo_rack_capacity=15
        for b in range(10):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"37mm_m1939_k61_magazine",False))
        for b in range(5):
            temp=spawn_object(world,world_coords,"37mm_m1939_k61_magazine",False)
            load_magazine(world,temp,'37x252_AP-T')
            z.ai.ammo_rack.append(temp)
        z.ai.min_wheels_per_side_front=1
        z.ai.min_wheels_per_side_rear=1
        z.ai.max_wheels=4
        z.ai.max_spare_wheels=0
        z.ai.front_left_wheels.append(spawn_object(world,world_coords,"gun_carriage_wheel",False))
        z.ai.front_right_wheels.append(spawn_object(world,world_coords,"gun_carriage_wheel",False))
        z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"gun_carriage_wheel",False))
        z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"gun_carriage_wheel",False))

    elif object_type=='gun_carriage_wheel':
        z=WorldObject(world,['volkswagen_wheel'],AIWheel)
        z.name='Gun Carriage Wheel'
        z.ai.compatible_vehicles=['soviet_37mm_m1939_61k_aa_gun_carriage']
            
    elif object_type=='37mm_m1939_61k_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['37mm_m1939_61k_turret','37mm_m1939_61k_turret'],AITurret)
        z.name='37mm_m1939_61k_turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=3
        z.ai.position_offset=[0,0]
        z.ai.rotation_range=[-360,360]
        z.ai.primary_weapon=spawn_object(world,world_coords,'37mm_m1939_k61',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-54,1]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_turret=True
        z.ai.primary_weapon_reload_speed=10
        z.no_save=True

    elif object_type=='german_pak40':
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['pak40_carriage_deployed','pak40_carriage_deployed'],AIVehicle)
        z.name='PAK 40'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.is_towed_gun=True
        z.ai.requires_afv_training=False
        z.ai.vehicle_armor['top']=[0,0,0]
        z.ai.vehicle_armor['bottom']=[13,0,0]
        z.ai.vehicle_armor['left']=[6,22,0]
        z.ai.vehicle_armor['right']=[6,22,0]
        z.ai.vehicle_armor['front']=[6,36,0]
        z.ai.vehicle_armor['rear']=[0,0,0]
        turret=spawn_object(world,world_coords,'pak40_turret',True)
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z

        role=VehicleRole('driver',z)
        role.is_driver=True
        role.seat_visible=True
        role.seat_offset=[13,20]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('gunner',z)
        role.is_gunner=True
        role.turret=turret
        role.seat_visible=True
        role.seat_offset=[7,-9]
        z.ai.vehicle_crew.append(role)

        role=VehicleRole('assistant_gunner',z)
        role.is_assistant_gunner=True
        role.seat_visible=True
        role.seat_offset=[13,15]
        z.ai.vehicle_crew.append(role)

        z.ai.engines.append(spawn_object(world,world_coords,"bicycle_pedals",False))
        z.ai.max_speed=100
        z.ai.max_offroad_speed=100
        z.ai.open_top=True
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=1400
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.rotation_angle=float(random.randint(0,359))
        z.ai.ammo_rack_capacity=30
        for b in range(20):
            z.ai.ammo_rack.append(spawn_object(world,world_coords,"75mm_pak40_magazine",False))
        for b in range(10):
            temp=spawn_object(world,world_coords,"75mm_pak40_magazine",False)
            load_magazine(world,temp,'Sprgr_34_75_L48')
            z.ai.ammo_rack.append(temp)
        z.ai.min_wheels_per_side_front=1
        z.ai.min_wheels_per_side_rear=0
        z.ai.max_wheels=4
        z.ai.max_spare_wheels=0
        z.ai.front_left_wheels.append(spawn_object(world,world_coords,"pak_wheel",False))
        z.ai.front_right_wheels.append(spawn_object(world,world_coords,"pak_wheel",False))

    elif object_type=='pak_wheel':
        z=WorldObject(world,['volkswagen_wheel'],AIWheel)
        z.name='PAK Wheel'
        z.ai.compatible_vehicles=['german_pak40']
       
    elif object_type=='pak40_turret':
        # !! note - turrets should be spawned with spawn TRUE as they are always in world
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['pak40_turret','pak40_turret'],AITurret)
        z.name='PAK 40 turret'
        z.is_turret=True
        z.ai.vehicle_mount_side='top'
        z.ai.turret_accuracy=1
        z.ai.turret_armor['top']=[0,0,0]
        z.ai.turret_armor['bottom']=[13,0,0]
        z.ai.turret_armor['left']=[6,22,0]
        z.ai.turret_armor['right']=[6,22,0]
        z.ai.turret_armor['front']=[6,36,0]
        z.ai.turret_armor['rear']=[0,0,0]
        z.ai.position_offset=[0,0]
        z.ai.rotation_range=[-60,60]
        z.ai.primary_weapon=spawn_object(world,world_coords,'75mm_pak40',False)
        z.ai.primary_weapon.ai.equipper=z
        z.ai.primary_weapon.ai.smoke_on_fire=True
        z.ai.primary_weapon.ai.smoke_type='cannon'
        z.ai.primary_weapon.ai.smoke_offset=[-76,0]
        z.ai.primary_weapon.ai.spawn_case=False
        z.ai.primary_turret=True
        z.ai.primary_weapon_reload_speed=20
        z.no_save=True

    elif object_type=='75mm_pak40':
        # this is the gun, not the whole pak40 object
        z=WorldObject(world,['mg34'],AIGun)
        z.name='75mm_pak40'
        z.no_update=True
        z.is_gun=True
        z.ai.mechanical_accuracy=1
        z.ai.magazine=spawn_object(world,world_coords,'75mm_pak40_magazine',False)
        z.ai.rate_of_fire=1
        z.ai.reload_speed=19
        z.ai.range=4000
        z.ai.type='cannon'
        z.ai.use_antitank=True
        z.ai.use_antipersonnel=True
        z.rotation_angle=0

    elif object_type=='75mm_pak40_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='75mm_kwk40_l48_magazine'
        z.minimum_visible_scale=0.4
        z.is_gun_magazine=True
        z.ai.compatible_guns=['75mm_pak40']
        z.ai.compatible_projectiles=['PzGr39_75_PAK40','Sprgr_34_75_L48']
        z.ai.capacity=1
        z.ai.disintegrating=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

  
    elif object_type=='german_kubelwagen':
        z=WorldObject(world,['kubelwagen','kubelwagen_destroyed'],AIVehicle)
        z.name='kubelwagen'
        z.is_vehicle=True
        z.is_towable=True
        z.ai.is_transport=True

        z.ai.max_speed=592

        driver=VehicleRole('driver',z)
        driver.is_driver=True
        z.ai.vehicle_crew.append(driver)

        for x in range(3):
            passenger=VehicleRole('passenger',z)
            passenger.is_passenger=True
            z.ai.vehicle_crew.append(passenger)

        z.ai.max_offroad_speed=177.6
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=800
        z.drag_coefficient=0.8
        z.frontal_area=3
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"volkswagen_type_82_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[65,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.ai.min_wheels_per_side_front=1
        z.ai.min_wheels_per_side_rear=1
        z.ai.max_wheels=4
        z.ai.max_spare_wheels=0
        z.ai.front_left_wheels.append(spawn_object(world,world_coords,"volkswagen_wheel",False))
        z.ai.front_right_wheels.append(spawn_object(world,world_coords,"volkswagen_wheel",False))
        z.ai.rear_left_wheels.append(spawn_object(world,world_coords,"volkswagen_wheel",False))
        z.ai.rear_right_wheels.append(spawn_object(world,world_coords,"volkswagen_wheel",False))
        z.ai.spare_wheels.append(spawn_object(world,world_coords,"volkswagen_wheel",False))
        z.ai.max_spare_wheels=1
        if random.randint(0,3)==1:
            mg=spawn_object(world,world_coords,'mg34',False)
            z.add_inventory(mg)
            z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
            z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
            z.add_inventory(spawn_object(world,world_coords,"german_mg_ammo_can",False))
            z.add_inventory(spawn_object(world,world_coords,"german_mg_ammo_can",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_german_military_equipment,False))
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='german_kubelwagen_camo':
        z=spawn_object(world,world_coords,'german_kubelwagen',False)
        z.image_list=['kubelwagen_camo','kubelwagen_camo_destroyed']

    elif object_type=='volkswagen_wheel':
        z=WorldObject(world,['volkswagen_wheel'],AIWheel)
        z.name='Volkswagen Wheel'
        z.ai.compatible_vehicles=['german_kubelwagen','german_kubelwagen_camo']


    elif object_type=='red_bicycle':
        z=WorldObject(world,['red_bicycle'],AIVehicle)
        z.name='red_bicycle'
        z.is_vehicle=True
        z.ai.is_transport=True
        z.ai.max_speed=177.6
        z.ai.max_offroad_speed=142.08
        z.ai.rotation_speed=50.

        driver=VehicleRole('driver',z)
        driver.is_driver=True
        driver.seat_visible=True
        z.ai.vehicle_crew.append(driver)

        z.ai.open_top=True
        z.collision_radius=50
        z.ai.engines.append(spawn_object(world,world_coords,"bicycle_pedals",False))
        z.weight=13
        z.drag_coefficient=0.8
        z.frontal_area=3
        z.ai.min_wheels_per_side_front=1
        z.ai.min_wheels_per_side_rear=0
        z.ai.max_wheels=4
        z.ai.max_spare_wheels=0
        z.ai.front_left_wheels.append(spawn_object(world,world_coords,"bicycle_wheel",False))
        z.ai.front_right_wheels.append(spawn_object(world,world_coords,"bicycle_wheel",False))
        z.rotation_angle=float(random.randint(0,359))

    elif object_type=='bicycle_wheel':
        z=WorldObject(world,['volkswagen_wheel'],AIWheel)
        z.name='Bicycle Wheel'
        z.ai.compatible_vehicles=['red_bicycle']

    elif object_type=='german_ju88':
        z=WorldObject(world,['ju88-winter-weathered','ju88-winter-weathered'],AIVehicle)
        z.name='Junkers Ju88'

        driver=VehicleRole('driver',z)
        driver.is_driver=True
        z.ai.vehicle_crew.append(driver)

        z.ai.max_speed=4736
        z.ai.max_offroad_speed=177.6
        z.ai.stall_speed=100
        z.ai.rotation_speed=50
        z.ai.acceleration=100
        z.ai.max_rate_of_climb=3
        z.ai.throttle_zero=False
        z.collision_radius=200
        mg=spawn_object(world,world_coords,'mg15',False)
        z.add_inventory(mg)
        z.ai.primary_weapon=mg
        z.add_inventory(spawn_object(world,world_coords,'mg15_drum_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mg15_drum_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mg15_drum_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mg15_drum_magazine',False))
        z.is_airplane=True
        z.is_vehicle=True 
        z.rotation_angle=float(random.randint(0,359))
        z.weight=9800
        z.drag_coefficient=0.8
        z.frontal_area=6
        # fuel tank ref : https://airpages.ru/eng/lw/ju88_2.shtml
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=415
        z.ai.fuel_tanks[1].volume=415
        z.ai.fuel_tanks[2].volume=425
        z.ai.fuel_tanks[3].volume=425
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        fill_container(world,z.ai.fuel_tanks[1],'gas_80_octane')
        fill_container(world,z.ai.fuel_tanks[2],'gas_80_octane')
        fill_container(world,z.ai.fuel_tanks[3],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"jumo_211",False))
        z.ai.engines.append(spawn_object(world,world_coords,"jumo_211",False))
        z.ai.engines[0].ai.exhaust_position_offset=[-10,65]
        z.ai.engines[1].ai.exhaust_position_offset=[-10,-75]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_24v",False))

    elif object_type=='german_fa_223_drache':
        z=WorldObject(world,['fa_223_drache','fa_223_drache'],AIVehicle)
        z.name='Focke Achgelis 223 Drache'

        driver=VehicleRole('driver',z)
        driver.is_driver=True
        z.ai.vehicle_crew.append(driver)
        
        z.ai.max_speed=4736
        z.ai.max_offroad_speed=177.6
        z.ai.stall_speed=100
        z.ai.rotation_speed=50
        z.ai.acceleration=100
        z.ai.max_rate_of_climb=3
        z.ai.throttle_zero=False
        z.collision_radius=200
        z.is_airplane=True
        z.is_vehicle=True 
        z.rotation_angle=float(random.randint(0,359))
        z.weight=9800
        z.drag_coefficient=0.8
        z.frontal_area=6
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=415
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"jumo_211",False))
        z.ai.engines[0].ai.exhaust_position_offset=[-10,65]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_24v",False))
        left_rotor=spawn_object(world,world_coords,'fa_223_rotor',True)
        left_rotor.ai.engine=z.ai.engines[0]
        left_rotor.ai.position_offset=[-50,-180]
        left_rotor.ai.rotor_rotation=0
        left_rotor.ai.vehicle=z
        z.ai.rotors.append(left_rotor)
        right_rotor=spawn_object(world,world_coords,'fa_223_rotor',True)
        right_rotor.ai.engine=z.ai.engines[0]
        right_rotor.ai.position_offset=[-50,180]
        right_rotor.ai.rotor_rotation=60
        right_rotor.ai.vehicle=z
        z.ai.rotors.append(right_rotor)

    elif object_type=='fa_223_rotor':
        z=WorldObject(world,['fa_223_drache_rotor','fa_223_drache_rotor'],AIRotor)
        z.name='FA 223 Drache Rotor'
        z.is_rotor=True

    # dani cat. wow!
    elif object_type=='dani':
        z=WorldObject(world,['dani'],AIDani)
        z.name='Dani'
        z.ai.speed=40
        z.collision_radius=15
        z.is_large_human_pickup=True
        z.large_pickup_offset=[-3,12]


    elif object_type=='civilian_man':
        z=WorldObject(world,['civilian_man','civilian_prone','civilian_dead'],AIHuman)
        z.name=engine.name_gen.get_name('civilian')
        z.ai.speed=30
        z.ai.morale=70
        z.collision_radius=15
        z.is_human=True
        if random.randint(0,1)==1:
            z.ai.wallet['Polish Zloty']=round(random.uniform(0.05,1.5),2)
        if random.randint(0,1)==1:
            z.ai.wallet['Soviet Ruble']=round(random.uniform(0.05,1.5),2)
        if random.randint(0,1)==1:
            z.ai.wallet['German Reichsmark']=round(random.uniform(0.05,1.5),2)

    elif object_type=='german_soldier':
        z=WorldObject(world,['german_soldier','german_soldier_prone','german_dead'],AIHuman)
        z.name=engine.name_gen.get_name('german')
        z.ai.speed=30
        z.collision_radius=15
        z.is_human=True
        z.ai.is_small_arms_trained=True

    elif object_type=='soviet_soldier':
        z=WorldObject(world,['soviet_soldier','soviet_soldier_prone','soviet_dead'],AIHuman)
        z.name=engine.name_gen.get_name('soviet')
        z.ai.speed=30
        z.collision_radius=15
        z.is_human=True
        z.ai.is_small_arms_trained=True

    elif object_type=='german_luftwaffe_ground_crew_kar98k':
        z=spawn_object(world,world_coords,'german_soldier',False)
        z.ai.morale=95
        z.image_list=['luftwaffe_ground_crew','luftwaffe_ground_crew_prone','luftwaffe_ground_crew_dead']
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'kar98k')

    elif object_type=='german_luftwaffe_ground_crew_mg15':
        z=spawn_object(world,world_coords,'german_soldier',False)
        z.ai.morale=95
        z.image_list=['luftwaffe_ground_crew','luftwaffe_ground_crew_prone','luftwaffe_ground_crew_dead']
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'mg15')

    elif object_type=='german_afv_crew_mp40':
        z=spawn_object(world,world_coords,'german_soldier',False)
        z.image_list=['german_afv_crew','german_afv_crew_prone','german_afv_crew_dead']
        z.ai.is_afv_trained=True
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        add_standard_loadout(z,world,'mp40')

    elif object_type=='german_afv_crew_pistol':
        z=spawn_object(world,world_coords,'german_soldier',False)
        z.image_list=['german_afv_crew','german_afv_crew_prone','german_afv_crew_dead']
        z.ai.is_afv_trained=True
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        add_random_pistol_to_inventory(z,world)

    elif object_type=='german_pistol_panzerschreck':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'panzerschreck')
        add_random_pistol_to_inventory(z,world)

    elif object_type=='german_mp40_panzerschreck':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'panzerschreck')
        add_standard_loadout(z,world,'mp40')

    elif object_type=='german_kar98k':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'kar98k')
        
    elif object_type=='german_kar98k_panzerfaust':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'kar98k')
        z.add_inventory(spawn_object(world,world_coords,'panzerfaust_60',False))
        
    elif object_type=='german_k43':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'k43')

    elif object_type=='german_k43_panzerfaust_100':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'k43')
        z.add_inventory(spawn_object(world,world_coords,'panzerfaust_100',False))
        
    elif object_type=='german_g41w':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'g41w')
        
    elif object_type=='german_mp40':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'mp40')

    elif object_type=='german_mp40_feldfunk':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'mp40')
        radio=spawn_object(world,world_coords,'radio_feldfu_b',True)
        z.ai.large_pickup=radio
    
    elif object_type=='german_mp40_feldfunk_charger':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'mp40')
        charger=spawn_object(world,world_coords,'feldfunk_battery_charger',True)
        z.ai.large_pickup=charger

    elif object_type=='german_mp40_molotov':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'mp40')
        z.add_inventory(spawn_object(world,world_coords,'molotov_cocktail',False))
        z.add_inventory(spawn_object(world,world_coords,'molotov_cocktail',False))

    elif object_type=='german_mp40_panzerfaust':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'mp40')
        z.add_inventory(spawn_object(world,world_coords,'panzerfaust_60',False))
        
    elif object_type=='german_mg34':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'mg34')
    
    elif object_type=='german_mg42':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'mg42')
        
    elif object_type=='german_stg44':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'stg44')

    elif object_type=='german_stg44_rpg43':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'stg44')
        z.add_inventory(spawn_object(world,world_coords,'rpg43',False))
        z.add_inventory(spawn_object(world,world_coords,'rpg43',False))
        
    elif object_type=='german_stg44_panzerfaust':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'stg44')
        z.add_inventory(spawn_object(world,world_coords,'panzerfaust_60',False))

    elif object_type=='german_stg44_panzerfaust_100':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'stg44')
        z.add_inventory(spawn_object(world,world_coords,'panzerfaust_100',False))
        
    elif object_type=='german_fg42-type2':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_standard_loadout(z,world,'fg42-type2')
    
    elif object_type=='german_medic':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        z.ai.is_medic=True

    elif object_type=='german_mechanic':
        z=spawn_object(world,world_coords,'german_soldier',False)
        add_standard_loadout(z,world,'standard_german_gear')
        add_random_pistol_to_inventory(z,world)
        z.ai.is_mechanic=True
        

    # --------- soviet types ----------------------------------------
    elif object_type=='soviet_afv_crew_tt33':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        z.ai.is_afv_trained=True
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        add_standard_loadout(z,world,'tt33')

    elif object_type=='soviet_mosin_nagant':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        add_standard_loadout(z,world,'mosin_nagant')
        
    elif object_type=='soviet_svt40':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        add_standard_loadout(z,world,'svt40')

    elif object_type=='soviet_svt40':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        add_standard_loadout(z,world,'svt40')

    elif object_type=='soviet_svt40_sniper':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        z.ai.is_expert_marksman=True
        z.add_inventory(spawn_object(world,[0,0],'svt40-sniper',False))
        for _ in range(6):
            z.add_inventory(spawn_object(world,[0,0],'svt40_magazine',False))
        
    elif object_type=='soviet_ppsh43':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        add_standard_loadout(z,world,'ppsh43')

    elif object_type=='soviet_ppsh41':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        add_standard_loadout(z,world,'ppsh41')

    elif object_type=='soviet_assault_engineer_ppsh43':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        add_standard_loadout(z,world,'ppsh43')
        z.add_inventory(spawn_object(world,world_coords,'sn_42_body_armor',False))
        z.add_inventory(spawn_object(world,world_coords,'rpg43',False))

    elif object_type=='soviet_ppsh43_rpg43':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        add_standard_loadout(z,world,'ppsh43')
        z.add_inventory(spawn_object(world,world_coords,'rpg43',False))
        z.add_inventory(spawn_object(world,world_coords,'rpg43',False))

    elif object_type=='soviet_ppsh43_molotov':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        add_standard_loadout(z,world,'ppsh43')
        z.add_inventory(spawn_object(world,world_coords,'molotov_cocktail',False))
        z.add_inventory(spawn_object(world,world_coords,'molotov_cocktail',False))

    elif object_type=='soviet_dp28':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        add_standard_loadout(z,world,'dp28')
        
    elif object_type=='soviet_tt33':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        add_standard_loadout(z,world,'tt33')

    elif object_type=='soviet_medic':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        z.ai.is_medic=True
    
    elif object_type=='soviet_mechanic':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        add_standard_loadout(z,world,'tt33')
        z.ai.is_mechanic=True

    elif object_type=='soviet_ptrs_41':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        add_standard_loadout(z,world,'standard_soviet_gear')
        add_standard_loadout(z,world,'ptrs_41')
        
    elif object_type=='civilian_big_cheese':
        # big cheese!
        z=spawn_object(world,world_coords,'civilian_man',False)
        z.name='big cheese'
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'camembert-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'camembert-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'camembert-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'camembert-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'camembert-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'mg34',False))
        z.add_inventory(spawn_object(world,world_coords,'mg34_drum_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'panzerfaust_60',False))
    
    elif object_type=='civilian_shovel_man':
        # a shovel enthusiast
        z=spawn_object(world,world_coords,'civilian_man',False)
        z.name='Mr. Shovel'
        z.add_inventory(spawn_object(world,world_coords,'coffee_tin',False))
        z.add_inventory(spawn_object(world,world_coords,'german_folding_shovel',False))
        z.add_inventory(spawn_object(world,world_coords,'german_field_shovel',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables_common,False))
    
    elif object_type=='brass':
        z=WorldObject(world,['brass'],AIAnimatedSprite)
        z.world_coords=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.name='brass'
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=150
        z.ai.rotation_speed=800
        z.ai.rotate_time_max=0.8
        z.ai.move_time_max=0.3
        z.ai.alive_time_max=300
        z.ai.self_remove=True
        z.ai.only_remove_when_not_visible=True
        z.no_save=True
    # steel bullet casing
    elif object_type=='steel_case':
        z=WorldObject(world,['steel_case'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='steel_case'
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=150
        z.ai.rotation_speed=800
        z.ai.rotate_time_max=0.8
        z.ai.move_time_max=0.3
        z.ai.alive_time_max=300
        z.ai.self_remove=True
        z.ai.only_remove_when_not_visible=True
        z.no_save=True
    elif object_type=='small_smoke':
        z=WorldObject(world,['small_smoke'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='small_smoke'
        z.minimum_visible_scale=0.2
        z.is_particle_effect=True
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=15
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=3
        z.ai.self_remove=True
        z.no_save=True
    elif object_type=='small_fire':
        z=WorldObject(world,['small_fire'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='small_fire'
        z.minimum_visible_scale=0.2
        z.is_particle_effect=True
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=15
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=3
        z.ai.self_remove=True
        z.no_save=True
    elif object_type=='small_explosion':
        z=WorldObject(world,['small_explosion'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='small_explosion'
        z.minimum_visible_scale=0.2
        z.is_particle_effect=True
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=15
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=3
        z.ai.self_remove=True
        z.no_save=True
    elif object_type=='small_flash':
        z=WorldObject(world,['explosion_flash'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='small_flash'
        z.minimum_visible_scale=0.2
        z.is_particle_effect=True
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=15
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=3
        z.ai.self_remove=True
        z.no_save=True
    elif object_type=='spark':
        z=WorldObject(world,['spark'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='spark'
        z.minimum_visible_scale=0.3
        z.is_particle_effect=True
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=random.randint(100,300)
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=3
        z.ai.self_remove=True
        z.no_save=True
    
    elif object_type=='blood_splatter':
        z=WorldObject(world,['blood_splatter'],AIAnimatedSprite)
        z.name='blood_splatter'
        z.minimum_visible_scale=0.2
        # not a particle effect so it gets positioned as a 
        # default 2, which is under the bodies (containers)
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=0
        z.ai.rotation_speed=0
        z.ai.rotate_time_max=0
        z.ai.move_time_max=0
        z.ai.alive_time_max=300
        z.ai.self_remove=True
        z.ai.only_remove_when_not_visible=True
        z.no_save=True

    elif object_type=='small_blood':
        z=WorldObject(world,['small_blood'],AIAnimatedSprite)
        z.name='small_blood'
        z.minimum_visible_scale=0.2
        z.is_particle_effect=True
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=0
        z.ai.rotation_speed=0
        z.ai.rotate_time_max=0
        z.ai.move_time_max=0
        z.ai.alive_time_max=300
        z.ai.self_remove=True
        z.ai.only_remove_when_not_visible=True
        z.no_save=True
           
    elif object_type=='dirt':
        z=WorldObject(world,['small_dirt'],AIAnimatedSprite)
        z.name='dirt'
        z.minimum_visible_scale=0.4
        z.is_particle_effect=True
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=0
        z.ai.rotation_speed=0
        z.ai.rotate_time_max=0
        z.ai.move_time_max=0
        z.ai.alive_time_max=75
        z.ai.self_remove=True
        z.ai.only_remove_when_not_visible=True
        z.no_save=True

    elif object_type=='tank_tracks':
        z=WorldObject(world,['tank_tracks'],AIAnimatedSprite)
        z.name='tank_tracks'
        z.static_render_level=True
        z.render_level=1
        z.minimum_visible_scale=0.4
        z.is_particle_effect=True
        z.rotation_angle=0
        z.ai.speed=0
        z.ai.rotation_speed=0
        z.ai.rotate_time_max=0
        z.ai.move_time_max=0
        z.ai.alive_time_max=75
        z.ai.self_remove=True
        z.ai.only_remove_when_not_visible=True
        z.no_save=True
    
    elif object_type=='brown_chair':
        z=WorldObject(world,['brown_chair'],AINone)
        z.name='brown_chair'
        z.minimum_visible_scale=0.4
        z.is_furniture=True
        z.is_large_human_pickup=True
        z.rotation_angle=float(random.randint(0,359))
        z.no_update=True
    elif object_type=='german_field_shovel':
        z=WorldObject(world,['german_field_shovel'],AIThrowable)
        z.name='german field shovel'
        z.minimum_visible_scale=0.4
        z.is_throwable=True
        z.ai.speed=112
        z.ai.max_speed=112
        z.ai.maxTime=2
        z.ai.range=310
        z.rotation_angle=float(random.randint(0,359)) 
    elif object_type=='german_folding_shovel':
        z=WorldObject(world,['german_folding_shovel'],AIThrowable)
        z.name='german folding shovel'
        z.minimum_visible_scale=0.4
        z.is_throwable=True
        z.ai.speed=112
        z.ai.max_speed=112
        z.ai.maxTime=2
        z.ai.range=310
        z.rotation_angle=float(random.randint(0,359))
    # https://en.wikipedia.org/wiki/Kharkiv_model_V-2
    elif object_type=='kharkiv_v2-34_engine':
        z=WorldObject(world,['deutz_diesel_65hp_engine'],AIEngine)
        z.name='Kharkiv V2-34 Engine'
        z.ai.fuel_type=['diesel']
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=505559.322
        z.rotation_angle=float(random.randint(0,359))
        z.weight=250 
    elif object_type=='deutz_diesel_65hp_engine':
        z=WorldObject(world,['deutz_diesel_65hp_engine'],AIEngine)
        z.name='Deutz 65 HP Diesel Engine'
        z.ai.fuel_type=['diesel']
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=65722.7
        z.rotation_angle=float(random.randint(0,359))
        z.weight=250 
    elif object_type=='volkswagen_type_82_engine':
        z=WorldObject(world,['volkswagen_type_82_engine'],AIEngine)
        z.name='Volkswagen Type 82 Engine'
        z.ai.fuel_type=['gas_80_octane']
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=25277.9
        z.rotation_angle=float(random.randint(0,359))
        z.weight=250
    elif object_type=='chrysler_flathead_straight_6_engine':
        z=WorldObject(world,['volkswagen_type_82_engine'],AIEngine)
        z.name='Chrysler Flathead Straight 6 Engine'
        z.ai.fuel_type=['gas_80_octane']
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=93022.91
        z.rotation_angle=float(random.randint(0,359))
        z.weight=250
    elif object_type=='maybach_hl42_engine':
        z=WorldObject(world,['maybach_hl42'],AIEngine)
        z.name='Maybach HL42 Engine'
        z.ai.fuel_type=['gas_80_octane']
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=93022.91
        z.rotation_angle=float(random.randint(0,359))
        z.weight=250
    elif object_type=='jumo_211':
        z=WorldObject(world,['jumo_211'],AIEngine)
        z.name='Jumo 211 Engine'
        z.ai.fuel_type=['gas_80_octane']
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=2549953.75 #based on 1000 hp
        z.rotation_angle=float(random.randint(0,359)) 
        z.weight=640
    elif object_type=='vehicle_fuel_tank':
        z=WorldObject(world,['vehicle_fuel_tank'],AIContainer)
        z.is_container=True
        z.volume=20
        z.name='vehicle_fuel_tank'
        z.world_builder_identity='vehicle_fuel_tank'
        z.rotation_angle=float(random.randint(0,359))
    elif object_type=='bicycle_pedals':
        z=WorldObject(world,['bicycle_pedals'],AIEngine)
        z.name='bicycle pedals'
        z.ai.internal_combustion=False
        z.ai.fuel_type='none'
        z.ai.fuel_consumption_rate=0
        z.ai.max_engine_force=131.44
        z.ai.engine_on=True
        z.rotation_angle=float(random.randint(0,359))
    elif object_type=='projectile':
        z=WorldObject(world,['projectile'],AIProjectile)
        z.name='projectile'
        z.ai.speed=1000.
        z.is_projectile=True
        z.no_save=True
    elif object_type=='gas_80_octane':
        z=WorldObject(world,['small_clear_spill'],AINone)
        z.name='gas_80_octane'
        z.is_liquid=True
        z.is_solid=False
        z.no_update=True
    elif object_type=='diesel':
        z=WorldObject(world,['small_clear_spill'],AINone)
        z.name='diesel'
        z.is_liquid=True
        z.is_solid=False
        z.no_update=True
    elif object_type=='water':
        z=WorldObject(world,['small_clear_spill'],AINone)
        z.name='water'
        z.is_liquid=True
        z.is_solid=False
        z.no_update=True
    elif object_type=='concrete_square':
        z=WorldObject(world,['concrete_square'],AINone)
        z.name='concrete_square'
        z.rotation_angle=0
        z.no_update=True
    elif object_type=='ground_cover':
        #z=WorldObject(world,['ground_dirt_vlarge'],AINone)
        z=WorldObject(world,['terrain_light_sand'],AINone)
        z.name='ground_dirt_vlarge'
        z.is_ground_texture=True
        z.rotation_angle=0
        z.no_update=True
    elif object_type=='terrain_mottled_transparent':
        z=WorldObject(world,['terrain_mottled_transparent'],AINone)
        z.name='ground_dirt_vlarge'
        z.is_ground_texture=True
        z.rotation_angle=0
        z.default_scale=1
        z.no_update=True
    elif object_type=='terrain_green':
        z=WorldObject(world,['terrain_green'],AINone)
        z.name='terrain_green'
        z.is_ground_texture=True
        z.rotation_angle=0
        z.default_scale=1
        z.no_update=True
    elif object_type=='wood_log':
        z=WorldObject(world,['wood_log'],AINone)
        z.name='wood_log'
        z.minimum_visible_scale=0.4
        z.is_large_human_pickup=True
        z.rotation_angle=float(random.randint(0,359))
        z.no_update=True
    elif object_type=='wood_quarter':
        z=WorldObject(world,['wood_log'],AINone)
        z.name='wood_log'
        z.minimum_visible_scale=0.4
        z.is_large_human_pickup=True
        z.rotation_angle=float(random.randint(0,359))
        z.no_update=True
    elif object_type=='coffee_beans':
        z=WorldObject(world,['coffee_beans'],AINone)
        z.name='coffee_beans'
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359))
        z.no_update=True
    elif object_type=='ground_coffee':
        z=WorldObject(world,['coffee_beans'],AINone)
        z.name='ground_coffee'
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359))
        z.no_update=True
    elif object_type=='coffee_grinder':
        z=WorldObject(world,['coffee_grinder'],AICoffeeGrinder)
        z.name='coffee_grinder'
        z.minimum_visible_scale=0.4
        z.rotation_angle=float(random.randint(0,359))
        z.no_update=True
    elif object_type=='bomb_sc250':
        z=WorldObject(world,['sc250'],AINone)
        z.name='bomb_sc250'
        z.weight=250
        z.rotation_angle=float(random.randint(0,359))
        z.no_update=True
    elif object_type=='grid_50_foot':
        z=WorldObject(world,['grid_50_foot'],AINone)
        z.name='grid_50_foot'
        z.weight=250
        z.rotation_angle=0
        z.no_update=True
    elif object_type=='battery_feldfunk_2v':
        z=WorldObject(world,['battery_vehicle_6v'],AIBattery)
        z.name='Feldfunk 2V battery'
        z.weight=3
        z.rotation_angle=float(random.randint(0,359))
    elif object_type=='battery_vehicle_6v':
        z=WorldObject(world,['battery_vehicle_6v'],AIBattery)
        z.name='battery_vehicle_6v'
        z.weight=25
        z.rotation_angle=float(random.randint(0,359)) 
    elif object_type=='battery_vehicle_24v':
        z=WorldObject(world,['battery_vehicle_6v'],AIBattery)
        z.name='battery_vehicle_24v'
        z.weight=25
        z.rotation_angle=float(random.randint(0,359))
    elif object_type=='sn_42_body_armor':
        z=WorldObject(world,['sn_42_body_armor'],AIWearable)
        z.name='SN 42 Body Armor'
        z.minimum_visible_scale=0.4
        z.weight=0.98
        z.is_wearable=True
        z.ai.wearable_region='upper_body'
        z.ai.armor['top']=[0,0,0]
        z.ai.armor['bottom']=[0,0,0]
        z.ai.armor['left']=[0,0,0]
        z.ai.armor['right']=[0,0,0]
        z.ai.armor['front']=[3,0,0]
        z.ai.armor['rear']=[0,0,0]
        z.rotation_angle=float(random.randint(0,359))
    elif object_type=='helmet_stahlhelm':
        z=WorldObject(world,['helmet_stahlhelm'],AIWearable)
        z.name='helmet_stahlhelm'
        z.minimum_visible_scale=0.4
        z.weight=0.98
        z.is_wearable=True
        z.ai.wearable_region='head'
        z.ai.armor['top']=[3,0,0]
        z.ai.armor['bottom']=[0,0,0]
        z.ai.armor['left']=[3,0,0]
        z.ai.armor['right']=[3,0,0]
        z.ai.armor['front']=[3,0,0]
        z.ai.armor['rear']=[3,0,0]
        z.rotation_angle=float(random.randint(0,359))
    elif object_type=='helmet_ssh40':
        z=WorldObject(world,['helmet_ssh40'],AIWearable)
        z.name='helmet_ssh40'
        z.minimum_visible_scale=0.4
        z.weight=0.98
        z.is_wearable=True
        z.ai.wearable_region='head'
        z.ai.armor['top']=[1.5,0,0]
        z.ai.armor['bottom']=[0,0,0]
        z.ai.armor['left']=[1.5,0,0]
        z.ai.armor['right']=[1.5,0,0]
        z.ai.armor['front']=[1.5,0,0]
        z.ai.armor['rear']=[1.5,0,0]
        z.rotation_angle=float(random.randint(0,359))
    elif object_type=='radio_feldfu_b':
        # ref https://feldfunker-la7sna.com/wehrm_foto.htm
        z=WorldObject(world,['radio_feldfunk'],AIRadio)
        z.name='Feldfunk.b'
        z.is_radio=True
        z.weight=15
        z.is_large_human_pickup=True
        #z.ai.frequency_range=[90.57,109.45]
        z.ai.frequency_range=[0,10]
        z.ai.battery=spawn_object(world,world_coords,"battery_feldfunk_2v",False)
        z.rotation_angle=float(random.randint(0,359)) 
    elif object_type=='feldfunk_battery_charger':
        # ref https://feldfunker-la7sna.com/wehrm_foto.htm
        z=WorldObject(world,['radio_feldfunk_charger'],AIRadio)
        z.name='Feldfunk battery charger'
        z.weight=15
        z.is_large_human_pickup=True
        z.rotation_angle=float(random.randint(0,359))
    elif object_type=='hit_marker':
        z=WorldObject(world,['hit_green','hit_orange'],AIHitMarker)
        z.name='Hit marker'
        z.minimum_visible_scale=0.2
        z.is_hit_marker=True
    elif object_type=='pinus_sylvestris':
        # scots pine
        z=WorldObject(world,['pinus_sylvestris'],AINone)
        z.name='pinus_sylvestris'
        z.weight=1000
        z.rotation_angle=float(random.randint(0,359))
        z.no_update=True

    else:
        print('!! Spawn Error: '+object_type+' is not recognized.')  

    # -- generic settings that apply to all --
    z.world_builder_identity=object_type
    # set world coords if they weren't already set
    if z.world_coords==[0,0]:
        z.world_coords=copy.copy(world_coords)

    # reset render level now that variables are set
    z.reset_render_level()
    if spawn :
        z.wo_start()
    return z

#------------------------------------------------------------------------------
def spawn_map_pointer(world,TARGET_COORDS,TYPE):
    if TYPE=='normal':
        z=WorldObject(world,['map_pointer_green'],AIMapPointer)
        z.ai.target_coords=TARGET_COORDS
        z.render_level=4
        z.is_map_pointer=True
        z.wo_start()
    if TYPE=='blue':
        z=WorldObject(world,['map_pointer_blue'],AIMapPointer)
        z.ai.target_coords=TARGET_COORDS
        z.render_level=4
        z.is_map_pointer=True
        z.wo_start()
    if TYPE=='orange':
        z=WorldObject(world,['map_pointer_orange'],AIMapPointer)
        z.ai.target_coords=TARGET_COORDS
        z.render_level=4
        z.is_map_pointer=True
        z.wo_start()

#------------------------------------------------------------------------------
# basically just a different kind of projectile
def spawn_shrapnel(world,world_coords,target_coords,ignore_list,projectile_type,min_time,max_time,originator,weapon):
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    # MOUSE_AIM bool as to whether to use mouse aim for calculations
    z=WorldObject(world,['shrapnel'],AIProjectile)
    z.name='shrapnel'
    z.world_coords=copy.copy(world_coords)
    z.ai.starting_coords=copy.copy(world_coords)
    z.ai.speed=300.
    z.ai.maxTime=random.uniform(min_time, max_time)
    z.is_projectile=True
    z.render_level=3
    z.ai.ignore_list=copy.copy(ignore_list)
    z.ai.projectile_type=projectile_type
    z.rotation_angle=engine.math_2d.get_rotation(world_coords,target_coords)
    z.heading=engine.math_2d.get_heading_vector(world_coords,target_coords)
    # increase the collision radius to make sure we get hits
    z.collision_radius=10
    z.ai.shooter=originator
    z.ai.weapon=weapon
    z.wo_start()

#------------------------------------------------------------------------------
def spawn_shrapnel_cloud(world,world_coords,amount,originator,weapon):
    ''' creates a shrapnel starburst pattern. used for grenades '''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    ignore_list=[]
    if world.friendly_fire_explosive is False:
        if originator.is_human:
            ignore_list+=originator.ai.squad.faction_tactical.allied_humans

    elif world.friendly_fire_explosive_squad is False:
        if originator.is_human:
            # just add the squad
            ignore_list+=originator.ai.squad.members

    for x in range(amount):
        target_coords=[float(random.randint(-150,150))+world_coords[0],float(random.randint(-150,150))+world_coords[1]]
        spawn_shrapnel(world,world_coords,target_coords,ignore_list,'shrapnel',0.1,0.4,originator,weapon)

#------------------------------------------------------------------------------
def spawn_smoke_cloud(world,world_coords,heading,amount=30):
    ''' spawn smoke cloud '''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel

    for x in range(amount):
        coords=[world_coords[0]+random.randint(-2,2),world_coords[1]+random.randint(-2,2)]
        z=spawn_object(world,coords,'small_smoke',True)
        z.heading=heading
        z.ai.speed=random.uniform(5,7)
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=random.uniform(2.5,3)

#------------------------------------------------------------------------------
def spawn_sparks(world,world_coords,amount=30):
    ''' spawn spark '''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel

    for x in range(amount):
        coords=[world_coords[0]+random.randint(-2,2),world_coords[1]+random.randint(-2,2)]
        z=spawn_object(world,coords,'spark',True)
        z.heading=engine.math_2d.get_heading_from_rotation(z.rotation_angle)
        z.ai.speed=random.uniform(110,130)
        z.ai.rotation_speed=0
        z.ai.rotate_time_max=0
        z.ai.move_time_max=0.91
        z.ai.alive_time_max=random.uniform(1.1,1.3)

#------------------------------------------------------------------------------
def spawn_heat_jet(world,world_coords,target_coords,AMOUNT,heat_projectile_type,originator,weapon):
    ''' creates a cone/line of shrapnel. used for panzerfaust'''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    # heat_projectile_type - a heat name from the projectile database that corresponds to the correct heat jet for the weapon
    for x in range(AMOUNT):
        target_coords=[float(random.randint(-5,5))+target_coords[0],float(random.randint(-5,5))+target_coords[1]]
        spawn_shrapnel(world,world_coords,target_coords,[],heat_projectile_type,0.1,0.3,originator,weapon)

# load squad data 
load_sqlite_squad_data()