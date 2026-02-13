
'''
repo : https://github.com/openmarmot/twe

notes : not sure this is needed 
'''


#import built in modules
import copy 

#import custom packages

#global variables

class AIContainer():
    def __init__(self, owner):
        self.owner=owner

        self.inventory=[]

        # contaminated if liquid_type isn't the same as what is added
        self.contaminated = False

        # self sealing fuel tanks should be relatively uncommon
        self.self_sealing= False

        self.punctured=False
        
        # 1 is fully intact, 0 is full of holes
        self.container_integrity=1

        # this is in the base object
        # these are in liters 
        #self.total_volume = 0
        #self.used_volume = 0 # filled volume

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # if puctured apply leak to liquid contents
        if self.punctured:
            for b in self.inventory:
                if b.is_liquid:
                    if b.volume > 0:
                        leak_rate = 1 - self.container_integrity
                        fractional_loss = b.volume * leak_rate * self.owner.world.time_passed_seconds
                        min_leak_rate = 0.5  # Fixed L/s baseline (tune this; e.g., 1.0 for faster)
                        fixed_loss = min_leak_rate * self.owner.world.time_passed_seconds
                        loss = max(fractional_loss, fixed_loss)  # Use the larger of fractional or fixed
                        b.volume = max(0, round(b.volume - loss, 2))  # Clamp to avoid negative

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
    def event_add_inventory(self,event_data):

        # merge liquids 
        if event_data.is_liquid:
            existing_liquid=None
            for b in self.inventory:
                if b.name==event_data.name:
                    existing_liquid=b
                    break
            
            if existing_liquid is None:
                # no existing liquid so just add the new liquid
                self.inventory.append(event_data)
            else:
                #combine them
                existing_liquid.volume+=event_data.volume

        else:
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