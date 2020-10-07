'''
module : wo_gun_mag.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :

gun magazine class

No AI needed. update function will be skipped.

Not 100% sure this will have art. its too small to be visible in the game world

'''


#import built in modules

#import custom packages
from engine.world_object import WorldObject
# module specific variables
module_version='0.0' #module software version
module_last_update_date='Sept 08 2020' #date of last update

#global variables

class WOGunMag(WorldObject):

    def __init__(self, world,type):
        super().__init__(world)
        self.mag_type=type #string
        self.max_capacity=0
        self.bullets=0
        self.bullet_type=None #string

        if type=='mp40':
            self.max_capacity=32
            self.bullets=self.max_capacity
            self.bullet_type='9mm'

