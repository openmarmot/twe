
'''
module : ai_turret.py
language : Python 3.x
email : andrew@openmarmot.com
notes : hit marker
'''

#import built in modules
import copy

#import custom packages
import engine.math_2d
import engine.log
import random


#global variables

class AIHitMarker(object):
    def __init__(self, owner):
        self.owner=owner

        # hit_data object
        self.hit_data=None

        self.hit_object=None
        self.last_position=[0,0]
        self.last_rotation=0

    #---------------------------------------------------------------------------
    def setup(self,hit_obj,hit_data):
        '''setup the hit market object'''
        # penetrated = bool whether it penetrated or not
        # side = string. what side was hit
        self.hit_object=hit_obj
        self.hit_data=hit_data
        if hit_data.penetrated:
            self.owner.image_index=1

        # run this once to get the correct angles
        self.update_physics()

    #---------------------------------------------------------------------------
    def update(self):
        self.update_physics()
    #---------------------------------------------------------------------------
    def update_physics(self):
        moved=False

        if self.last_position!=self.hit_object.world_coords:
            moved=True
            self.last_position=copy.copy(self.hit_object.world_coords)
        elif self.last_rotation!=self.hit_object.rotation_angle:
            moved=True
            self.last_rotation=copy.copy(self.hit_object.rotation_angle)

        if moved:
            self.owner.reset_image=True
            self.owner.rotation_angle=engine.math_2d.get_normalized_angle(self.hit_object.rotation_angle+self.hit_data.rotation_offset)
            self.owner.world_coords=engine.math_2d.calculate_relative_position(self.hit_object.world_coords,self.hit_object.rotation_angle,self.hit_data.position_offset)


