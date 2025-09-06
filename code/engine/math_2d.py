
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : 

static module consisting of math functions.

this started out as just 2d graphics math but it grew to have other functions.

I'm pretty sure something is fundamentally wrong with my math in this game 
some of these functions are the opposite of what they should be
lets just pretend this is all sane. super sane

# ref
# notes on som differenct collisiong algos
# https://www.h3xed.com/programming/bounding-box-vs-bounding-circle-collision-detection-performance-as3#:~:text=%2F%2F%20Collision!,-%7D&text=The%20above%20run%20took%20164,the%20nature%20of%20your%20game.
# more notes - similar 
# https://developer.mozilla.org/en-US/docs/Games/Techniques/2D_collision_detection
'''


#import built in modules
import math
import random
import copy

from functools import lru_cache

#import custom packages


#global variables

# constants (should be all caps as per pep8)
# velocity of gravity in meters/second
GRAVITY=-9.8

cache_check=[]

#------------------------------------------------------------------------------
def calculate_acceleration(force,rolling_resistance,drag_coefficient,air_density,frontal_area,weight):
    '''calculate acceleration'''
    # force - force in watts
    # rolling_resistance : maybe 0.015 for a jeep (1.5% of the vehicle weight)
    # drag_coefficient : maybe 0.8 for a jeep
    # air_density is the air density in kg/m^3 (typically around 1.225 kg/m^3 at sea level)
    # frontal_area is the objects frontal cross-sectional area in square meters
    # weight : kilograms

    # adjustment to game units
    adjustment=1

    # Calculate net force
    net_force = force - (rolling_resistance * weight) - (0.5 * air_density * frontal_area * drag_coefficient)

    # Calculate acceleration in m/s^2
    acceleration = net_force / weight

    # adjust to game units
    acceleration*=adjustment

    # round to 2 sd
    acceleration=round(acceleration,2)

    return acceleration

#------------------------------------------------------------------------------
def calculate_hit_side(vehicle_angle,projectile_angle):
    '''determine what side of a vehicle is hit'''

    # ! Note - this is very roughly accurate
    # for example if you hit the side while in front of the vehicle
    # it will tend to record as front
    
    relative_angle = (projectile_angle - vehicle_angle) % 360
    if 0 <= relative_angle < 45 or 315 <= relative_angle < 360:
        side = "rear"
    elif 45 <= relative_angle < 135:
        side = "right"
    elif 135 <= relative_angle < 225:
        side = "front"
    else:  # 225 <= relative_angle < 315
        side = "left"
    
    return side, relative_angle

#------------------------------------------------------------------------------
def calculate_offset_coords_and_rotation(base_coords,base_rotation,offset_obj_coords,offset_obj_rotation):
    '''for when you have two objects, and want to get the coords and rotation of one relative to the other'''

    # 1. calculate offset without taking into account the base rotation
    rotation_affected_offset=[offset_obj_coords[0]-base_coords[0],offset_obj_coords[1]-base_coords[1]]

    # apply rotation to get the true offset at zero rotation
    #true_offset=get_vector_rotation(rotation_affected_offset,base_rotation)
    true_offset=get_vector_rotation(rotation_affected_offset,base_rotation)

    # get offset rotation
    norm_base_rot=get_normalized_angle(base_rotation)
    norm_offset_rot=get_normalized_angle(offset_obj_rotation)
    true_offset_rot=norm_offset_rot-norm_base_rot
    true_offset_rot=get_normalized_angle(true_offset_rot)

    return true_offset,true_offset_rot

#------------------------------------------------------------------------------
def calculate_relative_position(coords,rotation,offset):
    ''' calculate a position based on a offset and a given coordinate and rotation'''
    rotated_offset=get_vector_rotation(offset,rotation)
    relative_position=get_vector_addition(coords,rotated_offset)
    return relative_position

#------------------------------------------------------------------------------
def checkCollisionCircleOneResult(wo, collision_list, ignore_list):
    # wo - (worldobject)the object possibly doing the colliding
    # collision_list - (list[worldobject] a list of all possible objects that
    # list of objects to ignore (should include wo)

    # returns the first result only

    collided=None
    for b in collision_list:
        if b.is_vehicle:
            # no collision on disabled vehicles
            if b.ai.vehicle_disabled:
                continue

        distance=get_distance(wo.world_coords,b.world_coords)

        if distance < (wo.collision_radius+b.collision_radius):
            if wo!=b and (b not in ignore_list):
                collided=b
                break
    return collided

#------------------------------------------------------------------------------
def checkCollisionCircleCoordsAllResults(world_coords,collision_range,collision_list, ignore_list):
    # modified collision checkt that uses a world_coords instead of an object
    # collision_range replaces wo.collision_radius

    collided=[]
    for b in collision_list:
        distance=get_distance(world_coords,b.world_coords)

        if distance < (collision_range+b.collision_radius):
            if b not in ignore_list:
                collided.append(b)
                
    return collided

#-----------------------------------------------------------------------------
def collision_sort(runs,wo_objects):
    ''' moves around objects so they no longer collide'''
    # RUNS - number of runs through the resort algo you want to do. probably >100
    # WO_OBJECTS - list of objects to sort
    for x in range(runs):
        for a in wo_objects:
            if checkCollisionCircleOneResult(a,wo_objects,[a]) !=None:
                #collided. lets move the building in a super intelligent way
                a.world_coords[0]+=float(random.randint(-100,100))
                a.world_coords[1]+=float(random.randint(-100,100))

#------------------------------------------------------------------------------
def get_distance(coords1, coords2):
    '''get the distance between two sets of coordinates'''
    x=coords1[0]-coords2[0]
    y=coords1[1]-coords2[1]
    distance=math.sqrt(x*x+y*y)
    #return round(distance,1) # turns out this is pretty slow and not needed
    return distance

#------------------------------------------------------------------------------
def get_column_coords(initial_coords, diameter, count, rotation_degrees, width):
    """
    Returns an array of world coordinates to arrange 'count' of objects in columns.
    The columns are rotated by 'rotation_degrees' and have 'width' number of objects wide.

    Parameters:
    - initial_coords: [x, y], the starting coordinates.
    - diameter: float, spacing between objects.
    - count: int, total number of objects.
    - rotation_degrees: float, rotation of the columns in degrees.
    - width: int, number of objects wide.

    Returns:
    - coords: list of [x, y] coordinates.
    """
    coords = []
    x = count // width  # Number of rows needed
    x_remaining = count % width  # Remaining objects for the last row if any

    # Convert rotation to radians for math functions
    theta = math.radians(rotation_degrees)
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)

    x0, y0 = initial_coords

    for i in range(count):
        # Compute column (x) and row (y) indices
        col = i % width
        row = i // width

        # Position in unrotated grid
        x_grid = col * diameter
        y_grid = row * diameter

        # Apply rotation
        x_rotated = x_grid * cos_theta - y_grid * sin_theta
        y_rotated = x_grid * sin_theta + y_grid * cos_theta

        # Translate back to initial coordinates
        x_x_final = x0 + x_rotated
        y_final = y0 + y_rotated

        coords.append([x_x_final, y_final])

    return coords

#------------------------------------------------------------------------------
def get_grid_coords(initial_coords, diameter, count):
    # returns an array of world_coords to grid spawn a 'count' of objects.
    grid_coords = []
    column_count = get_optimal_column_count(count)
    column_max = initial_coords[0] + (column_count - 1) * diameter
    last_coord = copy.copy(initial_coords)

    for _ in range(count):
        grid_coords.append(last_coord.copy())  # Append first, then increment
        if last_coord[0] >= column_max:
            last_coord[0] = initial_coords[0]
            last_coord[1] += diameter
        else:
            last_coord[0] += diameter
    return grid_coords

#------------------------------------------------------------------------------
def get_heading_vector(location,destination):
    ''' normalized vector representing the heading (direction) to a target'''

    # location = [float,float]
    # destination = [float,float]
    vec_to_dest=[destination[0]-location[0],destination[1]-location[1]]
    heading=get_normalized(vec_to_dest)
    return heading

#--------------------------------------------------------------------------------
@lru_cache(maxsize=2000)
def get_heading_from_rotation(rotation):
    ''' get heading vector. input is rotation in degrees'''

    r=math.radians(rotation)
    b=[math.degrees(-math.sin(r)),-math.degrees(math.cos(r))]
    return get_normalized(b)

#------------------------------------------------------------------------------
def get_normalized(vec2):
    l=math.sqrt(vec2[0]*vec2[0]+vec2[1]*vec2[1])
    b=[0.,0.]
    try:
        b=[vec2[0]/l,vec2[1]/l]
    except ZeroDivisionError:
        pass
    return b

#------------------------------------------------------------------------------
def get_normalized_angle(degrees):
    return round(degrees % 360,2)

#------------------------------------------------------------------------------
def get_optimal_column_count(amount):
    '''Calculates an optimal column count that balances columns and rows'''

    if amount <= 0:
        return 1  # Return 1 for zero or negative amounts for practical reasons

    optimal_columns = 1
    min_diff = float('inf')
    
    for columns in range(1, amount + 1):
        rows = -(-amount // columns)  # Ceiling division to get the number of rows
        diff = abs(columns - rows)
        if diff < min_diff:
            min_diff = diff
            optimal_columns = columns
        elif diff == min_diff and columns > optimal_columns:
            optimal_columns = columns  # Prefer more columns if the difference is the same
            
    return optimal_columns


#------------------------------------------------------------------------------
def get_random_constrained_coords(starting_coordinate, max_size, minimum_separation, count, avoid_coords, avoid_coords_separation):
    """
    Generates a list of map coordinates with specified constraints.
    Coordinates are whole numbers (integers).
    If max_attempts are exhausted, increases max_size by 1000 and retries.
    Parameters:
    - starting_coordinate (list or tuple): The starting coordinates [x, y]. should usually be [0,0]
    - max_size (int): The initial maximum absolute value for x or y.
    - minimum_separation (int): The minimum Euclidean distance between any two coordinates.
    - count (int): The number of coordinates to generate.
    - avoid_coords (array): list of coords to avoid
    - avoid_coords_separation: minimum distance from a avoided coordinate
    Returns:
    - list of lists: A list containing coordinate pairs [x, y].
    Raises:
    - ValueError: If it's impossible to place the desired number of points after multiple retries.
    """
       
    # Initialize variables
    current_max_size = max_size
    size_increment = 1000 # Increment to add to max_size upon failure
    retry_limit = 10 # Maximum number of retries to prevent infinite loops
    retries = 0
    while retries < retry_limit:
        # Initialize the list
        coordinates = []
       
        # Precompute the square of minimum separation to avoid sqrt in distance calculation
        min_sep_sq = minimum_separation ** 2
        min_avoid_sep_sq = avoid_coords_separation ** 2
       
        # Define the maximum number of attempts to prevent infinite loops
        max_attempts = count * 1000
        attempts = 0
       
        while len(coordinates) < count and attempts < max_attempts:
            # Generate a random x and y within the specified range as integers, offset around starting_coordinate
            offset_x = random.randint(-current_max_size, current_max_size)
            offset_y = random.randint(-current_max_size, current_max_size)
            x = starting_coordinate[0] + offset_x
            y = starting_coordinate[1] + offset_y
            new_coord = [x, y]
           
            # Check if the new coordinate is too close to any existing ones
            too_close = False
            for coord in coordinates:
                dx = coord[0] - x
                dy = coord[1] - y
                distance_sq = dx * dx + dy * dy
                if distance_sq < min_sep_sq:
                    too_close = True
                    break # No need to check further if one is too close
            if not too_close:
                for coord in avoid_coords:
                    dx = coord[0] - x
                    dy = coord[1] - y
                    distance_sq = dx * dx + dy * dy
                    if distance_sq < min_avoid_sep_sq:
                        too_close = True
                        break # No need to check further if one is too close
           
            # If the new coordinate is sufficiently far from all existing ones, add it
            if not too_close:
                coordinates.append(new_coord)
           
            attempts += 1
       
        if len(coordinates) == count:
            # Successfully generated the required number of coordinates
            return coordinates
        else:
            # Failed to generate the required number of coordinates, increase max_size and retry
            retries += 1
            current_max_size += size_increment
            print(f"Attempt {retries}: Could only generate {len(coordinates)} coordinates with max_size={current_max_size - size_increment}. Increasing max_size to {current_max_size} and retrying...")
   
    # If all retries are exhausted, raise an error
    raise ValueError(f"Failed to generate {count} coordinates after {retries} retries with max_size up to {current_max_size}.")
        
#------------------------------------------------------------------------------
def get_rotation(coords, target_coords):
    '''get rotation angle from one set of coordinates to another'''
    delta_x = coords[0] - target_coords[0]
    delta_y = coords[1] - target_coords[1]
    
    # Calculate the angle in radians
    angle_rad = math.atan2(delta_x, delta_y)
    
    # Convert the angle to degrees and ensure it's positive
    angle_deg = math.degrees(angle_rad)
        
    return get_normalized_angle(angle_deg)


#------------------------------------------------------------------------------
def get_round_vector_2(vector):
    
    return [round(vector[0],2),round(vector[1],2)]

#------------------------------------------------------------------------------
def get_transfer_results(source_amount, destination_amount, destination_maximum):
    '''get resulting numbers from transfering an amount of something somewhere else'''

    # Calculate the amount that can be transferred without going over the maximum
    transferable_amount = min(source_amount, destination_maximum - destination_amount)

    # Update the source and destination amounts
    source_amount -= transferable_amount
    destination_amount += transferable_amount

    # round 
    source_amount=round(source_amount,2)
    destination_amount=round(destination_amount,2)

    return source_amount, destination_amount

#------------------------------------------------------------------------------
def get_vector_addition(first_vec,second_vec):
    '''add together two vector 2s'''
    result=[first_vec[0]+second_vec[0],first_vec[1]+second_vec[1]]
    return result

#------------------------------------------------------------------------------
def get_vector_length(vec2):
    return math.sqrt(vec2[0]*vec2[0]+vec2[1]*vec2[1])

#------------------------------------------------------------------------------
def get_vector_rotation(vector,angle_degrees):
    # note this is adjusted to match how in game coordinates work
    # in the original code x and y were flipped
    # Convert angle to radians
    angle_rad = math.radians(angle_degrees)
    
    # Rotation matrix applied to vector
    y = vector[0] * math.cos(angle_rad) - vector[1] * math.sin(angle_rad)
    x = vector[0] * math.sin(angle_rad) + vector[1] * math.cos(angle_rad)
    
    return [x, y] 

#------------------------------------------------------------------------------
def moveAlongVector(speed,location,heading,time_passed):
    ''' returns a location vector that has been moved along a heading vector'''
    travel_distance=speed*time_passed
    change=[heading[0]*travel_distance,heading[1]*travel_distance]
    return get_round_vector_2([location[0]+change[0],location[1]+change[1]])

#------------------------------------------------------------------------------
def moveTowardsTarget(speed,location,destination, time_passed):
    vec_to_dest=[destination[0]-location[0],destination[1]-location[1]]
    distance=get_vector_length(vec_to_dest)
    heading=get_normalized(vec_to_dest)
    # basically takes the minimum of distance or travel so as not to go past the target
    travel_distance=min(distance,time_passed*speed)
    change=[heading[0]*travel_distance,heading[1]*travel_distance]
    return get_round_vector_2([location[0]+change[0],location[1]+change[1]])

#------------------------------------------------------------------------------
def randomize_coordinates(coords,amount):
    '''randomize a set of coordinates [x,y] and return the results'''
    return [coords[0]+float(random.randint(-amount,amount)),coords[1]+float(random.randint(-amount,amount))]

#------------------------------------------------------------------------------
def randomize_position_and_rotation(worldobj,amount=15,):
    ''' takes a world object and randomizes the rotation and position'''
    w=worldobj.world_coords
    worldobj.world_coords=[w[0]+float(random.randint(-amount,amount)),w[1]+float(random.randint(-amount,amount))]
    worldobj.rotation_angle=float(random.randint(0,359))
    worldobj.reset_image=True

#------------------------------------------------------------------------------
def regress_to_zero(var=None,time_passed=None,dead_zone=0.05):
    ''' regress a variable to zero over time '''
    if var>0:
        var-=1*time_passed
        if var<dead_zone:
            var=0
    elif var<0:
        var+=1*time_passed
        if var>-dead_zone:
            var=0

    # round
    var=round(var,2)

    return var
    