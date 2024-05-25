
'''
module : ai_medical.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
'''

#import built in modules

#import custom packages
from ai.ai_base import AIBase

#global variables

class AIMedical(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # should have some special properties just for medical gear

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
