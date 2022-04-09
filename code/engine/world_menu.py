'''
module : world_menu.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes :
this class contains code for the world in game menu
instantiated by the world class
'''


#import built in modules
import random


#import custom packages
import engine.world_builder 
import engine.math_2d
from ai.ai_squad import AISquad

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
                #self.world.is_paused=False
            else :
                if self.active_menu!='death':
                    self.deactivate_menu()
                    self.active_menu='debug'
                    #self.world.is_paused=True
                    #print('Game Paused')

        if Key=='esc':
            # exit any active menu
            if self.active_menu!='death':
                self.deactivate_menu()

        if self.active_menu=='vehicle':
            self.vehicle_menu(Key)
        elif self.active_menu=='debug':
            self.debug_menu(Key)
        elif self.active_menu=='gun':
            self.gun_menu(Key)
        elif self.active_menu=='storage':
            self.storage_menu(Key)
        elif self.active_menu=='generic':
            self.generic_item_menu(Key)
        elif self.active_menu=='start':
            self.start_menu(Key)
        elif self.active_menu=='human':
            self.human_menu(Key)
        elif self.active_menu=='airplane':
            self.airplane_menu(Key)
        elif self.active_menu=='death':
            self.death_menu(Key)
        

    def activate_menu(self, SELECTED_OBJECT):
        ''' takes in a object that was mouse clicked on and returns a appropriate context menu'''

        # this is necessary to prevent the player from accidentally exiting the death menu
        if self.active_menu !="death":
            # clear any current menu
            self.deactivate_menu()

            d=engine.math_2d.get_distance(self.world.player.world_coords,SELECTED_OBJECT.world_coords)

            # minimum distance for a context menu to pop up
            if d<150:
                self.selected_object=SELECTED_OBJECT

                if SELECTED_OBJECT.is_vehicle: 
                    self.active_menu='vehicle'
                    self.vehicle_menu(None)
                elif SELECTED_OBJECT.is_gun or SELECTED_OBJECT.is_handheld_antitank:
                    self.active_menu='gun'
                    self.gun_menu(None)
                elif SELECTED_OBJECT.is_container:
                    self.active_menu='storage'
                    self.storage_menu(None)
                elif SELECTED_OBJECT.is_human:
                    self.active_menu='human'
                    self.human_menu(None)
                elif SELECTED_OBJECT.is_airplane:
                    self.active_menu='airplane'
                    self.airplane_menu(None)
                else :
                    # just dump everything else in here for now
                    self.active_menu='generic'
                    self.generic_item_menu(None)
            else:
                print('Get closer to the object ',d)

    def airplane_menu(self, Key):
        if self.menu_state=='none':

            if self.world.player in self.selected_object.ai.passengers:
                self.menu_state='internal'
            else:
                self.menu_state='external'

        if self.menu_state=='external':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--External Airplane Menu --')
            self.world.graphic_engine.menu_text_queue.append('passenger count : '+str(len(self.selected_object.ai.passengers)))
            self.world.graphic_engine.menu_text_queue.append('1 - info (not implemented) ')
            self.world.graphic_engine.menu_text_queue.append('2 - enter vehicle ')
            self.world.graphic_engine.menu_text_queue.append('3 - storage')
            if Key=='1':
                pass
            if Key=='2':
                # enter the vehicle 
                self.selected_object.add_inventory(self.world.player)
                # remove the player from the world so we don't have a ghost
                self.world.remove_object(self.world.player)

                self.world.graphic_engine.display_vehicle_text=True
                self.world.graphic_engine.text_queue.insert(0, '[ You climb into the vehicle ]')
                self.deactivate_menu()
            if Key=='3':
                # pull up the storage/container menu
                self.change_menu('storage')

        if self.menu_state=='internal':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--Internal Airplane Menu --')
            self.world.graphic_engine.menu_text_queue.append('passenger count : '+str(len(self.selected_object.ai.passengers)))
            self.world.graphic_engine.menu_text_queue.append('1 - Engines')
            self.world.graphic_engine.menu_text_queue.append('2 - Flight Controls ')
            self.world.graphic_engine.menu_text_queue.append('3 - Landing Gear ')
            self.world.graphic_engine.menu_text_queue.append('4 - Exit Plane ')
            if Key=='1':
                pass
            if Key=='4':
                # exit the vehicle
                p=self.selected_object.ai.passengers[0]
                self.selected_object.remove_inventory(p)
                self.world.add_object(p)
                self.world.graphic_engine.display_vehicle_text=False
                self.world.graphic_engine.text_queue.insert(0, '[ You exit the vehicle ]')
                self.deactivate_menu()

    def change_menu(self,menu_name):
        '''change the menu to the specified menu'''
        self.menu_state='none'
        # clear this just in case as it is rather inconsistently done
        self.world.graphic_engine.menu_text_queue=[]
        self.active_menu=menu_name
        self.handle_input(None)


    def storage_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('-- Storage Menu --')
            self.world.graphic_engine.menu_text_queue.append('1 - List')
            self.world.graphic_engine.menu_text_queue.append('2 - Add (not implemented) ')
            self.world.graphic_engine.menu_text_queue.append('3 - Remove ')
            self.menu_state='base'

        if self.menu_state=='base':
            if Key=='1':
                Key=None
                self.menu_state='list'
            if Key=='2':
                Key=None
                pass
                #self.menu_state='add'
            if Key=='3':
                Key=None
                self.menu_state='remove'

        if self.menu_state=='list':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('-- List Inventory Menu --')
            for b in self.selected_object.ai.inventory:
                self.world.graphic_engine.menu_text_queue.append(' - '+b.name)

        if self.menu_state=='remove':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('-- Remove Inventory Menu --')
            selection_key=1
            for b in self.selected_object.ai.inventory:
                if selection_key<10:
                    self.world.graphic_engine.menu_text_queue.append(str(selection_key)+' - '+b.name)
                    selection_key+=1

            if Key=='1':
                if len(self.selected_object.ai.inventory)>0:
                    self.world.player.add_inventory(self.selected_object.ai.inventory.pop(0))
            if Key=='2':
                if len(self.selected_object.ai.inventory)>1:
                    self.world.player.add_inventory(self.selected_object.ai.inventory.pop(1))
            if Key=='3':
                if len(self.selected_object.ai.inventory)>2:
                    self.world.player.add_inventory(self.selected_object.ai.inventory.pop(2))
            if Key=='4':
                if len(self.selected_object.ai.inventory)>3:
                    self.world.player.add_inventory(self.selected_object.ai.inventory.pop(3))
            if Key=='5':
                if len(self.selected_object.ai.inventory)>4:
                    self.world.player.add_inventory(self.selected_object.ai.inventory.pop(4))
            if Key=='6':
                if len(self.selected_object.ai.inventory)>5:
                    self.world.player.add_inventory(self.selected_object.ai.inventory.pop(5))
            if Key=='7':
                if len(self.selected_object.ai.inventory)>6:
                    self.world.player.add_inventory(self.selected_object.ai.inventory.pop(6))
            if Key=='8':
                if len(self.selected_object.ai.inventory)>7:
                    self.world.player.add_inventory(self.selected_object.ai.inventory.pop(7))
            if Key=='9':
                if len(self.selected_object.ai.inventory)>8:
                    self.world.player.add_inventory(self.selected_object.ai.inventory.pop(8))

            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('-- Remove Inventory Menu --')
            selection_key=1
            for b in self.selected_object.ai.inventory:
                if selection_key<10:
                    self.world.graphic_engine.menu_text_queue.append(str(selection_key)+' - '+b.name)
                    selection_key+=1

                    

    def deactivate_menu(self):
        self.selected_object=None
        self.active_menu='none'
        self.menu_state='none'
        self.world.graphic_engine.menu_text_queue=[]

    def death_menu(self,Key):
        ''' menu options for when player dies '''
        if self.menu_state=='none':
            self.world.is_paused=True
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('You Died')
            self.world.graphic_engine.menu_text_queue.append(self.world.player.ai.last_collision_description)
            self.world.graphic_engine.menu_text_queue.append('1 - respawn as random existing bot')
            #self.world.graphic_engine.menu_text_queue.append('3 - pick up')
            #self.world.graphic_engine.menu_text_queue.append('3 - pick up')

            self.menu_state='base'
        if self.menu_state=='base':
            if Key=='1':
                self.world.random_player_spawn()
                self.world.is_paused=False
                self.deactivate_menu()

    def debug_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            # eventually 'spawn' should get its own submenu
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--Debug Menu (~ to exit) --')
            self.world.graphic_engine.menu_text_queue.append('1 - toggle map ')
            self.world.graphic_engine.menu_text_queue.append('2 - toggle debug mode')
            self.world.graphic_engine.menu_text_queue.append('3 - spawn a kubelwagen')
            self.world.graphic_engine.menu_text_queue.append('4 - spawn a building')
            self.menu_state='base'
        if self.menu_state=='base':
            if Key=='1':
                self.world.toggle_map()
                #engine.world_builder.spawn_crate(self.world, self.world.player.world_coords,"crate o danitzas",True)
            elif Key=='2':
                if self.world.debug_mode==True:
                    self.world.debug_mode=False
                else:
                    self.world.debug_mode=True
            elif Key=='3':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'kubelwagen',True)
            elif Key=='4':
                engine.world_builder.spawn_object(self.world, self.world.player.world_coords,'square_building',True)

    def generic_item_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('-- '+self.selected_object.name+' --')
            if self.world.debug_mode==True:
                d=engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
                self.world.graphic_engine.menu_text_queue.append('Distance: '+str(d))
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
            self.world.graphic_engine.menu_text_queue.append('-- '+self.selected_object.name+' --')
            d=engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
            self.world.graphic_engine.menu_text_queue.append('Distance: '+str(d))
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

    def human_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('-- '+self.selected_object.name+' --')


            self.world.graphic_engine.menu_text_queue.append('Health: '+str(self.selected_object.ai.health))
            if self.selected_object.ai.primary_weapon != None:
                self.world.graphic_engine.menu_text_queue.append(self.selected_object.ai.primary_weapon.name)
                self.world.graphic_engine.menu_text_queue.append('  - Rounds Fired: '+str(self.selected_object.ai.primary_weapon.ai.rounds_fired))
                self.world.graphic_engine.menu_text_queue.append('  - Ammo : '+str(self.selected_object.ai.primary_weapon.ai.get_ammo_count()))
            self.world.graphic_engine.menu_text_queue.append('Confirmed Kills: '+str(self.selected_object.ai.confirmed_kills))
            self.world.graphic_engine.menu_text_queue.append('Probable Kills: '+str(self.selected_object.ai.probable_kills))
            self.world.graphic_engine.menu_text_queue.append(str(self.selected_object.ai.last_collision_description))

            if self.world.debug_mode==True:
                d=engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
                d2=engine.math_2d.get_distance(self.selected_object.world_coords,self.selected_object.ai.squad.world_coords)

                self.world.graphic_engine.menu_text_queue.append('Distance from player: '+str(d))
                self.world.graphic_engine.menu_text_queue.append('Distance from squad: '+str(d2))
                self.world.graphic_engine.menu_text_queue.append('AI State: '+str(self.selected_object.ai.ai_state))
                self.world.graphic_engine.menu_text_queue.append('AI Goal: '+str(self.selected_object.ai.ai_goal))


            self.world.graphic_engine.menu_text_queue.append('1 - What are you up to ?')
            self.world.graphic_engine.menu_text_queue.append('2 - Will you join my squad?')
            self.world.graphic_engine.menu_text_queue.append('3 - Manage Inventory')
            self.menu_state='base'
        if self.menu_state=='base':
            if Key=='1':
                print('nothing much')
            elif Key=='2':
                # remove from old squad
                if self.selected_object.ai.squad!=None:
                    self.selected_object.ai.squad.members.remove(self.selected_object)

                # add to player squad 
                self.selected_object.ai.squad=self.world.player.ai.squad
                self.selected_object.ai.squad.members.append(self.selected_object)

                self.deactivate_menu()
                
            elif Key=='3':
                # pull up the storage/container menu
                self.change_menu('storage')


    def start_menu(self, Key):
        if self.menu_state=='none':
            self.world.is_paused=False
            # print out the basic menu
            # eventually 'spawn' should get its own submenu
            self.world.graphic_engine.menu_text_queue.append('TWE')
            self.world.graphic_engine.menu_text_queue.append('---------------')
            self.world.graphic_engine.menu_text_queue.append('Pick a Faction')
            self.world.graphic_engine.menu_text_queue.append('1 - American')
            self.world.graphic_engine.menu_text_queue.append('2 - German')
            self.world.graphic_engine.menu_text_queue.append('3 - Soviet')
            self.world.graphic_engine.menu_text_queue.append('4 - Civilian/Neutral')
            self.menu_state='base'
        if self.menu_state=='base':
            faction='none'
            if Key=='1':
                self.world.player.add_inventory(engine.world_builder.spawn_object(self.world,[0,0],'1911',False))
                self.world.player.add_inventory(engine.world_builder.spawn_object(self.world,[0,0],'model24',False))
                self.world.player.is_american=True
                self.world.american_ai.create_and_spawn_squad([self.world.player])
                print('Spawning as American')
            elif Key=='2':
                self.world.player.add_inventory(engine.world_builder.spawn_object(self.world,[0,0],'stg44',False))
                self.world.player.add_inventory(engine.world_builder.spawn_object(self.world,[0,0],'model24',False))
                self.world.player.is_german=True
                self.world.german_ai.create_and_spawn_squad([self.world.player])
                print('Spawning as German')
            elif Key=='3':
                self.world.player.add_inventory(engine.world_builder.spawn_object(self.world,[0,0],'ppsh43',False))
                self.world.player.add_inventory(engine.world_builder.spawn_object(self.world,[0,0],'model24',False))
                self.world.player.is_soviet=True
                self.world.soviet_ai.create_and_spawn_squad([self.world.player])
                print('Spawning as Soviet')
            elif Key=='4':
                self.world.player.add_inventory(engine.world_builder.spawn_object(self.world,[0,0],'ppk',False))
                self.world.player.add_inventory(engine.world_builder.spawn_object(self.world,[0,0],'model24',False))
                self.world.player.is_civilian=True
                self.world.civilian_ai.create_and_spawn_squad([self.world.player])
                print('Spawning as Civilian')
            
            if Key=='1' or Key=='2' or Key=='3' or Key=='4':
                # eventually load other menus
                self.world.is_paused=False
                self.deactivate_menu()
                


    def vehicle_menu(self, Key):
        if self.menu_state=='none':

            if self.world.player in self.selected_object.ai.passengers:
                self.menu_state='internal'
            else:
                self.menu_state='external'

        if self.menu_state=='external':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--External Vehicle Menu --')
            self.world.graphic_engine.menu_text_queue.append(self.selected_object.name)
            self.world.graphic_engine.menu_text_queue.append('Passenger count : '+str(len(self.selected_object.ai.passengers)))
            self.world.graphic_engine.menu_text_queue.append('Vehicle Health : '+str(self.selected_object.ai.health))
            self.world.graphic_engine.menu_text_queue.append('1 - info (not implemented) ')
            self.world.graphic_engine.menu_text_queue.append('2 - enter vehicle ')
            self.world.graphic_engine.menu_text_queue.append('3 - storage ')
            if Key=='1':
                pass
            if Key=='2':
                # enter the vehicle 
                self.selected_object.add_inventory(self.world.player)
                # remove the player from the world so we don't have a ghost
                self.world.remove_object(self.world.player)

                self.world.graphic_engine.display_vehicle_text=True
                self.world.graphic_engine.text_queue.insert(0, '[ You climb into the vehicle ]')
                self.deactivate_menu()
            if Key=='3':
                # pull up the storage/container menu
                self.change_menu('storage')


        if self.menu_state=='internal':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--Internal Vehicle Menu --')
            self.world.graphic_engine.menu_text_queue.append('passenger count : '+str(len(self.selected_object.ai.passengers)))
            self.world.graphic_engine.menu_text_queue.append('1 - info (not implemented) ')
            self.world.graphic_engine.menu_text_queue.append('2 - exit vehicle ')
            self.world.graphic_engine.menu_text_queue.append('3 - ?')
            if Key=='1':
                pass
            if Key=='2':
                # exit the vehicle
                p=self.selected_object.ai.passengers[0]
                self.selected_object.remove_inventory(p)
                self.world.add_object(p)
                self.world.graphic_engine.display_vehicle_text=False
                self.world.graphic_engine.text_queue.insert(0, '[ You exit the vehicle ]')
                self.deactivate_menu()





        
