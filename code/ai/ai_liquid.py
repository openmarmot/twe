
'''
module : ai_liquid.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes : special characteristics for a liquid
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase


# this is for objects that don't need AI

#global variables

class AINone(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # string set on creation. gas/diesel/water/etc 
        self.liquid_type=None

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------
