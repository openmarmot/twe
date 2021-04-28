
'''
module : ai_group.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes : AI that makes decisions for groups 
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

    
    #---------------------------------------------------------------------------
    def spawn_on_map():
        '''spawns the squad on the map at the squads world coords '''

        for b in self.members :
            b.world_coords=[self.world_coords[0]+float(random.randint(-15,15),self.world_coords[1]+float(random.randint(-15,15)]
            b.wo_start()

    #---------------------------------------------------------------------------
    def update(self):
        pass

    #---------------------------------------------------------------------------
