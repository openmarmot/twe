
'''
module : world_builder.py
language : Python 3.x
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
from ai.ai_vehicle import AIVehicle
from ai.ai_human import AIHuman
from engine.world_object import WorldObject
from engine.world_area import WorldArea
from engine.map_object import MapObject
import engine.world_radio


# load AI 
from ai.ai_human import AIHuman
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

#global variables

# ------ object rarity lists -----------------------------------
list_consumables=['green_apple','potato','turnip','cucumber','pickle','adler-cheese','camembert-cheese'
,'champignon-cheese','karwendel-cheese','wine','schokakola']
list_consumables_common=['green_apple','potato','turnip','cucumber','pickle']
list_consumables_rare=['adler-cheese','camembert-cheese','champignon-cheese','karwendel-cheese','wine','beer']
list_consumables_ultra_rare=['schokakola']

list_household_items=['blue_coffee_cup','coffee_tin','coffee_grinder','pickle_jar']

list_guns=['kar98k','stg44','mp40','mg34','mosin_nagant','ppsh43','dp28','1911','ppk','tt33','g41w','k43','svt40','svt40-sniper','mg15','fg42-type1','fg42-type2']
list_guns_common=['kar98k','mosin_nagant','ppsh43','tt33','svt40']
list_guns_rare=['mp40','ppk','stg44','mg34','dp28','k43','g41w']
list_guns_ultra_rare=['fg42-type1','fg42-type2','svt40-sniper','1911','mg15']
list_german_guns=['kar98k','stg44','mp40','mg34','ppk','k43','g41w','fg42-type1','fg42-type2']

list_guns_rifles=['kar98k','mosin_nagant','g41w','k43','svt40','svt40-sniper']
list_guns_smg=['mp40','ppsh43']
list_guns_assault_rifles=['stg44']
list_guns_machine_guns=['mg34','dp28','mg15','fg42-type1','fg42-type2']
list_guns_pistols=['1911','ppk','tt33']

list_german_military_equipment=['german_folding_shovel','german_field_shovel']

list_vehicles_german=['kubelwagen','sd_kfz_251']
list_vehicles_soviet=['dodge_g505_wc']
list_vehicles_american=[]
list_vehicles_civilian=[]

list_medical=['bandage','german_officer_first_aid_kit']
list_medical_common=['bandage']
list_medical_rare=['german_officer_first_aid_kit']
list_medical_ultra_rare=[]
#----------------------------------------------------------------

# ------ variables that get pulled from sqlite -----------------------------------
loaded=False
soviet_squad_data={}
german_squad_data={}
american_squad_data=[]
civilian_squad_data={}

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
            
            wo.rotation_angle=map_object.rotation
            
            if map_object.name !='none' and map_object.name !='':
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
                    if already_exists==False:
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
    for b in world.wo_objects:
        # a couple objects we don't want to save
        if (b.is_projectile==False and b.is_map_pointer==False and
            b.can_be_deleted==False and b.is_particle_effect==False 
            and b.is_turret==False):
            # assemble inventory name list
            inventory=[]
            if hasattr(b.ai,'inventory'):
                for i in b.ai.inventory:
                    inventory.append(i.world_builder_identity)
            temp=MapObject(b.world_builder_identity,b.name,b.world_coords,0,inventory)
            map_square.map_objects.append(temp)



    # handle objects that exited the map




#------------------------------------------------------------------------------
def fill_container(world,CONTAINER,FILL_NAME):
    ''' fill container with an object (liquid)'''
    # CONTAINER - should be empty
    # FILL_NAME - name of object (liquid) to fill the container with 

    fill=spawn_object(world,[0,0],FILL_NAME,False)
    fill.volume=CONTAINER.volume
    # need something more clever here.. maybe a density value per object
    fill.weight=CONTAINER.volume
    CONTAINER.ai.inventory.append(fill)


#------------------------------------------------------------------------------
def generate_clutter(map_objects):
    '''generates and auto places small objects around the map'''
    # map_objects - array of map_objects
    # returns array of map_objects
    clutter=[]

    for b in map_objects:

        # industrial clutter
        if b.world_builder_identity=='warehouse':
            chance=random.randint(1,15)
            coords=[b.world_coords[0]+random.randint(-20,20),b.world_coords[1]+random.randint(-20,20)]
            rotation=random.randint(0,359)
            if chance==1 or chance==2:
                clutter.append(MapObject('brown_chair','brown chair',coords,rotation,[]))
            if chance==1 or chance==3 or chance==4:
                # some overlap
                clutter.append(MapObject('cupboard','cupboard',coords,rotation,[]))
            if chance==5:
                clutter.append(MapObject('wood_log','wood log',coords,rotation,[]))
            if chance==6:
                clutter.append(MapObject('barrel','barrel',coords,rotation,[]))
            if chance==7:
                clutter.append(MapObject('red_bicycle','red bicycle',coords,rotation,[]))
            if chance==8 or chance==9:
                clutter.append(MapObject('crate_random_consumables','crate',coords,rotation,[]))
            if chance==10 or chance==11:
                coords[0]+=random.randint(-50,50)
                coords[1]+=random.randint(-50,50)
                count=random.randint(1,6)
                rotation=random.choice([0,90,180,270])
                coord_list=engine.math_2d.get_column_coords(coords,80,count,rotation,2)
                for _ in range(count):
                    clutter.append(MapObject('concrete_square','concrete_square',coord_list.pop(),rotation,[]))

        # house clutter 
        elif b.world_builder_identity=='square_building':
            chance=random.randint(1,15)
            coords=[b.world_coords[0]+random.randint(-20,20),b.world_coords[1]+random.randint(-20,20)]
            rotation=random.randint(0,359)
            if chance==1 or chance==2:
                clutter.append(MapObject('brown_chair','brown chair',coords,rotation,[]))
            if chance==1 or chance==3 or chance==4:
                # some overlap
                clutter.append(MapObject('cupboard','cupboard',coords,rotation,[]))
            if chance==5:
                clutter.append(MapObject('wood_log','wood log',coords,rotation,[]))
            if chance==6:
                clutter.append(MapObject('barrel','barrel',coords,rotation,[]))
            if chance==7:
                clutter.append(MapObject('red_bicycle','red bicycle',coords,rotation,[]))

    # add some crates 
                
    # add some vehicles 
                
    return clutter

#------------------------------------------------------------------------------
def generate_civilians(map_objects):
    '''generates and returns a array of civilian map_objects'''
    civilians=[]

    for b in map_objects:
        if b.world_builder_identity=='warehouse':
            count=random.randint(0,10)
            for _ in range(count):
                coords=[b.world_coords[0]+random.randint(-20,20),b.world_coords[1]+random.randint(-20,20)]
                rotation=random.randint(0,359)
                civilians.append(MapObject('civilian_man','',coords,rotation,[]))

        elif b.world_builder_identity=='square_building':
            count=random.randint(1,3)
            for _ in range(count):
                coords=[b.world_coords[0]+random.randint(-20,20),b.world_coords[1]+random.randint(-20,20)]
                rotation=random.randint(0,359)
                civilians.append(MapObject('civilian_man','',coords,rotation,[]))

    # unique civilian big cheese
    if random.randint(1,100)<5:
        coords=[random.randint(-1000,1000),random.randint(-1000,1000)]
        rotation=random.randint(0,359)
        civilians.append(MapObject('big_cheese','',coords,rotation,[]))
        engine.log.add_data('note','big_cheese added to map',True)

    # unique civilian shovel_man
    if random.randint(1,100)<5:
        coords=[random.randint(-1000,1000),random.randint(-1000,1000)]
        rotation=random.randint(0,359)
        civilians.append(MapObject('shovel_man','',coords,rotation,[]))
        engine.log.add_data('note','shovel_man added to map',True)

    return civilians

#------------------------------------------------------------------------------
def generate_dynamic_world_areas(world):
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

    # now generate a couple based on the world objects

#------------------------------------------------------------------------------
def generate_world_area(world_coords,area_type,name):
    ''' generates the world areas on a NEW map. existing maps will pull this from the database '''
    # area_type town, airport, bunkers, field_depot, train_depot 
    map_objects=[]
    if area_type=='town':
        map_objects=generate_world_area_town(world_coords)
    elif area_type=='airport':
        map_objects=generate_world_area_airport(world_coords)
    elif area_type=='rail_yard':
        map_objects=generate_world_area_rail_yard(world_coords)
    elif area_type=='fuel_dump':
        count=random.randint(11,157)
        diameter=20
        rotation=0
        map_objects=generate_world_area_simple(world_coords,count,diameter,'55_gallon_drum','fuel drum',rotation)
    elif area_type=='german_ammo_dump':
        count=random.randint(11,157)
        diameter=20
        rotation=0
        map_objects=generate_world_area_simple(world_coords,count,diameter,'german_mg_ammo_can','German Ammo Can',rotation)
    elif area_type=='german_fuel_can_dump':
        count=random.randint(11,157)
        diameter=20
        rotation=0
        map_objects=generate_world_area_simple(world_coords,count,diameter,'german_fuel_can','German Fuel Can',rotation)
    else:
        engine.log.add_data('error','worldbuilder.generate_world_area type '+area_type+' not recognized',True)

    # add a world_area map object so the tactical ai can recognize it, and so it shows up on maps
    world_area=MapObject('world_area_'+area_type,name,world_coords,0,[])
    map_objects.append(world_area)

    return map_objects

#------------------------------------------------------------------------------
def generate_world_area_airport(world_coords):
    map_objects=[]
    # create a long runway 
    count=400
    coords=engine.math_2d.get_column_coords(world_coords,80,count,270,4)
    for _ in range(count):
        map_objects.append(MapObject('concrete_square','',coords.pop(),random.choice([0,90,180,270]),[]))

    # add hangars
    map_objects.append(MapObject('hangar','',[world_coords[0]+1500,world_coords[1]+600],0,[]))
    map_objects.append(MapObject('hangar','',[world_coords[0]+2500,world_coords[1]+600],0,[]))
    map_objects.append(MapObject('hangar','',[world_coords[0]+3500,world_coords[1]+600],0,[]))

    return map_objects

#------------------------------------------------------------------------------
def generate_world_area_simple(world_coords,count,diameter,world_builder_identity,name,rotation):
    '''generates a simple one object type world area '''
    # count: int
    # diameter : int - rough size of the object
    coords=engine.math_2d.get_grid_coords(world_coords,diameter,count)
    map_objects=[]
    for _ in range(count):
        map_objects.append(MapObject(world_builder_identity,name,coords.pop(),rotation,[]))
    
    return map_objects

#------------------------------------------------------------------------------
def generate_world_area_rail_yard(world_coords):
    engine.log.add_data('warn','world_builder.generate_world_area_rail_yard: not implemented',True)
    return []

#------------------------------------------------------------------------------
def generate_world_area_town(world_coords):
    count_warehouse=random.randint(1,5)
    count_building=random.randint(2,14)
    coords=engine.math_2d.get_grid_coords(world_coords,600,count_warehouse+count_building)
    map_objects=[]
    rotation=random.choice([0,90,180,270])
    for _ in range(count_warehouse):
        map_objects.append(MapObject('warehouse','a old warehouse',coords.pop(),rotation,[]))
    
    for _ in range(count_building):
        map_objects.append(MapObject('square_building','some sort of building',coords.pop(),rotation,[]))

    return map_objects

#------------------------------------------------------------------------------
def get_random_from_list(world,world_coords,OBJECT_LIST,SPAWN):
    ''' returns a random object from a list'''
    # OBJECT_LIST : a list of strings that correspond to an object_Type for the 
    # spawn_object function
    index=random.randint(0,len(OBJECT_LIST)-1)
    return spawn_object(world,world_coords,OBJECT_LIST[index],SPAWN)

#------------------------------------------------------------------------------
def get_squad_map_objects(squad_name):
    '''get a list of map objects that make up a squad'''
    members=[]
    if 'German' in squad_name:
        members=german_squad_data[squad_name]['members'].split(',')
    elif 'Soviet' in squad_name:
        members=soviet_squad_data[squad_name]['members'].split(',')
    else:
        engine.log.add_data('error','ai_faction_strategic.deploy_squad_to_map squad_name '+squad_name+' not recognized',True)

    # convert each member to a map_object
    map_objects=[]
    for b in members:
        map_objects.append(MapObject(b,'none',[0,0],0,[]))
    
    return map_objects

#------------------------------------------------------------------------------
def load_magazine(world,magazine):
    '''loads a magazine with bullets'''
    count=len(magazine.ai.projectiles)
    while count<magazine.ai.capacity:
        z=spawn_object(world,[0,0],'projectile',False)
        z.ai.projectile_type=magazine.ai.compatible_projectiles[0]
        magazine.ai.projectiles.append(z)

        count+=1

#------------------------------------------------------------------------------
def load_quick_battle(world,spawn_faction):
    ''' load quick battle. called by game menu'''

    map_objects=[]

    # generate towns
    town_count=4
    coord_list=engine.math_2d.get_random_constrained_coords([0,0],6000,5000,town_count)
    for _ in range(town_count):
        coords=coord_list.pop()
        name='Town' # should generate a interessting name
        map_objects+=generate_world_area(coords,'town',name)

    # generate clutter
    map_objects+=generate_clutter(map_objects)

    # generate civilians
    map_objects+=generate_civilians(map_objects)

    # -- initial troops --
    squads=[]
    squads+=['German 1944 Rifle'] * 2
    squads+=['German 1944 Panzergrenadier Mech'] * 2
    squads+=['German 1944 Fallschirmjager'] * 1
    squads+=['Soviet 1943 Rifle'] * 2
    squads+=['Soviet 1944 SMG'] * 1
    squads+=['Soviet 1944 Rifle Motorized'] * 2

    for squad in squads:
        map_objects+=get_squad_map_objects(squad)

    load_world(world,map_objects,spawn_faction)

#------------------------------------------------------------------------------
def load_sqlite_data():
    ''' load a bunch of data that i put in sqlite '''
    global loaded
    global soviet_squad_data
    global german_squad_data
    global american_squad_data
    global civilian_squad_data
    
    if loaded==False:
        soviet_squad_data=load_sqlite_squad_data('soviet')
        german_squad_data=load_sqlite_squad_data('german')
        american_squad_data=load_sqlite_squad_data('american')
        civilian_squad_data=load_sqlite_squad_data('civilian')

    else:
        print('Error : Projectile data is already loaded')

#------------------------------------------------------------------------------
def load_sqlite_squad_data(faction):
    '''builds a squad_data dictionary from sqlite data'''

    squad_data={}

    conn = sqlite3.connect('data/data.sqlite')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM squad_data WHERE faction=?",(faction,))
    
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

    return squad_data

#------------------------------------------------------------------------------
def load_world(world,map_objects,spawn_faction):
    '''coverts map_objects to world_objects and does everything necessary to load the world'''

    # convert map_objects to world_objects
    # note - this also spawns them and creates the world_area objects
    convert_map_objects_to_world_objects(world,map_objects)

    # generate some minor world areas for battle flow
    generate_dynamic_world_areas(world)

    # generation squads 
    world.create_squads()

    # give the vehicles initial positions
    world.position_vehicles()

    # print debug info
    world.log_world_data()

    # spawn player
    world.spawn_player(spawn_faction)

    # add ground cover. this will eventually go somewhere else
    # 50 results in about 24,000 world coords in any direction
    count=50
    size=1015
    coords=engine.math_2d.get_grid_coords([-(count*size)*0.5,-(count*size)*0.5],size,count*count)
    for _ in range(count*count):
        temp=spawn_object(world,coords.pop(),'ground_cover',True)
        temp.rotation_angle=random.choice([0,90,180,270])

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
# currently used for wrecks and bodies
def spawn_container(name,world_object,image_index):
    '''spawns a custom container'''
    # name 
    # world_object - the world_object that is being replaced
    # image_index - index of the image to be used - from the world object
    z=WorldObject(world_object.world,[world_object.image_list[image_index]],AIContainer)
    z.is_container=True
    z.name=name
    z.world_coords=world_object.world_coords
    z.rotation_angle=world_object.rotation_angle
    z.ai.inventory=world_object.ai.inventory
    z.world_builder_identity='skip'
    z.volume=world_object.volume
    z.weight=world_object.weight
    z.collision_radius=world_object.collision_radius
    z.wo_start()


#------------------------------------------------------------------------------
def spawn_drop_canister(world,world_coords,CRATE_TYPE):
    ''' generates different crate types with contents'''

    z=spawn_object(world,world_coords,'german_drop_canister',True)


    if CRATE_TYPE=='mixed_supply':
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_german_guns,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_german_guns,False))
        z.ai.inventory.append(spawn_object(world,world_coords,'panzerfaust',False))
        z.ai.inventory.append(spawn_object(world,world_coords,'panzerfaust',False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_medical,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_medical,False))

#------------------------------------------------------------------------------
def spawn_flash(world,world_coords,heading,amount=2):
    ''' spawn smoke cloud '''

    for x in range(amount):
        coords=[world_coords[0]+random.randint(-2,2),world_coords[1]+random.randint(-2,2)]
        z=spawn_object(world,coords,'small_flash',True)
        z.heading=heading
        z.ai.speed=random.uniform(9,11)
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=random.uniform(0.1,0.4)
  
#------------------------------------------------------------------------------
def spawn_object(world,world_coords,OBJECT_TYPE, SPAWN):
    '''returns new object. optionally spawns it in the world'''
    z=None
    if OBJECT_TYPE=='warehouse':
        z=WorldObject(world,['warehouse-outside','warehouse-inside'],AIBuilding)
        z.name='warehouse'
        z.collision_radius=200
        z.weight=10000
        z.is_building=True

    elif OBJECT_TYPE=='square_building':
        z=WorldObject(world,['square_building_outside','square_building_inside'],AIBuilding)
        z.name='square building'
        z.collision_radius=60
        z.weight=10000
        z.is_building=True
    
    elif OBJECT_TYPE=='hangar':
        z=WorldObject(world,['hangar_outside','hangar_inside'],AIBuilding)
        z.name='hangar'
        z.collision_radius=600
        z.weight=10000
        z.is_building=True

    elif OBJECT_TYPE=='green_apple':
        z=WorldObject(world,['green_apple'],AIConsumable)
        z.name='Green Apple'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-10 

    elif OBJECT_TYPE=='potato':
        z=WorldObject(world,['potato'],AIConsumable)
        z.name='potato'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-70
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-20  

    elif OBJECT_TYPE=='turnip':
        z=WorldObject(world,['turnip'],AIConsumable)
        z.name='turnip'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-60
        z.ai.thirst_effect=-8
        z.ai.fatigue_effect=-10  
    
    elif OBJECT_TYPE=='cucumber':
        z=WorldObject(world,['cucumber'],AIConsumable)
        z.name='cucumber'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-60
        z.ai.thirst_effect=-8
        z.ai.fatigue_effect=-10  

    elif OBJECT_TYPE=='pickle':
        z=WorldObject(world,['cucumber'],AIConsumable)
        z.name='pickle'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-60
        z.ai.thirst_effect=-8
        z.ai.fatigue_effect=-10 

    elif OBJECT_TYPE=='adler-cheese':
        z=WorldObject(world,['adler-cheese'],AIConsumable)
        z.name='Adler cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-200
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif OBJECT_TYPE=='camembert-cheese':
        z=WorldObject(world,['camembert-cheese'],AIConsumable)
        z.name='Camembert cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-250
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif OBJECT_TYPE=='champignon-cheese':
        z=WorldObject(world,['champignon-cheese'],AIConsumable)
        z.name='Champignon cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-300
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif OBJECT_TYPE=='karwendel-cheese':
        z=WorldObject(world,['karwendel-cheese'],AIConsumable)
        z.name='Karwendel cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-500
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif OBJECT_TYPE=='wine':
        z=WorldObject(world,['wine_bottle'],AIConsumable)
        z.name='wine'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=-500
        z.ai.fatigue_effect=50

    elif OBJECT_TYPE=='beer':
        z=WorldObject(world,['green_bottle'],AIConsumable)
        z.name='beer'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=-500
        z.ai.fatigue_effect=50   

    elif OBJECT_TYPE=='schokakola':
        z=WorldObject(world,['schokakola'],AIConsumable)
        z.name='scho-ka-kola'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=15
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=10
        z.ai.fatigue_effect=-250 
    elif OBJECT_TYPE=='bandage':
        z=WorldObject(world,['bandage'],AIMedical)
        z.name='bandage'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_medical=True
        z.ai.health_effect=50
        z.ai.hunger_effect=0
        z.ai.thirst_effect=0
        z.ai.fatigue_effect=0
    elif OBJECT_TYPE=='german_officer_first_aid_kit':
        z=WorldObject(world,['german_officer_first_aid_kit'],AIMedical)
        z.name='German Officer First Aid Kit'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_medical=True
        z.ai.health_effect=150
        z.ai.hunger_effect=0
        z.ai.thirst_effect=0
        z.ai.fatigue_effect=-300  

    elif OBJECT_TYPE=='german_fuel_can':
        z=WorldObject(world,['german_fuel_can'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.volume=20
        z.name='german_fuel_can'
        z.world_builder_identity='german_fuel_can'
        z.rotation_angle=float(random.randint(0,359))
        fill_container(world,z,'gas_80_octane')

    elif OBJECT_TYPE=='blue_coffee_cup':
        z=WorldObject(world,['blue_coffee_cup'],AIContainer)
        z.is_container=True
        z.volume=0.3
        z.name='blue_coffee_cup'
        z.world_builder_identity='blue_coffee_cup'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='55_gallon_drum':
        z=WorldObject(world,['55_gallon_drum'],AIContainer)
        z.is_container=True
        z.volume=208
        z.name='55_gallon_drum'
        z.collision_radius=15
        z.world_builder_identity='55_gallon_drum'
        z.rotation_angle=float(random.randint(0,359))
        z.volume=208.2
        fill_container(world,z,'gas_80_octane')

    elif OBJECT_TYPE=='barrel':
        z=WorldObject(world,['barrel'],AIContainer)
        z.is_container=True
        z.volume=208
        z.name='barrel'
        z.collision_radius=15
        z.world_builder_identity='barrel'
        z.rotation_angle=float(random.randint(0,359))
        if random.randint(0,1)==1:
            fill_container(world,z,'water')

    elif OBJECT_TYPE=='german_mg_ammo_can':
        z=WorldObject(world,['german_mg_ammo_can'],AIContainer)
        z.is_ammo_container=True
        z.is_large_human_pickup=True
        z.name='german_mg_ammo_can'
        z.world_builder_identity='german_mg_ammo_can'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='german_drop_canister':
        z=WorldObject(world,['german_drop_canister'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.name='german drop canister'
        z.collision_radius=20
        z.world_builder_identity='german_drop_canister'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='crate':
        z=WorldObject(world,['crate'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.name='crate'
        z.collision_radius=20
        z.world_builder_identity='crate'
        z.rotation_angle=float(random.randint(0,359))
        z.volume=100
    
    elif OBJECT_TYPE=='crate_mp40':
        z=spawn_object(world,world_coords,'crate',False)
        z.world_builder_identity='crate_mp40'
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

    elif OBJECT_TYPE=='crate_random_consumables':
        z=spawn_object(world,world_coords,'small_crate',False)
        z.world_builder_identity='crate_random_consumables'
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))
        z.add_inventory(spawn_object(world,world_coords,random.choice(list_consumables),False))


    elif OBJECT_TYPE=='small_crate':
        z=WorldObject(world,['small_crate'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.name='small_crate'
        z.collision_radius=20
        z.world_builder_identity='small_crate'
        z.rotation_angle=float(random.randint(0,359))
        z.volume=100

    elif OBJECT_TYPE=='cupboard':
        z=WorldObject(world,['cupboard'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.name='cupboard'
        z.collision_radius=20
        z.world_builder_identity='cupboard'
        z.rotation_angle=float(random.randint(0,359))
        z.volume=100

        if random.randint(0,1)==1:
            z.ai.inventory.append(get_random_from_list(world,world_coords,list_household_items,False))
            z.ai.inventory.append(get_random_from_list(world,world_coords,list_household_items,False))
        if random.randint(0,1)==1:  
            z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables,False))


    elif OBJECT_TYPE=='coffee_tin':
        z=WorldObject(world,['coffee_tin'],AIContainer)
        z.is_container=True
        z.volume=1
        z.name='coffee_tin'
        z.world_builder_identity='coffee_tin'
        z.rotation_angle=float(random.randint(0,359))
        contents='coffee_beans'
        if random.randint(0,1)==1:
            contents='ground_coffee'
        fill_container(world,z,contents)

    elif OBJECT_TYPE=='jar':
        z=WorldObject(world,['jar'],AIContainer)
        z.is_container=True
        z.volume=1
        z.name='jar'
        z.world_builder_identity='jar'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='pickle_jar':
        z=spawn_object(world,world_coords,'jar',False)
        z.name='pickle jar'
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))

    elif OBJECT_TYPE=='panzerfaust':
        z=WorldObject(world,['panzerfaust','panzerfaust_empty'],AIGun)
        z.name='panzerfaust'
        z.ai.speed=300
        z.is_handheld_antitank=True
        z.ai.magazine=spawn_object(world,world_coords,'panzerfaust_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=0
        z.ai.flight_time=2
        z.ai.range=700
        z.ai.type='antitank launcher'
        z.ai.smoke_on_fire=True
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='panzerfaust_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='panzerfaust_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['panzerfaust']
        z.ai.compatible_projectiles=['panzerfaust_60']
        z.ai.capacity=1
        z.ai.removable=False
        z.rotation_angle=float(random.randint(0,359))
        p=spawn_object(world,world_coords,'projectile',False)
        p.image_list=['panzerfaust_warhead']
        p.ai.projectile_type='panzerfaust_60'
        z.ai.projectiles.append(p)

    elif OBJECT_TYPE=='model24':
        z=WorldObject(world,['model24'],AIThrowable)
        z.name='model24'
        z.is_grenade=True
        z.is_throwable=True
        z.ai.explosive=True
        z.ai.speed=112
        z.ai.max_speed=112
        z.ai.maxTime=3.0
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mp40':
        z=WorldObject(world,['mp40'],AIGun)
        z.name='mp40'
        z.world_builder_identity='gun_mp40'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'mp40_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=7
        z.ai.flight_time=2
        z.ai.range=700
        z.ai.type='submachine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mp40_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='mp40_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mp40']
        z.ai.compatible_projectiles=['9mm_124','9mm_115','9mm_ME']
        z.ai.capacity=32
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='ppsh43':
        z=WorldObject(world,['ppsh43'],AIGun)
        z.name='ppsh43'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'ppsh43_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=7
        z.ai.flight_time=2
        z.ai.range=700
        z.ai.type='submachine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='ppsh43_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='ppsh43_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['ppsh43']
        z.ai.compatible_projectiles=['7.62x25']
        z.ai.capacity=35
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='stg44':
        z=WorldObject(world,['stg44'],AIGun)
        z.name='stg44'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'stg44_magazine',False)
        z.ai.rate_of_fire=0.1
        z.ai.reload_speed=7
        z.ai.flight_time=2.5
        z.ai.range=800
        z.ai.type='assault rifle'
        z.rotation_angle=float(random.randint(0,359))
    
    elif OBJECT_TYPE=='stg44_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='stg44_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['stg44']
        z.ai.compatible_projectiles=['7.92x33_SME']
        z.ai.capacity=30
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='dp28':
        z=WorldObject(world,['dp28'],AIGun)
        z.name='dp28'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'dp28_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=30
        z.ai.flight_time=3.5
        z.ai.range=800
        z.ai.type='machine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='dp28_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='dp28_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['dp28']
        z.ai.compatible_projectiles=['7.62x54_L','7.62x54_D']
        z.ai.capacity=47
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='ppk':
        z=WorldObject(world,['ppk'],AIGun)
        z.name='ppk'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'ppk_magazine',False)
        z.ai.rate_of_fire=0.7
        z.ai.reload_speed=5
        z.ai.flight_time=1
        z.ai.range=380
        z.ai.type='pistol'
        z.rotation_angle=float(random.randint(0,359))

    # NOTE - this should be 32 ACP or something
    elif OBJECT_TYPE=='ppk_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='ppk_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['ppk']
        z.ai.compatible_projectiles=['9mm_ME']
        z.ai.capacity=8
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='tt33':
        z=WorldObject(world,['tt33'],AIGun)
        z.name='tt33'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'tt33_magazine',False)
        z.ai.rate_of_fire=0.9
        z.ai.reload_speed=5
        z.ai.flight_time=1
        z.ai.range=380
        z.ai.type='pistol'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='tt33_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='tt33_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['tt33']
        z.ai.compatible_projectiles=['7.62x25']
        z.ai.capacity=8
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='1911':
        z=WorldObject(world,['1911'],AIGun)
        z.name='1911'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'1911_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=5
        z.ai.flight_time=1
        z.ai.range=380
        z.ai.type='pistol'
        z.rotation_angle=float(random.randint(0,359))
    
    elif OBJECT_TYPE=='1911_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='1911_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['1911']
        z.ai.compatible_projectiles=['45acp']
        z.ai.capacity=7
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)


    elif OBJECT_TYPE=='mg34':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='mg34'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'mg34_drum_magazine',False)
        z.ai.rate_of_fire=0.05
        z.ai.reload_speed=13
        z.ai.flight_time=3.5
        z.ai.range=850
        z.ai.type='machine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mg34_drum_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='mg34_drum_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mg34']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=50
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='37mm_m1939_k61':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='37mm_m1939_k61'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'37mm_m1939_k61_magazine',False)
        z.ai.rate_of_fire=0.9
        z.ai.reload_speed=13
        z.ai.flight_time=3.5
        z.ai.range=850
        z.ai.type='automatic cannon'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='37mm_m1939_k61_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='37mm_m1939_k61_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['37mm_m1939_k61']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=5
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='mg15':
        z=WorldObject(world,['mg15'],AIGun)
        z.name='mg15'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'mg15_drum_magazine',False)
        z.ai.rate_of_fire=0.06
        z.ai.reload_speed=13
        z.ai.flight_time=3.5
        z.ai.range=850
        z.ai.type='machine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mg15_drum_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='mg15_drum_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mg15']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=75
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='kar98k':
        z=WorldObject(world,['kar98k'],AIGun)
        z.name='kar98k'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'kar98k_magazine',False)
        z.ai.rate_of_fire=1.1
        z.ai.reload_speed=10
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='rifle'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='kar98k_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='kar98k_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['kar98k']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=5
        z.ai.removable=False
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='g41w':
        z=WorldObject(world,['g41w'],AIGun)
        z.name='g41w'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'g41w_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='semi auto rifle'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='g41w_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='g41w_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['g41w']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=10
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='k43':
        z=WorldObject(world,['k43'],AIGun)
        z.name='k43'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'k43_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='semi auto rifle'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='k43_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='k43_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['k43']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=10
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='fg42-type1':
        z=WorldObject(world,['fg42-type1'],AIGun)
        z.name='fg42-type1'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'fg42_type1_magazine',False)
        z.ai.rate_of_fire=0.06
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='machine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='fg42_type1_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='fg42_type1_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['fg42-type1']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=20
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='fg42-type2':
        z=WorldObject(world,['fg42-type2'],AIGun)
        z.name='fg42-type2'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'fg42_type2_magazine',False)
        z.ai.rate_of_fire=0.08
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='machine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='fg42_type2_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='fg42_type2_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['fg42-type2']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=20
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='mosin_nagant':
        z=WorldObject(world,['mosin_nagant'],AIGun)
        z.name='mosin_nagant'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'mosin_magazine',False)
        z.ai.rate_of_fire=1.1
        z.ai.reload_speed=11
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='rifle'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mosin_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='mosin_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mosin_nagant']
        z.ai.compatible_projectiles=['7.62x54_L','7.62x54_D']
        z.ai.capacity=5
        z.ai.removable=False
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)
    
    elif OBJECT_TYPE=='svt40':
        z=WorldObject(world,['svt40'],AIGun)
        z.name='svt40'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'svt40_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='semi auto rifle'
        z.ai.projectile_type='7.62x54_L'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='svt40_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='svt40_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['svt40','svt40-sniper']
        z.ai.compatible_projectiles=['7.62x54_L','7.62x54_D']
        z.ai.capacity=10
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='svt40-sniper':
        z=WorldObject(world,['svt40-sniper'],AIGun)
        z.name='svt40-sniper'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'svt40_magazine',False)
        z.ai.mag_capacity=10
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=8
        z.ai.flight_time=3.5
        z.ai.range=850
        z.ai.type='semi auto rifle'
        z.ai.projectile_type='7.62x54_L'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='dodge_g505_wc':
        # ref : https://truck-encyclopedia.com/ww2/us/Dodge-WC-3-4-tons-series.php
        # ref : https://truck-encyclopedia.com/ww2/us/dodge-WC-62-63-6x6.php
        z=WorldObject(world,['dodge_g505_wc','dodge_g505_wc'],AIVehicle)
        z.name='Dodge G505 WC Truck'
        z.is_vehicle=True
        z.ai.max_occupants=10
        z.ai.max_speed=200
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=2380
        z.rolling_resistance=0.03
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

    elif OBJECT_TYPE=='sd_kfz_251':
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['sd_kfz_251','sd_kfz_251'],AIVehicle)
        z.name='Sd.Kfz.251'
        z.is_vehicle=True
        z.ai.armor_thickness=13
        z.ai.max_occupants=10
        z.ai.max_speed=200
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=7800
        z.rolling_resistance=0.03
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
        turret=spawn_object(world,world_coords,'sd_kfz_251_mg34_turret',True)
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z
        # turret ammo, temporary 
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,'radio_feldfu_b',False))

        
    elif OBJECT_TYPE=='sd_kfz_251_mg34_turret':
        # !! note - turrets should be spawned with SPAWN TRUE as they are always in world
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['sd_kfz_251_mg34_turret','sd_kfz_251_mg34_turret'],AITurret)
        z.name='Sd.Kfz.251 MG34 Turret'
        z.is_turret=True
        z.ai.position_offset=[-10,0]
        z.ai.rotation_range=[-20,20]
        z.ai.primary_weapon=spawn_object(world,world_coords,'mg34',False)
        z.ai.primary_weapon.ai.equipper=z

    elif OBJECT_TYPE=='37mm_m1939_61k_aa_gun_carriage':
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['zu_7_carriage','zu_7_carriage'],AIVehicle)
        z.name='37mm_m1939_61k_aa_gun'
        z.is_vehicle=True
        z.ai.armor_thickness=0
        z.ai.max_occupants=2
        z.ai.max_speed=2
        z.ai.open_top=True
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=7800
        z.rolling_resistance=0.03
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.rotation_angle=float(random.randint(0,359))
        turret=spawn_object(world,world_coords,'37mm_m1939_61k_turret',True)
        for b in range(15):
            z.add_inventory(spawn_object(world,world_coords,"37mm_m1939_k61_magazine",False))
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z

    elif OBJECT_TYPE=='37mm_m1939_61k_turret':
        # !! note - turrets should be spawned with SPAWN TRUE as they are always in world
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['37mm_m1939_61k_turret','37mm_m1939_61k_turret'],AITurret)
        z.name='37mm_m1939_61k_turret'
        z.is_turret=True
        z.ai.position_offset=[-10,0]
        z.ai.rotation_range=[-360,360]
        z.ai.primary_weapon=spawn_object(world,world_coords,'37mm_m1939_k61',False)
        z.ai.primary_weapon.ai.equipper=z

  
    elif OBJECT_TYPE=='kubelwagen':
        z=WorldObject(world,['kubelwagen','kubelwagen_destroyed'],AIVehicle)
        z.name='kubelwagen'
        z.is_vehicle=True
        z.ai.max_speed=200
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=800
        z.rolling_resistance=0.015
        z.drag_coefficient=0.8
        z.frontal_area=3
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"volkswagen_type_82_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[65,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
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
        z.add_inventory(spawn_object(world,world_coords,'radio_feldfu_b',False))
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='red_bicycle':
        # note second image is used for the wreck..
        z=WorldObject(world,['red_bicycle','red_bicycle'],AIVehicle)
        z.name='red_bicycle'
        z.is_vehicle=True
        z.ai.max_speed=100
        z.ai.rotation_speed=50.
        z.ai.max_occupants=1
        z.ai.open_top=True
        z.collision_radius=50
        z.ai.engines.append(spawn_object(world,world_coords,"bicycle_pedals",False))
        z.weight=13
        z.rolling_resistance=0.015
        z.drag_coefficient=0.8
        z.frontal_area=3

        if random.randint(0,3)==1:
            z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='ju88':
        z=WorldObject(world,['ju88-winter-weathered','ju88-winter-weathered'],AIVehicle)
        z.name='Junkers Ju88'
        z.ai.max_speed=500
        z.ai.stall_speed=100
        z.ai.rotation_speed=50
        z.ai.acceleration=100
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
        z.rolling_resistance=0.015
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

    elif OBJECT_TYPE=='civilian_man':
        z=WorldObject(world,['civilian_man','civilian_prone','civilian_dead'],AIHuman)
        z.name=engine.name_gen.get_name('civilian')
        z.ai.speed=float(random.randint(10,25))
        z.collision_radius=10
        z.is_human=True
        z.is_civilian=True

    elif OBJECT_TYPE=='german_soldier':
        z=WorldObject(world,['german_soldier','german_soldier_prone','german_dead'],AIHuman)
        z.name=engine.name_gen.get_name('german')
        z.ai.speed=float(random.randint(20,25))
        z.collision_radius=10
        z.is_human=True
        z.is_soldier=True
        z.is_german=True

    elif OBJECT_TYPE=='soviet_soldier':
        z=WorldObject(world,['soviet_soldier','soviet_soldier_prone','soviet_dead'],AIHuman)
        z.name=engine.name_gen.get_name('soviet')
        z.ai.speed=float(random.randint(20,25))
        z.collision_radius=10
        z.is_human=True
        z.is_soldier=True
        z.is_soviet=True

    elif OBJECT_TYPE=='german_kar98k':
        z=spawn_object(world,world_coords,'german_soldier',False)
        z.world_builder_identity='german_kar98k'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        
    elif OBJECT_TYPE=='german_kar98k_panzerfaust':
        z=spawn_object(world,world_coords,'german_soldier',False)
        z.world_builder_identity='german_kar98k'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'panzerfaust',False))
        
    elif OBJECT_TYPE=='german_k43':
        z=spawn_object(world,world_coords,'german_soldier',False)
        z.world_builder_identity='german_k43'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'k43',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'k43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'k43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'k43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'k43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'k43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'k43_magazine',False))
        
    elif OBJECT_TYPE=='german_g41w':
        z=spawn_object(world,world_coords,'german_soldier',False)
        z.world_builder_identity='german_g41w'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w_magazine',False))
        
    elif OBJECT_TYPE=='german_mp40':
        z=spawn_object(world,world_coords,'german_soldier',False)
        z.world_builder_identity='german_mp40'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        
    elif OBJECT_TYPE=='german_mg34':
        z=spawn_object(world,world_coords,'german_soldier',False)
        z.world_builder_identity='german_mg34'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'mg34',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'mg34_drum_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mg34_drum_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mg34_drum_magazine',False))
        
    elif OBJECT_TYPE=='german_stg44':
        z=spawn_object(world,world_coords,'german_soldier',False)
        z.world_builder_identity='german_stg44'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        
    elif OBJECT_TYPE=='german_stg44_panzerfaust':
        z=spawn_object(world,world_coords,'german_soldier',False)
        z.world_builder_identity='german_stg44'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'panzerfaust',False))
        
    elif OBJECT_TYPE=='german_fg42-type2':
        z=spawn_object(world,world_coords,'german_soldier',False)
        z.world_builder_identity='german_fg42-type2'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42-type2',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42_type2_magazine',False))
        

    # --------- soviet types ----------------------------------------
    elif OBJECT_TYPE=='soviet_mosin_nagant':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        z.world_builder_identity='soviet_mosin_nagant'
        z.add_inventory(spawn_object(world,world_coords,'helmet_ssh40',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_nagant',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_magazine',False))
        
    elif OBJECT_TYPE=='soviet_svt40':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        z.world_builder_identity='soviet_svt40'
        z.add_inventory(spawn_object(world,world_coords,'helmet_ssh40',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40_magazine',False))
        
    elif OBJECT_TYPE=='soviet_ppsh43':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        z.world_builder_identity='soviet_ppsh43'
        z.add_inventory(spawn_object(world,world_coords,'helmet_ssh40',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43_magazine',False))
        
    elif OBJECT_TYPE=='soviet_dp28':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        z.world_builder_identity='soviet_dp28'
        z.add_inventory(spawn_object(world,world_coords,'helmet_ssh40',False))
        z.add_inventory(spawn_object(world,world_coords,'dp28',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'dp28_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'dp28_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'dp28_magazine',False))
        
    elif OBJECT_TYPE=='soviet_tt33':
        z=spawn_object(world,world_coords,'soviet_soldier',False)
        z.world_builder_identity='soviet_tt33'
        z.add_inventory(spawn_object(world,world_coords,'helmet_ssh40',False))
        z.add_inventory(spawn_object(world,world_coords,'tt33',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'tt33_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'tt33_magazine',False)) 
        
    elif OBJECT_TYPE=='big_cheese':
        # big cheese!
        z=spawn_object(world,world_coords,'civilian_man',False)
        z.ai.health*=2
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
        z.add_inventory(spawn_object(world,world_coords,'panzerfaust',False))
    
    elif OBJECT_TYPE=='shovel_man':
        # a shovel enthusiast
        z=spawn_object(world,world_coords,'civilian_man',False)
        z.ai.health*=2
        z.name='Mr. Shovel'
        z.add_inventory(spawn_object(world,world_coords,'coffee_tin',False))
        z.add_inventory(spawn_object(world,world_coords,'german_folding_shovel',False))
        z.add_inventory(spawn_object(world,world_coords,'german_field_shovel',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables_common,False))
    
    elif OBJECT_TYPE=='brass':
        z=WorldObject(world,['brass'],AIAnimatedSprite)
        z.world_coords=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.name='brass'
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=150
        z.ai.rotation_speed=800
        z.ai.rotate_time_max=0.8
        z.ai.move_time_max=0.3
        z.ai.alive_time_max=1
        z.can_be_deleted=True  
    # steel bullet casing
    elif OBJECT_TYPE=='steel_case':
        z=WorldObject(world,['steel_case'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='steel_case'
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=150
        z.ai.rotation_speed=800
        z.ai.rotate_time_max=0.8
        z.ai.move_time_max=0.3
        z.ai.alive_time_max=1
        z.can_be_deleted=True
    elif OBJECT_TYPE=='small_smoke':
        z=WorldObject(world,['small_smoke'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='small_smoke'
        z.is_particle_effect=True
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=15
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=3
        z.ai.self_remove=True
        z.can_be_deleted=True
    elif OBJECT_TYPE=='small_flash':
        z=WorldObject(world,['explosion_flash'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='small_flash'
        z.is_particle_effect=True
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=15
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=3
        z.ai.self_remove=True
        z.can_be_deleted=True
    elif OBJECT_TYPE=='spark':
        z=WorldObject(world,['spark'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='spark'
        z.is_particle_effect=True
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=random.randint(100,300)
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=3
        z.ai.self_remove=True
        z.can_be_deleted=True 
    
    elif OBJECT_TYPE=='blood_splatter':
        z=WorldObject(world,['blood_splatter'],AINone)
        z.name='blood_splatter'
        z.rotation_angle=float(random.randint(0,359))
        z.can_be_deleted=True 

    elif OBJECT_TYPE=='small_blood':
        z=WorldObject(world,['small_blood'],AINone)
        z.name='small_blood'
        z.rotation_angle=float(random.randint(0,359))
        z.can_be_deleted=True 
           
    elif OBJECT_TYPE=='dirt':
        z=WorldObject(world,['small_dirt'],AINone)
        z.name='dirt'
        z.rotation_angle=float(random.randint(0,359))
        z.can_be_deleted=True
    
    elif OBJECT_TYPE=='brown_chair':
        z=WorldObject(world,['brown_chair'],AINone)
        z.name='brown_chair'
        z.is_furniture=True
        z.is_large_human_pickup=True
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='german_field_shovel':
        z=WorldObject(world,['german_field_shovel'],AIThrowable)
        z.name='german field shovel'
        z.is_throwable=True
        z.ai.speed=112
        z.ai.max_speed=112
        z.ai.maxTime=2
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='german_folding_shovel':
        z=WorldObject(world,['german_folding_shovel'],AIThrowable)
        z.name='german folding shovel'
        z.is_throwable=True
        z.ai.speed=112
        z.ai.max_speed=112
        z.ai.maxTime=2
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='volkswagen_type_82_engine':
        z=WorldObject(world,['volkswagen_type_82_engine'],AIEngine)
        z.name='Volkswagen Type 82 Engine'
        z.ai.fuel_type=['gas_80_octane']
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=25277.9
        z.rotation_angle=float(random.randint(0,359))
        z.weight=250
    elif OBJECT_TYPE=='chrysler_flathead_straight_6_engine':
        z=WorldObject(world,['volkswagen_type_82_engine'],AIEngine)
        z.name='Chrysler Flathead Straight 6 Engine'
        z.ai.fuel_type=['gas_80_octane']
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=93022.91
        z.rotation_angle=float(random.randint(0,359))
        z.weight=250
    elif OBJECT_TYPE=='maybach_hl42_engine':
        z=WorldObject(world,['maybach_hl42'],AIEngine)
        z.name='Maybach HL42 Engine'
        z.ai.fuel_type=['gas_80_octane']
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=93022.91
        z.rotation_angle=float(random.randint(0,359))
        z.weight=250
    elif OBJECT_TYPE=='jumo_211':
        z=WorldObject(world,['jumo_211'],AIEngine)
        z.name='Jumo 211 Engine'
        z.ai.fuel_type=['gas_80_octane']
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=2549953.75 #based on 1000 hp
        z.rotation_angle=float(random.randint(0,359)) 
        z.weight=640
    elif OBJECT_TYPE=='vehicle_fuel_tank':
        z=WorldObject(world,['vehicle_fuel_tank'],AIContainer)
        z.is_container=True
        z.volume=20
        z.name='vehicle_fuel_tank'
        z.world_builder_identity='vehicle_fuel_tank'
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='bicycle_pedals':
        z=WorldObject(world,['bicycle_pedals'],AIEngine)
        z.name='bicycle pedals'
        z.ai.internal_combustion=False
        z.ai.fuel_type='none'
        z.ai.fuel_consumption_rate=0
        z.ai.max_engine_force=131.44
        z.ai.engine_on=True
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='projectile':
        z=WorldObject(world,['projectile'],AIProjectile)
        z.name='projectile'
        z.ai.speed=350.
        z.is_projectile=True
    elif OBJECT_TYPE=='gas_80_octane':
        z=WorldObject(world,['small_clear_spill'],AINone)
        z.name='gas_80_octane'
        z.is_liquid=True
        z.is_solid=False
    elif OBJECT_TYPE=='water':
        z=WorldObject(world,['small_clear_spill'],AINone)
        z.name='water'
        z.is_liquid=True
        z.is_solid=False
    elif OBJECT_TYPE=='concrete_square':
        z=WorldObject(world,['concrete_square'],AINone)
        z.name='concrete_square'
        z.rotation_angle=0
    elif OBJECT_TYPE=='ground_cover':
        z=WorldObject(world,['ground_dirt_vlarge'],AINone)
        z.name='ground_dirt_vlarge'
        z.is_ground_texture=True
        z.rotation_angle=0
    elif OBJECT_TYPE=='wood_log':
        z=WorldObject(world,['wood_log'],AINone)
        z.name='wood_log'
        z.is_large_human_pickup=True
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='wood_quarter':
        z=WorldObject(world,['wood_log'],AINone)
        z.name='wood_log'
        z.is_large_human_pickup=True
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='coffee_beans':
        z=WorldObject(world,['coffee_beans'],AINone)
        z.name='coffee_beans'
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='ground_coffee':
        z=WorldObject(world,['coffee_beans'],AINone)
        z.name='ground_coffee'
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='coffee_grinder':
        z=WorldObject(world,['coffee_grinder'],AICoffeeGrinder)
        z.name='coffee_grinder'
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='bomb_sc250':
        z=WorldObject(world,['sc250'],AINone)
        z.name='bomb_sc250'
        z.weight=250
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='battery_feldfunk_2v':
        z=WorldObject(world,['battery_vehicle_6v'],AIBattery)
        z.name='Feldfunk 2V battery'
        z.weight=3
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='battery_vehicle_6v':
        z=WorldObject(world,['battery_vehicle_6v'],AIBattery)
        z.name='battery_vehicle_6v'
        z.weight=25
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='battery_vehicle_24v':
        z=WorldObject(world,['battery_vehicle_6v'],AIBattery)
        z.name='battery_vehicle_24v'
        z.weight=25
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='helmet_stahlhelm':
        z=WorldObject(world,['helmet_stahlhelm'],AIWearable)
        z.name='helmet_stahlhelm'
        z.weight=0.98
        z.is_wearable=True
        z.ai.wearable_region='head'
        z.ai.armor_thickness=3
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='helmet_ssh40':
        z=WorldObject(world,['helmet_ssh40'],AIWearable)
        z.name='helmet_ssh40'
        z.weight=0.98
        z.is_wearable=True
        z.ai.wearable_region='head'
        z.ai.armor_thickness=2
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='radio_feldfu_b':
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
    elif OBJECT_TYPE=='feldfunk_battery_charger':
        # ref https://feldfunker-la7sna.com/wehrm_foto.htm
        z=WorldObject(world,['radio_feldfunk_charger'],AIRadio)
        z.name='Feldfunk battery charger'
        z.weight=15
        z.is_large_human_pickup=True
        z.rotation_angle=float(random.randint(0,359)) 

    else:
        print('!! Spawn Error: '+OBJECT_TYPE+' is not recognized.')  

    # -- generic settings that apply to all --
    z.world_builder_identity=OBJECT_TYPE
    # set world coords if they weren't already set
    if z.world_coords==[0,0]:
        z.world_coords=copy.copy(world_coords)

    # reset render level now that variables are set
    z.reset_render_level()
    if SPAWN :
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
def spawn_shrapnel(world,world_coords,TARGET_COORDS,IGNORE_LIST,PROJECTILE_TYPE,MIN_TIME,MAX_TIME,ORIGINATOR,WEAPON_NAME):
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    # MOUSE_AIM bool as to whether to use mouse aim for calculations
    z=WorldObject(world,['shrapnel'],AIProjectile)
    z.name='shrapnel'
    z.world_coords=copy.copy(world_coords)
    z.ai.starting_coords=copy.copy(world_coords)
    z.ai.speed=300.
    z.ai.maxTime=random.uniform(MIN_TIME, MAX_TIME)
    z.is_projectile=True
    z.render_level=3
    z.ai.ignore_list=copy.copy(IGNORE_LIST)
    z.ai.projectile_type=PROJECTILE_TYPE
    z.rotation_angle=engine.math_2d.get_rotation(world_coords,TARGET_COORDS)
    z.heading=engine.math_2d.get_heading_vector(world_coords,TARGET_COORDS)
    # increase the collision radius to make sure we get hits
    z.collision_radius=10
    z.ai.shooter=ORIGINATOR
    z.ai.weapon_name=WEAPON_NAME
    z.wo_start()

#------------------------------------------------------------------------------
def spawn_shrapnel_cloud(world,world_coords,AMOUNT,ORIGINATOR,WEAPON_NAME):
    ''' creates a shrapnel starburst pattern. used for grenades '''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    ignore_list=[]
    if world.friendly_fire_explosive==False:
        if ORIGINATOR.is_german:
                ignore_list+=world.wo_objects_german
        elif ORIGINATOR.is_soviet:
            ignore_list+=world.wo_objects_soviet
        elif ORIGINATOR.is_american:
            ignore_list+=world.wo_objects_american
    elif world.friendly_fire_explosive_squad==False:
        # just add the squad
        ignore_list+=ORIGINATOR.ai.squad.members

    for x in range(AMOUNT):
        target_coords=[float(random.randint(-150,150))+world_coords[0],float(random.randint(-150,150))+world_coords[1]]
        spawn_shrapnel(world,world_coords,target_coords,ignore_list,'shrapnel',0.1,0.4,ORIGINATOR,WEAPON_NAME)

#------------------------------------------------------------------------------
def spawn_smoke_cloud(world,world_coords,heading,amount=30):
    ''' spawn smoke cloud '''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel

    for x in range(amount):
        coords=[world_coords[0]+random.randint(-2,2),world_coords[1]+random.randint(-2,2)]
        z=spawn_object(world,coords,'small_smoke',True)
        z.heading=heading
        z.ai.speed=random.uniform(9,11)
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=random.uniform(1.5,3)

#------------------------------------------------------------------------------
def spawn_sparks(world,world_coords,amount=30):
    ''' spawn spark '''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel

    for x in range(amount):
        coords=[world_coords[0]+random.randint(-2,2),world_coords[1]+random.randint(-2,2)]
        z=spawn_object(world,coords,'spark',True)
        z.heading=engine.math_2d.get_heading_from_rotation(z.rotation_angle)
        z.ai.speed=random.uniform(60,70)
        z.ai.rotation_speed=0
        z.ai.rotate_time_max=0
        z.ai.move_time_max=1
        z.ai.alive_time_max=random.uniform(1.5,2)

#------------------------------------------------------------------------------
def spawn_heat_jet(world,world_coords,TARGET_COORDS,AMOUNT,ORIGINATOR,WEAPON_NAME):
    ''' creates a cone/line of shrapnel. used for panzerfaust'''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    for x in range(AMOUNT):
        target_coords=[float(random.randint(-5,5))+TARGET_COORDS[0],float(random.randint(-5,5))+TARGET_COORDS[1]]
        spawn_shrapnel(world,world_coords,target_coords,[],'HEAT_jet',0.1,0.3,ORIGINATOR,WEAPON_NAME)


# init 
load_sqlite_data()
