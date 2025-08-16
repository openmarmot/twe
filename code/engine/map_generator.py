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
def generate_map(map_areas):
    '''
    generate a map. return a list of map objects

    map_areas : list of map areas to be created 
    options airport,rail_yard,town
    '''

    map_objects=[]

    min_world_size=20000

    world_size=max(min_world_size,len(map_areas)*4000)

    for map_area in map_areas:
        if map_area=='airport':
            pass


#------------------------------------------------------------------------------
def generate_map_area_airport(world_coords):
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
    world_area=MapObject('world_area_'+area_type,name,world_coords,0,[])
    map_objects.append(world_area)

    return map_objects

#------------------------------------------------------------------------------
def generate_map_area_rail_yard(world_coords):
    '''generate rail yard map area'''
    engine.log.add_data('warn','world_builder.generate_world_area_rail_yard: not implemented',True)
    return []

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
def generate_map_area_town(world_coords):
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



