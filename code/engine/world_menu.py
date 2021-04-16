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
module_last_update_date='March 17 2021' #date of last update

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

        if Key=='esc':
            # exit any active menu
            self.deactivate_menu()

        if self.active_menu=='vehicle':
            self.vehicle_menu(Key)
        elif self.active_menu=='debug':
            self.debug_menu(Key)
        elif self.active_menu=='gun':
            self.gun_menu(Key)
        elif self.active_menu=='crate':
            self.crate_menu(Key)
        elif self.active_menu=='generic':
            self.generic_item_menu(Key)
        

    def activate_menu(self, Selected_Object):
        # clear any current menu
        self.deactivate_menu()
        self.selected_object=Selected_Object

        if Selected_Object.is_vehicle: 
            self.active_menu='vehicle'
            self.vehicle_menu(None)
        elif Selected_Object.is_gun:
            self.active_menu='gun'
            self.gun_menu(None)
        elif Selected_Object.is_crate:
            self.active_menu='crate'
            self.crate_menu(None)
        else :
            # just dump everything else in here for now
            self.active_menu='generic'
            self.generic_item_menu(None)



    def deactivate_menu(self):
        self.selected_object=None
        self.active_menu='none'
        self.menu_state='none'
        self.world.graphic_engine.menu_text_queue.clear()

    def crate_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('-- Crate Menu --')
            self.world.graphic_engine.menu_text_queue.append('1 - info ?')
            self.world.graphic_engine.menu_text_queue.append('2 - ?')
            self.world.graphic_engine.menu_text_queue.append('3 - ?')
            self.menu_state='base'
            
    def generic_item_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('-- Item Menu --')
            self.world.graphic_engine.menu_text_queue.append('1 - info (not implemented)?')
            self.world.graphic_engine.menu_text_queue.append('2 - ? (not implemented)?')
            self.world.graphic_engine.menu_text_queue.append('3 - pick up')
            self.menu_state='base'
        if self.menu_state=='base':
            if Key=='1':
                pass
            elif Key=='2':
                pass
            elif Key=='3':
                self.world.player.add_inventory(self.selected_object)
                self.world.remove_object(self.selected_object)
                self.deactivate_menu()


    def gun_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('-- Gun Menu --')
            self.world.graphic_engine.menu_text_queue.append('1 - info (not implemented)?')
            self.world.graphic_engine.menu_text_queue.append('2 - ? (not implemented)?')
            self.world.graphic_engine.menu_text_queue.append('3 - pick up')
            self.menu_state='base'
        if self.menu_state=='base':
            if Key=='1':
                pass
            elif Key=='2':
                pass
            elif Key=='3':
                self.world.player.add_inventory(self.selected_object)
                self.world.remove_object(self.selected_object)
                self.deactivate_menu()

    def vehicle_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('--Vehicle Menu --')
            self.world.graphic_engine.menu_text_queue.append('1 - info (not implemented) ')
            self.world.graphic_engine.menu_text_queue.append('2 - enter (not implemented)')
            self.world.graphic_engine.menu_text_queue.append('3 - ?')
            self.menu_state='base'
            

    def debug_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            # eventually 'spawn' should get its own submenu
            self.world.graphic_engine.menu_text_queue.append('--Debug Menu (~ to exit) --')
            self.world.graphic_engine.menu_text_queue.append('1 - spawn a crate')
            self.world.graphic_engine.menu_text_queue.append('2 - spawn like 50 zombies')
            self.world.graphic_engine.menu_text_queue.append('3 - spawn a kubelwagen')
            self.world.graphic_engine.menu_text_queue.append('4 - spawn a warehouse')
            self.menu_state='base'
        if self.menu_state=='base':
            if Key=='1':
                engine.world_builder.spawn_crate(self.world, self.world.player.world_coords,"crate o danitzas")
            elif Key=='2':
                engine.world_builder.spawn_zombie_horde(self.world, self.world.player.world_coords, 50)
            elif Key=='3':
                engine.world_builder.spawn_kubelwagen(self.world, self.world.player.world_coords)
            elif Key=='4':
                engine.world_builder.spawn_warehouse(self.world, self.world.player.world_coords)

        
