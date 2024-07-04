
'''
module : ai_wearable.py
language : Python 3.x
email : andrew@openmarmot.com
notes : a wearable is a piece of clothing armor, etc. something you can wear
'''

#import built in modules

#import custom packages
from ai.ai_base import AIBase


# this is for objects that don't need AI

#global variables

class AIWearable(AIBase):
    def __init__(self, owner):
        super().__init__(owner)
        # head / whatever
        self.wearable_region='none'
        # thickness of armor grade steel in mm
        self.armor_thickness=0

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------
