'''
repo : https://github.com/openmarmot/twe

notes : various penetration "calculations"

see tools/armor_thickness.py for a simple tool to help visualize the effects of armor and armor slope

remember for armor
0 - vertical. no slope. no advantage to effective armor
90 - full slope. (impossible)
the closer to 90 the more effective armor you get as the shell has 
to travel through more armor place to pierce through

'''


#import built in modules
import random
import sqlite3
import math

#import custom packages
import engine.math_2d
import engine.log


# velocity is in feet per second
# note velocity doesn't make sense here - it should be per weapon per projectile type

loaded=False

# dictionary of ammo types 
# {name:{projectile_material,case_material,grain_weight,velocity,contact_effect,shrapnel_count},}
projectile_data={}

# the max distance in the penetration data 
max_distance=4000

#---------------------------------------------------------------------------
def evaluate_spaced_armor(projectile_type, max_penetration, spaced_armor_thickness):
    '''Evaluate effect of spaced armor on a projectile
    
    Spaced armor (Schürzen) historically worked by destabilizing/tumbling incoming
    projectiles before they hit the main armor. A tumbled bullet hits at a sub-optimal
    angle with chaotic energy distribution, drastically reducing penetration.
    
    Returns: (adjusted_penetration, effect_string)
    effect_string: '' (none), 'destabilized', 'defeated' (thickness added but no tumble)
    '''
    if spaced_armor_thickness <= 0:
        return max_penetration, ''

    diameter = projectile_data[projectile_type]['diameter']

    if diameter < 20:
        tumble_chance = min(95, 70 + (spaced_armor_thickness * 5))
    elif diameter < 75:
        tumble_chance = max(0, 50 - int(diameter * 1.5))
    else:
        tumble_chance = 0

    if random.randint(1, 100) <= tumble_chance:
        reduction = random.uniform(0.60, 0.70)
        adjusted_penetration = max_penetration * (1 - reduction)
        return adjusted_penetration, 'destabilized'
    else:
        if diameter >= 75 and spaced_armor_thickness < 10:
            return max_penetration, ''
        return max_penetration, 'defeated'

#---------------------------------------------------------------------------
def calculate_penetration(projectile, distance, armor_type, armor, side, relative_angle):
    '''calculate penetration
    Returns: (penetrated: bool, pen_value: float, armor_value: float, spaced_effect: str)
    spaced_effect: '' (none), 'destabilized', 'defeated'
    '''
    # for slope 0 is vertical, whereas 90 is full horizontal armor
    # normalize distance to nearest 500

    if distance<0:
        engine.log.add_data('error',f'penetration_calculator.calculate_penetration() error negative distance {distance}',True)
        distance=0

    armor_thickness = armor[0]
    armor_slope = armor[1]
    spaced_armor = armor[2]

    # get penetration value for projectile at range
    max_penetration = 0
    if distance > max_distance:
        # not sure how this is happening yet..
        engine.log.add_data('Error', f'penetration_calculator.calculate_penetration {projectile.ai.projectile_type} excess range: {distance} armor: {armor} flightTime:{projectile.ai.flightTime} maxTime:{projectile.ai.maxTime}', True)
        max_penetration = projectile_data[projectile.ai.projectile_type][str(max_distance)]
    else:
        # Calculate the lower and upper 500 increments
        lower_distance = int((distance // 500) * 500)
        upper_distance = int(lower_distance + 500)
        # Use linear interpolation between lower and upper distance penetration values
        lower_penetration = projectile_data[projectile.ai.projectile_type][str(lower_distance)]
        upper_penetration = projectile_data[projectile.ai.projectile_type][str(upper_distance)]
        # Calculate interpolation factor
        t = (distance - lower_distance) / 500
        # Linearly interpolate between lower and upper penetration values
        max_penetration = round(lower_penetration + t * (upper_penetration - lower_penetration),2)

    # evaluate spaced armor effects (tumbling/destabilization)
    effective_penetration, spaced_effect = evaluate_spaced_armor(
        projectile.ai.projectile_type, max_penetration, spaced_armor)

    # Compute horizontal obliquity
    centers = {
        "rear": 0,
        "right": 90,
        "front": 180,
        "left": 270,
        "top": 0,
        "bottom": 0
    }
    # Handle wrap-around for rear
    if side == "rear" and relative_angle > 180:
        relative_angle -= 360
    phi_h = abs(relative_angle - centers[side])
    cos_phi_h = math.cos(math.radians(phi_h))

    # calculate effective thickness, including both the vertical angle of the armor and
    # the horizontal angle relative to the projectile
    # if destabilized, spaced armor already reduced penetration so don't add thickness
    if spaced_effect == 'destabilized':
        effective_thickness = armor_thickness / (math.cos(math.radians(armor_slope)) * cos_phi_h)
    else:
        effective_thickness = (armor_thickness / (math.cos(math.radians(armor_slope)) * cos_phi_h)) + spaced_armor

    if effective_penetration > effective_thickness:
        return True, effective_penetration, effective_thickness, spaced_effect
    else:
        return False, effective_penetration, effective_thickness, spaced_effect


#---------------------------------------------------------------------------
def check_passthrough(projectile,target):
    ''' returns bool as to whether or not a projectile passed through (over pen) an object '''
    global projectile_data

    # PROJECTILE - world_object representing the projectile
    # TARGET - world_object that is hit by the projectile

    passthrough=False
    if target.is_building:
        passthrough=get_building_passthrough(projectile,target)
    elif target.is_human:
        passthrough=get_human_passthrough(projectile,target)

    return passthrough

#---------------------------------------------------------------------------
def get_building_passthrough(PROJECTILE,TARGET):
    global projectile_data

    proj_material=projectile_data[PROJECTILE.ai.projectile_type]['projectile_material']
    passthrough=False
    if proj_material=='mild_steel':
        if random.randint(1,100) <40:
            passthrough=True
    elif proj_material=='hard_steel':
        if random.randint(1,100) <60:
            passthrough=True
    elif proj_material=='tungsten':
        if random.randint(1,100) <80:
            passthrough=True
    else :
        # everything else - mostly lead
        if random.randint(1,100) <20:
            passthrough=True
    return passthrough

#---------------------------------------------------------------------------
def get_human_passthrough(PROJECTILE,TARGET):
    global projectile_data

    proj_material=projectile_data[PROJECTILE.ai.projectile_type]['projectile_material']
    passthrough=False
    if proj_material=='mild_steel':
        if random.randint(1,100) <50:
            passthrough=True
    elif proj_material=='hard_steel':
        if random.randint(1,100) <80:
            passthrough=True
    elif proj_material=='tungsten':
        if random.randint(1,100) <90:
            passthrough=True
    else :
        # everything else - mostly lead
        if random.randint(1,100) <20:
            passthrough=True
    return passthrough

            
#---------------------------------------------------------------------------
def load_projectile_data():
    global projectile_data
    global loaded

    if loaded==False:

        # Connect to the SQLite database
        conn = sqlite3.connect('data/data.sqlite')

        # Create a cursor object
        cursor = conn.cursor()

        #cursor.execute("SELECT name,projectile_material,case_material,grain_weight,velocity,contact_effect,shrapnel_count FROM projectile_data")
        cursor.execute("SELECT * FROM projectile_data")
        # Fetch all column names
        column_names = [description[0] for description in cursor.description]

        # Fetch all rows from the table
        rows = cursor.fetchall()

        # Close the database connection
        conn.close()

        projectile_data={}
        # Convert rows to dictionary, excluding the 'id' field
        for row in rows:
            row_dict = {column_names[i]: row[i] for i in range(len(column_names)) if column_names[i] != 'id'}
            key = row_dict.pop('name')
            projectile_data[key] = row_dict

        print('Projectile data load complete')
        #print(projectile_data)
        loaded=True

    else:
        print('Error : Projectile data is already loaded')

# init
load_projectile_data()
