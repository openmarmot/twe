
'''
module : ai_liquid_container.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules
import copy 

#import custom packages
from ai.ai_base import AIBase
# module specific variables
module_version='0.0' #module software version
module_last_update_date='September 20 2022' #date of last update

# this is for objects that don't need AI

#global variables

class AILiquidContainer(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # new containers are None. after that they can be gas/diesel/water/anything
        self.liquid_type = None

        # contaminated if liquid_type isn't the same as what is added
        self.contaminated = False

        # these are in liters 
        self.total_volume = 0
        self.used_volume = 0 # filled volume

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------
    def event_add_liquid(self,EVENT_DATA):
        # EVENT_DATA - [string liquid type, float amount]

        if self.liquid_type == None :
            self.liquid_type=EVENT_DATA[0]
        else:
            if self.liquid_type != EVENT_DATA[0]:
                self.liquid_type=EVENT_DATA[0]
                self.contaminated=True

        if (self.used_volume+EVENT_DATA[1])>self.total_volume:
            self.used_volume=self.total_volume
            print('spill') # probably spawn a spilled liquid sprite in the future
        else:
            self.used_volume+=EVENT_DATA[1]
    
    #---------------------------------------------------------------------------
    def event_remove_liquid(self,EVENT_DATA):

        if (self.used_volume-EVENT_DATA[1])>-1:
            self.used_volume-=EVENT_DATA[1]
        else:
            print('Your attempt to remove more liquid than the container holds spawns a black hole')


    #---------------------------------------------------------------------------
    def handle_event(self, EVENT, EVENT_DATA):
        ''' overrides base handle_event'''
        # EVENT - text describing event
        # EVENT_DATA - most likely a world_object but could be anything

        if EVENT=='add_liquid':
            self.event_add_inventory(EVENT_DATA)
        #elif EVENT=='collision':
        #    self.event_collision(EVENT_DATA)
        elif EVENT=='remove_liquid':
            self.event_remove_inventory(EVENT_DATA)
        else:
            print('Error: '+self.owner.name+' cannot handle event '+EVENT)
