
'''
module : module_template.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
'''

#import built in modules

#import custom packages
from engine.map_object import MapObject
import engine.log

#global variables


class MapSquare(object):

    def __init__(self,name,screen_coords):
        self.name=name
        self.screen_coords=screen_coords
        self.scale_modifier=0.5
        self.image=None
        self.image_index=0
        self.image_list=['map_blue','map_red','map_grey']
        self.image_size=None
        self.rotation_angle=0
        self.reset_image=True

        # neighboring squares
        self.north=None
        self.south=None
        self.west=None
        self.east=None

        # some big deal map features 
        self.rail_yard=False
        self.airport=False
        self.town=False

        # when this is updated the image_index should also be updated
        # 'german'/'soviet'/'neutral'
        self.map_control='none'

        # array of MapObject(s) for this map
        # a MapObject is a world_object in a compressed form that is used for saving and loading
        self.map_objects=[]



    def update_map_control(self):
        ''' check who controls the map and update the map image'''

        # if we have no map objects we won't update the map control
        if len(self.map_objects)>0:
            german_count=0
            american_count=0
            soviet_count=0

            for b in self.map_objects:
                if 'german' in b.world_builder_identity:
                    german_count+=1
                elif 'soviet' in b.world_builder_identity:
                    soviet_count+=1
                elif 'american' in b.world_builder_identity:
                    american_count+=1

            if german_count>0 and soviet_count==0 and american_count==0:
                self.map_control='german'
                self.image_index=2
            elif soviet_count>0 and german_count==0 and american_count==0:
                self.map_control='soviet'
                self.image_index=1
            elif american_count>0 and german_count==0 and soviet_count==0:
                self.map_control='american'
                self.image_index=0 # need a american map color 
                # engine is not really setup for 3v3 yet
                engine.log.add_data('warn','map_square.update_map_control - square is american. not ready for this')
            elif american_count==0 and german_count==0 and soviet_count==0:
                # we could either reset to neutral or just do nothing here
                pass

            

        
