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

class Penetration_Calculator(object):
    
    def __init__(self):
        # this object is created by world init 
        projectile_data={}
        projectile_data['9mm_124']={'material':'lead','grain_weight':124,'velocity':1050,'notes':'standard german early war fmj 9mm'}
        projectile_data['9mm_115']={'material':'lead','grain_weight':115,'velocity':1200,'notes':'standard us/commonwealth fmj 9mm'}
        projectile_data['9mm_ME']={'material':'mild_steel','grain_weight':94,'velocity':1500,'notes':'standard german issue late war iron core'}
        projectile_data['45acp']={'material':'lead','grain_weight':230,'velocity':800,'notes':'standard issue 45 ACP'}
        projectile_data['7.62x25']={'material':'lead','grain_weight':90,'velocity':1450,'notes':'standar tokarev ammo, probably light ap'}
        projectile_data['7.92x57_SSP']={'material':'lead','grain_weight':197.53,'velocity':2493,'notes':'german early war/sniper ss patrone '}
        projectile_data['7.92x57_SME']={'material':'mild_steel','grain_weight':178.2,'velocity':2592,'notes':'standard issue german iron core '}
        projectile_data['7.92x57_SMK']={'material':'hard_steel','grain_weight':182.9,'velocity':2575,'notes':'german standard ap '}
        projectile_data['7.92x57_SMKH']={'material':'tungsten','grain_weight':178.2,'velocity':2592,'notes':'extra hard ap '}
        projectile_data['7.92x33_SME']={'material':'mild_steel','grain_weight':125,'velocity':2250,'notes':'standard issue german iron core for stg44 '}
        projectile_data['shrapnel']={'material':'mild_steel','grain_weight':50,'velocity':1100,'notes':'fragment from a grenade '}





    #---------------------------------------------------------------------------
    def check_passthrough(self,PROJECTILE,TARGET):
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