'''
module : engine/penetration_calculator.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes : various penetration "calculations"
'''


#import built in modules
import random
#import custom packages
import engine.math_2d
# module specific variables
module_version='0.0' #module software version
module_last_update_date='April 10 2021' #date of last update


#---------------------------------------------------------------------------
def check_passthrough(PROJECTILE,TARGET):
    ''' returns bool as to whether or not a projectile passed through (over pen) an object '''
    # PROJECTILE - world_object representing the projectile
    # TARGET - world_object that is hit by the projectile

    passthrough=False

    if TARGET.is_building:
        if random.randint(1,5) >3:
            passthrough=True
    elif TARGET.is_human:
        if random.randint(1,5)>3:
            passthrough=True
    elif TARGET.is_vehicle:
        if random.randint(1,5)>4:
            passthrough=True

    return passthrough