
'''
module : ai_container.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes : not sure this is needed 
'''


#import built in modules
import copy 

#import custom packages
from ai.ai_base import AIBase


# this is for objects that don't need AI

#global variables

class AIContainer(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        self.inventory=[]

        # contaminated if liquid_type isn't the same as what is added
        self.contaminated = False

        # self sealing fuel tanks should be relatively uncommon
        self.self_sealing= False

        self.punctured=False
        
        # decimal percent. 0 is none, 1 is uh maximum puncture
        self.punctured_percent=0

        # this is in the base object
        # these are in liters 
        #self.total_volume = 0
        #self.used_volume = 0 # filled volume

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # check if leaking 

        # check if contaminated 
        if not self.contaminated:
            liquid=False
            liquid_count=0
            solid=False
            for b in self.inventory:
                if b.is_liquid:
                    liquid=True
                    liquid_count+=1
                elif b.is_solid:
                    solid=True
            
            if liquid_count>1:
                self.contaminated=True
            if liquid==True and solid==True:
                self.contaminated=True

            # apply contamination to inventory objects
            if self.contaminated:
                pass

    #---------------------------------------------------------------------------
    def event_add_inventory(self,EVENT_DATA):
        self.owner.world.remove_object(EVENT_DATA)
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
        else:
            print('Error: '+self.owner.name+' cannot handle event '+EVENT)