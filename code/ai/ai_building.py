
'''
module : ai_building.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
# module specific variables
module_version='0.0' #module software version
module_last_update_date='March 28 2021' #date of last update

# this is for objects that don't need AI

#global variables

class AIBuilding(AIBase):
    def __init__(self, owner):
        super().__init__(owner)
        self.show_interior=False
        self.show_interior_distance=500
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        if self.show_interior :
            # check timeout to see if we should check distance to player
            pass
        else :
            # check distance to player
            b=engine.math_2d.get_distance(self.owner.world_coords,self.owner.world.player.world_coords)
            #print(str(b))
            if b<self.show_interior_distance:
                # show the inside
                self.owner.image_index=1
                # todo - start a cooldown before checking distance again
                # this way building aren't constantly flicking between inside and outside
            else:
                # show the outside
                self.owner.image_index=0
            
    #---------------------------------------------------------------------------
