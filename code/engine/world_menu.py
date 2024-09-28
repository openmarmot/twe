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

        self.text_queue=[]

    #---------------------------------------------------------------------------
    def handle_input(self,key):
        # called by graphics_2d_pygame when there is a suitable key press
        # key is a string corresponding to the actual key being pressed
        
        # reset timer
        self.time_since_input=0

        # '~' is used to activate/deactivate the debug menu
        if key=='tilde':
            if self.active_menu=='debug':
                self.deactivate_menu()
                #self.world.is_paused=False
            else :
                if self.active_menu!='death':
                    self.deactivate_menu()
                    self.active_menu='debug'
                    #self.world.is_paused=True
                    #print('Game Paused')
        elif key=='esc':
            # exit any active menu
            if self.active_menu!='death':
                self.deactivate_menu()

        if self.active_menu=='vehicle':
            self.vehicle_menu(key)
        elif self.active_menu=='debug':
            self.debug_menu(key)
        elif self.active_menu=='gun':
            self.gun_menu(key)
        elif self.active_menu=='storage':
            self.storage_menu(key)
        elif self.active_menu=='generic':
            self.generic_item_menu(key)
        elif self.active_menu=='human':
            self.human_menu(key)
        elif self.active_menu=='airplane':
            self.airplane_menu(key)
        elif self.active_menu=='death':
            self.death_menu(key)
        elif self.active_menu=='consumable':
            self.consumable_menu(key)
        elif self.active_menu=='fuel':
            self.fuel_menu(key)
        elif self.active_menu=='change_vehicle_role':
            self.change_vehicle_role_menu(key)
        elif self.active_menu=='coffee_grinder':
            self.coffee_grinder_menu(key)
        elif self.active_menu=='squad':
            self.squad_menu(key)
        elif self.active_menu=='eat_drink':
            self.eat_drink_menu(key)
        elif self.active_menu=='first_aid':
            self.first_aid_menu(key)
        elif self.active_menu=='engine_menu':
            self.engine_menu(key)
        elif self.active_menu=='radio_menu':
            self.radio_menu(key)
        else:
            if self.active_menu!='none':
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
        self.text_queue=[]
        self.active_menu=menu_name
        self.handle_input(None)

    #---------------------------------------------------------------------------
    def change_vehicle_role_menu(self, key):
        if self.menu_state=='none':
            # print out the basic menu
            self.text_queue.append('-- Change Vehicle Role --')
            currentRole=self.world.player.ai.memory['task_vehicle_crew']['role']
            if currentRole==None:
                currentRole='None!'

            self.text_queue.append('Vehicle : '+self.selected_object.name)
            self.text_queue.append('Current Role : '+currentRole)
            self.text_queue.append('1 - Driver')
            self.text_queue.append('2 - Gunner')
            self.text_queue.append('3 - Passenger')
            self.text_queue.append('4 - Chef')
            self.menu_state='base'
        if self.menu_state=='base':
            if key=='1':
                self.world.player.ai.player_vehicle_role_change('driver')
                self.deactivate_menu()
            elif key=='2':
                self.world.player.ai.player_vehicle_role_change('gunner')
                self.deactivate_menu()
            elif key=='3':
                self.world.player.ai.player_vehicle_role_change('passenger')
                self.deactivate_menu()

     #---------------------------------------------------------------------------
    def coffee_grinder_menu(self, key):
        # print out the basic menu
        self.text_queue.append('-- Coffee Grinder Menu --')
        
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
            self.text_queue.append('Ground Coffee weight: '+str(grounds.weight))
        if beans==None:
            self.text_queue.append("I will need to get some coffee beans first..")
        else:
            self.text_queue.append('Beans.. volume? : '+str(beans.volume))
            self.text_queue.append('Beans.. weight? : '+str(beans.weight))
        
            self.text_queue.append('1 - Grind Beans')
            self.text_queue.append('4 - Exit')

            if key=='1':
                result=self.selected_object.ai.grind(beans)
                if result!=None:
                    self.world.player.add_inventory(result)
                    self.world.player.remove_inventory(beans)
                self.coffee_grinder_menu(None)
            elif key=='2':
                pass
            elif key=='3':
                pass
            elif key=='4':
                self.deactivate_menu(None)

    #---------------------------------------------------------------------------
    def consumable_menu(self, key):
        distance = engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
        if self.menu_state=='none':
            # print out the basic menu
            self.text_queue.append('-- '+self.selected_object.name+' --')
            if self.world.debug_mode==True:
                d=engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
                self.text_queue.append('Distance: '+str(d))

            if distance<self.max_menu_distance:    
                self.text_queue.append('1 - Eat')
                self.text_queue.append('2 - Pick up')
                self.menu_state='base'
        if self.menu_state=='base':
            if key=='1':
                self.world.player.ai.pickup_object(self.selected_object)
                self.world.player.ai.eat(self.selected_object)
                self.deactivate_menu()
            elif key=='2':
                self.world.player.ai.pickup_object(self.selected_object)
                self.deactivate_menu()

    #---------------------------------------------------------------------------
    def deactivate_menu(self):
        self.selected_object=None
        self.active_menu='none'
        self.menu_state='none'
        self.text_queue=[]

    #---------------------------------------------------------------------------
    def death_menu(self,key):
        ''' menu options for when player dies '''
        if self.menu_state=='none':
            self.world.is_paused=True
            self.text_queue=[]
            self.text_queue.append('You Died')
            self.text_queue.append(self.world.player.ai.last_collision_description)
            self.text_queue.append('1 - respawn as random existing bot')
            #self.text_queue.append('3 - pick up')
            #self.text_queue.append('3 - pick up')

            self.menu_state='base'
        if self.menu_state=='base':
            if key=='1':
                self.world.spawn_player('random')
                self.world.is_paused=False
                self.deactivate_menu()

    #---------------------------------------------------------------------------
    def debug_menu(self, key):
        if self.menu_state=='none':
            # print out the basic menu
            # eventually 'spawn' should get its own submenu
            self.text_queue=[]
            self.text_queue.append('--Debug Menu (~ to exit) --')
            self.text_queue.append('1 - toggle map ')
            self.text_queue.append('2 - toggle debug mode')
            self.text_queue.append('3 - spawn menu')
            self.text_queue.append('4 - none')
            self.text_queue.append('5 - none')
            self.text_queue.append('6 - none')

            if key=='1':
                self.world.toggle_map()
            elif key=='2':
                self.world.debug_mode=not self.world.debug_mode
            elif key=='3':
                self.menu_state='spawn'
                key=None
            elif key=='4':
                pass
            elif key=='5':
                print('boop')
            elif key=='6':
                pass
        if self.menu_state=='spawn':
            self.text_queue=[]
            self.text_queue.append('--Debug -> Spawn Menu --')
            self.text_queue.append('1 - Vehicles ')
            self.text_queue.append('2 - Weapons ')
            self.text_queue.append('3 - Squads ')
            self.text_queue.append('4 - Misc')
 
            if key=='1':
                self.menu_state='spawn_vehicles'
                key=None
            elif key=='2':
                self.menu_state='spawn_weapons'
                key=None
            elif key=='3':
                self.menu_state='spawn_squads'
                key=None   
            elif key=='4':
                self.menu_state='spawn_misc'
                key=None
        if self.menu_state=='spawn_vehicles':
            self.text_queue=[]
            self.text_queue.append('--Debug -> Spawn Menu -> Vehicles --')
            self.text_queue.append('1 - Kubelwagen ')
            self.text_queue.append('2 - Red Bicycle ')
            self.text_queue.append('3 - Ju88 ')
            self.text_queue.append('4 - Dodge G505 Weapons Carrier ')
            self.text_queue.append('5 - sd_kfz_251 ')
            if key=='1':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'kubelwagen',True)
            elif key=='2':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'red_bicycle',True)
            elif key=='3':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'ju88',True)
            elif key=='4':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'dodge_g505_wc',True)
            elif key=='5':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'sd_kfz_251',True)
        if self.menu_state=='spawn_weapons':
            self.text_queue=[]
            self.text_queue.append('--Debug -> Spawn Menu -> Weapons --')
            self.text_queue.append('1 - FG-42 Type 2 ')
            self.text_queue.append('2 - Panzerfaust ')
            self.text_queue.append('3 - Model 24 Stick Grenade ')
            self.text_queue.append('4 - German Field Shovel')
            if key=='1':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'fg42-type2',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'fg42_type2_magazine',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'fg42_type2_magazine',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'fg42_type2_magazine',True)
            elif key=='2':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'panzerfaust',True)
            elif key=='3':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'model24',True)
            elif key=='4':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'german_field_shovel',True)
        if self.menu_state=='spawn_squads':
            self.text_queue=[]
            self.text_queue.append('--Debug -> Spawn Menu -> Squads --')
            self.text_queue.append('1 - German 1944 Rifle  ')
            self.text_queue.append('2 - German 1944 VG Storm Group ')
            self.text_queue.append('3 - Soviet 1944 Rifle')
            self.text_queue.append('4 - Soviet 1944 Submachine Gun')
            if key=='1':
                print('this needs a rewrite')
                #engine.world_builder.create_standard_squad(self.world,self.world.german_ai,self.world.player.world_coords,'german 1944 rifle')
            elif key=='2':
                print('this needs a rewrite')
                #engine.world_builder.create_standard_squad(self.world,self.world.german_ai,self.world.player.world_coords,'german 1944 volksgrenadier storm group')
            elif key=='3':
                print('this needs a rewrite')
                #engine.world_builder.create_standard_squad(self.world,self.world.soviet_ai,self.world.player.world_coords,'soviet 1944 rifle')
            elif key=='4':
                print('this needs a rewrite')
                #engine.world_builder.create_standard_squad(self.world,self.world.soviet_ai,self.world.player.world_coords,'soviet 1944 submachine gun')
        if self.menu_state=='spawn_misc':
            self.text_queue=[]
            self.text_queue.append('--Debug -> Spawn Menu -> Misc --')
            self.text_queue.append('1 - smoke cloud  ')
            self.text_queue.append('2 - Feldfunk radio and charger ')
            self.text_queue.append('3 - Maybach HL42')
            self.text_queue.append('4 - ?')
            if key=='1':
                heading=engine.math_2d.get_heading_from_rotation(self.world.player.rotation_angle-90)
                engine.world_builder.spawn_smoke_cloud(self.world,[self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],heading)

            elif key=='2':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+40,self.world.player.world_coords[1]],'radio_feldfu_b',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+60,self.world.player.world_coords[1]],'feldfunk_battery_charger',True)
            elif key=='3':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+40,self.world.player.world_coords[1]],'maybach_hl42_engine',True)
            elif key=='4':
                pass


    #---------------------------------------------------------------------------            
    def eat_drink_menu(self, key):

        # print out the basic menu
        self.text_queue=[]
        self.text_queue.append('-- Eat/Drink Menu --')
        self.text_queue.append('Health: '+str(round(self.selected_object.ai.health,1)))
        self.text_queue.append('Hunger: '+str(round(self.selected_object.ai.hunger,1)))
        self.text_queue.append('Thirst: '+str(round(self.selected_object.ai.thirst,1)))
        self.text_queue.append('Fatigue ' + str(round(self.selected_object.ai.fatigue,1)))

        selectable_objects=[]
        selection_key=1
        for b in self.selected_object.ai.inventory:
            if selection_key<10 and b.is_consumable:
                self.text_queue.append(str(selection_key)+' - '+b.name)
                selection_key+=1
                selectable_objects.append(b)

        # get the array position corresponding to the key press
        temp=self.translate_key_to_array_position(key)
        if temp !=None:
            if len(selectable_objects)>temp:
                self.selected_object.ai.eat(selectable_objects[temp])
                # reset the menue
                self.eat_drink_menu(None)

    #---------------------------------------------------------------------------            
    def engine_menu(self, key):

        vehicle=self.world.player.ai.memory['task_vehicle_crew']['vehicle']

        # print out the basic menu
        self.text_queue=[]
        self.text_queue.append('-- Engine Menu --')
        self.text_queue.append('Engine Status')
        
        selectable_objects=vehicle.ai.engines
        selection_key=1
        for b in selectable_objects:
            self.text_queue.append(str(selection_key) + ': ' + b.name + ' ' + str(b.ai.engine_on))
            selection_key+=1

        self.text_queue.append('1 - Start Engines')
        self.text_queue.append('2 - Stop Engines')

        if key=='1':
            vehicle.ai.handle_start_engines()
            self.engine_menu(None)
        if key=='2':
            vehicle.ai.handle_stop_engines()
            self.engine_menu(None)


    #---------------------------------------------------------------------------            
    def first_aid_menu(self, key):

        # print out the basic menu
        self.text_queue=[]
        self.text_queue.append('-- First Aid Menu --')
        self.text_queue.append('Health: '+str(round(self.selected_object.ai.health,1)))
        self.text_queue.append('Hunger: '+str(round(self.selected_object.ai.hunger,1)))
        self.text_queue.append('Thirst: '+str(round(self.selected_object.ai.thirst,1)))
        self.text_queue.append('Fatigue ' + str(round(self.selected_object.ai.fatigue,1)))

        selectable_objects=[]
        selection_key=1
        for b in self.selected_object.ai.inventory:
            if selection_key<10 and b.is_medical:
                self.text_queue.append(str(selection_key)+' - '+b.name)
                selection_key+=1
                selectable_objects.append(b)

        # get the array position corresponding to the key press
        temp=self.translate_key_to_array_position(key)
        if temp !=None:
            if len(selectable_objects)>temp:
                self.selected_object.ai.use_medical_object(selectable_objects[temp])
                # reset the menue
                self.first_aid_menu(None)

    #---------------------------------------------------------------------------
    def fuel_menu(self, key):
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
        self.text_queue=[]
        self.text_queue.append('-- Fuel Menu: '+self.selected_object.name+' --')
        self.text_queue.append('Fuel Can Contents: '+ fuel.name)
        self.text_queue.append('Current Fuel Load : '+str(fuel_tank.ai.inventory[0].volume))
        self.text_queue.append('Maximum Fuel Capacity : '+str(fuel_tank.volume))
        self.text_queue.append('1 - Add Fuel')
        self.text_queue.append('2 - Remove Fuel')
        if key=='1':
            self.world.player.ai.transfer_liquid(fuel,fuel_tank)
            # update text
            self.fuel_menu('')
        elif key=='2':
            self.world.player.ai.transfer_liquid(fuel,self.selected_object)
            # update text
            self.fuel_menu('')

    #---------------------------------------------------------------------------
    def generic_item_menu(self, key):
        distance = engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)

        # print out the basic menu
        self.text_queue=[]
        self.text_queue.append('-- '+self.selected_object.name+' --')
        if self.world.debug_mode==True:
            self.text_queue.append('Distance: '+str(distance))

        if distance<self.max_menu_distance:
            if self.selected_object.is_human==False and self.selected_object.volume<21 and self.selected_object.weight<50:
                self.text_queue.append('1 - pick up')
                if key=='1':
                    self.world.player.ai.pickup_object(self.selected_object)
                    self.deactivate_menu()


    #---------------------------------------------------------------------------
    def gun_menu(self, key):
        distance = engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
        if self.menu_state=='none':
            # print out the basic menu
            self.text_queue.append('-- '+self.selected_object.name+' --')
            if self.world.debug_mode==True:
                self.text_queue.append('Distance: '+str(distance))
            
            if distance<self.max_menu_distance: 
                self.text_queue.append('1 - pick up')
                self.menu_state='base'
        if self.menu_state=='base':
            if key=='1':
                self.world.player.ai.pickup_object(self.selected_object)
                self.deactivate_menu()

    #---------------------------------------------------------------------------
    def human_menu(self, key):

        self.text_queue=[]

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

        self.text_queue.append('-- Human --')
        self.text_queue.append('Name: '+name)
        self.text_queue.append('Faction: '+faction)

        # -- determine what the next menu will be
        if self.selected_object==self.world.player:
            self.text_queue.append('[player]')
            self.menu_state = 'player_menu'
        else:
            if distance<150:
                if self.selected_object.ai.squad==self.world.player.ai.squad:
                    self.text_queue.append('[in your squad]')
                    self.menu_state = 'squad_member_menu'
                else:
                    self.menu_state = 'non_squad_member_menu'

        if distance<500:
            self.text_queue.append('')
            self.text_queue.append('--- Squad Info ---')
            if self.selected_object.ai.squad.squad_leader==self.selected_object:
                self.text_queue.append('Squad Leader')
            self.text_queue.append('Squad Size: '+str(len(self.selected_object.ai.squad.members)))
            self.text_queue.append('Health: '+str(round(self.selected_object.ai.health,1)))
            self.text_queue.append('Hunger: '+str(round(self.selected_object.ai.hunger,1)))
            self.text_queue.append('Thirst: '+str(round(self.selected_object.ai.thirst,1)))
            self.text_queue.append('Fatigue ' + str(round(self.selected_object.ai.fatigue,1)))
            if self.selected_object.ai.primary_weapon != None:
                self.text_queue.append('')
                self.text_queue.append('--- Weapon Info ---')
                ammo_gun,ammo_inventory,magazine_count=self.selected_object.ai.check_ammo(self.selected_object.ai.primary_weapon)
                self.text_queue.append('weapon: '+self.selected_object.ai.primary_weapon.name)
                self.text_queue.append('- ammo in gun: '+str(ammo_gun))
                self.text_queue.append('- ammo in inventory: '+str(ammo_inventory))
                self.text_queue.append('- magazine count: '+str(magazine_count))
                self.text_queue.append('- rounds Fired: '+str(self.selected_object.ai.primary_weapon.ai.rounds_fired))

            if self.selected_object.ai.throwable!=None:
                self.text_queue.append('[throw] '+self.selected_object.ai.throwable.name)
            self.text_queue.append('Confirmed Kills: '+str(self.selected_object.ai.confirmed_kills))
            self.text_queue.append('Probable Kills: '+str(self.selected_object.ai.probable_kills))
            self.text_queue.append(str(self.selected_object.ai.last_collision_description))

            self.text_queue.append('')

        if self.world.debug_mode==True:
            self.text_queue.append('')
            self.text_queue.append('--- Debug Info ---')
            d=engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords,True)
            d2='no squad lead'
            if self.selected_object.ai.squad.squad_leader!=None:
                d2=engine.math_2d.get_distance(self.selected_object.world_coords,self.selected_object.ai.squad.squad_leader.world_coords,True)
            self.text_queue.append('current task: '+self.selected_object.ai.memory['current_task'])
            self.text_queue.append('Distance from player: '+str(d))
            self.text_queue.append('Distance from squad: '+str(d2))
            self.text_queue.append('AI in building: '+str(self.selected_object.ai.in_building))

            self.text_queue.append('')

        if self.menu_state == 'player_menu':
            self.text_queue.append('1 - Manage Inventory')
            self.text_queue.append('2 - Squad Menu')
            self.text_queue.append('3 - Eat/Drink')
            self.text_queue.append('4 - First Aid')
            if self.selected_object.ai.large_pickup!=None:
                self.text_queue.append('5 - Drop '+self.selected_object.ai.large_pickup.name)
                if key=='5':
                    self.selected_object.ai.drop_object(self.selected_object.ai.large_pickup)
                    self.deactivate_menu()
            if key=='1':
                self.change_menu('storage')
            if key=='2':
                self.change_menu('squad')
            if key=='3':
                self.change_menu('eat_drink')
            if key=='4':
                self.change_menu('first_aid')
            
        elif self.menu_state == 'squad_member_menu':
            self.text_queue.append('1 - [Speak] What are you up to ?')
            self.text_queue.append('2 - Manage Inventory')
            self.text_queue.append('3 - [Speak] Can you upgrade your gear?')
            if self.world.player.ai.memory['current_task']=='task_vehicle_crew':
                self.text_queue.append('4 - [Speak] Climb aboard!')
            if key=='1':
                self.selected_object.ai.speak('status')
            if key=='2':
                # pull up the storage/container menu
                self.change_menu('storage')
            if key=='3':
                self.selected_object.ai.handle_event('speak',['ask to upgrade gear',None])
            if key=='4' and self.world.player.ai.memory['current_task']=='task_vehicle_crew':
                self.selected_object.ai.handle_event('speak',['task_enter_vehicle',self.world.player.ai.vehicle])
        elif self.menu_state == 'non_squad_member_menu':
            self.text_queue.append('1 - What are you up to ?')
            self.text_queue.append('2 - Will you join my squad?')
            if key=='1':
                self.selected_object.ai.speak('status')
            if key=='2':
                self.selected_object.ai.handle_event('speak',['ask to join squad',self.world.player.ai.squad])
                self.deactivate_menu()


    #---------------------------------------------------------------------------            
    def radio_menu(self, key):

        # print out the basic menu
        self.text_queue=[]
        self.text_queue.append('-- Radio Menu --')
        self.text_queue.append('Radio: '+self.selected_object.name)
        self.text_queue.append('Power status: '+str(self.selected_object.ai.power_on))
        self.text_queue.append('Frequency: '+str(self.selected_object.ai.current_frequency))
        self.text_queue.append('Volume: '+str(self.selected_object.ai.volume))
        self.text_queue.append('Transmission Power: '+str(self.selected_object.ai.transmission_power))
        

        if self.world.check_object_exists(self.selected_object):
            self.text_queue.append('1 - pick up')
            if key=='1':
                self.world.player.ai.pickup_object(self.selected_object)
                self.deactivate_menu()
                # we don't want to process anyhting after this so nothing else prints
                return

        self.text_queue.append('2 - Toggle power')

        if key=='2':
            self.selected_object.ai.power_on= not self.selected_object.ai.power_on
            self.radio_menu(None)
            

    #---------------------------------------------------------------------------
    def squad_menu(self,key):
        distance = engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
        if self.menu_state=='none':
            squad=self.world.player.ai.squad
            # print out the basic menu
            self.text_queue=[]
            self.text_queue.append('-- Squad Menu --')
            self.text_queue.append('Faction: '+squad.faction)
            self.text_queue.append('Squad size: '+str(len(squad.members)))


            self.text_queue.append('1 - Disband')
            self.text_queue.append('2 - Re-arm')
            self.text_queue.append('3 - Loose formation (not implemented)')
            self.text_queue.append('4 - Tight formation (not implemented)')

            if key=='1':
                self.world.text_queue.append('[ Squad disbanded ]')
                # note - this will remove everyone but the player from the player's squad
                # and put them in a new squad
                members=[]
                for b in squad.members:
                    if b.is_player==False:
                        members.append(b)
                squad.faction_tactical.split_squad(members)

                # go back to the menu to reset the text
                self.squad_menu(None)

            if key=='2':
                # tell each ai to rearm if possible 
                for b in squad.members:
                    if b.is_player==False:
                        b.ai.handle_event('speak',['ask to upgrade gear',None])
            
    #---------------------------------------------------------------------------            
    def storage_menu(self, key):
        distance = engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
        if self.menu_state=='none':
            # print out the basic menu
            self.text_queue.append('-- Storage Menu: ' + self.selected_object.name + ' --')

            if distance<self.max_menu_distance:  

                if self.selected_object.is_player==False:
                    self.text_queue.append('1 - Add Items ')
                    if key=='1':
                        key=None
                        self.menu_state='add'

                self.text_queue.append('2 - Remove Items ')
                if key=='2':
                    key=None
                    self.menu_state='remove'
                # should make this decision on max vol for pickup somewhere else
                # 100 pounds is about 45 kilograms. thats about max that a normal human would carry
                if self.selected_object.is_human==False and self.selected_object.volume<21 and self.selected_object.weight<50:
                    self.text_queue.append('3 - Pick up '+self.selected_object.name)
                    if key=='3':
                        key=None
                        self.world.player.ai.pickup_object(self.selected_object)
                        self.deactivate_menu()
                        # exit function
                        return
                
                # print out contents
                count=0
                self.text_queue.append('------------- ')
                for b in self.selected_object.ai.inventory:
                    if count<6:
                        if b.is_gun_magazine:
                            self.text_queue.append(b.name+' '+str(len(b.ai.projectiles)))
                        else:
                            self.text_queue.append(b.name)
                    else:
                        self.text_queue.append('...')
                        break
                self.text_queue.append('------------- ')

            else:
                print('get closer')

        if self.menu_state=='add':
            self.text_queue=[]
            self.text_queue.append('-- Add Inventory Menu --')

            selectable_objects=[]
            selection_key=1
            for b in self.world.player.ai.inventory:
                if selection_key<10:
                    self.text_queue.append(str(selection_key)+' - '+b.name)
                    selection_key+=1
                    selectable_objects.append(b)

            # get the array position corresponding to the key press
            temp=self.translate_key_to_array_position(key)
            if temp !=None:
                if len(selectable_objects)>temp:
                    self.world.player.remove_inventory(selectable_objects[temp])
                    self.selected_object.add_inventory(selectable_objects[temp])

                    # reset menu 
                    self.storage_menu(None)

        if self.menu_state=='remove':
            self.text_queue=[]
            self.text_queue.append('-- Remove Inventory Menu --')

            selectable_objects=[]
            selection_key=1
            for b in self.selected_object.ai.inventory:
                if selection_key<10:
                    self.text_queue.append(str(selection_key)+' - '+b.name)
                    selection_key+=1
                    selectable_objects.append(b)

            # get the array position corresponding to the key press
            temp=self.translate_key_to_array_position(key)
            if temp !=None:
                if len(selectable_objects)>temp:

                    if self.selected_object.is_player:
                        #player is looking at their own storage, so dump anything they remove on the ground
                        self.world.player.ai.drop_object(selectable_objects[temp])
                    else:
                        # player is grabbing objects from some other object so put in players inventory
                        # remove from the other object
                        self.selected_object.remove_inventory(selectable_objects[temp])
                        # add to the player
                        self.world.player.add_inventory(selectable_objects[temp])
                    # reset menu 
                    self.storage_menu(None)



    #--------------------------------------------------------------------------
    def translate_key_to_array_position(self,key):
        '''translates a key string to a array position'''
        temp=None
        if key=='1':
            temp=0
        elif key=='2':
            temp=1
        elif key=='3':
            temp=2
        elif key=='4':
            temp=3
        elif key=='5':
            temp=4
        elif key=='6':
            temp=5
        elif key=='7':
            temp=6
        elif key=='8':
            temp=7
        elif key=='9':
            temp=8

        return temp

    #---------------------------------------------------------------------------
    def vehicle_menu(self, key):
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

            self.text_queue=[]
            self.text_queue.append('--External Vehicle Menu : ' + self.selected_object.name + ' --')
            self.text_queue.append('Vehicle : '+self.selected_object.name)
            self.text_queue.append('Health : '+str(self.selected_object.ai.health))

            # -- add debug info --
            if self.world.debug_mode==True:
                self.text_queue.append('--debug info --')
                #self.text_queue.append('fuel type: '+self.selected_object.ai.fuel_type)
                #self.text_queue.append('fuel amount: '+str(self.selected_object.ai.fuel))
                self.text_queue.append('throttle: '+str(self.selected_object.ai.throttle))
                self.text_queue.append('brake power: '+str(self.selected_object.ai.brake_power))
                self.text_queue.append('wheel steering: '+str(self.selected_object.ai.wheel_steering))
                self.text_queue.append('vehicle speed: '+str(self.selected_object.ai.current_speed))
                self.text_queue.append('acceleration: '+str(self.selected_object.ai.acceleration))
                self.text_queue.append('passenger count: '+str(len(self.selected_object.ai.passengers)))
                if self.selected_object.ai.driver==None:
                    self.text_queue.append('driver: None')
                else:
                    self.text_queue.append('---- driver info -------------------')
                    self.text_queue.append('driver: '+self.selected_object.ai.driver.name)
                    vehicle_destination_distance=engine.math_2d.get_distance(self.selected_object.world_coords,self.selected_object.ai.driver.ai.memory['task_vehicle_crew']['destination'])
                    self.text_queue.append('distance to driver destination: '+str(vehicle_destination_distance))
                # passenger info
                self.text_queue.append('---- passenger info -------------------')
                self.text_queue.append('Name/Faction/Role')
                for b in self.selected_object.ai.passengers:
                    self.text_queue.append(b.name + '/'+b.ai.squad.faction+'/'+b.ai.memory['task_vehicle_crew']['role'])
                self.text_queue.append('------------------------------------')

            if distance<self.max_menu_distance:
                self.text_queue.append('Passenger count : '+str(len(self.selected_object.ai.passengers)))
                self.text_queue.append('Vehicle Health : '+str(self.selected_object.ai.health))
                self.text_queue.append('1 - info (not implemented) ')
                self.text_queue.append('2 - enter vehicle ')
                self.text_queue.append('3 - storage ')
                if fuel_option:
                    self.text_queue.append('4 - fuel ')

                if key=='1':
                    pass
                if key=='2':
                    # enter the vehicle 
                    self.world.player.ai.switch_task_enter_vehicle(self.selected_object,[0,0])
                    # honestly this menu is kinda ugly. maybe better to leave it off
                    #self.world.display_vehicle_text=True
                    self.world.text_queue.append('[ You climb into the vehicle ]')
                    self.deactivate_menu()
                if key=='3':
                    # pull up the storage/container menu
                    self.change_menu('storage')
                if key=='4' and fuel_option:
                    self.change_menu('fuel')

        if self.menu_state=='internal':
            currentRole=self.world.player.ai.memory['task_vehicle_crew']['role']
            if currentRole==None:
                currentRole='none'

            radio=False
            if self.selected_object.ai.radio!=None:
                radio=True
            self.text_queue=[]
            self.text_queue.append('--Internal Vehicle Menu --')
            self.text_queue.append('Vehicle : '+self.selected_object.name)
            self.text_queue.append('Health : '+str(self.selected_object.ai.health))
            self.text_queue.append('Current Role : '+currentRole)
            if radio:
                self.text_queue.append('Radio : '+self.selected_object.ai.radio.name)
            if len(self.selected_object.ai.engines)>0:
                self.text_queue.append('Engine : '+str(self.selected_object.ai.engines[0].ai.engine_on))
            self.text_queue.append('passenger count : '+str(len(self.selected_object.ai.passengers)))
            self.text_queue.append('1 - change role')
            self.text_queue.append('2 - exit vehicle ')
            self.text_queue.append('3 - engine menu')
            self.text_queue.append('4 - toggle HUD')
            if radio:
                self.text_queue.append('5 - radio')
            if key=='1':
                self.change_menu('change_vehicle_role')
            if key=='2':
                # exit the vehicle
                self.world.player.ai.switch_task_exit_vehicle(self.world.player.ai.memory['task_vehicle_crew']['vehicle'])
                self.world.display_vehicle_text=False
                self.world.text_queue.append('[ You exit the vehicle ]')
                self.deactivate_menu()
            if key=='3':
                self.change_menu('engine_menu')
            if key=='4':
                #flip the bool
                self.world.display_vehicle_text=not self.world.display_vehicle_text
                #refresh the text
                self.vehicle_menu('none')
            if key=='5' and radio:
                self.selected_object=self.selected_object.ai.radio
                self.change_menu('radio_menu')

    #---------------------------------------------------------------------------
    def update(self):

        # should maybe check if a menu is active first. no need for this to be constantly running
        # make the menu auto close after a period of time
        self.time_since_input+=self.world.time_passed_seconds
        if self.time_since_input>self.max_menu_idle_time and self.active_menu!='start':
            self.deactivate_menu()

