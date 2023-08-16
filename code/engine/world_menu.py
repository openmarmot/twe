'''
module : world_menu.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes :
this class contains code for the world in game menu
instantiated by the world class

this should mostly call methods from other classes. I don't want 
a lot of game logic here

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
        elif self.active_menu=='liquid_container':
            self.liquid_container_menu(Key)
        elif self.active_menu=='consumable':
            self.consumable_menu(Key)
        elif self.active_menu=='fuel':
            self.fuel_menu(Key)
        elif self.active_menu=='change_vehicle_role':
            self.change_vehicle_role_menu(Key)
        else:
            print('Error : active menu not recognized ',self.active_menu)

    def activate_menu(self, SELECTED_OBJECT):
        ''' takes in a object that was mouse clicked on and returns a appropriate context menu'''

        # this is necessary to prevent the player from accidentally exiting the death menu
        if self.active_menu !="death" and self.active_menu!='start':
            # clear any current menu
            self.deactivate_menu()
            
            self.selected_object=SELECTED_OBJECT

            if SELECTED_OBJECT.is_vehicle: 
                self.active_menu='vehicle'
                self.vehicle_menu(None)
            elif SELECTED_OBJECT.is_gun or SELECTED_OBJECT.is_handheld_antitank:
                self.active_menu='gun'
                self.gun_menu(None)
            elif SELECTED_OBJECT.is_object_container:
                self.active_menu='storage'
                self.storage_menu(None)
            elif SELECTED_OBJECT.is_human:
                self.active_menu='human'
                self.human_menu(None)
            elif SELECTED_OBJECT.is_airplane:
                #self.active_menu='airplane'
                #self.airplane_menu(None)
                self.active_menu='vehicle'
                self.vehicle_menu(None)
            elif SELECTED_OBJECT.is_liquid_container:
                self.active_menu='liquid_container'
                self.liquid_container_menu(None)
            elif SELECTED_OBJECT.is_consumable:
                self.active_menu='consumable'
                self.consumable_menu(None)
            else :
                # just dump everything else in here for now
                self.active_menu='generic'
                self.generic_item_menu(None)


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
                self.world.player.ai.handle_enter_vehicle(self.selected_object)

                self.world.display_vehicle_text=True
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
                self.world.player.ai.handle_exit_vehicle(self.selected_object)
                self.world.display_vehicle_text=False
                self.world.graphic_engine.text_queue.insert(0, '[ You exit the vehicle ]')
                self.deactivate_menu()

    def change_menu(self,menu_name):
        '''change the menu to the specified menu'''
        self.menu_state='none'
        # clear this just in case as it is rather inconsistently done
        self.world.graphic_engine.menu_text_queue=[]
        self.active_menu=menu_name
        self.handle_input(None)

    def change_vehicle_role_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('-- Change Vehicle Role --')
            currentRole='None'
            primaryWeapon='None'
            if self.selected_object.ai.driver==self.world.player:
                currentRole='Driver'
            if self.selected_object.ai.gunner==self.world.player:
                currentRole='Gunner'
            if self.selected_object.ai.primary_weapon!=None:
                primaryWeapon=self.selected_object.ai.primary_weapon.name

            self.world.graphic_engine.menu_text_queue.append('Vehicle : '+self.selected_object.name)
            self.world.graphic_engine.menu_text_queue.append('Primary Weapon: '+primaryWeapon)
            self.world.graphic_engine.menu_text_queue.append('Current Role : '+currentRole)
            self.world.graphic_engine.menu_text_queue.append('1 - Driver')
            self.world.graphic_engine.menu_text_queue.append('2 - Gunner')
            self.world.graphic_engine.menu_text_queue.append('3 - Passenger')
            self.menu_state='base'
        if self.menu_state=='base':
            if Key=='1':
                self.world.player.ai.handle_change_vehicle_role('driver')
                self.deactivate_menu()
            elif Key=='2':
                self.world.player.ai.handle_change_vehicle_role('gunner')
                self.deactivate_menu()
            elif Key=='3':
                self.world.player.ai.handle_change_vehicle_role('passenger')
                self.deactivate_menu()

    def consumable_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('-- '+self.selected_object.name+' --')
            if self.world.debug_mode==True:
                d=engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
                self.world.graphic_engine.menu_text_queue.append('Distance: '+str(d))
            self.world.graphic_engine.menu_text_queue.append('1 - Eat')
            self.world.graphic_engine.menu_text_queue.append('2 - Pick up')
            self.menu_state='base'
        if self.menu_state=='base':
            if Key=='1':
                self.world.player.ai.handle_eat(self.selected_object)
                self.world.remove_object(self.selected_object)
                self.deactivate_menu()
            elif Key=='2':
                self.world.player.add_inventory(self.selected_object)
                self.world.remove_object(self.selected_object)
                self.deactivate_menu()

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
            self.world.graphic_engine.menu_text_queue.append('5 - toggle collision circle visual')
            self.world.graphic_engine.menu_text_queue.append('6 - smooth display jitter')
            self.menu_state='base'
        if self.menu_state=='base':
            if Key=='1':
                self.world.toggle_map()
                #engine.world_builder.spawn_crate(self.world, self.world.player.world_coords,"crate o danitzas",True)
            elif Key=='2':
                self.world.debug_mode=not self.world.debug_mode
            elif Key=='3':
                k1=engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'kubelwagen',True)
                k1.ai.fuel=k1.ai.fuel_capacity
            elif Key=='4':
                engine.world_builder.spawn_object(self.world, self.world.player.world_coords,'square_building',True)
            elif Key=='5':
                self.world.graphic_engine.draw_collision = not self.world.graphic_engine.draw_collision
            elif Key=='6':
                self.world.graphic_engine.smooth_jitter = not self.world.graphic_engine.smooth_jitter
                print('Graphic Engine smooth_jitter: ',self.world.graphic_engine.smooth_jitter)

    def fuel_menu(self, Key):
        # i think if you get here it assumes you are holding fuel and have clicked on a vehicle
        # no need for a menu state
        # print out the basic menu
        self.world.graphic_engine.menu_text_queue=[]
        self.world.graphic_engine.menu_text_queue.append('-- Fuel Menu: '+self.selected_object.name+' --')
        self.world.graphic_engine.menu_text_queue.append('Fuel Can Contents: '+str(self.world.player.ai.large_pickup.ai.used_volume)+self.world.player.ai.large_pickup.ai.liquid_type)
        self.world.graphic_engine.menu_text_queue.append('Current Fuel Load : '+str(self.selected_object.ai.fuel))
        self.world.graphic_engine.menu_text_queue.append('Maximum Fuel Capacity : '+str(self.selected_object.ai.fuel_capacity))
        self.world.graphic_engine.menu_text_queue.append('1 - Add Fuel')
        self.world.graphic_engine.menu_text_queue.append('2 - Remove Fuel')
        if Key=='1':
            self.world.player.ai.handle_transfer(self.world.player.ai.large_pickup,self.selected_object)
            # update text
            self.fuel_menu('')
        elif Key=='2':
            self.world.player.ai.handle_transfer(self.world.player.ai.large_pickup,self.selected_object)
            # update text
            self.fuel_menu('')

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

            # -- determine what the next menu will be
            if self.selected_object==self.world.player:
                self.world.graphic_engine.menu_text_queue.append('[player]')
                self.menu_state = 'player_menu'
            else:
                if self.selected_object.ai.squad==self.world.player.ai.squad:
                    self.world.graphic_engine.menu_text_queue.append('[in your squad]')
                    self.menu_state = 'squad_member_menu'
                else:
                    self.menu_state = 'non_squad_member_menu'

            self.world.graphic_engine.menu_text_queue.append('Squad Size: '+str(len(self.selected_object.ai.squad.members)))

            self.world.graphic_engine.menu_text_queue.append('Health: '+str(round(self.selected_object.ai.health,1)))
            self.world.graphic_engine.menu_text_queue.append('Hunger: '+str(round(self.selected_object.ai.hunger,1)))
            self.world.graphic_engine.menu_text_queue.append('Thirst: '+str(round(self.selected_object.ai.thirst,1)))
            self.world.graphic_engine.menu_text_queue.append('Fatigue ' + str(round(self.selected_object.ai.fatigue,1)))
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
                self.world.graphic_engine.menu_text_queue.append('Personal Enemies Count: '+str(len(self.selected_object.ai.personal_enemies)))
                self.world.graphic_engine.menu_text_queue.append('AI in building: '+str(self.selected_object.ai.in_building))

            if self.menu_state == 'player_menu':
                self.world.graphic_engine.menu_text_queue.append('1 - Manage Inventory')
            elif self.menu_state == 'squad_member_menu':
                self.world.graphic_engine.menu_text_queue.append('1 - [Speak] What are you up to ?')
                self.world.graphic_engine.menu_text_queue.append('2 - Manage Inventory')
                self.world.graphic_engine.menu_text_queue.append('3 - [Speak] Can you upgrade your gear?')
                if self.world.player.ai.in_vehicle:
                    self.world.graphic_engine.menu_text_queue.append('4 - [Speak] Climb aboard!')
            elif self.menu_state == 'non_squad_member_menu':
                self.world.graphic_engine.menu_text_queue.append('1 - What are you up to ?')
                self.world.graphic_engine.menu_text_queue.append('2 - Will you join my squad?')

        if self.menu_state=='player_menu':
            if Key=='1':
                # pull up the storage/container menu
                self.change_menu('storage')
        elif self.menu_state == 'squad_member_menu':
            if Key=='1':
                self.selected_object.ai.speak('status')
            if Key=='2':
                # pull up the storage/container menu
                self.change_menu('storage')
            if Key=='3':
                self.selected_object.ai.react_asked_to_upgrade_gear()
            if Key=='4' and self.world.player.ai.in_vehicle:
                self.selected_object.ai.react_asked_to_enter_vehicle(self.world.player.ai.vehicle)
        elif self.menu_state == 'non_squad_member_menu':
            if Key=='1':
                self.selected_object.ai.speak('status')
            elif Key=='2':
                # ask the ai to join the squad
                self.selected_object.ai.react_asked_to_join_squad(self.world.player.ai.squad)
                self.deactivate_menu()
    
    def liquid_container_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('-- '+self.selected_object.name+' --')
            if self.world.debug_mode==True:
                d=engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
                self.world.graphic_engine.menu_text_queue.append('Distance: '+str(d))
            self.world.graphic_engine.menu_text_queue.append('Contents : '+self.selected_object.ai.liquid_type)
            self.world.graphic_engine.menu_text_queue.append(str(self.selected_object.ai.used_volume)+' liters')
            if self.selected_object.ai.contaminated:
                self.world.graphic_engine.menu_text_queue.append('Liquid is contaminated')
            self.world.graphic_engine.menu_text_queue.append('1 - Drink')
            self.world.graphic_engine.menu_text_queue.append('2 - Pick up')
            self.menu_state='base'
        if self.menu_state=='base':
            if Key=='1':
                self.world.player.ai.handle_drink(self.selected_object)
                self.deactivate_menu()
            elif Key=='2':
                self.world.player.add_inventory(self.selected_object)
                self.world.remove_object(self.selected_object)
                self.deactivate_menu()

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
            spawned=False
            faction='none'
            if Key=='1':
                if len(self.world.wo_objects_american)>0:
                    self.world.spawn_player('american')
                    spawned=True
                else:
                    print('No bots of this type available')
            elif Key=='2':
                if len(self.world.wo_objects_german)>0:
                    self.world.spawn_player('german')
                    spawned=True
                else:
                    print('No bots of this type available')
            elif Key=='3':
                if len(self.world.wo_objects_soviet)>0:
                    self.world.spawn_player('soviet')
                    spawned=True
                else:
                    print('No bots of this type available')
            elif Key=='4':
                if len(self.world.wo_objects_civilian)>0:
                    self.world.spawn_player('civilian')
                    spawned=True
                else:
                    print('No bots of this type available')
            
            if spawned:
                # eventually load other menus
                self.world.is_paused=False
                self.deactivate_menu()
                
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
                    temp=self.selected_object.ai.inventory[0]
                    self.selected_object.remove_inventory(temp)
                    self.world.add_object(temp)
            if Key=='2':
                if len(self.selected_object.ai.inventory)>1:
                    temp=self.selected_object.ai.inventory[1]
                    self.selected_object.remove_inventory(temp)
                    self.world.add_object(temp)
            if Key=='3':
                if len(self.selected_object.ai.inventory)>2:
                    temp=self.selected_object.ai.inventory[2]
                    self.selected_object.remove_inventory(temp)
                    self.world.add_object(temp)
            if Key=='4':
                if len(self.selected_object.ai.inventory)>3:
                    temp=self.selected_object.ai.inventory[3]
                    self.selected_object.remove_inventory(temp)
                    self.world.add_object(temp)
            if Key=='5':
                if len(self.selected_object.ai.inventory)>4:
                    temp=self.selected_object.ai.inventory[4]
                    self.selected_object.remove_inventory(temp)
                    self.world.add_object(temp)
            if Key=='6':
                if len(self.selected_object.ai.inventory)>5:
                    temp=self.selected_object.ai.inventory[5]
                    self.selected_object.remove_inventory(temp)
                    self.world.add_object(temp)
            if Key=='7':
                if len(self.selected_object.ai.inventory)>6:
                    temp=self.selected_object.ai.inventory[6]
                    self.selected_object.remove_inventory(temp)
                    self.world.add_object(temp)
            if Key=='8':
                if len(self.selected_object.ai.inventory)>7:
                    temp=self.selected_object.ai.inventory[7]
                    self.selected_object.remove_inventory(temp)
                    self.world.add_object(temp)
            if Key=='9':
                if len(self.selected_object.ai.inventory)>8:
                    temp=self.selected_object.ai.inventory[8]
                    self.selected_object.remove_inventory(temp)
                    self.world.add_object(temp)

            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('-- Remove Inventory Menu --')
            selection_key=1
            for b in self.selected_object.ai.inventory:
                if selection_key<10:
                    self.world.graphic_engine.menu_text_queue.append(str(selection_key)+' - '+b.name)
                    selection_key+=1

    def vehicle_menu(self, Key):
        if self.menu_state=='none':

            if self.world.player in self.selected_object.ai.passengers:
                self.menu_state='internal'
            else:
                self.menu_state='external'

        if self.menu_state=='external':
            fuel_option=False
            if self.world.player.ai.large_pickup!=None:
                if self.world.player.ai.large_pickup.is_liquid_container:
                    fuel_option=True
            primaryWeapon='None'
            if self.selected_object.ai.primary_weapon!=None:
                primaryWeapon=self.selected_object.ai.primary_weapon.name
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--External Vehicle Menu --')
            self.world.graphic_engine.menu_text_queue.append('Vehicle : '+self.selected_object.name)
            self.world.graphic_engine.menu_text_queue.append('Primary Weapon: '+primaryWeapon)
            self.world.graphic_engine.menu_text_queue.append('Passenger count : '+str(len(self.selected_object.ai.passengers)))
            self.world.graphic_engine.menu_text_queue.append('Vehicle Health : '+str(self.selected_object.ai.health))
            self.world.graphic_engine.menu_text_queue.append('1 - info (not implemented) ')
            self.world.graphic_engine.menu_text_queue.append('2 - enter vehicle ')
            self.world.graphic_engine.menu_text_queue.append('3 - storage ')
            if fuel_option:
                self.world.graphic_engine.menu_text_queue.append('4 - fuel ')

            # -- add debug info --
            if self.world.debug_mode==True:
                self.world.graphic_engine.menu_text_queue.append('--debug info --')
                self.world.graphic_engine.menu_text_queue.append('fuel type: '+self.selected_object.ai.fuel_type)
                self.world.graphic_engine.menu_text_queue.append('fuel amount: '+str(self.selected_object.ai.fuel))
                self.world.graphic_engine.menu_text_queue.append('throttle: '+str(self.selected_object.ai.throttle))
                self.world.graphic_engine.menu_text_queue.append('brake power: '+str(self.selected_object.ai.brake_power))
                self.world.graphic_engine.menu_text_queue.append('wheel steering: '+str(self.selected_object.ai.wheel_steering))
                self.world.graphic_engine.menu_text_queue.append('vehicle speed: '+str(self.selected_object.ai.vehicle_speed))
                self.world.graphic_engine.menu_text_queue.append('acceleration: '+str(self.selected_object.ai.acceleration))
                self.world.graphic_engine.menu_text_queue.append('passenger count: '+str(len(self.selected_object.ai.passengers)))
                if self.selected_object.ai.driver==None:
                    self.world.graphic_engine.menu_text_queue.append('driver: None')
                else:
                    self.world.graphic_engine.menu_text_queue.append('---- driver info -------------------')
                    self.world.graphic_engine.menu_text_queue.append('driver: '+self.selected_object.ai.driver.name)
                    self.world.graphic_engine.menu_text_queue.append('in_vehicle: '+str(self.selected_object.ai.driver.ai.in_vehicle))
                    distance=engine.math_2d.get_distance(self.selected_object.world_coords,self.selected_object.ai.driver.ai.ai_vehicle_destination)
                    self.world.graphic_engine.menu_text_queue.append('distance to destination: '+str(distance))
                    r = engine.math_2d.get_rotation(self.selected_object.world_coords,self.selected_object.ai.driver.ai.ai_vehicle_destination)
                    self.world.graphic_engine.menu_text_queue.append('rotation to destination: '+str(r))
                    self.world.graphic_engine.menu_text_queue.append('vehicle rotation: '+str(self.selected_object.rotation_angle))
                    self.world.graphic_engine.menu_text_queue.append('driver ai_state: '+self.selected_object.ai.driver.ai.ai_state)
                    self.world.graphic_engine.menu_text_queue.append('driver ai_goal: '+self.selected_object.ai.driver.ai.ai_goal)
                    self.world.graphic_engine.menu_text_queue.append('------------------------------------')

                self.world.graphic_engine.menu_text_queue.append('throttle: '+str(self.selected_object.ai.throttle))

            if Key=='1':
                pass
            if Key=='2':
                # enter the vehicle 
                self.world.player.ai.handle_enter_vehicle(self.selected_object)
                self.world.display_vehicle_text=True
                self.world.graphic_engine.text_queue.insert(0, '[ You climb into the vehicle ]')
                self.deactivate_menu()
            if Key=='3':
                # pull up the storage/container menu
                self.change_menu('storage')
            if Key=='4' and fuel_option:
                self.change_menu('fuel')


        if self.menu_state=='internal':
            currentRole='None'
            primaryWeapon='None'
            if self.selected_object.ai.driver==self.world.player:
                currentRole='Driver'
            if self.selected_object.ai.gunner==self.world.player:
                currentRole='Gunner'
            if self.selected_object.ai.primary_weapon!=None:
                primaryWeapon=self.selected_object.ai.primary_weapon.name
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--Internal Vehicle Menu --')
            self.world.graphic_engine.menu_text_queue.append('Vehicle : '+self.selected_object.name)
            self.world.graphic_engine.menu_text_queue.append('fuel type: '+self.selected_object.ai.fuel_type)
            self.world.graphic_engine.menu_text_queue.append('fuel amount: '+str(self.selected_object.ai.fuel))
            self.world.graphic_engine.menu_text_queue.append('Primary Weapon: '+primaryWeapon)
            self.world.graphic_engine.menu_text_queue.append('Current Role : '+currentRole)
            self.world.graphic_engine.menu_text_queue.append('Engine : '+str(self.selected_object.ai.engine_on))
            self.world.graphic_engine.menu_text_queue.append('passenger count : '+str(len(self.selected_object.ai.passengers)))
            self.world.graphic_engine.menu_text_queue.append('1 - change role')
            self.world.graphic_engine.menu_text_queue.append('2 - exit vehicle ')
            self.world.graphic_engine.menu_text_queue.append('3 - start/stop engine')
            self.world.graphic_engine.menu_text_queue.append('4 - toggle HUD')
            if Key=='1':
                self.change_menu('change_vehicle_role')
            if Key=='2':
                # exit the vehicle
                self.world.player.ai.handle_exit_vehicle()
                self.world.display_vehicle_text=False
                self.world.graphic_engine.text_queue.insert(0, '[ You exit the vehicle ]')
                self.deactivate_menu()
            if Key=='3':
                #flip the bool
                self.selected_object.ai.engine_on=not self.selected_object.ai.engine_on
                #refresh the text
                self.vehicle_menu('none')
            if Key=='4':
                #flip the bool
                self.world.display_vehicle_text=not self.world.display_vehicle_text
                #refresh the text
                self.vehicle_menu('none')



        # --

