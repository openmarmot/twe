
'''
module : ai_container.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase
# module specific variables
module_version='0.0' #module software version
module_last_update_date='November 13 2021' #date of last update

# this is for objects that don't need AI

#global variables

class AIContainer(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        self.inventory=[]

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    def handle_event(self, EVENT, EVENT_DATA):
        ''' overrides base handle_event'''
        # EVENT - text describing event
        # EVENT_DATA - most likely a world_object but could be anything

        # not sure what to do here yet. will have to think of some standard events
        #if EVENT=='add_inventory':
        #    self.event_add_inventory(EVENT_DATA)
        #elif EVENT=='collision':
        #    self.event_collision(EVENT_DATA)

        pass
