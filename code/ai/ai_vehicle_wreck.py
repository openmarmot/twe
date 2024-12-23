
'''
module : ai_container.py
language : Python 3.x
email : andrew@openmarmot.com
notes : some extra stuff for vehicle wrecks
'''


#import built in modules
import copy 

#import custom packages
from ai.ai_base import AIBase


#global variables

class AIVehicleWreck(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        self.inventory=[]

        self.collision_log=[]

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        pass

    #---------------------------------------------------------------------------
    def event_add_inventory(self,event_data):

        self.inventory.append(event_data)
    
    #---------------------------------------------------------------------------
    def event_remove_inventory(self,event_data):

        if event_data in self.inventory:

            # make sure the obj world_coords reflect the obj that had it in inventory
            event_data.world_coords=copy.copy(self.owner.world_coords)

            self.inventory.remove(event_data)

    #---------------------------------------------------------------------------
    def handle_event(self, event, event_data):
        ''' overrides base handle_event'''
        # event - text describing event
        # event_data - most likely a world_object but could be anything

        if event=='add_inventory':
            self.event_add_inventory(event_data)
        #elif EVENT=='collision':
        #    self.event_collision(event_data)
        elif event=='remove_inventory':
            self.event_remove_inventory(event_data)
        else:
            print('Error: '+self.owner.name+' cannot handle event '+event)