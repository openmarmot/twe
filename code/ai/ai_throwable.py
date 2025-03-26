
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
'''

#import built in modules
import copy
import random

#import custom packages
import engine.math_2d
import engine.world_builder 



#global variables

class AIThrowable(object):
    def __init__(self, owner):
        self.owner=owner

        # whether the grenade is active or inactive
        self.thrown=False

        # whether the grenade collided with something
        self.collided=False

        # time in flight
        self.flightTime=0
        # max flight time, basically the fuse length
        self.max_flight_time=3.

        # default speed
        self.max_speed=0

        # current speed
        self.speed=0

        # this is checked by ai_human when determining if a grenade throw is in range
        self.range=310

        # objects to ignore for collision purposes
        self.ignore_list=[]

        self.has_fuse=False
        self.fuse_active=False
        self.fuse_active_time=0
        self.fuse_max_time=5

        # does this object explode?
        self.explosive=False
        # amount of shrapnel (basically grenade power)
        self.shrapnel_count=0
        self.explosion_radious=15

        # explode when it hits something
        self.explode_on_contact=False
        self.unreliable_contact_fuse=False

        # does this object result in a fire 
        self.flammable=False
        # number of flame areas
        self.flame_amount=0

        # is the objecct a HEAT projectile
        self.heat=False
        self.heat_projectile_type=None # matches up with the projectile_data dict in penetration_calculator.py

        # the object (human) that actually equipped this weapon
        # set by ai_man.event_inventory
        self.equipper=None

        self.redirected=False

        # gives the AI hints on how to use this weapon
        self.use_antitank=False
        self.use_antipersonnel=False

    #---------------------------------------------------------------------------
    def handle_explosion(self):
        '''handles all the various explosion types and effects'''

        if self.explosive:
            self.explode()
        if self.flammable:
            self.explode_flame()
        if self.heat:
            self.explode_heat()

        self.owner.world.remove_queue.append(self.owner)

    #---------------------------------------------------------------------------
    def explode(self):        
        self.owner.world.create_explosion(self.owner.world_coords,15,self.shrapnel_count,self.equipper,self.owner.name,0.5,1)

    #---------------------------------------------------------------------------
    def explode_flame(self):

        for flame in range(self.flame_amount):
            coords=engine.math_2d.randomize_coordinates(self.owner.world_coords,random.randint(15,75))
            engine.world_builder.spawn_explosion_and_fire(self.owner.world,self.owner.world_coords,10,5)

            possible=self.owner.world.wo_objects_human+self.owner.world.wo_objects_vehicle

            hit_list=engine.math_2d.checkCollisionCircleCoordsAllResults(coords,10,possible,[])

            for hit in hit_list:
                hit.ai.handle_hit_with_flame()

        self.owner.world.remove_queue.append(self.owner)

    #---------------------------------------------------------------------------
    def explode_heat(self):
        target_coords=engine.math_2d.moveAlongVector(self.speed,self.owner.world_coords,self.owner.heading,2)
        engine.world_builder.spawn_flash(self.owner.world,self.owner.world_coords,engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle))
        engine.world_builder.spawn_heat_jet(self.owner.world,self.owner.world_coords,target_coords,1,self.heat_projectile_type,self.equipper,self.owner.name)
        engine.world_builder.spawn_sparks(self.owner.world,self.owner.world_coords,random.randint(1,5))

    #---------------------------------------------------------------------------
    def redirect(self,target_coords):
        ''' redirect/rethrow after grenade has been thrown'''
        print('redirect')
        # grenade should already be thrown
        if self.thrown==False:
            print('grenade error, redirect w/o thrown')
        
        self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,target_coords)
        self.owner.heading=engine.math_2d.get_heading_vector(self.owner.world_coords,target_coords)
        self.collided=True
        self.speed=190
        self.maxTime-=self.flightTime
        # subtract a little extra for the time it takes to pick it up
        self.maxTime-=0.5 
        self.flightTime=0
        self.redirected=True

        # clear the ignore list so it can collide with anything 
        self.ignore_list=[]

    #---------------------------------------------------------------------------
    def throw(self):
        '''throw the object'''
        if self.equipper!=None:
            if self.equipper.is_human:
                self.ignore_list=[]
                self.ignore_list+=self.equipper.ai.squad.faction_tactical.allied_humans
        self.thrown=True
        self.flightTime=0
        self.speed=self.max_speed
        
        if self.has_fuse:
            self.fuse_active=True
            self.fuse_active_time=0

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        time_passed=self.owner.world.time_passed_seconds

        if self.has_fuse:
            if self.fuse_active:
                self.fuse_active_time+=time_passed

                if self.fuse_active_time>self.fuse_max_time:
                    self.handle_explosion()
                    return

        if self.thrown:
            self.flightTime+=time_passed
            if(self.flightTime>self.max_flight_time):

                if self.explode_on_contact:
                    if self.unreliable_contact_fuse:
                        if random.randint(0,1)==1:
                            self.handle_explosion()
                        else:
                            # contact explosion failed, just reset the grenade
                            self.thrown=False
                            self.flightTime=0
                            self.speed=self.max_speed
                    else:
                        self.handle_explosion()
                else:

                    # reset. should stop movement
                    self.thrown=False
                    self.flightTime=0
                    self.speed=self.max_speed
            else:
                # move along path
                self.owner.world_coords=engine.math_2d.moveAlongVector(self.speed,self.owner.world_coords,self.owner.heading,time_passed)

                # give it a little time to get away from the thrower 
                if self.flightTime>0.1:
                    objects=self.owner.world.wo_objects_human+self.owner.world.wo_objects_vehicle
                    if self.owner.world.check_collision_return_object(self.owner,self.ignore_list,objects,True) !=None:
                        if self.explode_on_contact:
                            if self.unreliable_contact_fuse:
                                if random.randint(0,1)==1:
                                    self.handle_explosion()
                                else:
                                    # contact explosion failed, just reset the grenade
                                    self.thrown=False
                                    self.flightTime=0
                                    self.speed=self.max_speed
                            else:
                                self.handle_explosion()

                        else:
                            # just stop the grenade. maybe some spin or reverse movement?
                            if self.redirected==False:
                                self.speed=-20
                                self.flightTime=self.max_flight_time-1

                                # clear the ignore list so it can collide with anything
                                self.ignore_list=[]

                            else:
                                # basically give it another chance to collide
                                self.redirected=False



