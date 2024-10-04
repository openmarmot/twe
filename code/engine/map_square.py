
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

        # large world areas that are visible on the map interface
        self.rail_yard=False
        self.airport=False
        self.town=False

        # when this is updated the image_index should also be updated
        # 'german'/'soviet'/'neutral'
        self.map_control='none'
        self.german_count=0
        self.soviet_count=0
        self.american_count=0
        self.civilian_count=0

        # a count of how many neigbhoring squares are hostile. 0-4
        self.hostile_count=0

        # array of MapObject(s) for this map
        # a MapObject is a world_object in a compressed form that is used for saving and loading
        self.map_objects=[]

    # ---------------------------------------------------------------------------
    def update_hostile_count(self):
        '''returns a count of how many hostile squares border the square'''
        self.hostile_count=0
        if self.north!=None:
            if self.north.map_control != 'neutral' and self.north.map_control !=self.map_control:
                self.hostile_count+=1
        if self.south!=None:
            if self.south.map_control != 'neutral' and self.south.map_control !=self.map_control:
                self.hostile_count+=1
        if self.west!=None:
            if self.west.map_control != 'neutral' and self.west.map_control !=self.map_control:
                self.hostile_count+=1
        if self.east!=None:
            if self.east.map_control != 'neutral' and self.east.map_control !=self.map_control:
                self.hostile_count+=1


    #---------------------------------------------------------------------------
    def update_map_control(self):
        ''' check who controls the map and update the map image'''

        # if we have no map objects we won't update the map control
        if len(self.map_objects)>0:
            self.german_count=0
            self.american_count=0
            self.soviet_count=0
            self.civilian_count=0

            for b in self.map_objects:
                if 'german' in b.world_builder_identity:
                    self.german_count+=1
                elif 'soviet' in b.world_builder_identity:
                    self.soviet_count+=1
                elif 'american' in b.world_builder_identity:
                    self.american_count+=1
                elif 'civilian' in b.world_builder_identity:
                    self.civilian_count+=1

            if self.german_count>0 and self.soviet_count==0 and self.american_count==0:
                self.map_control='german'
                self.image_index=2
            elif self.soviet_count>0 and self.german_count==0 and self.american_count==0:
                self.map_control='soviet'
                self.image_index=1
            elif self.american_count>0 and self.german_count==0 and self.soviet_count==0:
                self.map_control='american'
                self.image_index=0 # need a american map color 
                # engine is not really setup for 3v3 yet
                engine.log.add_data('warn','map_square.update_map_control - square is american. not ready for this')
            elif self.american_count==0 and self.german_count==0 and self.soviet_count==0:
                # we could either reset to neutral or just do nothing here
                pass

    #---------------------------------------------------------------------------
    def update_map_features(self):
        '''update the map features based on world_area in map objects'''

        # reset everything to false
        self.rail_yard=False
        self.airport=False
        self.town=False

        for b in self.map_objects:
            if b.world_builder_identity.startswith('world_area_'):
                # split out the actual type from the name
                area_type=b.world_builder_identity.split('world_area_')[1]

                if area_type=='rail_yard':
                    self.rail_yard=True
                elif area_type=='town':
                    self.town=True
                elif area_type=='airport':
                    self.airport=True
                else:
                    engine.log.add_data('error','map_square.update_map_features - area unknown: '+area_type,True)


    

            

        
