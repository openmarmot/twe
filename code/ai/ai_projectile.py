
'''
module : ai_projectile.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
'''

#import built in modules
import random 

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

        # initial coordinates for the bullet. set when fired
        # used for distance calculation for penetration testing
        self.starting_coords=None

        # max flight time
        self.maxTime=5.
        self.ignore_list=[]

        # variables for collision checks
        self.last_collision_check=0
        self.collision_check_interval=0.1

        # matches up with the projectile_data dict in penetration_calculator.py
        self.projectile_type=None


        # the weapon that created this
        self.weapon_name=''
        # the equipper of the gun that fired the projectile. this can be a human or a turret
        self.shooter=None

        self.speed=0

    #---------------------------------------------------------------------------
    def contact_effect(self):
        # kablooey!
        print('kablooey!')
        # add the shrapnel
        target_coords=engine.math_2d.moveAlongVector(self.speed,self.owner.world_coords,self.owner.heading,2)
        shrapnel_count=engine.penetration_calculator.projectile_data[self.projectile_type]['shrapnel_count']
        contact_effect=engine.penetration_calculator.projectile_data[self.projectile_type]['contact_effect']
        if contact_effect=='HEAT':
            engine.world_builder.spawn_flash(self.owner.world,self.owner.world_coords,engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle))
            engine.world_builder.spawn_heat_jet(self.owner.world,self.owner.world_coords,target_coords,shrapnel_count,self.shooter,self.owner.name)
            engine.world_builder.spawn_sparks(self.owner.world,self.owner.world_coords,random.randint(1,10))
        else:
            print('ERROR - projectile ai contact_effect not recognized: ',contact_effect)

        # remove the grenade
        # this also stops code execution for this object as its not anywhere else
        self.owner.world.remove_queue.append(self.owner)


    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        time_passed=self.owner.world.time_passed_seconds

        self.flightTime+=time_passed
        if(self.flightTime>self.maxTime):
            if engine.penetration_calculator.projectile_data[self.projectile_type]['contact_effect']!='none':
                self.contact_effect()
            else:
                engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'dirt',True)
                # remove from world
                self.owner.world.remove_queue.append(self.owner)
        else:

            # move along path
            self.owner.world_coords=engine.math_2d.moveAlongVector(self.speed,self.owner.world_coords,self.owner.heading,time_passed)

            # check collision 
            if self.flightTime>self.last_collision_check+self.collision_check_interval:
                self.last_collision_check=self.flightTime
                objects=self.owner.world.wo_objects_human+self.owner.world.wo_objects_vehicle+self.owner.world.wo_objects_building
                collide_obj=self.owner.world.check_collision_return_object(self.owner,self.ignore_list,objects,True)
                if collide_obj !=None:
                    if engine.penetration_calculator.projectile_data[self.projectile_type]['contact_effect']!='none':
                        # bullet has collided and exploded
                        self.contact_effect()
                    else:
                        penetration=engine.penetration_calculator.calculate_penetration(self.owner,collide_obj)
                        if penetration:
                            collide_obj.ai.handle_event('collision',self.owner)
                            # bullet has collided, check if it over penetrates and keeps going
                            if engine.penetration_calculator.check_passthrough(self.owner,collide_obj):
                                # add the collided object to ignore list so we don't hit it again
                                # this is mostly to deal with buildings where we would hit it a ton of times
                                self.ignore_list.append(collide_obj)
                            else:
                                # bullet stuck in something. remove bullet from world
                                self.owner.world.remove_queue.append(self.owner) 
                        else:
                            # penetration fails! 
                            # should probably have some sort of non-penetration event
                            #engine.world_builder.spawn_flash(self.owner.world,self.owner.world_coords,engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle))
                            engine.world_builder.spawn_sparks(self.owner.world,self.owner.world_coords,random.randint(1,3))
                            self.owner.world.remove_queue.append(self.owner) 


