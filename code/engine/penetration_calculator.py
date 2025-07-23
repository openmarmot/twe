'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : various penetration "calculations"
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
def calculate_penetration(projectile,distance,armor_type,armor):
    '''calculate penetration, return bool'''
    # for slope 0 is vertical, whereas 90 is full horizontal armor
    # normalize distance to nearest 500
    distance=round(distance/500)*500

    armor_thickness=armor[0]
    armor_slope=armor[1]
    spaced_armor=armor[2]

    # get penetration value for projectile at range
    max_penetration=0
    if distance>max_distance:
        # not sure how this is happening yet..
        engine.log.add_data('Error',f'penetration_calculator.calculate_penetration {projectile.ai.projectile_type} excess range: {distance} armor: {armor} flightTime:{projectile.ai.flightTime} maxTime:{projectile.ai.maxTime}',True)
        max_penetration=projectile_data[projectile.ai.projectile_type][str(max_distance)]
    else:
        max_penetration=projectile_data[projectile.ai.projectile_type][str(distance)]

    # fast check first
    if max_penetration<(armor_thickness+spaced_armor):
        return False,max_penetration,(armor_thickness+spaced_armor)
    else:
        # more complicated penetration check

        # calculate effective thickness
        # here we could also take into account elevation differences between the shooter and the target
        # to adjust the armor angle
        # taking the cosine means that the slope is more beneficial as it approaches 90 degrees (full horizontal)
        effective_thickness = (armor_thickness / math.cos(math.radians(armor_slope))) + spaced_armor
        
        if max_penetration>effective_thickness:
            return True,max_penetration,effective_thickness
        else:
            return False,max_penetration,effective_thickness


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
