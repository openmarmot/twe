'''
module : engine/penetration_calculator.py
language : Python 3.x
email : andrew@openmarmot.com
notes : various penetration "calculations"
'''


#import built in modules
import random
import sqlite3

#import custom packages
import engine.math_2d



# velocity is in feet per second
# note velocity doesn't make sense here - it should be per weapon per projectile type

loaded=False

# dictionary of ammo types 
# {name:{projectile_material,case_material,grain_weight,velocity,contact_effect,shrapnel_count},}
projectile_data={}



#---------------------------------------------------------------------------
def calculate_penetration(projectile,target):
    '''calculate penetration, return bool'''
    penetration=False
    distance=engine.math_2d.get_distance(projectile.ai.starting_coords,target.world_coords)

    # normalize distance to nearest 500
    distance=round(distance/500)*500

    # get penetration value for projectile at range
    max_penetration=projectile_data[projectile.ai.projectile_type][str(distance)]

    if target.is_human:
        body_part=random.randint(1,3)
        if body_part==1:
            if target.ai.wearable_head==None:
                penetration=True
            else:
                if max_penetration>=target.ai.wearable_head.ai.armor_thickness:
                    penetration=True
        else:
            penetration=True
    elif target.is_vehicle:
        if max_penetration>=target.ai.armor_thickness:
                penetration=True
        else:
            pass
            # maybe do a redirect here 
    else:
        penetration=True
    
    return penetration


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
    elif target.is_vehicle:
        passthrough=get_vehicle_passthrough(projectile,target)

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
def get_vehicle_passthrough(PROJECTILE,TARGET):
    global projectile_data

    # eventually vehicles will get a unique penetration calculation to check armor 

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
