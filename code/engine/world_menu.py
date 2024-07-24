'''
module : world_menu.py
language : Python 3.x
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

    #---------------------------------------------------------------------------
    def __init__(self,World):
        # called/created by world.__init__

        self.world=World
        self.selected_object=None
        self.active_menu='none' # which menu type (debug/weapon/vehicle/etc)
        self.menu_state='none' # where you are in the menu
        
        # variables that handle when a menu should be cleared from the screen
        self.time_since_input=0
        self.max_menu_idle_time=25 # how long a menu should be up before its closed/cleared
        
        # max distance at which you can select something (open a context menu)
        self.max_menu_distance=90

    #---------------------------------------------------------------------------
    def handle_input(self,Key):
        # called by graphics_2d_pygame when there is a suitable key press
        # Key is a string corresponding to the actual key being pressed
        
        # reset timer
        self.time_since_input=0

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
        elif self.active_menu=='consumable':
            self.consumable_menu(Key)
        elif self.active_menu=='fuel':
            self.fuel_menu(Key)
        elif self.active_menu=='change_vehicle_role':
            self.change_vehicle_role_menu(Key)
        elif self.active_menu=='coffee_grinder':
            self.coffee_grinder_menu(Key)
        elif self.active_menu=='squad':
            self.squad_menu(Key)
        elif self.active_menu=='eat_drink':
            self.eat_drink_menu(Key)
        elif self.active_menu=='first_aid':
            self.first_aid_menu(Key)
        elif self.active_menu=='engine_menu':
            self.engine_menu(Key)
        elif self.active_menu=='radio_menu':
            self.radio_menu(Key)
        else:
            print('Error : active menu not recognized ',self.active_menu)

    #---------------------------------------------------------------------------
    def activate_menu(self, SELECTED_OBJECT):
        ''' takes in a object that was mouse clicked on and returns a appropriate context menu'''

        self.time_since_input=0

        # this is necessary to prevent the player from accidentally exiting the death menu
        if self.active_menu !="death" and self.active_menu!='start':
            # clear any current menu
            self.deactivate_menu()
            
            self.selected_object=SELECTED_OBJECT
            if SELECTED_OBJECT.name=='coffee_grinder':
                self.active_menu='coffee_grinder'
                self.coffee_grinder_menu(None)
            elif SELECTED_OBJECT.is_vehicle: 
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
                self.active_menu='vehicle'
                self.vehicle_menu(None)
            elif SELECTED_OBJECT.is_consumable:
                self.active_menu='consumable'
                self.consumable_menu(None)
            elif SELECTED_OBJECT.is_radio:
                self.active_menu='radio_menu'
                self.radio_menu(None)
            else :
                print('warn - generic menu activated')
                # just dump everything else in here for now
                self.active_menu='generic'
                self.generic_item_menu(None)

    #---------------------------------------------------------------------------
    def change_menu(self,menu_name):
        '''change the menu to the specified menu'''
        self.menu_state='none'
        # clear this just in case as it is rather inconsistently done
        self.world.graphic_engine.menu_text_queue=[]
        self.active_menu=menu_name
        self.handle_input(None)

    #---------------------------------------------------------------------------
    def change_vehicle_role_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('-- Change Vehicle Role --')
            currentRole=self.world.player.ai.ai_vehicle_role
            if currentRole==None:
                currentRole='None!'

            self.world.graphic_engine.menu_text_queue.append('Vehicle : '+self.selected_object.name)
            self.world.graphic_engine.menu_text_queue.append('Current Role : '+currentRole)
            self.world.graphic_engine.menu_text_queue.append('1 - Driver')
            self.world.graphic_engine.menu_text_queue.append('2 - Gunner')
            self.world.graphic_engine.menu_text_queue.append('3 - Passenger')
            self.world.graphic_engine.menu_text_queue.append('4 - Chef')
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

     #---------------------------------------------------------------------------
    def coffee_grinder_menu(self, Key):
        # print out the basic menu
        self.world.graphic_engine.menu_text_queue.append('-- Coffee Grinder Menu --')
        
        beans=None
        grounds=None
        for b in self.world.player.ai.inventory:
            if b.name=='coffee_beans':
                if beans!=None:
                    print('!!Warning multi-bean-verse detected!!')
                beans=b
            if b.name=='ground_coffee':
                grounds=b

        if grounds!=None:
            self.world.graphic_engine.menu_text_queue.append('Ground Coffee weight: '+str(grounds.weight))
        if beans==None:
            self.world.graphic_engine.menu_text_queue.append("I will need to get some coffee beans first..")
        else:
            self.world.graphic_engine.menu_text_queue.append('Beans.. volume? : '+str(beans.volume))
            self.world.graphic_engine.menu_text_queue.append('Beans.. weight? : '+str(beans.weight))
        
            self.world.graphic_engine.menu_text_queue.append('1 - Grind Beans')
            self.world.graphic_engine.menu_text_queue.append('4 - Exit')

            if Key=='1':
                result=self.selected_object.ai.grind(beans)
                if result!=None:
                    self.world.player.add_inventory(result)
                    self.world.player.remove_inventory(beans)
                self.coffee_grinder_menu(None)
            elif Key=='2':
                pass
            elif Key=='3':
                pass
            elif Key=='4':
                self.deactivate_menu(None)

    #---------------------------------------------------------------------------
    def consumable_menu(self, Key):
        distance = engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('-- '+self.selected_object.name+' --')
            if self.world.debug_mode==True:
                d=engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
                self.world.graphic_engine.menu_text_queue.append('Distance: '+str(d))

            if distance<self.max_menu_distance:    
                self.world.graphic_engine.menu_text_queue.append('1 - Eat')
                self.world.graphic_engine.menu_text_queue.append('2 - Pick up')
                self.menu_state='base'
        if self.menu_state=='base':
            if Key=='1':
                self.world.player.ai.handle_pickup_object(self.selected_object)
                self.world.player.ai.handle_eat(self.selected_object)
                self.deactivate_menu()
            elif Key=='2':
                self.world.player.ai.handle_pickup_object(self.selected_object)
                self.deactivate_menu()

    #---------------------------------------------------------------------------
    def deactivate_menu(self):
        self.selected_object=None
        self.active_menu='none'
        self.menu_state='none'
        self.world.graphic_engine.menu_text_queue=[]

    #---------------------------------------------------------------------------
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

    #---------------------------------------------------------------------------
    def debug_menu(self, Key):
        if self.menu_state=='none':
            # print out the basic menu
            # eventually 'spawn' should get its own submenu
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--Debug Menu (~ to exit) --')
            self.world.graphic_engine.menu_text_queue.append('1 - toggle map ')
            self.world.graphic_engine.menu_text_queue.append('2 - toggle debug mode')
            self.world.graphic_engine.menu_text_queue.append('3 - spawn menu')
            self.world.graphic_engine.menu_text_queue.append('4 - none')
            self.world.graphic_engine.menu_text_queue.append('5 - toggle collision circle visual')
            self.world.graphic_engine.menu_text_queue.append('6 - none')

            if Key=='1':
                self.world.toggle_map()
            elif Key=='2':
                self.world.debug_mode=not self.world.debug_mode
            elif Key=='3':
                self.menu_state='spawn'
                Key=None
            elif Key=='4':
                pass
            elif Key=='5':
                self.world.graphic_engine.draw_collision = not self.world.graphic_engine.draw_collision
            elif Key=='6':
                pass
        if self.menu_state=='spawn':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--Debug -> Spawn Menu --')
            self.world.graphic_engine.menu_text_queue.append('1 - Vehicles ')
            self.world.graphic_engine.menu_text_queue.append('2 - Weapons ')
            self.world.graphic_engine.menu_text_queue.append('3 - Squads ')
            self.world.graphic_engine.menu_text_queue.append('4 - Misc')
 
            if Key=='1':
                self.menu_state='spawn_vehicles'
                Key=None
            elif Key=='2':
                self.menu_state='spawn_weapons'
                Key=None
            elif Key=='3':
                self.menu_state='spawn_squads'
                Key=None   
            elif Key=='4':
                self.menu_state='spawn_misc'
                Key=None
        if self.menu_state=='spawn_vehicles':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--Debug -> Spawn Menu -> Vehicles --')
            self.world.graphic_engine.menu_text_queue.append('1 - Kubelwagen ')
            self.world.graphic_engine.menu_text_queue.append('2 - Red Bicycle ')
            self.world.graphic_engine.menu_text_queue.append('3 - Ju88 ')
            self.world.graphic_engine.menu_text_queue.append('4 - Dodge G505 Weapons Carrier ')
            self.world.graphic_engine.menu_text_queue.append('5 - sd_kfz_251 ')
            if Key=='1':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'kubelwagen',True)
            elif Key=='2':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'red_bicycle',True)
            elif Key=='3':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'ju88',True)
            elif Key=='4':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'dodge_g505_wc',True)
            elif Key=='5':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'sd_kfz_251',True)
        if self.menu_state=='spawn_weapons':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--Debug -> Spawn Menu -> Weapons --')
            self.world.graphic_engine.menu_text_queue.append('1 - FG-42 Type 2 ')
            self.world.graphic_engine.menu_text_queue.append('2 - Panzerfaust ')
            self.world.graphic_engine.menu_text_queue.append('3 - Model 24 Stick Grenade ')
            self.world.graphic_engine.menu_text_queue.append('4 - German Field Shovel')
            if Key=='1':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'fg42-type2',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'fg42_type2_magazine',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'fg42_type2_magazine',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'fg42_type2_magazine',True)
            elif Key=='2':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'panzerfaust',True)
            elif Key=='3':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'model24',True)
            elif Key=='4':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'german_field_shovel',True)
        if self.menu_state=='spawn_squads':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--Debug -> Spawn Menu -> Squads --')
            self.world.graphic_engine.menu_text_queue.append('1 - German 1944 Rifle  ')
            self.world.graphic_engine.menu_text_queue.append('2 - German 1944 VG Storm Group ')
            self.world.graphic_engine.menu_text_queue.append('3 - Soviet 1944 Rifle')
            self.world.graphic_engine.menu_text_queue.append('4 - Soviet 1944 Submachine Gun')
            if Key=='1':
                engine.world_builder.create_standard_squad(self.world,self.world.german_ai,self.world.player.world_coords,'german 1944 rifle')
            elif Key=='2':
                engine.world_builder.create_standard_squad(self.world,self.world.german_ai,self.world.player.world_coords,'german 1944 volksgrenadier storm group')
            elif Key=='3':
                engine.world_builder.create_standard_squad(self.world,self.world.soviet_ai,self.world.player.world_coords,'soviet 1944 rifle')
            elif Key=='4':
                engine.world_builder.create_standard_squad(self.world,self.world.soviet_ai,self.world.player.world_coords,'soviet 1944 submachine gun')
        if self.menu_state=='spawn_misc':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--Debug -> Spawn Menu -> Misc --')
            self.world.graphic_engine.menu_text_queue.append('1 - smoke cloud  ')
            self.world.graphic_engine.menu_text_queue.append('2 - Feldfunk radio and charger ')
            self.world.graphic_engine.menu_text_queue.append('3 - ?')
            self.world.graphic_engine.menu_text_queue.append('4 - ?')
            if Key=='1':
                heading=engine.math_2d.get_heading_from_rotation(self.world.player.rotation_angle-90)
                engine.world_builder.spawn_smoke_cloud(self.world,[self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],heading)

            elif Key=='2':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+40,self.world.player.world_coords[1]],'radio_feldfu_b',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+60,self.world.player.world_coords[1]],'feldfunk_battery_charger',True)
            elif Key=='3':
                pass
            elif Key=='4':
                pass


    #---------------------------------------------------------------------------            
    def eat_drink_menu(self, Key):

        # print out the basic menu
        self.world.graphic_engine.menu_text_queue=[]
        self.world.graphic_engine.menu_text_queue.append('-- Eat/Drink Menu --')
        self.world.graphic_engine.menu_text_queue.append('Health: '+str(round(self.selected_object.ai.health,1)))
        self.world.graphic_engine.menu_text_queue.append('Hunger: '+str(round(self.selected_object.ai.hunger,1)))
        self.world.graphic_engine.menu_text_queue.append('Thirst: '+str(round(self.selected_object.ai.thirst,1)))
        self.world.graphic_engine.menu_text_queue.append('Fatigue ' + str(round(self.selected_object.ai.fatigue,1)))

        selectable_objects=[]
        selection_key=1
        for b in self.selected_object.ai.inventory:
            if selection_key<10 and b.is_consumable:
                self.world.graphic_engine.menu_text_queue.append(str(selection_key)+' - '+b.name)
                selection_key+=1
                selectable_objects.append(b)

        # get the array position corresponding to the key press
        temp=self.translate_key_to_array_position(Key)
        if temp !=None:
            if len(selectable_objects)>temp:
                self.selected_object.ai.handle_eat(selectable_objects[temp])
                # reset the menue
                self.eat_drink_menu(None)

    #---------------------------------------------------------------------------            
    def engine_menu(self, Key):

        # print out the basic menu
        self.world.graphic_engine.menu_text_queue=[]
        self.world.graphic_engine.menu_text_queue.append('-- Engine Menu --')
        self.world.graphic_engine.menu_text_queue.append('Engine / Turned On')
        
        selectable_objects=self.world.player.ai.vehicle.ai.engines
        selection_key=1
        for b in selectable_objects:
            self.world.graphic_engine.menu_text_queue.append(str(selection_key) + ': ' + b.name + ' ' + str(b.ai.engine_on))
            selection_key+=1

        self.world.graphic_engine.menu_text_queue.append('1 - Start Engines')
        self.world.graphic_engine.menu_text_queue.append('2 - Stop Engines')

        if Key=='1':
            self.world.player.ai.vehicle.ai.handle_start_engines()
            self.engine_menu(None)
        if Key=='2':
            self.world.player.ai.vehicle.ai.handle_stop_engines()
            self.engine_menu(None)


    #---------------------------------------------------------------------------            
    def first_aid_menu(self, Key):

        # print out the basic menu
        self.world.graphic_engine.menu_text_queue=[]
        self.world.graphic_engine.menu_text_queue.append('-- First Aid Menu --')
        self.world.graphic_engine.menu_text_queue.append('Health: '+str(round(self.selected_object.ai.health,1)))
        self.world.graphic_engine.menu_text_queue.append('Hunger: '+str(round(self.selected_object.ai.hunger,1)))
        self.world.graphic_engine.menu_text_queue.append('Thirst: '+str(round(self.selected_object.ai.thirst,1)))
        self.world.graphic_engine.menu_text_queue.append('Fatigue ' + str(round(self.selected_object.ai.fatigue,1)))

        selectable_objects=[]
        selection_key=1
        for b in self.selected_object.ai.inventory:
            if selection_key<10 and b.is_medical:
                self.world.graphic_engine.menu_text_queue.append(str(selection_key)+' - '+b.name)
                selection_key+=1
                selectable_objects.append(b)

        # get the array position corresponding to the key press
        temp=self.translate_key_to_array_position(Key)
        if temp !=None:
            if len(selectable_objects)>temp:
                self.selected_object.ai.handle_use_medical_object(selectable_objects[temp])
                # reset the menue
                self.first_aid_menu(None)

    #---------------------------------------------------------------------------
    def fuel_menu(self, Key):
        # to get to this menu you have to be holding a container with fuel and clicking a vehicle
        # no need for a menu state

        # find the actual fuel
        fuel=None
        for b in self.world.player.ai.large_pickup.ai.inventory:
            if 'gas' in b.name:
                fuel=b

        # in the future should distribute across the tanks 
        fuel_tank=self.selected_object.ai.fuel_tanks[0]

        # print out the basic menu
        self.world.graphic_engine.menu_text_queue=[]
        self.world.graphic_engine.menu_text_queue.append('-- Fuel Menu: '+self.selected_object.name+' --')
        self.world.graphic_engine.menu_text_queue.append('Fuel Can Contents: '+ fuel.name)
        self.world.graphic_engine.menu_text_queue.append('Current Fuel Load : '+str(fuel_tank.ai.inventory[0].volume))
        self.world.graphic_engine.menu_text_queue.append('Maximum Fuel Capacity : '+str(fuel_tank.volume))
        self.world.graphic_engine.menu_text_queue.append('1 - Add Fuel')
        self.world.graphic_engine.menu_text_queue.append('2 - Remove Fuel')
        if Key=='1':
            self.world.player.ai.handle_transfer(fuel,fuel_tank)
            # update text
            self.fuel_menu('')
        elif Key=='2':
            self.world.player.ai.handle_transfer(fuel,self.selected_object)
            # update text
            self.fuel_menu('')

    #---------------------------------------------------------------------------
    def generic_item_menu(self, Key):
        distance = engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)

        # print out the basic menu
        self.world.graphic_engine.menu_text_queue=[]
        self.world.graphic_engine.menu_text_queue.append('-- '+self.selected_object.name+' --')
        if self.world.debug_mode==True:
            self.world.graphic_engine.menu_text_queue.append('Distance: '+str(distance))

        if distance<self.max_menu_distance:
            if self.selected_object.is_human==False and self.selected_object.volume<21 and self.selected_object.weight<50:
                self.world.graphic_engine.menu_text_queue.append('1 - pick up')
                if Key=='1':
                    self.world.player.ai.handle_pickup_object(self.selected_object)
                    self.deactivate_menu()


    #---------------------------------------------------------------------------
    def gun_menu(self, Key):
        distance = engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('-- '+self.selected_object.name+' --')
            if self.world.debug_mode==True:
                self.world.graphic_engine.menu_text_queue.append('Distance: '+str(distance))
            
            if distance<self.max_menu_distance: 
                self.world.graphic_engine.menu_text_queue.append('1 - pick up')
                self.menu_state='base'
        if self.menu_state=='base':
            if Key=='1':
                self.world.player.ai.handle_pickup_object(self.selected_object)
                self.deactivate_menu()

    #---------------------------------------------------------------------------
    def human_menu(self, Key):

        self.world.graphic_engine.menu_text_queue=[]

        # get distance
        distance = engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
        if self.world.debug_mode==True:
            # do this so that ALL the text shows up
            distance=0

        # print out the basic menu
        name=''
        faction=''
        if distance<500:
            name=self.selected_object.name
            faction=self.selected_object.ai.squad.faction
        elif distance<2500:
            name='unknown'
            faction=self.selected_object.ai.squad.faction

        else:
            name='unknown'
            faction='unknown'

        self.world.graphic_engine.menu_text_queue.append('-- Human --')
        self.world.graphic_engine.menu_text_queue.append('Name: '+name)
        self.world.graphic_engine.menu_text_queue.append('Faction: '+faction)

        # -- determine what the next menu will be
        if self.selected_object==self.world.player:
            self.world.graphic_engine.menu_text_queue.append('[player]')
            self.menu_state = 'player_menu'
        else:
            if distance<150:
                if self.selected_object.ai.squad==self.world.player.ai.squad:
                    self.world.graphic_engine.menu_text_queue.append('[in your squad]')
                    self.menu_state = 'squad_member_menu'
                else:
                    self.menu_state = 'non_squad_member_menu'

        if distance<500:
            self.world.graphic_engine.menu_text_queue.append('')
            self.world.graphic_engine.menu_text_queue.append('--- Squad Info ---')
            if self.selected_object.ai.squad.squad_leader==self.selected_object:
                self.world.graphic_engine.menu_text_queue.append('Squad Leader')
            self.world.graphic_engine.menu_text_queue.append('Squad Size: '+str(len(self.selected_object.ai.squad.members)))
            self.world.graphic_engine.menu_text_queue.append('Health: '+str(round(self.selected_object.ai.health,1)))
            self.world.graphic_engine.menu_text_queue.append('Hunger: '+str(round(self.selected_object.ai.hunger,1)))
            self.world.graphic_engine.menu_text_queue.append('Thirst: '+str(round(self.selected_object.ai.thirst,1)))
            self.world.graphic_engine.menu_text_queue.append('Fatigue ' + str(round(self.selected_object.ai.fatigue,1)))
            if self.selected_object.ai.primary_weapon != None:
                self.world.graphic_engine.menu_text_queue.append('')
                self.world.graphic_engine.menu_text_queue.append('--- Weapon Info ---')
                ammo=self.selected_object.ai.handle_check_ammo(self.selected_object.ai.primary_weapon)
                self.world.graphic_engine.menu_text_queue.append('weapon: '+self.selected_object.ai.primary_weapon.name)
                self.world.graphic_engine.menu_text_queue.append('- ammo in gun: '+str(ammo[0]))
                self.world.graphic_engine.menu_text_queue.append('- ammo in inventory: '+str(ammo[1]))
                self.world.graphic_engine.menu_text_queue.append('- magazine count: '+str(ammo[2]))
                self.world.graphic_engine.menu_text_queue.append('- rounds Fired: '+str(self.selected_object.ai.primary_weapon.ai.rounds_fired))

            if self.selected_object.ai.throwable!=None:
                self.world.graphic_engine.menu_text_queue.append('[throw] '+self.selected_object.ai.throwable.name)
            self.world.graphic_engine.menu_text_queue.append('Confirmed Kills: '+str(self.selected_object.ai.confirmed_kills))
            self.world.graphic_engine.menu_text_queue.append('Probable Kills: '+str(self.selected_object.ai.probable_kills))
            self.world.graphic_engine.menu_text_queue.append(str(self.selected_object.ai.last_collision_description))

            self.world.graphic_engine.menu_text_queue.append('')

        if self.world.debug_mode==True:
            self.world.graphic_engine.menu_text_queue.append('')
            self.world.graphic_engine.menu_text_queue.append('--- Debug Info ---')
            d=engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords,True)
            d2='no squad lead'
            if self.selected_object.ai.squad.squad_leader!=None:
                d2=engine.math_2d.get_distance(self.selected_object.world_coords,self.selected_object.ai.squad.squad_leader.world_coords,True)

            d3='no target object'
            if self.selected_object.ai.target_object!=None:
                d3=engine.math_2d.get_distance(self.selected_object.world_coords,self.selected_object.ai.target_object.world_coords,True)

            self.world.graphic_engine.menu_text_queue.append('Distance from player: '+str(d))
            self.world.graphic_engine.menu_text_queue.append('Distance from squad: '+str(d2))
            self.world.graphic_engine.menu_text_queue.append('Distance from target object: '+str(d3))
            self.world.graphic_engine.menu_text_queue.append('AI State: '+str(self.selected_object.ai.ai_state))
            self.world.graphic_engine.menu_text_queue.append('AI Goal: '+str(self.selected_object.ai.ai_goal))
            self.world.graphic_engine.menu_text_queue.append('AI Vehicle Goal: '+str(self.selected_object.ai.ai_vehicle_goal))
            self.world.graphic_engine.menu_text_queue.append('Personal Enemies Count: '+str(len(self.selected_object.ai.personal_enemies)))
            self.world.graphic_engine.menu_text_queue.append('AI in building: '+str(self.selected_object.ai.in_building))

            self.world.graphic_engine.menu_text_queue.append('')

        if self.menu_state == 'player_menu':
            self.world.graphic_engine.menu_text_queue.append('1 - Manage Inventory')
            self.world.graphic_engine.menu_text_queue.append('2 - Squad Menu')
            self.world.graphic_engine.menu_text_queue.append('3 - Eat/Drink')
            self.world.graphic_engine.menu_text_queue.append('4 - First Aid')
            if self.selected_object.ai.large_pickup!=None:
                self.world.graphic_engine.menu_text_queue.append('5 - Drop '+self.selected_object.ai.large_pickup.name)
                if Key=='5':
                    self.selected_object.ai.handle_drop_object(self.selected_object.ai.large_pickup)
                    self.deactivate_menu()
            if Key=='1':
                self.change_menu('storage')
            if Key=='2':
                self.change_menu('squad')
            if Key=='3':
                self.change_menu('eat_drink')
            if Key=='4':
                self.change_menu('first_aid')
            
        elif self.menu_state == 'squad_member_menu':
            self.world.graphic_engine.menu_text_queue.append('1 - [Speak] What are you up to ?')
            self.world.graphic_engine.menu_text_queue.append('2 - Manage Inventory')
            self.world.graphic_engine.menu_text_queue.append('3 - [Speak] Can you upgrade your gear?')
            if self.world.player.ai.in_vehicle:
                self.world.graphic_engine.menu_text_queue.append('4 - [Speak] Climb aboard!')
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
            self.world.graphic_engine.menu_text_queue.append('1 - What are you up to ?')
            self.world.graphic_engine.menu_text_queue.append('2 - Will you join my squad?')
            if Key=='1':
                self.selected_object.ai.speak('status')
            if Key=='2':
            # ask the ai to join the squad
                self.selected_object.ai.react_asked_to_join_squad(self.world.player.ai.squad)
                self.deactivate_menu()


    #---------------------------------------------------------------------------            
    def radio_menu(self, Key):

        # print out the basic menu
        self.world.graphic_engine.menu_text_queue=[]
        self.world.graphic_engine.menu_text_queue.append('-- Radio Menu --')
        self.world.graphic_engine.menu_text_queue.append('Radio: '+self.selected_object.name)
        self.world.graphic_engine.menu_text_queue.append('Power status: '+str(self.selected_object.ai.power_on))
        self.world.graphic_engine.menu_text_queue.append('Frequency: '+str(self.selected_object.ai.current_frequency))
        self.world.graphic_engine.menu_text_queue.append('Volume: '+str(self.selected_object.ai.volume))
        self.world.graphic_engine.menu_text_queue.append('Transmission Power: '+str(self.selected_object.ai.transmission_power))
        

        if self.world.check_object_exists(self.selected_object):
            self.world.graphic_engine.menu_text_queue.append('1 - pick up')
            if Key=='1':
                self.world.player.ai.handle_pickup_object(self.selected_object)
                self.deactivate_menu()
                # we don't want to process anyhting after this so nothing else prints
                return

        self.world.graphic_engine.menu_text_queue.append('2 - Toggle power')

        if Key=='2':
            self.selected_object.ai.power_on= not self.selected_object.ai.power_on
            self.radio_menu(None)
            self.deactivate_menu()

    #---------------------------------------------------------------------------
    def squad_menu(self,Key):
        distance = engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
        if self.menu_state=='none':
            squad=self.world.player.ai.squad
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('-- Squad Menu --')
            self.world.graphic_engine.menu_text_queue.append('Faction: '+squad.faction)
            self.world.graphic_engine.menu_text_queue.append('Squad size: '+str(len(squad.members)))
            #self.world.graphic_engine.menu_text_queue.append('Very near enemies: '+str(len(squad.very_near_enemies)))
            #self.world.graphic_engine.menu_text_queue.append('Near enemies: '+str(len(squad.near_enemies)))
            #self.world.graphic_engine.menu_text_queue.append('Far enemies: '+str(len(squad.far_enemies)))

            self.world.graphic_engine.menu_text_queue.append('1 - Disband')
            self.world.graphic_engine.menu_text_queue.append('2 - Re-arm')
            self.world.graphic_engine.menu_text_queue.append('3 - Loose formation (not implemented)')
            self.world.graphic_engine.menu_text_queue.append('4 - Tight formation (not implemented)')

            if Key=='1':
                self.world.graphic_engine.add_text('[ Squad disbanded ]')
                # note - this will remove everyone but the player from the player's squad
                # and put them in a new squad
                members=[]
                for b in squad.members:
                    if b.is_player==False:
                        members.append(b)
                squad.faction_tactical.split_squad(members)

                # go back to the menu to reset the text
                self.squad_menu(None)

            if Key=='2':
                # tell each ai to rearm if possible 
                for b in squad.members:
                    if b.is_player==False:
                        b.ai.react_asked_to_upgrade_gear()

    #---------------------------------------------------------------------------
    def start_menu(self, Key):
        if self.menu_state=='none':
            self.world.is_paused=False
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('TWE: To Whatever End')
            self.world.graphic_engine.menu_text_queue.append('---------------')
            self.world.graphic_engine.menu_text_queue.append('Pick a Test Scenario to Load')
            self.world.graphic_engine.menu_text_queue.append('1 - Meeting Engagement : German vs Soviet')
            self.world.graphic_engine.menu_text_queue.append('2 -  ')
            self.world.graphic_engine.menu_text_queue.append('3 - ')
            #self.world.graphic_engine.menu_text_queue.append('4 - Nothing')

            if Key=='1' or Key=='2' or Key=='3':
                Key='1'
                self.menu_state='faction_select'
                engine.world_builder.load_test_environment(self.world,Key)
                Key=None

        if self.menu_state=='faction_select':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('TWE: To Whatever End')
            self.world.graphic_engine.menu_text_queue.append('---------------')
            self.world.graphic_engine.menu_text_queue.append('Pick a Faction')
            self.world.graphic_engine.menu_text_queue.append('1 - American')
            self.world.graphic_engine.menu_text_queue.append('2 - German')
            self.world.graphic_engine.menu_text_queue.append('3 - Soviet')
            self.world.graphic_engine.menu_text_queue.append('4 - Civilian/Neutral')
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

                    # disband player squad, as they are super annoying
                    squad=self.world.player.ai.squad
                    members=[]
                    for b in squad.members:
                        if b.is_player==False:
                            members.append(b)
                    squad.faction_tactical.split_squad(members)


                else:
                    print('No bots of this type available')
            
            if spawned:
                # eventually load other menus
                self.world.is_paused=False
                self.deactivate_menu()
                
    #---------------------------------------------------------------------------            
    def storage_menu(self, Key):
        distance = engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
        if self.menu_state=='none':
            # print out the basic menu
            self.world.graphic_engine.menu_text_queue.append('-- Storage Menu: ' + self.selected_object.name + ' --')

            if distance<self.max_menu_distance:  

                if self.selected_object.is_player==False:
                    self.world.graphic_engine.menu_text_queue.append('1 - Add Items ')
                    if Key=='1':
                        Key=None
                        self.menu_state='add'

                self.world.graphic_engine.menu_text_queue.append('2 - Remove Items ')
                if Key=='2':
                    Key=None
                    self.menu_state='remove'
                # should make this decision on max vol for pickup somewhere else
                # 100 pounds is about 45 kilograms. thats about max that a normal human would carry
                if self.selected_object.is_human==False and self.selected_object.volume<21 and self.selected_object.weight<50:
                    self.world.graphic_engine.menu_text_queue.append('3 - Pick up '+self.selected_object.name)
                    if Key=='3':
                        Key=None
                        self.world.player.ai.handle_pickup_object(self.selected_object)
                        self.deactivate_menu()
                        # exit function
                        return
                
                # print out contents
                count=0
                self.world.graphic_engine.menu_text_queue.append('------------- ')
                for b in self.selected_object.ai.inventory:
                    if count<6:
                        self.world.graphic_engine.menu_text_queue.append(b.name)
                    else:
                        self.world.graphic_engine.menu_text_queue.append('...')
                        break
                self.world.graphic_engine.menu_text_queue.append('------------- ')


                
                
            else:
                print('get closer')

        if self.menu_state=='add':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('-- Add Inventory Menu --')

            selectable_objects=[]
            selection_key=1
            for b in self.world.player.ai.inventory:
                if selection_key<10:
                    self.world.graphic_engine.menu_text_queue.append(str(selection_key)+' - '+b.name)
                    selection_key+=1
                    selectable_objects.append(b)

            # get the array position corresponding to the key press
            temp=self.translate_key_to_array_position(Key)
            if temp !=None:
                if len(selectable_objects)>temp:
                    self.world.player.remove_inventory(selectable_objects[temp])
                    self.selected_object.add_inventory(selectable_objects[temp])

                    # reset menu 
                    self.storage_menu(None)

        if self.menu_state=='remove':
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('-- Remove Inventory Menu --')

            selectable_objects=[]
            selection_key=1
            for b in self.selected_object.ai.inventory:
                if selection_key<10:
                    self.world.graphic_engine.menu_text_queue.append(str(selection_key)+' - '+b.name)
                    selection_key+=1
                    selectable_objects.append(b)

            # get the array position corresponding to the key press
            temp=self.translate_key_to_array_position(Key)
            if temp !=None:
                if len(selectable_objects)>temp:

                    if self.selected_object.is_player:
                        #player is looking at their own storage, so dump anything they remove on the ground
                        self.world.player.ai.handle_drop_object(selectable_objects[temp])
                    else:
                        # player is grabbing objects from some other object so put in players inventory
                        # remove from the other object
                        self.selected_object.remove_inventory(selectable_objects[temp])
                        # add to the player
                        self.world.player.add_inventory(selectable_objects[temp])
                    # reset menu 
                    self.storage_menu(None)



    #--------------------------------------------------------------------------
    def translate_key_to_array_position(self,Key):
        '''translates a Key string to a array position'''
        temp=None
        if Key=='1':
            temp=0
        elif Key=='2':
            temp=1
        elif Key=='3':
            temp=2
        elif Key=='4':
            temp=3
        elif Key=='5':
            temp=4
        elif Key=='6':
            temp=5
        elif Key=='7':
            temp=6
        elif Key=='8':
            temp=7
        elif Key=='9':
            temp=8

        return temp

    #---------------------------------------------------------------------------
    def vehicle_menu(self, Key):
        distance = engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
        if self.menu_state=='none':

            if self.world.player in self.selected_object.ai.passengers:
                self.menu_state='internal'
            else:
                self.menu_state='external'

        if self.menu_state=='external':
            fuel_option=False
            # determine if the large pickup contains fuel
            if self.world.player.ai.large_pickup!=None:
                if self.world.player.ai.large_pickup.is_container:
                    # some vehicles don't use a fuel tank
                    if len(self.selected_object.ai.fuel_tanks)>0:
                        for b in self.world.player.ai.large_pickup.ai.inventory:
                            if 'gas' in b.name:
                                fuel_option=True

            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--External Vehicle Menu : ' + self.selected_object.name + ' --')
            self.world.graphic_engine.menu_text_queue.append('Vehicle : '+self.selected_object.name)
            self.world.graphic_engine.menu_text_queue.append('Health : '+str(self.selected_object.ai.health))

            # -- add debug info --
            if self.world.debug_mode==True:
                self.world.graphic_engine.menu_text_queue.append('--debug info --')
                #self.world.graphic_engine.menu_text_queue.append('fuel type: '+self.selected_object.ai.fuel_type)
                #self.world.graphic_engine.menu_text_queue.append('fuel amount: '+str(self.selected_object.ai.fuel))
                self.world.graphic_engine.menu_text_queue.append('throttle: '+str(self.selected_object.ai.throttle))
                self.world.graphic_engine.menu_text_queue.append('brake power: '+str(self.selected_object.ai.brake_power))
                self.world.graphic_engine.menu_text_queue.append('wheel steering: '+str(self.selected_object.ai.wheel_steering))
                self.world.graphic_engine.menu_text_queue.append('vehicle speed: '+str(self.selected_object.ai.current_speed))
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
                    self.world.graphic_engine.menu_text_queue.append('---- passenger info -------------------')
                    self.world.graphic_engine.menu_text_queue.append('Name [faction/ai_state/ai_goal/vehicle_ai_goal/ai_vehicle_role]')
                    for b in self.selected_object.ai.passengers:
                        self.world.graphic_engine.menu_text_queue.append(b.name + '['+b.ai.squad.faction+' / '+b.ai.ai_state+' / '+b.ai.ai_goal+' / '+b.ai.ai_vehicle_goal+' / '+b.ai.ai_vehicle_role+']')
                    self.world.graphic_engine.menu_text_queue.append('------------------------------------')


            if distance<self.max_menu_distance:
                self.world.graphic_engine.menu_text_queue.append('Passenger count : '+str(len(self.selected_object.ai.passengers)))
                self.world.graphic_engine.menu_text_queue.append('Vehicle Health : '+str(self.selected_object.ai.health))
                self.world.graphic_engine.menu_text_queue.append('1 - info (not implemented) ')
                self.world.graphic_engine.menu_text_queue.append('2 - enter vehicle ')
                self.world.graphic_engine.menu_text_queue.append('3 - storage ')
                if fuel_option:
                    self.world.graphic_engine.menu_text_queue.append('4 - fuel ')

                if Key=='1':
                    pass
                if Key=='2':
                    # enter the vehicle 
                    self.world.player.ai.handle_enter_vehicle(self.selected_object)
                    # honestly this menu is kinda ugly. maybe better to leave it off
                    #self.world.display_vehicle_text=True
                    self.world.graphic_engine.add_text('[ You climb into the vehicle ]')
                    self.deactivate_menu()
                if Key=='3':
                    # pull up the storage/container menu
                    self.change_menu('storage')
                if Key=='4' and fuel_option:
                    self.change_menu('fuel')

        if self.menu_state=='internal':
            currentRole=self.world.player.ai.ai_vehicle_role
            if currentRole==None:
                currentRole='none'

            radio=False
            if self.selected_object.ai.radio!=None:
                radio=True
            self.world.graphic_engine.menu_text_queue=[]
            self.world.graphic_engine.menu_text_queue.append('--Internal Vehicle Menu --')
            self.world.graphic_engine.menu_text_queue.append('Vehicle : '+self.selected_object.name)
            self.world.graphic_engine.menu_text_queue.append('Health : '+str(self.selected_object.ai.health))
            self.world.graphic_engine.menu_text_queue.append('Current Role : '+currentRole)
            if radio:
                self.world.graphic_engine.menu_text_queue.append('Radio : '+self.selected_object.ai.radio.name)
            if len(self.selected_object.ai.engines)>0:
                self.world.graphic_engine.menu_text_queue.append('Engine : '+str(self.selected_object.ai.engines[0].ai.engine_on))
            self.world.graphic_engine.menu_text_queue.append('passenger count : '+str(len(self.selected_object.ai.passengers)))
            self.world.graphic_engine.menu_text_queue.append('1 - change role')
            self.world.graphic_engine.menu_text_queue.append('2 - exit vehicle ')
            self.world.graphic_engine.menu_text_queue.append('3 - engine menu')
            self.world.graphic_engine.menu_text_queue.append('4 - toggle HUD')
            if radio:
                self.world.graphic_engine.menu_text_queue.append('5 - radio')
            if Key=='1':
                self.change_menu('change_vehicle_role')
            if Key=='2':
                # exit the vehicle
                self.world.player.ai.handle_exit_vehicle()
                self.world.display_vehicle_text=False
                self.world.graphic_engine.text_queue.insert(0, '[ You exit the vehicle ]')
                self.deactivate_menu()
            if Key=='3':
                self.change_menu('engine_menu')
            if Key=='4':
                #flip the bool
                self.world.display_vehicle_text=not self.world.display_vehicle_text
                #refresh the text
                self.vehicle_menu('none')
            if Key=='5' and radio:
                self.selected_object=self.selected_object.ai.radio
                self.change_menu('radio_menu')

    #---------------------------------------------------------------------------
    def update(self):

        # should maybe check if a menu is active first. no need for this to be constantly running
        # make the menu auto close after a period of time
        self.time_since_input+=self.world.graphic_engine.time_passed_seconds
        if self.time_since_input>self.max_menu_idle_time and self.active_menu!='start':
            self.deactivate_menu()

