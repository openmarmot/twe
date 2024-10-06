'''
module : strategic_menu.py
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


class StrategicMenu(object):
    ''' in game menu '''

    #---------------------------------------------------------------------------
    def __init__(self,strategic_map):
        # called/created by world.__init__

        self.active_menu='start' # which menu type (debug/weapon/vehicle/etc)
        self.menu_state='none' # where you are in the menu
        
        # variables that handle when a menu should be cleared from the screen
        self.time_since_input=0
        self.max_menu_idle_time=25 # how long a menu should be up before its closed/cleared
        
        self.text_queue=[]

        self.strategic_map=strategic_map

        # get the initial text going
        self.start_menu('none')

    #---------------------------------------------------------------------------
    def activate_menu(self, selected_object):
        ''' takes in a object that was mouse clicked on and returns a appropriate context menu'''

        self.time_since_input=0
        
        # clear any current menu
        self.deactivate_menu()

        # set selected object
        self.selected_object=selected_object

        # at the moment the only clickable thing is a map square
        self.active_menu='map_square'
        self.map_square_menu(None)

    #---------------------------------------------------------------------------
    def handle_input(self,key):
        # called by graphics_2d_pygame when there is a suitable key press
        # key is a string corresponding to the actual key being pressed
        
        # reset timer
        self.time_since_input=0

        if key=='esc':
            self.deactivate_menu()
            self.change_menu('start')


        if self.active_menu=='start':
            self.start_menu(key)
        elif self.active_menu=='spawn':
            self.spawn_menu(key)
        elif self.active_menu=='map_square':
            self.map_square_menu(key)

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
    def map_square_menu(self, key):

        # print out the basic menu
        self.text_queue=[]
        self.text_queue.append('-- Map Square ' + self.selected_object.name + ' --')
        self.text_queue.append('North: '+(self.selected_object.north.name if self.selected_object.north is not None else 'None'))
        self.text_queue.append('South: '+(self.selected_object.south.name if self.selected_object.south is not None else 'None'))
        self.text_queue.append('West: '+(self.selected_object.west.name if self.selected_object.west is not None else 'None'))
        self.text_queue.append('East: '+(self.selected_object.east.name if self.selected_object.east is not None else 'None'))
        self.text_queue.append('Airport: '+str(self.selected_object.airport))
        self.text_queue.append('Rail yard: '+str(self.selected_object.rail_yard))
        self.text_queue.append('Town: '+str(self.selected_object.town))

        self.text_queue.append('German Units: '+str(self.selected_object.german_count))
        self.text_queue.append('Soviet Units: '+str(self.selected_object.soviet_count))
        self.text_queue.append('American Units: '+str(self.selected_object.american_count))
        self.text_queue.append('Civilians: '+str(self.selected_object.civilian_count))

        self.text_queue.append('Esc - back to main menu')

        if (self.selected_object.german_count+self.selected_object.soviet_count+self.selected_object.american_count+self.selected_object.civilian_count)>0:
            self.text_queue.append('1 - Spawn')
            if key=='1':
                self.change_menu('spawn')

    #---------------------------------------------------------------------------
    def spawn_menu(self,key):
        self.text_queue=[]
        self.text_queue.append('Spawn on map '+self.selected_object.name)
        self.text_queue.append('-----------')
        self.text_queue.append('Esc - back to main menu')
        

        if self.selected_object.german_count>0:
            self.text_queue.append('1 - Spawn German')
            if key=='1':
                self.strategic_map.load_world(self.selected_object,'german')
                self.deactivate_menu()
                return
        if self.selected_object.soviet_count>0:
            self.text_queue.append('2 - Spawn Soviet')
            if key=='2':
                self.strategic_map.load_world(self.selected_object,'soviet')
                self.deactivate_menu()
                return
        if self.selected_object.american_count>0:
            self.text_queue.append('3 - Spawn American')
            if key=='3':
                self.strategic_map.load_world(self.selected_object,'american')
                self.deactivate_menu()
                return
        if self.selected_object.civilian_count>0:
            self.text_queue.append('4 - Spawn Civilian')
            if key=='4':
                self.strategic_map.load_world(self.selected_object,'civilian')
                self.deactivate_menu()
                return
    #---------------------------------------------------------------------------
    def start_menu(self, key):
        if self.menu_state=='none':
            #self.graphics_engine.world.is_paused=False
            self.text_queue=[]
            self.text_queue.append('Situation Map')
            self.text_queue.append('--- Map Key ---')
            self.text_queue.append('A:Airport')
            self.text_queue.append('R:Rail Yard')
            self.text_queue.append('T:Town')
            self.text_queue.append('Grey Square : German controlled')
            self.text_queue.append('Blue Square : Neutral')
            self.text_queue.append('Red Square : Soviet Controlled')
            self.text_queue.append('-----------')
            self.text_queue.append('[Select a Map Square to spawn on that map.]')
            self.text_queue.append('-----------')

            conflict=0
            for b in self.strategic_map.map_squares:
                if b.map_control=='contested':
                    conflict+=1
            if conflict>0:
                self.text_queue.append(str(conflict)+' squares in conflict')
                self.text_queue.append('2 - Auto resolve battles')
                if key=='2':
                    self.strategic_map.auto_resolve_battles()
                    self.start_menu('none')
                    return
            else:
                self.text_queue.append('1 - Advance time one turn')
                if key=='1':
                    self.strategic_map.advance_turn()
                    self.start_menu('none')
                    return

            self.text_queue.append('3 - Save and exit ')
            if key=='3':
                self.strategic_map.save_and_exit_game()



    #---------------------------------------------------------------------------
    def update(self,time_passed_seconds):

        # should maybe check if a menu is active first. no need for this to be constantly running
        # make the menu auto close after a period of time
        self.time_since_input+=time_passed_seconds
        if self.time_since_input>self.max_menu_idle_time and self.active_menu!='start':
            self.deactivate_menu()

