
'''
module : module_template.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
'''

#import built in modules

#import custom packages
from engine.strategic_menu import StrategicMenu

#global variables


class StrategicMap(object):

    def __init__(self, graphics_engine):

        self.graphics_engine=graphics_engine

        self.strategic_menu=StrategicMenu(self)

        self.map_squares=[]


    #---------------------------------------------------------------------------
    def handle_keydown(self,key):
        '''handle keydown events. called by graphics engine'''
        # these are for one off (not repeating) key presses

        #print('key ',KEY)
        self.strategic_menu.handle_input(key)

    #---------------------------------------------------------------------------
    def update(self):
        pass

