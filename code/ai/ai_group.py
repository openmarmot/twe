
'''
module : ai_group.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes : AI that makes decisions for groups 
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
# module specific variables
module_version='0.0' #module software version
module_last_update_date='April 21 2021' #date of last update


#global variables

class AINone(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # ai in the group will try to stay close to the group world coords
        self.world_coords=[0.,0.]
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------
