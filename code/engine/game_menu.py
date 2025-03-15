'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
this class contains code for the main game menu



'''

#import built in modules
import random
import os

#import custom packages
import engine.world_builder
import engine.math_2d


#global variables


class GameMenu():
    ''' in game menu '''

    #---------------------------------------------------------------------------
    def __init__(self,graphics_engine):
        # called/created by world.__init__

        self.active_menu='start' # which menu type (debug/weapon/vehicle/etc)
        self.menu_state='none' # where you are in the menu

        self.text_queue=[]

        self.graphics_engine=graphics_engine

        # used for multiple page layouts
        self.current_page=0

        # get the initial text going
        self.start_menu('none')
    #---------------------------------------------------------------------------
    def handle_input(self,key):
        '''handle input from the user'''
        # called by graphics_2d_pygame when there is a suitable key press
        # key is a string corresponding to the actual key being pressed

        if key=='esc':
            self.deactivate_menu()
            self.change_menu('start')

        if self.active_menu=='start':
            self.start_menu(key)
        elif self.active_menu=='load_save':
            self.load_save_menu(key)

        else:
            print('Error : active menu not recognized ',self.active_menu)

    #---------------------------------------------------------------------------
    def change_menu(self,menu_name):
        '''change the menu to the specified menu'''
        self.menu_state='none'
        self.current_page=0
        # clear this just in case as it is rather inconsistently done
        self.text_queue=[]
        self.active_menu=menu_name
        self.handle_input(None)

    #---------------------------------------------------------------------------
    def deactivate_menu(self):
        '''deactivate the menu'''
        self.active_menu='none'
        self.menu_state='none'
        self.text_queue=[]

    #---------------------------------------------------------------------------
    def load_save_menu(self, key):
        '''load save menu'''
        if self.menu_state == 'none':
            # self.graphics_engine.world.is_paused = False
            self.text_queue = []
            self.text_queue.append('Load a save game')
            self.text_queue.append('--- List of Save files ---')

            save_file_names = []

            # Add a list of all file names in ./saves to save_file_names
            save_folder = './saves'
            if os.path.exists(save_folder):
                save_file_names = [f for f in os.listdir(save_folder) if os.path.isfile(os.path.join(save_folder, f)) and f.endswith('.sqlite')]

            if len(save_file_names)==0:
                self.text_queue.append('No Save Files Exist')
                self.text_queue.append('Press [Esc] to return to the main menu')
            else:

                # Dynamically print a key and the corresponding save file name from save_file_names
                files_per_page = 9
                total_pages = (len(save_file_names) + files_per_page - 1) // files_per_page

                start_index = self.current_page * files_per_page
                end_index = min(start_index + files_per_page, len(save_file_names))

                for index, file_name in enumerate(save_file_names[start_index:end_index]):
                    self.text_queue.append(f"{index + 1} - {file_name}")

                if len(save_file_names) > files_per_page:
                    if self.current_page < total_pages - 1:
                        self.text_queue.append("[+] - Next page")
                    if self.current_page > 0:
                        self.text_queue.append("[-] - Previous page")


                # Handle the key selection for more than 10 save files
                if key is not None:
                    if key.isdigit():
                        key_index = int(key) - 1
                        if 0 <= key_index < len(save_file_names[start_index:end_index]):
                            selected_file = save_file_names[start_index + key_index]
                            self.graphics_engine.mode=2
                            self.graphics_engine.strategic_map.load_campaign_from_save('saves/'+selected_file)
                            self.deactivate_menu()
                    elif key == '+' and self.current_page < total_pages - 1:
                        self.current_page += 1
                        self.load_save_menu('')
                    elif key == '-' and self.current_page > 0:
                        self.current_page -= 1
                        self.load_save_menu('')

    #---------------------------------------------------------------------------
    def start_menu(self, key):
        '''start menu'''
        if self.menu_state=='none':
            #self.graphics_engine.world.is_paused=False
            self.text_queue=[]
            self.text_queue.append('TWE: To Whatever End')
            self.text_queue.append('---------------')
            self.text_queue.append('')
            self.text_queue.append('1 - New Campaign (preview: work in progess)')
            self.text_queue.append('2 - Load Campaign (preview: work in progress)')
            self.text_queue.append('3 - Quick Battle (choose this)')
            self.text_queue.append('4 - Exit')

            if key=='1':
                self.graphics_engine.mode=2
                self.graphics_engine.strategic_map.start_new_campaign()
                self.deactivate_menu()
            elif key=='2':
                self.change_menu('load_save')
            elif key=='3':
                self.menu_state='faction_select'
                key='none'
            elif key=='4':
                print('----------------------')
                print('Good Bye!')
                self.graphics_engine.quit=True

        if self.menu_state=='faction_select':
            self.text_queue=[]
            self.text_queue.append('TWE: To Whatever End')
            self.text_queue.append('---------------')
            self.text_queue.append('Pick a Faction')
            self.text_queue.append('1 - American (not implemented)')
            self.text_queue.append('2 - German')
            self.text_queue.append('3 - Soviet')
            self.text_queue.append('4 - Civilian/Neutral')

            # note 1 is missing as americans are not implemented
            if key in ['2','3','4']:
                if key=='1':
                    self.graphics_engine.world.player_spawn_faction='american'
                elif key=='2':
                    self.graphics_engine.world.player_spawn_faction='german'
                elif key=='3':
                    self.graphics_engine.world.player_spawn_faction='soviet'
                elif key=='4':
                    self.graphics_engine.world.player_spawn_faction='civilian'

                self.menu_state='battle_select'
                key='none'

        if self.menu_state=='battle_select':
            faction=self.graphics_engine.world.player_spawn_faction
            self.text_queue=[]
            self.text_queue.append('TWE: To Whatever End')
            self.text_queue.append('---------------')
            self.text_queue.append('Pick a Quick Battle Scenario')
            self.text_queue.append('Note - balance varies wildly with code updates.')
            self.text_queue.append('1 - Large mixed unit battle (choose this) ')
            if key=='1':
                engine.world_builder.load_quick_battle(self.graphics_engine.world,'1')
                self.graphics_engine.switch_mode(1)
                self.deactivate_menu()
            if faction in ['german','civilian']:
                self.text_queue.append('2 - German and Civilian only (No fighting)')
                if key=='2':
                    engine.world_builder.load_quick_battle(self.graphics_engine.world,'2')
                    self.graphics_engine.switch_mode(1)
                    self.deactivate_menu()
            if faction in ['soviet','civilian']:
                self.text_queue.append('3 - Soviet and Civilian only (No fighting)')
                if key=='3':
                    engine.world_builder.load_quick_battle(self.graphics_engine.world,'3')
                    self.graphics_engine.switch_mode(1)
                    self.deactivate_menu()

            self.text_queue.append('4 - Reserved for testing, content will vary')
            if key=='4':
                engine.world_builder.load_quick_battle(self.graphics_engine.world,'4')
                self.graphics_engine.switch_mode(1)
                self.deactivate_menu() 



    #---------------------------------------------------------------------------
    def update(self,time_passed_seconds):
        '''update'''

        # should maybe check if a menu is active first. no need for this to be constantly running
        # make the menu auto close after a period of time

        pass
