'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
this class contains code for the world in game menu
instantiated by the world class

this should mostly call methods from other classes. I don't want 
a lot of game logic here

'''

#import built in modules
import random
import copy

#import custom packages
import engine.world_builder 
import engine.math_2d
import engine.world_radio
import engine.log

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

        # used for multiple page layouts
        self.current_page=0

        # used by storage menu 
        self.storage_menu_selection=None

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
        elif self.active_menu=='exit_world':
            self.exit_world_menu(key)
        elif self.activate_menu=='hit_marker':
            self.hit_marker_menu(key)
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
                self.current_page=0
                self.storage_menu_selection=None
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
            elif SELECTED_OBJECT.is_hit_marker:
                self.active_menu='hit_marker'
                self.hit_marker_menu(None)
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
            vehicle=self.world.player.ai.memory['task_vehicle_crew']['vehicle']
            if currentRole==None:
                currentRole='None!'

            self.text_queue.append('Vehicle : '+self.selected_object.name)
            self.text_queue.append('Current Role : '+currentRole)
            if currentRole!='driver':
                self.text_queue.append('1 - Driver')
                if key=='1':
                    self.world.player.ai.player_vehicle_role_change('driver')
                    self.deactivate_menu()
                    return
            if currentRole!='gunner_1' and 'gunner_1' in vehicle.ai.vehicle_crew:
                self.text_queue.append('2 - Turret: '+vehicle.ai.vehicle_crew['gunner_1'][5].name)
                if key=='2':
                    self.world.player.ai.player_vehicle_role_change('gunner_1')
                    self.deactivate_menu()
                    return
            if currentRole!='gunner_2' and 'gunner_2' in vehicle.ai.vehicle_crew:
                if len(vehicle.ai.turrets)>1:
                    self.text_queue.append('3 - Turret: '+vehicle.ai.vehicle_crew['gunner_2'][5].name)
                    if key=='3':
                        self.world.player.ai.player_vehicle_role_change('gunner_2')
                        self.deactivate_menu()
                        return

            if currentRole!='passenger_1' and 'passenger_1' in vehicle.ai.vehicle_crew:
                self.text_queue.append('4 - Passenger')
                if key=='4':
                    self.world.player.ai.player_vehicle_role_change('passenger_1')
                    self.deactivate_menu()
                    return

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
            self.text_queue.append('Collision Log:')
            for b in self.world.player.ai.collision_log:
                self.text_queue.append(b)



            self.text_queue.append('1 - respawn as a random bot on your team')
            if key=='1':
                if self.world.spawn_player():
                    self.world.is_paused=False
                    self.deactivate_menu()
                    return
                else:
                    self.text_queue.append('! No more humans left on your team')
            


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
            self.text_queue.append('4 - send test radio messages')
            self.text_queue.append('5 - start self debug')
            self.text_queue.append('6 - toggle_hit_markers')
            self.text_queue.append('7 - kill all humans except for the player')
            self.text_queue.append('8 - print squad info')

            if key=='1':
                self.world.toggle_map()
                return
            elif key=='2':
                self.world.debug_mode=not self.world.debug_mode
                return
            elif key=='3':
                self.menu_state='spawn'
                key=None
            elif key=='4':
                for ai in self.world.tactical_ai.values():
                    ai.send_radio_comms_check()
                engine.log.add_data('info','comms check sent on all tactical_ai channels',True)

            elif key=='5':
                self.world.run_self_debug()
            elif key=='6':
                self.world.toggle_hit_markers()
                return
            elif key=='7':
                self.world.kill_all_nonplayer_humans()
                return
            elif key=='8':
                for tactical in self.world.tactical_ai.values():
                    print(f'============{tactical.faction}============')
                    for squad in tactical.squads:
                        print(f'----Squad: {squad.name}----')
                        print(f'radio contact: {squad.radio_contact}')
                        print(f'radio recieve queue length: {len(squad.radio_receive_queue)}')
                        print(f'radio send queue length: {len(squad.radio_send_queue)}')
                        print(f'members: {len(squad.members)}')
                        
                        print('---------------------')
        if self.menu_state=='spawn':
            self.text_queue=[]
            self.text_queue.append('--Debug -> Spawn Menu --')
            self.text_queue.append('1 - Vehicles ')
            self.text_queue.append('2 - Weapons ')
            self.text_queue.append('3 - Squads (disabled) ')
            self.text_queue.append('4 - Misc')
 
            if key=='1':
                self.menu_state='spawn_vehicles'
                key=None
            elif key=='2':
                self.menu_state='spawn_weapons'
                key=None
            elif key=='3':
                #self.menu_state='spawn_squads'
                #key=None
                pass   
            elif key=='4':
                self.menu_state='spawn_misc'
                key=None
        if self.menu_state=='spawn_vehicles':
            self.text_queue=[]
            self.text_queue.append('--Debug -> Spawn Menu -> Vehicles --')
            self.text_queue.append('1 - Kubelwagen ')
            self.text_queue.append('2 - german_sd_kfz_251-22')
            self.text_queue.append('3 - german_panzer_iv_ausf_h')
            self.text_queue.append('4 - german_panzer_iv_ausf_j')
            self.text_queue.append('5 - rso pak')
            self.text_queue.append('6 - T20 armored tractor')
            self.text_queue.append('7 - RSO')
            self.text_queue.append('8 - t34-76 model 1943')
            self.text_queue.append('9 - german_fa_223_drache')
            if key=='1':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'german_kubelwagen',True)
            elif key=='2':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'german_sd_kfz_251/22',True)
            elif key=='3':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'german_panzer_iv_ausf_h',True)
            elif key=='4':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'german_panzer_iv_ausf_j',True)
            elif key=='5':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'german_rso_pak',True)
            elif key=='6':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'soviet_t20',True)
            elif key=='7':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'german_rso',True)
            elif key=='8':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'soviet_t34_76_model_1943',True)
            elif key=='9':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'german_fa_223_drache',True)
        if self.menu_state=='spawn_weapons':
            self.text_queue=[]
            self.text_queue.append('--Debug -> Spawn Menu -> Weapons --')
            self.text_queue.append('1 - MG34 ')
            self.text_queue.append('2 - Panzerschreck')
            self.text_queue.append('3 - Model 24 Stick Grenade ')
            self.text_queue.append('4 - molotov')
            self.text_queue.append('5 - MG42')
            self.text_queue.append('6 - ptrs-41')
            self.text_queue.append('7 - rpg43')
            if key=='1':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'mg34',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'mg34_belt',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'mg34_belt',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'mg34_belt',True)
            elif key=='2':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'panzerschreck',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'panzerschreck_magazine',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'panzerschreck_magazine',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'panzerschreck_magazine',True)
            elif key=='3':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'model24',True)
            elif key=='4':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'molotov_cocktail',True)
            elif key=='5':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'mg42',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'mg34_belt',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'mg34_belt',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'mg34_belt',True)
            elif key=='6':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'ptrs_41',True)
            elif key=='7':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+50,self.world.player.world_coords[1]],'rpg43',True)
            

                
        if self.menu_state=='spawn_squads':
            self.text_queue=[]
            self.text_queue.append('--Debug -> Spawn Menu -> Squads --')
            self.text_queue.append('1 - German 1944 Rifle  ')
            self.text_queue.append('2 - German 1944 VG Storm Group ')
            self.text_queue.append('3 - Soviet 1944 Rifle')
            self.text_queue.append('4 - Soviet 1944 Submachine Gun')
            if key=='1':
                print('this needs a rewrite')
            elif key=='2':
                print('this needs a rewrite')
            elif key=='3':
                print('this needs a rewrite')
            elif key=='4':
                print('this needs a rewrite')
        if self.menu_state=='spawn_misc':
            self.text_queue=[]
            self.text_queue.append('--Debug -> Spawn Menu -> Misc --')
            self.text_queue.append('1 - dani')
            self.text_queue.append('2 - Feldfunk radio and charger ')
            self.text_queue.append('3 - Maybach HL42')
            self.text_queue.append('4 - Pickle Jar')
            self.text_queue.append('5 - wine ')
            self.text_queue.append('6 - hangar')
            self.text_queue.append('7 - concrete runway')
            self.text_queue.append('8 - german_fuel_can')
            self.text_queue.append('9 - grid 50 foot')

            if key=='1':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+40,self.world.player.world_coords[1]],'dani',True)

            elif key=='2':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+40,self.world.player.world_coords[1]],'radio_feldfu_b',True)
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+60,self.world.player.world_coords[1]],'feldfunk_battery_charger',True)
            elif key=='3':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+40,self.world.player.world_coords[1]],'maybach_hl42_engine',True)
            elif key=='4':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+40,self.world.player.world_coords[1]],'pickle_jar',True)
            elif key=='5':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+40,self.world.player.world_coords[1]],'wine',True)
            elif key=='6':
                engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+40,self.world.player.world_coords[1]],'hangar',True)
            elif key=='7':
                #engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+40,self.world.player.world_coords[1]],'concrete_square',True)
                count=30
                #coords=engine.math_2d.get_grid_coords(self.world.player.world_coords,50,count)
                #rotation=random.randint(0,360)
                rotation=270
                coords=engine.math_2d.get_column_coords(self.world.player.world_coords,80,count,rotation,2)
                for _ in range(count):
                    temp=engine.world_builder.spawn_object(self.world,coords.pop(),'concrete_square',True)
                    temp.rotation_angle=random.choice([0,90,180,270])
                    #temp.rotation_angle=rotation
            elif key=='8':
                temp=engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0]+40,self.world.player.world_coords[1]],'german_fuel_can',True)
                temp.rotation_angle=0
            elif key=='9':
                temp=engine.world_builder.spawn_object(self.world, [self.world.player.world_coords[0],self.world.player.world_coords[1]],'grid_50_foot',True)
                temp.rotation_angle=0



    #---------------------------------------------------------------------------            
    def eat_drink_menu(self, key):

        # print out the basic menu
        self.text_queue=[]
        self.text_queue.append('-- Eat/Drink Menu --')
        self.text_queue.append('Blood Pressure: '+str(round(self.selected_object.ai.blood_pressure,1)))
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
        if 'task_vehicle_crew' in self.world.player.ai.memory:
            vehicle=self.world.player.ai.memory['task_vehicle_crew']['vehicle']

            # print out the basic menu
            self.text_queue=[]
            self.text_queue.append('-- Engine Menu --')
            self.text_queue.append('Transmission: '+vehicle.ai.current_gear)
            self.text_queue.append('Engine Status')
            
            for b in vehicle.ai.engines:
                self.text_queue.append(f"{b.name} {'[on]' if b.ai.engine_on else '[off]'}")

            for b in vehicle.ai.batteries:
                self.text_queue.append(f"{b.name} charge {round(b.ai.state_of_charge)}/{b.ai.max_capacity}")

            self.text_queue.append('1 - Start Engines')
            self.text_queue.append('2 - Stop Engines')
            self.text_queue.append('3 - Change Gears')

            if key=='1':
                vehicle.ai.handle_start_engines()
                self.engine_menu(None)
            if key=='2':
                vehicle.ai.handle_stop_engines()
                self.engine_menu(None)
            if key=='3':
                if vehicle.ai.current_speed<5:
                    if vehicle.ai.current_gear=='drive':
                        vehicle.ai.current_gear='neutral'
                        self.engine_menu('')
                        return
                    elif vehicle.ai.current_gear=='neutral':
                        vehicle.ai.current_gear='reverse'
                        self.engine_menu('')
                        return
                    elif vehicle.ai.current_gear=='reverse':
                        vehicle.ai.current_gear='drive'
                        self.engine_menu('')
                        return
                else:
                    engine.log.add_data('warn','going too fast for gear change',True)
        else:
            self.deactivate_menu()

    #---------------------------------------------------------------------------
    def exit_world_menu(self,key):
        '''handle exiting the world -> strategic map'''
        # print out the basic menu
        self.text_queue=[]
        self.text_queue.append('-- Exit World Menu --')
        self.text_queue.append('Current coordinates '+str(engine.math_2d.get_round_vector_2(self.world.player.world_coords)))

        if self.world.map_square_name==None:
            # this means we are playing quick battle.
            # just quit the game
            engine.log.export_all()
            exit()
        else:
            self.text_queue.append('Current Map: '+self.world.map_square_name)

            self.text_queue.append('1 - Exit World')
            if key=='1':
                engine.log.export_all()
                self.world.exit_world=True
                self.deactivate_menu()

            # check which exit zone the player is in (if any)

    #---------------------------------------------------------------------------            
    def first_aid_menu(self, key):

        # print out the basic menu
        self.text_queue=[]
        self.text_queue.append('-- First Aid Menu --')
        self.text_queue.append('Blood Pressure: '+str(round(self.selected_object.ai.blood_pressure,1)))
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
            self.text_queue=[]
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
    def hit_marker_menu(self, key):

        # print out the basic menu
        self.text_queue=[]
        self.text_queue.append('-- hit marker --')
        self.text_queue.append('object: ' +self.selected_object.ai.hit_data.hit_object_name)
        self.text_queue.append('projectile: ' +self.selected_object.ai.hit_data.projectile_name)
        self.text_queue.append('penetration: ' +str(self.selected_object.ai.hit_data.penetrated))
        self.text_queue.append('hit side: ' +self.selected_object.ai.hit_data.hit_side)
        self.text_queue.append('hit compartment: ' +self.selected_object.ai.hit_data.hit_compartment)
        self.text_queue.append('distance: ' +str(self.selected_object.ai.hit_data.distance))




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
            if self.selected_object.ai.is_medic:
                self.text_queue.append('Medic')
            if self.selected_object.ai.is_afv_trained:
                self.text_queue.append('AFV Trained')
            if self.selected_object.ai.is_expert_marksman:
                self.text_queue.append('Marksman')
            if self.selected_object.ai.squad.squad_leader==self.selected_object:
                self.text_queue.append('Squad Leader')

            self.text_queue.append('')
            self.text_queue.append('--- Stats ---')
            self.text_queue.append('Blood Pressure: '+str(round(self.selected_object.ai.blood_pressure,1)))
            self.text_queue.append('Hunger: '+str(round(self.selected_object.ai.hunger,1)))
            self.text_queue.append('Thirst: '+str(round(self.selected_object.ai.thirst,1)))
            self.text_queue.append('Fatigue ' + str(round(self.selected_object.ai.fatigue,1)))
            self.text_queue.append('Confirmed Kills: '+str(self.selected_object.ai.confirmed_kills))
            self.text_queue.append('Probable Kills: '+str(self.selected_object.ai.probable_kills))
            
            
            self.text_queue.append('')
            self.text_queue.append('--- Equipment Info ---')
            if self.selected_object.ai.primary_weapon != None:
                ammo_gun,ammo_inventory,magazine_count=self.selected_object.ai.check_ammo(self.selected_object.ai.primary_weapon,self.selected_object)
                self.text_queue.append('[primary weapon]: '+self.selected_object.ai.primary_weapon.name)
                self.text_queue.append('- ammo in gun: '+str(ammo_gun))
                self.text_queue.append('- ammo in inventory: '+str(ammo_inventory))
                self.text_queue.append('- magazine count: '+str(magazine_count))
                self.text_queue.append('- rounds Fired: '+str(self.selected_object.ai.primary_weapon.ai.rounds_fired))
            if self.selected_object.ai.throwable!=None:
                self.text_queue.append('[throwing weapon]: '+self.selected_object.ai.throwable.name)
            if self.selected_object.ai.antitank!=None:
                self.text_queue.append('[anti-tank weapon]: '+self.selected_object.ai.antitank.name)

            self.text_queue.append('')
            self.text_queue.append('--- Wallet ---')
            for currency_name,currency_amount in self.selected_object.ai.wallet.items():
                self.text_queue.append(currency_name+': '+str(currency_amount))
                
            self.text_queue.append('')
            
            self.text_queue.append('Squad Size: '+str(len(self.selected_object.ai.squad.members)))

        if self.world.debug_mode==True:
            self.text_queue.append('')
            self.text_queue.append('--- Debug Info ---')
            self.text_queue.append('rotation angle: '+str(self.selected_object.rotation_angle))
            d=engine.math_2d.get_distance(self.world.player.world_coords,self.selected_object.world_coords)
            d2='no squad lead'
            if self.selected_object.ai.squad.squad_leader!=None:
                d2=engine.math_2d.get_distance(self.selected_object.world_coords,self.selected_object.ai.squad.squad_leader.world_coords)
            self.text_queue.append('current task: '+self.selected_object.ai.memory['current_task'])
            if self.selected_object.ai.memory['current_task']=='task_vehicle_crew':
                self.text_queue.append('Vehicle Role: '+self.selected_object.ai.memory['task_vehicle_crew']['role'])
            self.text_queue.append('Distance from player: '+str(d))
            self.text_queue.append('Distance from squad: '+str(d2))
            self.text_queue.append('AI in building: '+str(self.selected_object.ai.in_building))

        if self.menu_state == 'player_menu':
            self.text_queue.append('')
            self.text_queue.append('--- Actions ---')
            self.text_queue.append('1 - Manage Inventory')
            self.text_queue.append('2 - Squad Menu')
            self.text_queue.append('3 - Eat/Drink')
            self.text_queue.append('4 - First Aid')
            self.text_queue.append('5 - Exit World')
            if self.selected_object.ai.large_pickup!=None:
                self.text_queue.append('6 - Drop '+self.selected_object.ai.large_pickup.name)
                if key=='6':
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
            if key=='5':
                self.change_menu('exit_world')
            
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
                vehicle=self.world.player.ai.memory['task_vehicle_crew']['vehicle']
                self.selected_object.ai.handle_event('speak',['task_enter_vehicle',vehicle])
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
        if self.selected_object.ai.battery!=None:
            self.text_queue.append('Battery State of Charge: '+str(round(self.selected_object.ai.battery.ai.state_of_charge,2))
                +'/'+str(self.selected_object.ai.battery.ai.max_capacity))
        

        if self.world.check_object_exists(self.selected_object):
            self.text_queue.append('1 - pick up')
            if key=='1':
                self.world.player.ai.pickup_object(self.selected_object)
                self.deactivate_menu()
                # we don't want to process anyhting after this so nothing else prints
                return

        self.text_queue.append('2 - Toggle power')
        if key=='2':
            if self.selected_object.ai.power_on:
                self.selected_object.ai.turn_power_off()
            else:
                self.selected_object.ai.turn_power_on()

            self.radio_menu(None)
            return

        self.text_queue.append('3 - Frequency Up')
        if key=='3':
            self.selected_object.ai.turn_frequency_up()
            self.radio_menu(None)
            return

        self.text_queue.append('4 - Frequency Down')
        if key=='4':
            self.selected_object.ai.turn_frequency_down()
            self.radio_menu(None)
            return

        self.text_queue.append('5 - Volume Up')
        if key=='5':
            if self.selected_object.ai.volume<self.selected_object.ai.volume_range[1]:
                self.selected_object.ai.volume+=1
                self.radio_menu(None)
                return
        
        self.text_queue.append('6 - Volume Down')
        if key=='6':
            if self.selected_object.ai.volume>self.selected_object.ai.volume_range[0]:
                self.selected_object.ai.volume-=1
                self.radio_menu(None)
                return
            

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

        # base storage menu
        if self.menu_state=='none':
            # print out the basic menu
            self.text_queue=[]
            self.text_queue.append('-- Storage Menu: ' + self.selected_object.name + ' --')

            # determine if we can pickup the storage object itself
            if self.selected_object.is_human==False and self.selected_object.volume<21 and self.selected_object.weight<50:
                self.text_queue.append('z - pickup '+self.selected_object.name)
                if key=='z':
                    self.world.player.ai.pickup_object(self.selected_object)
                    self.deactivate_menu()
                    # exit function
                    return
            if self.selected_object.is_player==False:
                self.text_queue.append('x - add items')
            
            items=self.selected_object.ai.inventory

            files_per_page = 9
            total_pages = (len(items) + files_per_page - 1) // files_per_page

            start_index = self.current_page * files_per_page
            end_index = min(start_index + files_per_page, len(items))

            for index, wo in enumerate(items[start_index:end_index]):
                self.text_queue.append(f"{index + 1} - {wo.name}")

            if len(items) > files_per_page:
                if self.current_page < total_pages - 1:
                    self.text_queue.append("[+] - Next page")
                if self.current_page > 0:
                    self.text_queue.append("[-] - Previous page")


            # Handle the key selection for more than 10 save files
            if key is not None:
                if key.isdigit():
                    key_index = int(key) - 1
                    if 0 <= key_index < len(items[start_index:end_index]):
                        self.storage_menu_selection = items[start_index + key_index]
                        self.menu_state='selected_object'
                        key=None
                elif key == '+' and self.current_page < total_pages - 1:
                    self.current_page += 1
                    self.storage_menu('')
                elif key == '-' and self.current_page > 0:
                    self.current_page -= 1
                    self.storage_menu('')
                elif key== 'x':
                    self.menu_state='add_object'
                    key=None
                    self.current_page=0

        # interact with a selected object
        if self.menu_state=='selected_object':
            self.text_queue=[]
            self.text_queue.append('-- Storage Menu: ' + self.selected_object.name + ' --')
            self.text_queue.append(self.storage_menu_selection.name)
            self.text_queue.append('z - back')
            self.text_queue.append('1 - drop on ground')
            if key=='1':
                self.selected_object.remove_inventory(self.storage_menu_selection)
                self.storage_menu_selection.world_coords=copy.copy(self.selected_object.world_coords)
                engine.math_2d.randomize_position_and_rotation(self.storage_menu_selection)
                self.world.add_queue.append(self.storage_menu_selection)
                self.storage_menu_selection=None
                self.current_page=0
                self.menu_state='none'
                self.storage_menu(None)
                return
            if self.selected_object.is_player==False:
                self.text_queue.append('2 - add to your inventory')
                if key=='2':
                    self.selected_object.remove_inventory(self.storage_menu_selection)
                    self.world.player.add_inventory(self.storage_menu_selection)
                    self.current_page=0
                    self.storage_menu_selection=None
                    self.menu_state='none'
                    self.storage_menu(None)
                    return
            if key=='z':
                self.current_page=0
                self.storage_menu_selection=None
                self.menu_state='none'
                self.storage_menu(None)
                return

        # add a object from the players inventory
        if self.menu_state=='add_object':
            self.text_queue=[]
            self.text_queue.append('-- Select a object to add to : ' + self.selected_object.name + ' --')
            self.text_queue.append('z - back')
            items=self.world.player.ai.inventory

            # optionally put your large human pickup in there
            if self.selected_object.is_player==False:
                if self.world.player.ai.large_pickup!=None:
                    self.text_queue.append('x - add '+self.world.player.ai.large_pickup.name)
                    if key=='x':
                        temp=self.world.player.ai.large_pickup
                        self.world.player.ai.large_pickup=None
                        self.world.remove_queue.append(temp)
                        self.selected_object.add_inventory(temp)
                        self.menu_state='none'
                        key=None
                        self.current_page=0
                        self.storage_menu(None)
                        return

            files_per_page = 9
            total_pages = (len(items) + files_per_page - 1) // files_per_page

            start_index = self.current_page * files_per_page
            end_index = min(start_index + files_per_page, len(items))

            for index, wo in enumerate(items[start_index:end_index]):
                self.text_queue.append(f"{index + 1} - {wo.name}")

            if len(items) > files_per_page:
                if self.current_page < total_pages - 1:
                    self.text_queue.append("[+] - Next page")
                if self.current_page > 0:
                    self.text_queue.append("[-] - Previous page")


            # Handle the key selection for more than 10 save files
            if key is not None:
                if key.isdigit():
                    key_index = int(key) - 1
                    if 0 <= key_index < len(items[start_index:end_index]):
                        temp=items[start_index + key_index]
                        self.world.player.remove_inventory(temp)
                        self.selected_object.add_inventory(temp)
                        self.menu_state='none'
                        key=None
                        self.current_page=0
                        self.storage_menu(None)
                        return
                elif key == '+' and self.current_page < total_pages - 1:
                    self.current_page += 1
                    self.storage_menu('')
                elif key == '-' and self.current_page > 0:
                    self.current_page -= 1
                    self.storage_menu('')
                elif key == 'z':
                    self.menu_state='none'
                    key=None
                    self.current_page=0
                    self.storage_menu(None)
                    return


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

            if self.selected_object.ai.check_if_human_in_vehicle(self.world.player):
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
            if self.selected_object.ai.vehicle_disabled:
                self.text_queue.append('Vehicle Disabled')



            if distance<self.max_menu_distance:
                self.text_queue.append('')
                self.text_queue.append('-- Actions --')
                self.text_queue.append('1 - info (not implemented) ')
                self.text_queue.append('2 - enter vehicle ')
                self.text_queue.append('3 - storage ')
                if fuel_option:
                    self.text_queue.append('4 - fuel ')
                if distance<300 and self.world.player.ai.memory['current_task']=='task_vehicle_crew':
                    vehicle=self.world.player.ai.memory['task_vehicle_crew']['vehicle']
                    self.text_queue.append('5 - Tow Vehicle')
                    if key=='5':
                        self.world.text_queue.append('[You attach the vehicle for towing]')
                        vehicle.ai.attach_tow_object(self.selected_object)
                        self.deactivate_menu()
                        return
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
            if 'task_vehicle_crew' in self.world.player.ai.memory:
                currentRole=self.world.player.ai.memory['task_vehicle_crew']['role']
                if currentRole==None:
                    currentRole='none'

                radio=False
                if self.selected_object.ai.radio!=None:
                    radio=True
                self.text_queue=[]
                self.text_queue.append('--Internal Vehicle Menu --')
                self.text_queue.append(f'Your BP: {self.world.player.ai.blood_pressure}')
                self.text_queue.append(f'Current Vehicle Role: {currentRole}')
                self.text_queue.append(f'Vehicle: {self.selected_object.name}')
                self.text_queue.append('Disabled : '+str(self.selected_object.ai.vehicle_disabled))
                
                if radio:
                    self.text_queue.append('Radio : '+self.selected_object.ai.radio.name)

                # - engine data - 
                self.text_queue.append('-')
                for b in self.selected_object.ai.engines:
                    self.text_queue.append(f'Engine: {b.name}')
                    self.text_queue.append(f' - Engine On: {b.ai.engine_on}')
                    self.text_queue.append(f' - Engine Damaged: {b.ai.damaged}')

                # - fuel tanks -
                self.text_queue.append('-')
                for b in self.selected_object.ai.fuel_tanks:
                    fuel=0
                    if len(b.ai.inventory)>0:
                        if 'gas' in b.ai.inventory[0].name:
                            fuel=b.ai.inventory[0].volume
                    fuel_text=str(b.volume) + '|' + str(round(fuel,2))
                    self.text_queue.append('Fuel Tank: ' + b.name + ' ' + fuel_text)
                
                # - turret data - 
                for b in self.selected_object.ai.turrets:
                    self.text_queue.append('-')
                    self.text_queue.append(f'Turret: {b.name}')
                    if b.ai.turret_jammed:
                        self.text_queue.append(' - Turret ring is jammed')
                    
                    if b.ai.primary_weapon!=None:
                        self.text_queue.append(f' - {b.ai.primary_weapon.name}')
                        if b.ai.primary_weapon.ai.action_jammed:
                            self.text_queue.append(' -- action is jammed')
                        if b.ai.primary_weapon.ai.damaged:
                            self.text_queue.append(' -- weapon is damaged')
                        ammo_gun,ammo_inventory,magazine_count=self.world.player.ai.check_ammo(b.ai.primary_weapon,self.selected_object)
                        self.text_queue.append(f' -- ammo {ammo_gun}/{ammo_inventory}')

                    if b.ai.coaxial_weapon!=None:
                        self.text_queue.append(f' - {b.ai.coaxial_weapon.name}')
                        if b.ai.coaxial_weapon.ai.action_jammed:
                            self.text_queue.append(' -- action is jammed')
                        if b.ai.coaxial_weapon.ai.damaged:
                            self.text_queue.append(' -- weapon is damaged')
                        ammo_gun,ammo_inventory,magazine_count=self.world.player.ai.check_ammo(b.ai.coaxial_weapon,self.selected_object)
                        self.text_queue.append(f' -- ammo {ammo_gun}/{ammo_inventory}')

                # - wheel data -
                self.text_queue.append('-')
                for b in self.selected_object.ai.wheels:
                    wheel_text=b.name
                    if b.ai.damaged:
                        wheel_text+=' damaged'
                    if b.ai.destroyed:
                        wheel_text+=' destroyed'
                    self.text_queue.append(wheel_text)

                self.text_queue.append(' ----')

                self.text_queue.append('- crew -')
                for k,value in self.selected_object.ai.vehicle_crew.items():
                    text=k+': '
                    if value[0]==True:
                        text+=value[1].name
                        text+=': '+value[1].ai.memory['task_vehicle_crew']['current_action']
                    else:
                        text+='unoccupied'
                    self.text_queue.append(text)
                self.text_queue.append('----')

                self.text_queue.append('')
                self.text_queue.append('-- Actions --')
                self.text_queue.append('1 - change role')
                self.text_queue.append('2 - exit vehicle ')
                self.text_queue.append('3 - engine menu')
                self.text_queue.append('4 - toggle HUD')
                if radio:
                    self.text_queue.append('5 - radio')

                if self.selected_object.ai.towed_object!=None:
                    self.text_queue.append('6 - Stop Towing')
                    if key=='6':
                        self.world.text_queue.append('[You detach the vehicle from the tow bar]')
                        self.selected_object.ai.detach_tow_object()
                        self.deactivate_menu()
                        return

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
            else:
                # task_vehicle_crew not in memory, so internal is a mistake. player probably died and was removed from the vehicle
                self.deactivate_menu()

        # -- add debug info --
        if self.world.debug_mode==True:
            if self.selected_object!=None:
                self.text_queue.append('')
                self.text_queue.append('--debug info --')
                self.text_queue.append('distance from player: '+str(distance))
                if self.selected_object.ai.vehicle_crew['driver'][0]==True:
                    squad_dist=engine.math_2d.get_distance(self.selected_object.world_coords,self.selected_object.ai.vehicle_crew['driver'][1].ai.squad.destination)
                    self.text_queue.append('distance from driver squad destination: '+str(squad_dist))
                self.text_queue.append('rotation angle: '+str(self.selected_object.rotation_angle))
                #self.text_queue.append('fuel type: '+self.selected_object.ai.fuel_type)
                #self.text_queue.append('fuel amount: '+str(self.selected_object.ai.fuel))
                self.text_queue.append('throttle: '+str(self.selected_object.ai.throttle))
                self.text_queue.append('brake power: '+str(self.selected_object.ai.brake_power))
                self.text_queue.append('wheel steering: '+str(self.selected_object.ai.wheel_steering))
                self.text_queue.append('vehicle speed: '+str(self.selected_object.ai.current_speed))
                self.text_queue.append('acceleration: '+str(self.selected_object.ai.acceleration))

                self.text_queue.append('- crew debug -')
                for k,value in self.selected_object.ai.vehicle_crew.items():
                    text=k+': '
                    if value[0]==True:
                        text+=value[1].name
                        text+=': '+value[1].ai.memory['task_vehicle_crew']['current_action']
                    else:
                        text+='unoccupied'
                    self.text_queue.append(text)
                self.text_queue.append('----')

                self.text_queue.append('- weapons debug -')
                for b in self.selected_object.ai.turrets:
                    primary_weapon='None'
                    coaxial_weapon='None'
                    if b.ai.primary_weapon!=None:
                        self.text_queue.append('- '+b.name)
                        ammo_gun,ammo_inventory,magazine_count=self.world.player.ai.check_ammo(b.ai.primary_weapon,self.selected_object)
                        self.text_queue.append('-- '+b.ai.primary_weapon.name+': '+str(ammo_gun)+'/'+str(ammo_inventory))
                        if b.ai.coaxial_weapon!=None:
                            ammo_gun,ammo_inventory,magazine_count=self.world.player.ai.check_ammo(b.ai.coaxial_weapon,self.selected_object)
                            self.text_queue.append('-- '+b.ai.coaxial_weapon.name+': '+str(ammo_gun)+'/'+str(ammo_inventory))

                self.text_queue.append(' ----')

                # engine debug 
                if len(self.selected_object.ai.engines)>0:
                    self.text_queue.append('Engine : '+str(self.selected_object.ai.engines[0].ai.engine_on))



    #---------------------------------------------------------------------------
    def update(self):

        # should maybe check if a menu is active first. no need for this to be constantly running
        # make the menu auto close after a period of time
        self.time_since_input+=self.world.time_passed_seconds
        if self.time_since_input>self.max_menu_idle_time and self.active_menu!='start':
            self.deactivate_menu()

