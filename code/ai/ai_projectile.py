
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


    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        time_passed=self.owner.world.graphic_engine.time_passed_seconds
        # move along path
        self.owner.world_coords=engine.math_2d.moveAlongVector(self.owner.speed,self.owner.world_coords,self.owner.heading,time_passed)
    #---------------------------------------------------------------------------
