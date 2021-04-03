
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

class AIGun(AIBase):
    def __init__(self, owner):
        super().__init__(owner)
        #int representing round count in current mag 
        self.magazine=0
        #max mag capacity - this limits us from using different mag types. hrmm
        # is this even needed??
        self.mag_capacity=0
        
        #
        #time since last fired
        self.fire_time_passed=0. 

        # fire rate in seconds?
        self.rate_of_fire=0.5 

    #---------------------------------------------------------------------------
    def update(self, time_passed):
        ''' overrides base update '''
        #self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,self.owner.world.player.world_coords)
        #self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.screen_coords,self.owner.world.player.screen_coords)
        #print(str(self.rotation_angle))

       # self.owner.world_coords=engine.math_2d.moveTowardsTarget(self.owner.speed,self.owner.world_coords,self.owner.world.player.world_coords,time_passed)
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    def change_magazine(self):
        ''' change magazine. input is new magazine. output is old magazine'''
        pass

    #---------------------------------------------------------------------------
    def fire(self, time_passed):
        ''' fire the gun '''
        self.fire_time_passed+=time_passed
  
        # start with a time check
        if(self.fire_time_passed>self.rate_of_fire):
            self.fire_time_passed=0.
            # start by ruling out empty mag 
            if self.magazine<1:
                # auto reload ?
                print("magazine empty")
            else :
                print("pew pew")
                self.magazine-=1
        


    #---------------------------------------------------------------------------
    def reload_current_mag(self):
        ''' reload the current magazine'''
        pass