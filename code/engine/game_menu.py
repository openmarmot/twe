'''
module : game_menu.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
this class contains code for the main game menu



'''

#import built in modules
import random


#import custom packages
import engine.world_builder 
import engine.math_2d

#global variables


class GameMenu(object):
    ''' in game menu '''

    #---------------------------------------------------------------------------
    def __init__(self,graphics_engine):
        # called/created by world.__init__

        self.active_menu='start' # which menu type (debug/weapon/vehicle/etc)
        self.menu_state='none' # where you are in the menu
        
        self.text_queue=[]

        self.graphics_engine=graphics_engine

        # get the initial text going
        self.start_menu('none')
    #---------------------------------------------------------------------------
    def handle_input(self,key):
        # called by graphics_2d_pygame when there is a suitable key press
        # key is a string corresponding to the actual key being pressed
        
        # reset timer
        self.time_since_input=0

        if key=='esc':
            pass


        if self.active_menu=='start':
            self.start_menu(key)

        else:
            print('Error : active menu not recognized ',self.active_menu)



    #---------------------------------------------------------------------------
    def change_menu(self,menu_name):
        '''change the menu to the specified menu'''
        self.menu_state='none'
        # clear this just in case as it is rather inconsistently done
        self.text_queue=[]
        self.active_menu=menu_name
        self.handle_input(None)

    #---------------------------------------------------------------------------
    def deactivate_menu(self):
        self.selected_object=None
        self.active_menu='none'
        self.menu_state='none'
        self.text_queue=[]

    #---------------------------------------------------------------------------
    def start_menu(self, key):
        if self.menu_state=='none':
            #self.graphics_engine.world.is_paused=False
            self.text_queue=[]
            self.text_queue.append('TWE: To Whatever End')
            self.text_queue.append('---------------')
            self.text_queue.append('')
            self.text_queue.append('1 - New Campaign (preview: work in progess)')
            self.text_queue.append('2 - Load Campaign (not implemented)')
            self.text_queue.append('3 - Quick Battle (choose this)')
            #self.text_queue.append('4 - Nothing') 

            if key=='1':
                self.graphics_engine.mode=2
                self.graphics_engine.strategic_map.start_new_campaign()
                self.deactivate_menu()
            elif key=='2':
                pass
            elif key=='3':
                self.menu_state='faction_select'
                key='none'

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
                faction=''
                if key=='1':
                    faction='american'
                elif key=='2':
                    faction='german'
                elif key=='3':
                    faction='soviet'
                elif key=='4':
                    faction='civilian'

                engine.world_builder.load_quick_battle(self.graphics_engine.world,faction)

                self.graphics_engine.mode=1
                self.deactivate_menu()
                
 



    #---------------------------------------------------------------------------
    def update(self,time_passed_seconds):

        # should maybe check if a menu is active first. no need for this to be constantly running
        # make the menu auto close after a period of time

        pass

        #self.time_since_input+=time_passed_seconds
        #if self.time_since_input>self.max_menu_idle_time and self.active_menu!='start':
        #    self.deactivate_menu()

