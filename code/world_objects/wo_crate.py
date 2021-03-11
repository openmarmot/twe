'''
module : wo_crate.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :

generic crate that can hold stuff

'''


#import built in modules
import random

#import custom packages
from engine.world_object import WorldObject
from world_objects.wo_gun import WOGun

# module specific variables
module_version='0.0' #module software version
module_last_update_date='March 08 2021' #date of last update

#global variables

class WOCrate(WorldObject):

    def __init__(self, world,crate_type):
        super().__init__(world)
        
        self.render_level=1
        self.crate_type=crate_type
        self.image_name='crate'
        self.name='crate'
        self.is_crate=True
        
       # self.ai=AIZombie(self) # not sure this needs multiple AI

        if self.crate_type=='mp40_crate':
            # generate several mp40s and put them in worldobject.inventory
            # !! -- this needs to be re-done to use world_menu
            for x in range(random.randint(0,5)):
                mp40=WOGun(world,'mp40')
                self.inventory.append(mp40)



    #---------------------------------------------------------------------------
    def update(self, time_passed):
        ''' overrides base update '''
        # no need for a seperate AI in this class 

        # but -- does this even an update at all?



