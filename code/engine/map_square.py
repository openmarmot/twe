
'''
module : module_template.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
'''

#import built in modules

#import custom packages

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


    #---------------------------------------------------------------------------
    def add_inventory(self, ITEM):
        self.ai.handle_event('add_inventory',ITEM)


