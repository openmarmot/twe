
'''
repo : https://github.com/openmarmot/twe

notes :
'''

#import built in modules
import copy
import random

#import custom packages
import engine.math_2d
import engine.world_builder 



#global variables

class AIThrowable():
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

        # this is when the throwable is stuck on a vehicle and is moving with it
        self.on_vehicle=False
        self.vehicle=None

    #---------------------------------------------------------------------------
    def handle_explosion(self):
        '''handles all the various explosion types and effects'''

        if self.explosive:
            self.explode()
        if self.flammable:
            self.explode_flame()
        if self.heat:
            self.explode_heat()

        if self.on_vehicle:
            self.vehicle.ai.handle_event('throwable_explosion_on_top_of_vehicle',self.owner)

        self.owner.world.remove_queue.append(self.owner)

    #---------------------------------------------------------------------------
    def explode(self):        
        self.owner.world.create_explosion(self.owner.world_coords,self.explosion_radious,self.shrapnel_count,self.equipper,self.owner,0.5,1)

    #---------------------------------------------------------------------------
    def explode_flame(self):
        flame_radius=20
        self.owner.world.create_fire(self.owner.world_coords,self.flame_amount,flame_radius,10,5)

    #---------------------------------------------------------------------------
    def explode_heat(self):
        target_coords=engine.math_2d.moveAlongVector(self.speed,self.owner.world_coords,self.owner.heading,2)
        engine.world_builder.spawn_flash(self.owner.world,self.owner.world_coords,engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle))
        engine.world_builder.spawn_heat_jet(self.owner.world,self.owner.world_coords,target_coords,1,self.heat_projectile_type,self.equipper,self.owner)
        engine.world_builder.spawn_sparks(self.owner.world,self.owner.world_coords,random.randint(1,5))

    #---------------------------------------------------------------------------
    def redirect(self,target_coords):
        ''' redirect/rethrow after grenade has been thrown'''
        self.on_vehicle=False
        self.vehicle=None
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
                if self.on_vehicle:
                    # moves with the vehicle it is on
                    self.owner.world_coords=copy.copy(self.vehicle.world_coords)
                else:

                    # move along path
                    self.owner.world_coords=engine.math_2d.moveAlongVector(self.speed,self.owner.world_coords,self.owner.heading,time_passed)

                    # give it a little time to get away from the thrower 
                    if self.flightTime>0.1:
                        objects=self.owner.grid_square.wo_objects_projectile_collision
                        hit_object=self.owner.world.check_collision_return_object(self.owner,self.ignore_list,objects,True)
                        if hit_object is not None:
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

                                if hit_object.is_vehicle:
                                    # chance to get stuck on vehicle
                                    if random.randint(0,1)==1:
                                        self.on_vehicle=True
                                        self.vehicle=hit_object
                                        return

                                # just stop the grenade. maybe some spin or reverse movement?
                                if self.redirected==False:
                                    self.speed=-20
                                    self.flightTime=self.max_flight_time-1

                                    # clear the ignore list so it can collide with anything but what it just hit
                                    self.ignore_list=[hit_object]

                                else:
                                    # basically give it another chance to collide
                                    self.redirected=False



