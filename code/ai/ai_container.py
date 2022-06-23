
'''
module : ai_container.py
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
    def event_add_inventory(self,EVENT_DATA):
        self.inventory.add(EVENT_DATA)
    
    #---------------------------------------------------------------------------
    def event_remove_inventory(self,EVENT_DATA):

        if EVENT_DATA in self.inventory:

            # make sure the obj world_coords reflect the obj that had it in inventory
            EVENT_DATA.world_coords=copy.copy(self.owner.world_coords)

            self.inventory.remove(EVENT_DATA)


    #---------------------------------------------------------------------------
    def handle_event(self, EVENT, EVENT_DATA):
        ''' overrides base handle_event'''
        # EVENT - text describing event
        # EVENT_DATA - most likely a world_object but could be anything

        if EVENT=='add_inventory':
            self.event_add_inventory(EVENT_DATA)
        #elif EVENT=='collision':
        #    self.event_collision(EVENT_DATA)
        elif EVENT=='remove_inventory':
            self.event_remove_inventory(EVENT_DATA)
