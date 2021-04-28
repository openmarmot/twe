
'''
module : ai_faction_tactical.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes : AI that controls all a factions squads on the tactical map 
'''


#import built in modules
import random 

#import custom packages
import engine.math_2d
# module specific variables
module_version='0.0' #module software version
module_last_update_date='April 21 2021' #date of last update


#global variables

class AISquad(object):
    def __init__(self):

        # ai in the group will try to stay close to the group world coords
        self.world_coords=[0.,0.]
        # people in the squad 
        self.members=[] 
