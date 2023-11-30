
'''
module : ai_magazine.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes : A (gun) magazine is a object that holds projectiles
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase
# module specific variables
module_version='0.0' #module software version

#global variables

class AIMagazine(AIBase):
    def __init__(self, owner):
        super().__init__(owner)
        # list of compatible gun names
        self.compatible_guns=[]

        # list of compatible projectiles
        # from projectile_data dict in penetration_calculator.py
        self.compatible_projectiles=[]

        # int max number of projectiles
        self.capacity=0

        # whether the magazine is integrated into the gun or not
        self.removable=True

        # list of projectiles (world_object)
        self.projectiles=[]
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------
