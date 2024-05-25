
'''
module : ai_liquid.py
language : Python 3.x
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

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # evaporate

        # leak 

    #---------------------------------------------------------------------------
