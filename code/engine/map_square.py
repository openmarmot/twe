
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

        self.map_coords=[0,0]


    #---------------------------------------------------------------------------
    def add_inventory(self, ITEM):
        self.ai.handle_event('add_inventory',ITEM)


