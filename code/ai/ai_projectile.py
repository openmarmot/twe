
'''
module : ai_projectile.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes :
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
import engine.penetration_calculator
import engine.world_builder
# module specific variables
module_version='0.0' #module software version
module_last_update_date='june 16 2021' #date of last update

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
            engine.world_builder.spawn_sprite(self.owner.world,self.owner.world_coords,'dirt')
            self.owner.world.remove_object(self.owner)
        else:

            # move along path
            self.owner.world_coords=engine.math_2d.moveAlongVector(self.owner.speed,self.owner.world_coords,self.owner.heading,time_passed)


            # this is expensive, do we need to do it every update cycle? maybe put on a timer
            collide_obj=self.owner.world.check_collision_return_object(self.owner,self.ignore_list,True,False)
            if collide_obj !=None:
                if engine.penetration_calculator.check_passthrough(self.owner,collide_obj):
                    # add the collided object to ignore list so we don't hit it again
                    # this is mostly to deal with buildings where we would hit it a ton of times
                    print('passthrough: '+collide_obj.name)
                    # this causes invulnerability from AI bullets (but not from player bullets)
                    # i do not know why. either something goofy with how that ref is being passed or .. ? 
                    self.ignore_list.append(collide_obj)
                    print(len(self.ignore_list))
                else:
                    # bullet stuck in something. remove bullet from world
                    self.owner.world.remove_object(self.owner) 




    #---------------------------------------------------------------------------
