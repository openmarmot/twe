
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
module_last_update_date='July 16 2021' #date of last update

#global variables

class AIPanzerfaust(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # whether the grenade is active or inactive
        self.launched=False

        # whether the grenade collided with something
        self.collided=False

        # time in flight
        self.flightTime=0
        # max flight time, basically the fuse length
        self.maxTime=3.

        # amount of shrapnel (basically grenade power)
        self.shrapnel_count=60

        # the object (human) that actually equipped this weapon
        # set by ai_man.event_inventory
        self.equipper=None

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        time_passed=self.owner.world.graphic_engine.time_passed_seconds



        if self.launched:
            self.flightTime+=time_passed
            if(self.flightTime>self.maxTime):
                self.explode()
            # move along path
            self.owner.world_coords=engine.math_2d.moveAlongVector(self.owner.speed,self.owner.world_coords,self.owner.heading,time_passed)

            
            if self.owner.world.check_collision_bool(self.owner,[self.equipper],True,False):
                self.explode()
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    def explode(self):
        # kablooey!
        # add the shrapnel
        target_coords=engine.math_2d.moveAlongVector(self.owner.speed,self.owner.world_coords,self.owner.heading,2)
        engine.world_builder.spawn_shrapnel_cone(self.owner.world,self.owner.world_coords,target_coords,self.shrapnel_count)

        # remove the grenade
        # this also stops code execution for this object as its not anywhere else
        self.owner.world.remove_object(self.owner)

    #---------------------------------------------------------------------------
    def launch(self,TARGET_COORDS):

        # whatever is calling this should add the panzerfaust to the world map and remove it from inventory

        self.launched=True

        # change image from the whole thing to just the warhead
        self.owner.image_index=1

        # reset coords 
        self.owner.world_coords=copy.copy(self.equipper.world_coords)
        if self.equipper.is_player :
            # do computations based off of where the mouse is. TARGET_COORDS is ignored
            self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world.graphic_engine.get_player_screen_coords(),self.owner.world.graphic_engine.get_mouse_screen_coords())
            self.owner.heading=engine.math_2d.get_heading_vector(self.owner.world.graphic_engine.get_player_screen_coords(),self.owner.world.graphic_engine.get_mouse_screen_coords())
        else :
            self.owner.rotation_angle=engine.math_2d.get_rotation(self.equipper.world_coords,TARGET_COORDS)
            self.owner.heading=engine.math_2d.get_heading_vector(self.equipper.world_coords,TARGET_COORDS)

        self.owner.reset_image=True



