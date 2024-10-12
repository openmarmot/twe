
'''
module : ai_none.py
language : Python 3.x
email : andrew@openmarmot.com
notes : default ai class for objects that don't use AI
'''

#import built in modules
import copy

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d



class AIGroundCover(AIBase):
    def __init__(self, owner):
        super().__init__(owner)
        self.position_offset=[0,0]
        self.initial_offset=[-4000,-4000]
        self.last_distance=0

    #---------------------------------------------------------------------------
    def update(self):
        distance=engine.math_2d.get_distance(self.owner.world.player.world_coords,self.owner.world_coords)
        if distance>(self.last_distance+1500):
            for b in self.owner.world.wo_objects:
                if b.is_ground_texture:
                    b.ai.reset_offset()
            #self.reset_offset()
            self.last_distance=distance
    #---------------------------------------------------------------------------
            
    def reset_offset(self):
        coords=engine.math_2d.get_vector_addition(self.owner.world.player.world_coords,self.initial_offset)
        self.owner.world_coords=engine.math_2d.get_vector_addition(coords,self.position_offset)
