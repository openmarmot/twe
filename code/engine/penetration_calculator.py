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

# dictionary of weapon penetration data
# {weapon:{distance:penetration,distance:penetration}}
penetration_data=[]

#---------------------------------------------------------------------------
def check_passthrough(PROJECTILE,TARGET):
    ''' returns bool as to whether or not a projectile passed through (over pen) an object '''
    global projectile_data

    # PROJECTILE - world_object representing the projectile
    # TARGET - world_object that is hit by the projectile

    passthrough=False
    if TARGET.is_building:
        passthrough=get_building_passthrough(PROJECTILE,TARGET)
    elif TARGET.is_human:
        passthrough=get_human_passthrough(PROJECTILE,TARGET)
    elif TARGET.is_vehicle:
        passthrough=get_vehicle_passthrough(PROJECTILE,TARGET)

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

        cursor.execute("SELECT name,projectile_material,case_material,grain_weight,velocity,contact_effect,shrapnel_count FROM projectile_data")

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
