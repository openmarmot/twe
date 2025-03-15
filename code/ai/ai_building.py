
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
'''


#import built in modules

#import custom packages
import engine.math_2d

# this is for objects that don't need AI

#global variables

class AIBuilding(object):
    def __init__(self, owner):
        self.owner=owner
        self.show_interior=False
        self.show_interior_distance=500

        self.time_since_vis_update=6
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        time_passed=self.owner.world.time_passed_seconds
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
                self.owner.render_level=1
            else:
                # show the outside
                self.owner.image_index=0
                self.owner.reset_image=True
                self.owner.render_level=6
            

    #---------------------------------------------------------------------------
    def event_collision(self,event_data):
        if event_data.is_projectile:
            #self.health-=random.randint(25,75)
            engine.world_builder.spawn_object(self.owner.world,event_data.world_coords,'dirt',True)
        elif event_data.is_grenade:
            print('The mighty building laughs at your puny grenade')


    #---------------------------------------------------------------------------
    def handle_event(self, EVENT, event_data):
        ''' overrides base handle_event'''
        # EVENT - text describing event
        # event_data - most likely a world_object but could be anything

        # not sure what to do here yet. will have to think of some standard events
        if EVENT=='add_inventory':
            #self.event_add_inventory(event_data)
            pass
        elif EVENT=='collision':
            self.event_collision(event_data)
        else:
            print('Error: '+self.owner.name+' cannot handle event '+EVENT)
