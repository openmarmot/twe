'''
module : wo_vehicle.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :

vehicle class - reusable for all vehicles - or maybe just the unarmed ones

'''


#import built in modules

#import custom packages
from engine.world_object import WorldObject

# module specific variables
module_version='0.0' #module software version
module_last_update_date='March 10 2021' #date of last update

#global variables

class WOVehicle(WorldObject):

    def __init__(self, world,vehicle_type):
        super().__init__(world)
        
        self.render_level=1
        self.vehicle_type=vehicle_type
        self.is_vehicle=True
       # self.ai=AIZombie(self) # not sure this needs multiple AI

        if vehicle_type=='kubelwagen':
            # generate a new mag
            self.image_name='kubelwagen'
            self.name='kubelwagen'

    #---------------------------------------------------------------------------
    def change_magazine(self,magazine):
        ''' change magazine. input is new magazine. output is old magazine'''
        old=self.mag
        self.mag=magazine
        return old

    #---------------------------------------------------------------------------
    def update(self, time_passed):
        ''' overrides base update '''
        # no need for a seperate AI in this class as all guns should have the same AI

        # but -- does this even an update at all?



