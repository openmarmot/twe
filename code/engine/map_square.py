
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

    def __init__(self, world,IMAGE_LIST,AI):
        self.name=''
        self.map_coords=[0,0]
        self.screen_coords=[0,0]
        self.scale_modifier=1
        self.image=None
        self.image_index=0
        self.image_list=['map_blue','map_red','map_grey']
        self.image_size=None
        self.rotation_angle=0


    #---------------------------------------------------------------------------
    def add_inventory(self, ITEM):
        self.ai.handle_event('add_inventory',ITEM)


