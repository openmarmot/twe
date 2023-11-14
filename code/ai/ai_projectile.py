
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

        # variables for collision checks
        self.last_collision_check=0
        self.collision_check_interval=0.1

        # matches up with the projectile_data dict in penetration_calculator.py
        self.projectile_type=None

        self.is_shrapnel=False # not used at the moment
        self.is_bullet=False # not used at the moment

        self.is_explosive=False
        self.shrapnel_count=0

        # the weapon that created this
        self.weapon_name=''
        # the equipper of the gun that fired the projectile
        self.shooter=None

        self.speed=0

    #---------------------------------------------------------------------------
    def explode(self):
        # kablooey!
        # add the shrapnel
        target_coords=engine.math_2d.moveAlongVector(self.speed,self.owner.world_coords,self.owner.heading,2)
        engine.world_builder.spawn_heat_jet(self.owner.world,self.owner.world_coords,target_coords,self.shrapnel_count,self.equipper,self.owner.name)

        # remove the grenade
        # this also stops code execution for this object as its not anywhere else
        self.owner.world.remove_object(self.owner)

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        time_passed=self.owner.world.graphic_engine.time_passed_seconds

        self.flightTime+=time_passed
        if(self.flightTime>self.maxTime):
            if self.is_explosive:
                self.explode()
            else:
                engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'dirt',True)
                self.owner.world.remove_object(self.owner)
        else:

            # move along path
            self.owner.world_coords=engine.math_2d.moveAlongVector(self.speed,self.owner.world_coords,self.owner.heading,time_passed)

            # check collision 
            if self.flightTime>self.last_collision_check+self.collision_check_interval:
                self.last_collision_check=self.flightTime
                collide_obj=self.owner.world.check_collision_return_object(self.owner,self.ignore_list,True,False,True)
                if collide_obj !=None:
                    if self.is_explosive:
                        self.explode()
                    else:
                        if self.owner.world.penetration_calculator.check_passthrough(self.owner,collide_obj):
                            # add the collided object to ignore list so we don't hit it again
                            # this is mostly to deal with buildings where we would hit it a ton of times
                            self.ignore_list.append(collide_obj)
                        else:
                            # bullet stuck in something. remove bullet from world
                            self.owner.world.remove_object(self.owner) 


