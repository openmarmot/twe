
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
module_last_update_date='July 02 2016' #date of last update

#global variables

class AIZombie(AIBase):
    def __init__(self, owner):
        super().__init__(owner)
        self.owner.speed=20

    #---------------------------------------------------------------------------
    def update(self, time_passed):
        ''' overrides base update '''
        self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,self.owner.world.player.world_coords)
        #self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.screen_coords,self.owner.world.player.screen_coords)
        #print(str(self.rotation_angle))

        self.owner.world_coords=engine.math_2d.moveTowardsTarget(self.owner.speed,self.owner.world_coords,self.owner.world.player.world_coords,time_passed)
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    def change_magazine(self,magazine):
        ''' change magazine. input is new magazine. output is old magazine'''
        old=self.mag
        self.mag=magazine
        return old
