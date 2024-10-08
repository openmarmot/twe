
'''
module : ai_throwable.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
'''

#import built in modules
import copy

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
import engine.world_builder 



#global variables

class AIThrowable(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # whether the grenade is active or inactive
        self.thrown=False

        # whether the grenade collided with something
        self.collided=False

        # time in flight
        self.flightTime=0
        # max flight time, basically the fuse length
        self.maxTime=5.

        # default speed
        self.max_speed=0

        # current speed
        self.speed=0

        # does this object explode?
        self.explosive=False
        # amount of shrapnel (basically grenade power)
        self.shrapnel_count=40

        # the object (human) that actually equipped this weapon
        # set by ai_man.event_inventory
        self.equipper=None

        self.redirected=False

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        time_passed=self.owner.world.time_passed_seconds



        if self.thrown:
            self.flightTime+=time_passed
            if(self.flightTime>self.maxTime):
                if self.explosive:
                    self.explode()
                else:
                    # reset. should stop movement
                    self.thrown=False
                    self.flightTime=0
                    self.speed=self.max_speed
            # move along path
            self.owner.world_coords=engine.math_2d.moveAlongVector(self.speed,self.owner.world_coords,self.owner.heading,time_passed)

            # give it a little time to get away from the thrower 
            if self.flightTime>0.1:
                objects=self.owner.world.wo_objects_human+self.owner.world.wo_objects_vehicle
                ignore=[self.equipper]
                if self.owner.world.check_collision_return_object(self.owner,ignore,objects,True) !=None:
                    # just stop the grenade. maybe some spin or reverse movement?
                    if self.redirected==False:
                        self.speed=-20
                        self.flightTime=self.maxTime-1
                    else:
                        # basically give it another chance to collide
                        self.redirected=False

    #---------------------------------------------------------------------------
    def explode(self):
        # kablooey!
        # add the shrapnel
        engine.world_builder.spawn_shrapnel_cloud(self.owner.world,self.owner.world_coords,self.shrapnel_count,self.equipper,self.owner.name)

        # remove the grenade
        # this also stops code execution for this object as its not anywhere else
        self.owner.world.remove_queue.append(self.owner)

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

