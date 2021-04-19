
'''
module : ai_grenade.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules
import copy

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
import engine.world_builder 

# module specific variables
module_version='0.0' #module software version
module_last_update_date='April 15 2021' #date of last update

#global variables

class AIGrenade(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # whether the grenade is active or inactive
        self.thrown=False

        # time in flight
        self.flightTime=0
        # max flight time, basically the fuse length
        self.maxTime=5.

        # amount of shrapnel (basically grenade power)
        self.shrapnel_count=40

        # the object (human) that actually equipped this weapon
        # set by ai_man.event_inventory
        self.equipper=None

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        time_passed=self.owner.world.graphic_engine.time_passed_seconds



        if self.thrown:
            self.flightTime+=time_passed
            if(self.flightTime>self.maxTime):
                self.explode()
            # move along path
            self.owner.world_coords=engine.math_2d.moveAlongVector(self.owner.speed,self.owner.world_coords,self.owner.heading,time_passed)

            if self.owner.world.check_collision_bool(self.owner,[self.equipper],False,True):
                # just stop the grenade. maybe some spin or reverse movement?
                if self.owner.speed>1:
                    self.owner.speed=-1
                else:
                    self.owner.speed-=2
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    def explode(self):
        # kablooey!
        # add the shrapnel
        engine.world_builder.spawn_shrapnel_cloud(self.owner.world,self.owner.world_coords,self.shrapnel_count)

        # remove the grenade
        # this also stops code execution for this object as its not anywhere else
        self.owner.world.remove_object(self.owner)

    #---------------------------------------------------------------------------
    def throw(self,TARGET_COORDS):

        # whatever is calling this should add the grenade to the world map (if it isn't there)

        # MOUSE_AIM bool as to whether you want to throw it at the mouse
        self.thrown=True

        # reset coords 
        self.owner.world_coords=copy.copy(self.equipper.world_coords)
        if self.equipper.is_player :
            # do computations based off of where the mouse is. TARGET_COORDS is ignored
            self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world.graphic_engine.get_player_screen_coords(),self.owner.world.graphic_engine.get_mouse_screen_coords())
            self.owner.heading=engine.math_2d.get_heading_vector(self.owner.world.graphic_engine.get_player_screen_coords(),self.owner.world.graphic_engine.get_mouse_screen_coords())
        else :
            self.owner.rotation_angle=engine.math_2d.get_rotation(self.equipper.world_coords,TARGET_COORDS)
            self.owner.heading=engine.math_2d.get_heading_vector(self.equipper.world_coords,TARGET_COORDS)



