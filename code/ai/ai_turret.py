
'''
module : ai_turret.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes : the turret for a tank, or the mg mount on a vehicle
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase
# module specific variables
module_version='0.0' #module software version
module_last_update_date='Dec 03 2021' #date of last update

# this is for objects that don't need AI

#global variables

class AITurret(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------
