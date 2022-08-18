
'''
module : ai_none.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase
# module specific variables
module_version='0.0' #module software version
module_last_update_date='August 17 2022' #date of last update

# this is for objects that don't need AI

#global variables

class AIConsumable(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # positive or negative. will be added to corresponding attribute
        self.health_effect=0
        self.hunger_effect=0
        self.thirst_effect=0
        self.fatigue_effect=0
        self.spoiled=False

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------
