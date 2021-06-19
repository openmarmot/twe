
'''
module : ai_zombie.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes :
'''


#import built in modules
import random 

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
import engine.world_builder 

# module specific variables
module_version='0.0' #module software version
module_last_update_date='April 05 2021' #date of last update

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
        self.rate_of_fire=0.

        # spread
        self.spread=15

        # the object (human) that actually equipped this weapon
        # set by ai_man.event_inventory
        self.equipper=None

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        self.fire_time_passed+=self.owner.world.graphic_engine.time_passed_seconds
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    def change_magazine(self):
        ''' change magazine. input is new magazine. output is old magazine'''
        pass

    #---------------------------------------------------------------------------
    def fire(self,WORLD_COORDS,TARGET_COORDS):
        ''' fire the gun '''

  
        # start with a time check
        if(self.fire_time_passed>self.rate_of_fire):
            self.fire_time_passed=0.
            # start by ruling out empty mag 
            if self.magazine<1:
                # auto reload ?
                if self.equipper.is_player:
                    print("magazine empty")
                # infinite ammo cheat for now
                self.magazine=self.mag_capacity
            else :
                self.magazine-=1
                spr=[random.randint(-self.spread,self.spread),random.randint(-self.spread,self.spread)]
                if self.equipper.is_player:
                    engine.world_builder.spawn_projectile(self.owner.world,WORLD_COORDS,TARGET_COORDS,spr,[self.equipper],True,self.equipper)
                elif self.equipper.is_soldier:
                    # squad gets added to make immune to friendly fire
                    engine.world_builder.spawn_projectile(self.owner.world,WORLD_COORDS,TARGET_COORDS,spr,self.equipper.ai.squad.members,False,self.equipper)
                else:
                    engine.world_builder.spawn_projectile(self.owner.world,WORLD_COORDS,TARGET_COORDS,spr,[self.equipper],False,self.equipper)

                # spawn brass 
                engine.world_builder.spawn_sprite(self.owner.world,WORLD_COORDS,'brass')

        


    #---------------------------------------------------------------------------
    def reload_current_mag(self):
        ''' reload the current magazine'''
        pass