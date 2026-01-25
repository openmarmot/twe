
'''
repo : https://github.com/openmarmot/twe

notes : hit marker
'''

#import built in modules
import copy

#import custom packages
import engine.math_2d
import engine.log
import random


#global variables

class AIHitMarker():
    def __init__(self, owner):
        self.owner=owner

        # hit_data object
        self.hit_data=None

        self.hit_object=None
        self.last_position=[0,0]
        self.last_rotation=0

        self.spawn_time=0
        self.max_alive_time=60
        self.self_remove=False

    #---------------------------------------------------------------------------
    def setup(self,hit_obj,hit_data):
        '''setup the hit market object'''
        # penetrated = bool whether it penetrated or not
        # side = string. what side was hit
        self.hit_object=hit_obj
        self.hit_data=hit_data
        if hit_data.penetrated:
            self.owner.image_index=1
            self.self_remove=True
            self.spawn_time=self.owner.world.world_seconds
        else:
            self.self_remove=True
            self.spawn_time=self.owner.world.world_seconds

        # make sure the initial angle is correct 
        self.owner.reset_image=True
        self.owner.rotation_angle=engine.math_2d.get_normalized_angle(self.hit_object.rotation_angle+self.hit_data.rotation_offset)
        self.owner.world_coords=engine.math_2d.calculate_relative_position(self.hit_object.world_coords,self.hit_object.rotation_angle,self.hit_data.position_offset)

    #---------------------------------------------------------------------------
    def update(self):
        self.update_physics()

        if self.self_remove:
            if self.spawn_time+self.max_alive_time<self.owner.world.world_seconds:
                self.owner.wo_stop()
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



