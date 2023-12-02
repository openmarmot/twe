
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


        # the weapon that created this
        self.weapon_name=''
        # the equipper of the gun that fired the projectile
        self.shooter=None

        self.speed=0

    #---------------------------------------------------------------------------
    def contact_effect(self):
        # kablooey!
        print('kablooey!')
        # add the shrapnel
        target_coords=engine.math_2d.moveAlongVector(self.speed,self.owner.world_coords,self.owner.heading,2)
        shrapnel_count=self.owner.world.penetration_calculator.projectile_data[self.projectile_type]['shrapnel_count']
        contact_effect=self.owner.world.penetration_calculator.projectile_data[self.projectile_type]['contact_effect']
        if contact_effect=='HEAT':
            engine.world_builder.spawn_heat_jet(self.owner.world,self.owner.world_coords,target_coords,shrapnel_count,self.shooter,self.owner.name)
        else:
            print('ERROR - projectile ai contact_effect not recognized: ',contact_effect)

        # remove the grenade
        # this also stops code execution for this object as its not anywhere else
        self.owner.world.remove_object(self.owner)


    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        time_passed=self.owner.world.graphic_engine.time_passed_seconds

        self.flightTime+=time_passed
        if(self.flightTime>self.maxTime):
            if self.owner.world.penetration_calculator.projectile_data[self.projectile_type]['contact_effect']!='none':
                self.contact_effect()
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
                    if self.owner.world.penetration_calculator.projectile_data[self.projectile_type]['contact_effect']!='none':
                        self.contact_effect()
                    else:
                        if self.owner.world.penetration_calculator.check_passthrough(self.owner,collide_obj):
                            # add the collided object to ignore list so we don't hit it again
                            # this is mostly to deal with buildings where we would hit it a ton of times
                            self.ignore_list.append(collide_obj)
                        else:
                            # bullet stuck in something. remove bullet from world
                            self.owner.world.remove_object(self.owner) 


