'''
module : world_menu.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
this class contains code for the world in game menu
'''


#import built in modules


#import custom packages

# module specific variables
module_version='0.0' #module software version
module_last_update_date='Nov 29 2020' #date of last update

#global variables


class World_Menu(object):
    ''' in game menu '''

    def __init__(self,World):
        # called/created by world.__init__

        self.world=World
        self.gun_menu=False
        self.vehicle_menu=False
        self.crate_menu=False

    def handle_input(self,Key):
        # called by graphics_2d_pygame when there is a suitable key press
        # Key is a string corresponding to the actual key being pressed
        pass
