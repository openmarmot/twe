
'''
module : ai_zombie.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
# module specific variables
module_version='0.0' #module software version
module_last_update_date='April 10 2021' #date of last update

#global variables

class AIProjectile(AIBase):
    def __init__(self, owner):
        super().__init__(owner)
        self.flightTime=0.
        self.maxTime=5.
        self.ignore_list=[]

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        time_passed=self.owner.world.graphic_engine.time_passed_seconds

        self.flightTime+=time_passed
        if(self.flightTime>self.maxTime):
            self.owner.world.remove_object(self.owner)

        # move along path
        self.owner.world_coords=engine.math_2d.moveAlongVector(self.owner.speed,self.owner.world_coords,self.owner.heading,time_passed)

        if self.owner.world.check_collision_bool(self.owner,self.ignore_list,False,True):
            self.owner.world.remove_object(self.owner)



    #---------------------------------------------------------------------------
