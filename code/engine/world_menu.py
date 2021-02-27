'''
module : world_menu.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
this class contains code for the world in game menu
instantiated by the world class
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
        self.selected_object=None
        self.active_menu='none'
        self.menu_state='none'

    def handle_input(self,Key):
        # called by graphics_2d_pygame when there is a suitable key press
        # Key is a string corresponding to the actual key being pressed

        # '~' is used to activate/deactivate the debug menu
        if Key=='tilde':
            if self.menu_state=='debug':
                self.deactivate_menu()
            else :
                self.menu_state='debug'

        if self.active_menu=='vehicle':
            self.vehicle_menu(Key)
        elif self.active_menu=='debug':
            self.debug_menu(Key)
        

    def activate_menu(self, Selected_Object, Active_Menu):
        self.selected_object=Selected_Object
        self.active_menu=Active_Menu
        self.menu_state='none'

    def deactivate_menu(self):
        self.selected_object=None
        self.active_menu='none'
        self.menu_state='none'

    def crate_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            pass

    def vehicle_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            pass

    def debug_menu(self, Key):
        pass
