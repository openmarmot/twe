
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

        # max flight time
        self.maxTime=5.
        self.ignore_list=[]

        # matches up with the projectile_data dict in penetration_calculator.py
        self.projectile_type=None

        self.is_shrapnel=False # not used at the moment
        self.is_bullet=False # not used at the moment

        # the weapon that created this
        self.weapon_name=''
        # the equipper of the gun that fired the projectile
        self.shooter=None

        self.speed=0

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        time_passed=self.owner.world.graphic_engine.time_passed_seconds

        self.flightTime+=time_passed
        if(self.flightTime>self.maxTime):
            engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'dirt',True)
            self.owner.world.remove_object(self.owner)
        else:

            # move along path
            self.owner.world_coords=engine.math_2d.moveAlongVector(self.speed,self.owner.world_coords,self.owner.heading,time_passed)


            # this is expensive, do we need to do it every update cycle? maybe put on a timer
            collide_obj=self.owner.world.check_collision_return_object(self.owner,self.ignore_list,True,False,True)
            if collide_obj !=None:
                if self.owner.world.penetration_calculator.check_passthrough(self.owner,collide_obj):
                    # add the collided object to ignore list so we don't hit it again
                    # this is mostly to deal with buildings where we would hit it a ton of times
                    self.ignore_list.append(collide_obj)
                else:
                    # bullet stuck in something. remove bullet from world
                    self.owner.world.remove_object(self.owner) 


