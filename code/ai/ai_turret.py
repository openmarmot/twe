
'''
module : ai_turret.py
language : Python 3.x
email : andrew@openmarmot.com
notes : the turret for a tank, or the mg mount on a vehicle
'''

#import built in modules

#import custom packages
from ai.ai_base import AIBase

# this is for objects that don't need AI

#global variables

class AITurret(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------
