'''
module : wo_gun.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :

gun class that should be re-usable for all regular guns in game

'''


#import built in modules

#import custom packages
from engine.world_object import WorldObject
from wo_gun_mag import WOGunMag
# module specific variables
module_version='0.0' #module software version
module_last_update_date='Sept 08 2020' #date of last update

#global variables

class WOGun(WorldObject):

    def __init__(self, world,type):
        super().__init__(world)
        self.image_name='mp40'
        self.render_level=1
        self.type=type
        self.mag=None # mag object is a wo_gun_mag
       # self.ai=AIZombie(self) # not sure this needs multiple AI

        if type=='mp40':
            # generate a new mag
            self.mag=WOGunMag(world,'mp40')

    #---------------------------------------------------------------------------
    def update(self, time_passed):
        ''' overrides base update '''
        # no need for a seperate AI in this class as all guns should have the same AI

        # but -- does this even an update at all?

    #---------------------------------------------------------------------------
    def change_magazine(magazine)
        ''' change magazine. input is new magazine. output is old magazine'''
        old=self.mag
        self.mag=magazine
        return old

