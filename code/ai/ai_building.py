
'''
module : ai_building.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
# module specific variables
module_version='0.0' #module software version
module_last_update_date='March 28 2021' #date of last update

# this is for objects that don't need AI

#global variables

class AIBuilding(AIBase):
    def __init__(self, owner):
        super().__init__(owner)
        self.show_interior=False
        self.show_interior_distance=500

        self.time_since_vis_update=6
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        time_passed=self.owner.world.graphic_engine.time_passed_seconds
        self.time_since_vis_update+=time_passed

        if self.time_since_vis_update>5 :
            self.time_since_vis_update=0
            # check distance to player
            b=engine.math_2d.get_distance(self.owner.world_coords,self.owner.world.player.world_coords)
            #print(str(b))
            if b<self.show_interior_distance:
                # show the inside
                self.owner.image_index=1
                self.owner.reset_image=True
            else:
                # show the outside
                self.owner.image_index=0
                self.owner.reset_image=True
            
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    def event_collision(self,EVENT_DATA):
        if EVENT_DATA.is_projectile:
            #self.health-=random.randint(25,75)
            engine.world_builder.spawn_sprite(self.owner.world,EVENT_DATA.world_coords,'dirt')
        elif EVENT_DATA.is_grenade:
            print('The mighty building laughs at your puny grenade')


    #---------------------------------------------------------------------------
    def handle_event(self, EVENT, EVENT_DATA):
        ''' overrides base handle_event'''
        # EVENT - text describing event
        # EVENT_DATA - most likely a world_object but could be anything

        # not sure what to do here yet. will have to think of some standard events
        if EVENT=='add_inventory':
            #self.event_add_inventory(EVENT_DATA)
            pass
        elif EVENT=='collision':
            self.event_collision(EVENT_DATA)
