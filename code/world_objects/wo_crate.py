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
module_last_update_date='Jan 10 2021' #date of last update

#global variables

class WOCrate(WorldObject):

    def __init__(self, world,type):
        super().__init__(world)
        
        self.render_level=1
        self.type=type
        self.image_name='crate'
        self.name='crate'
        
       # self.ai=AIZombie(self) # not sure this needs multiple AI

        if type=='mp40_crate':
            # generate several mp40s and put them in worldobject.inventory
            for x in range(random.randint(0,5)):
                mp40=WOGun(world,'mp40')
                self.inventory.append(mp40)



    #---------------------------------------------------------------------------
    def update(self, time_passed):
        ''' overrides base update '''
        # no need for a seperate AI in this class as all guns should have the same AI

        # but -- does this even an update at all?



