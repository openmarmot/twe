'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
'''

# import built in modules
import random


# import custom modules 
from engine.map_object import MapObject
import engine.math_2d
import engine.world_builder
import engine.log

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
        civilians.append(MapObject('civilian_big_cheese','',coords,rotation,[]))
        engine.log.add_data('note','big_cheese added to map',True)

    # unique civilian shovel_man
    if random.randint(1,100)<5:
        coords=[random.randint(-1000,1000),random.randint(-1000,1000)]
        rotation=random.randint(0,359)
        civilians.append(MapObject('civilian_shovel_man','',coords,rotation,[]))
        engine.log.add_data('note','shovel_man added to map',True)

    return civilians

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
def generate_map(map_areas):
    '''
    entry point 
    generate a map. return a list of map objects

    map_areas : list of map areas to be created 
    options airport,rail_yard,town
    '''

    map_objects=[]

    min_world_size=20000

    world_size=max(min_world_size,len(map_areas)*4000)

    coord_list=engine.math_2d.get_random_constrained_coords([0,0],8000,5000,len(map_areas),[],0) 

    for map_area in map_areas:
        if map_area=='airport':
            map_objects+=generate_map_area_airport(coord_list.pop(),'airport')
        elif map_area=='rail_yard':
            map_objects+=generate_map_area_rail_yard(coord_list.pop(),'rail_yard')
        elif map_area=='town':
            map_objects+=generate_map_area_town(coord_list.pop(),'town')

    # generate clutter 
    map_objects+=generate_clutter(map_objects)

    # generate vegetation
    map_objects+=generate_vegetation(map_objects,world_size)  

    # generate civilians
    map_objects+=generate_civilians(map_objects)

    # generate terrain 

    return map_objects


#------------------------------------------------------------------------------
def generate_map_area_airport(world_coords,name):
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

    # add a world_area map object so the tactical ai can recognize it, and so it shows up on maps
    world_area=MapObject('world_area_'+'airport',name,world_coords,0,[])
    map_objects.append(world_area)

    return map_objects

#------------------------------------------------------------------------------
def generate_map_area_rail_yard(world_coords,name):
    '''generate rail yard map area'''
    engine.log.add_data('warn','world_builder.generate_world_area_rail_yard: not implemented',True)
    map_objects=[]

    # add a world_area map object so the tactical ai can recognize it, and so it shows up on maps
    world_area=MapObject('world_area_'+'rail_yard',name,world_coords,0,[])
    map_objects.append(world_area)
    return map_objects

#------------------------------------------------------------------------------
def generate_map_area_simple(world_coords,count,diameter,world_builder_identity,name,rotation):
    '''generates a simple one object type world area '''
    # count: int
    # diameter : int - rough size of the object
    coords=engine.math_2d.get_grid_coords(world_coords,diameter,count)
    map_objects=[]
    for _ in range(count):
        map_objects.append(MapObject(world_builder_identity,name,coords.pop(),rotation,[]))
    
    return map_objects

#------------------------------------------------------------------------------
def generate_map_area_town(world_coords,name):
    count_warehouse=random.randint(2,5)
    count_building=random.randint(2,14)
    
    map_objects=[]
    
    # add warehouses in a grid
    warehouse_seperation=850
    coords=engine.math_2d.get_grid_coords(world_coords,warehouse_seperation,count_warehouse)
    rotation=random.choice([0,90,180,270])
    coords_to_avoid=[]
    for _ in range(count_warehouse):
        warehouse_coord=coords.pop()
        coords_to_avoid.append(warehouse_coord)
        map_objects.append(MapObject('warehouse','a old warehouse',warehouse_coord,rotation,[]))
    
    # add smaller square buildings in a more random pattern, avoiding the warehouses 
    building_max_area=2000
    building_seperation=200
    building_coords=engine.math_2d.get_random_constrained_coords(world_coords,building_max_area,
        building_seperation,count_building,coords_to_avoid,warehouse_seperation)
    for _ in range(count_building):
        map_objects.append(MapObject('square_building','some sort of building',building_coords.pop(),rotation,[]))

    # add a world_area map object so the tactical ai can recognize it, and so it shows up on maps
    world_area=MapObject('world_area_'+'town',name,world_coords,0,[])
    map_objects.append(world_area)

    return map_objects

#------------------------------------------------------------------------------
def generate_vegetation(map_objects,world_size):
    '''generates vegetation
    this should be run after buildings are created
    map_objects - list of existing map objects
    world_size - size of map in all directions. should be > than town generation size
    returns a list of vegetation map objects
    '''
    vegetation=[]

    # generate a list of coordinates to avoid
    coordinates_to_avoid=[]
    names_to_avoid=['warehouse','square_building','hangar','concrete_square']
    for obj in map_objects:
        if obj.world_builder_identity in names_to_avoid:
            coordinates_to_avoid.append(obj.world_coords)

    # generate coord list of forested areas
    max_size=world_size
    min_seperation=1000
    coord_count=random.randint(50,200)
    forest_areas=engine.math_2d.get_random_constrained_coords([0,0],max_size,
        min_seperation,coord_count,coordinates_to_avoid,600)

    # generate each forest clump 
    for area in forest_areas:
        # - generate trees -
        max_size=1000
        min_seperation=100
        coord_count=random.randint(1,20)
        tree_coords=engine.math_2d.get_random_constrained_coords(area,max_size,
            min_seperation,coord_count,[],0)
        
        for coords in tree_coords:
            rotation=random.randint(0,359)
            vegetation.append(MapObject('pinus_sylvestris','pinus_sylvestris',coords,rotation,[]))

    return vegetation



