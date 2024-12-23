
'''
module : ai_map_pointer.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
'''

#import built in modules

#import custom packages
import engine.math_2d

#global variables

class AIMapPointer(object):
    def __init__(self, owner):
        self.owner=owner
        self.target_coords=None

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world.player.world_coords,self.target_coords)
        self.owner.heading=engine.math_2d.get_heading_vector(self.owner.world.player.world_coords,self.target_coords)
        self.owner.world_coords=engine.math_2d.moveAlongVector(125,self.owner.world.player.world_coords,self.owner.heading,1)
        self.owner.reset_image=True

    #---------------------------------------------------------------------------
