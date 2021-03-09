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
import engine.world_builder 

# module specific variables
module_version='0.0' #module software version
module_last_update_date='March 08 2021' #date of last update

#global variables


class World_Menu(object):
    ''' in game menu '''

    def __init__(self,World):
        # called/created by world.__init__

        self.world=World
        self.selected_object=None
        self.active_menu='none' # which menu type (debug/weapon/vehicle/etc)
        self.menu_state='none' # where you are in the menu

    def handle_input(self,Key):
        # called by graphics_2d_pygame when there is a suitable key press
        # Key is a string corresponding to the actual key being pressed

        # '~' is used to activate/deactivate the debug menu
        if Key=='tilde':
            if self.active_menu=='debug':
                self.deactivate_menu()
            else :
                self.active_menu='debug'
                print("poooooooo!")

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
        self.world.graphic_engine.menu_text_queue.clear()

    def crate_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            pass

    def vehicle_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            pass

    def debug_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            # eventually 'spawn' should get its own submenu
            self.world.graphic_engine.menu_text_queue.append('--Debug Menu (~ to exit) --')
            self.world.graphic_engine.menu_text_queue.append('1 - spawn a crate')
            self.world.graphic_engine.menu_text_queue.append('2 - spawn like 50 zombies')
            self.world.graphic_engine.menu_text_queue.append('3 - exciting option coming soon')
            self.menu_state='base'
        if self.menu_state=='base':
            if Key=='1':
                engine.world_builder.spawn_crate(self.world, self.world.player.world_coords,"crate o danitzas")
            elif Key=='2':
                engine.world_builder.spawn_zombie_horde(self.world, self.world.player.world_coords, 50)
            elif Key=='3':
                engine.world_builder.spawn_kubelwagen(self.world, self.world.player.world_coords)

        
