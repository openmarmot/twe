
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
The world class should handle all of the world logic and world objects.
It should not have any specific graphic engine code (pygame, etc)
'''

#import built in modules
import random
import copy


#import custom packages

from engine.world_menu import World_Menu
import engine.math_2d
import engine.world_builder
import engine.log
from ai.ai_faction_tactical import AIFactionTactical
import engine.world_radio
from engine.world_grid_manager import WorldGridManager


#global variables


class World():
    '''world class. holds everything to do with simulating the living world'''
    #---------------------------------------------------------------------------
    def __init__(self):
        '''initialize world'''
        # name of the map square that world was loaded from. set by strategic_map.load_world()
        # this is None for a quick battle
        self.map_square_name=None

        # triggers a unload of the world and the transition to strategic_map
        self.exit_world=False

        # triggers a switch to the vehicle diagnostics mode
        self.vehicle_diagnostics=False
        # the specific vehicle for the diagnostics page
        self.vehicle_diagnostics_vehicle=None
        
        # spawn locations
        self.spawn_center=[0.,0.]
        self.spawn_north=[0.,-8000.]
        self.spawn_south=[0.,8000.]
        self.spawn_west=[-8000.,0.]
        self.spawn_east=[8000.,0.]
        self.spawn_far_east=[10000.,0.]

        # reset world_radio to defaults so there are no old radio objects from previous worlds
        engine.world_radio.reset_world_radio()

        # tactical AIs. This also adds radios !
        self.tactical_ai={}
        self.tactical_ai['german']=AIFactionTactical(self,'german',[],['soviet'],self.spawn_west,3)
        self.tactical_ai['soviet']=AIFactionTactical(self,'soviet',[],['german'],self.spawn_east,5)
        self.tactical_ai['american']=AIFactionTactical(self,'american',[],[],self.spawn_north,10)
        self.tactical_ai['civilian']=AIFactionTactical(self,'civilian',[],[],self.spawn_center,12)

        # off man reinforcements
        # array of  [time,faction,[spawn_point,squad]]
        self.reinforcements=[]

        # world objects that need to exit the map 
        self.exit_queue=[]

        # objects to be added to the world
        self.add_queue=[]

        # objects to be removed from the world
        self.remove_queue=[]

        #world areas
        self.world_areas=[]
        

        # size of the map in every direction from 0,0
        self.map_size=100000
        self.map_check_interval=5
        self.last_map_check=0
        self.exited_object_count=0

        
        self.world_menu=World_Menu(self)

        self.player=None

        # faction set for player. set when world is created
        self.player_spawn_faction=''

        # a way to pause the action
        self.is_paused=False

        # debug text and other stuff checks this condition
        self.debug_mode=False

        # display vehicle text. set by world menu
        self.display_vehicle_text=False
        self.vehicle_text_queue=[]

        # debug info queue
        self.debug_text_queue=[]

        # general text queue
        self.text_queue=[]
        # used for temporary text. call add_text to add 
        self.text_queue_clear_rate=4
        self.text_queue_display_size=5
        self.time_since_last_text_clear=0

        #bool
        self.map_enabled=False

        # automatic screenshots
        self.aar_mode_enabled=False

        # checked by ai_gun.fire() and world_builder.spawn_shrapnel_cloud
        # True== get hurt, False== don't get hurt
        self.friendly_fire=False # complete friendly fire
        self.friendly_fire_squad=False # only at the squad level
        self.friendly_fire_explosive=True # grenade shrap clouds
        self.friendly_fire_explosive_squad=True # only at the squad level
        self.friendly_fire_vehicle=False # False means friendly vehicles are added to the ignore list


        # physics stuff 

        # air density in kg/m^3. good default is 1.225
        self.air_density=1.225

        # seconds that the world has existed for 
        # can be used by other classes for time keeping
        self.world_seconds=0

        # seconds between the last update. updated by self.update()
        self.time_passed_seconds=0

        # -- some stat counters for the debug info screen --
        self.panzerfaust_launches=0
        # incremented when a medic heals someone
        self.medic_heals=0
        # incremented when a mechanic fixes a vehicle
        self.mechanic_fixes=0
        # count on how many times a helmet bounces a projectile
        self.helmet_bounces=0
        # count how many times a body armor bounces a projectile
        self.body_armor_bounces=0


        # whether hit markers exist or not
        self.hit_markers=True
        self.hit_markers_non_pen=False

        # checked by graphics_2d_pygame render
        self.display_weapon_range=False

        # 
        self.grid_manager=WorldGridManager()

    #---------------------------------------------------------------------------
    def activate_context_menu(self):
        '''called when player hits tab, activates a menu based on the context'''

        if self.world_menu.active_menu=='none':

            if self.player.ai.memory['current_task']=='task_vehicle_crew':
                vehicle=self.player.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
                self.world_menu.activate_menu(vehicle)
            else:
                self.world_menu.activate_menu(self.player)
        else:
            self.world_menu.deactivate_menu()

    #---------------------------------------------------------------------------
    def add_object(self, world_object):
        '''add object to the world'''
        # !! NOTE this should not be called by objects directly. use the add_queue instead

        # reset the image so that the graphics engine can make sure it matches the current view scale
        world_object.reset_image=True


        world_object.in_world=True

        # init the grid square
        self.grid_manager.update_wo_object_square(world_object)
        
        # set or reset spawn time in world_seconds
        world_object.spawn_time=self.world_seconds

    #---------------------------------------------------------------------------
    def check_collision_return_object(self,collider,ignore_list, objects,consider_prone=False):
        ''' collision check. returns colliding object or None'''
        # note - this no longer hands out collision events 

        # collider - worldobject doing the colliding
        # ignore_list - list of objects to ignore
        # objects - array of objects to check collision against

        
        # note - this function skips collision on disabled vehicles
        collided=engine.math_2d.checkCollisionCircleOneResult(collider,objects,ignore_list)
        if collided is not None:
            if collided.is_human:
                if collided.ai.memory['current_task']=='task_vehicle_crew':
                    collided=collided.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
                else:
                    # check if object misses due to prone
                    if consider_prone:
                        chance=random.randint(0,1)
                        if chance==1:
                            # missed due to prone
                            collided=None
            
        return collided
    
    #---------------------------------------------------------------------------
    def check_map_bounds(self):
        '''check if anything is out of bounds'''
        # this could be better

        check_objects=self.grid_manager.get_objects_from_all_grid_squares(True,True)
        for b in check_objects:
            if b.world_coords[0]>self.map_size or b.world_coords[0]<-self.map_size \
                or b.world_coords[1]>self.map_size or b.world_coords[1]<-self.map_size:
                self.exit_queue.append(b)


    #---------------------------------------------------------------------------
    def check_object_exists(self,wo_obj):
        '''returns a bool as to whether the object is in the world'''

        # note this has been neutered a bit. no longer checks if the object is really in world

        if wo_obj in self.remove_queue:
            engine.log.add_data('debug',f'check_object_exists on object: {wo_obj.name} in remove_queue',True)
            return False
        elif wo_obj in self.exit_queue:
            engine.log.add_data('debug',f'check_object_exists on object: {wo_obj.name} in exit_queue',True)
            return False
        else:
            return True

    #------------------------------------------------------------------------------
    def create_explosion(self,world_coords,explosion_radius,shrapnel_count,originator,weapon,fire_duration,smoke_duration):
        '''create a explosion that deals damage'''
        # originator - the ai_human that fired the weapon
        # weaponName - the weapon that created the explosion

        # damage objects within damage radius 
        possible=self.grid_manager.get_objects_from_grid_squares_near_world_coords(world_coords,explosion_radius,True,True)

        for b in possible:
            distance=engine.math_2d.get_distance(world_coords,b.world_coords)
            if distance<explosion_radius:
                # power reverse scales with distance
                power=100*(1-(distance/explosion_radius))
                if b.is_human:
                    b.ai.handle_event('explosion',power) 
                if b.is_vehicle:
                    engine.log.add_data('warn',f'world.create_explosion {b.name} hit by {weapon.name} unhandled',True)       

        # stun objects within stun radius 
                    
        # shrapnel
        if shrapnel_count>0:
            engine.world_builder.spawn_shrapnel_cloud(self,world_coords,shrapnel_count,originator,weapon)


        # spawn effects 
        engine.world_builder.spawn_object(self,world_coords,'dirt',True)
        engine.world_builder.spawn_explosion_and_fire(self,world_coords,fire_duration,smoke_duration)

    #------------------------------------------------------------------------------
    def create_fire(self,world_coords,flame_amount,flame_radius,fire_duration,smoke_duration):
        '''create a fire that does damage'''
        possible=self.grid_manager.get_objects_from_grid_squares_near_world_coords(world_coords,flame_radius,True,True)
        for flame in range(flame_amount):
            coords=engine.math_2d.randomize_coordinates(world_coords,random.randint(1,15))
            engine.world_builder.spawn_explosion_and_fire(self,coords,fire_duration,smoke_duration)
            hit_list=engine.math_2d.checkCollisionCircleCoordsAllResults(coords,flame_radius,possible,[])

            for hit in hit_list:
                if hit.is_vehicle:
                    hit.ai.handle_hit_with_flame()
                elif hit.is_human:
                    if hit.ai.memory['current_task']!= 'task_vehicle_crew':
                        hit.ai.handle_hit_with_flame()


    #---------------------------------------------------------------------------
    def generate_ignore_list(self,obj):
        ''' generates a ignore list for collision checking'''
        # obj - the world object that needs the ignore list
        # this is for objects that use ai_human
        ignore_list=[obj]

        if obj.is_turret:
            if obj.ai.vehicle is not None:
                # reset to (any) human that is crewing the vehicle
                for role in obj.ai.vehicle.ai.vehicle_crew:
                    if role.role_occupied:
                        obj=role.human
                        break
        
        # this should always be true at this point
        if obj.is_human:
            if self.friendly_fire is False:
                ignore_list+=obj.ai.squad.faction_tactical.allied_humans
                
            elif self.friendly_fire_squad is False:
                # just add the squad
                ignore_list+=obj.ai.squad.members

            if self.friendly_fire_vehicle is False:
                ignore_list+=obj.ai.squad.faction_tactical.allied_crewed_vehicles
                
            if obj.is_player:
                pass

            if obj.ai.memory['current_task']=='task_vehicle_crew':
                # add the vehicle otherwise it tends to get hit
                ignore_list.append(obj.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle)
                for b in obj.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle.ai.turrets:
                    ignore_list.append(b)

                # add the vehicle crew
                for b in obj.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle.ai.vehicle_crew:
                    if b.role_occupied:
                        ignore_list.append(b.human)

            if obj.ai.in_building:
                # add possible buildings the equipper is in.
                # assuming they are shooting out windows so should not hit the building
                ignore_list+=obj.ai.building_list
        else:
            engine.log.add_data('error','world.generate_ignore_list obj is not human'+obj.name,True)

        return ignore_list

    #---------------------------------------------------------------------------
    def get_closest_object(self, world_coords,object_list,max_distance):
        ''' can be used on its own or referenced like get_closest_gun() does'''
        best_distance=max_distance
        best_object=None
        for b in object_list:
            d=engine.math_2d.get_distance(world_coords,b.world_coords)
            if d<best_distance:
                best_distance=d 
                best_object=b

        return best_object
    
    #---------------------------------------------------------------------------
    def get_closest_vehicle(self, human,max_distance):
        '''gets the closest vehicle that has passenger space and is the right faction'''
        # human - the bot that wants to get in the vehicle
        # max_distance - maximum distance away that is ok
        best_distance=max_distance
        best_object=None

        possible_vehicles=self.grid_manager.get_objects_from_grid_squares_near_world_coords(human.world_coords,max_distance,False,True)

        for b in possible_vehicles:
            acceptable=True
            
            if b.ai.vehicle_disabled:
                continue
            
            # first check if its full
            if b.ai.check_if_vehicle_is_full():
                continue

            if b.is_airplane and human.ai.is_pilot is False:
                continue

            if b.ai.requires_afv_training and human.ai.is_afv_trained is False:
                continue

            # factions
            for role in b.ai.vehicle_crew:
                if role.role_occupied:
                    if role.human.ai.squad.faction!=human.ai.squad.faction:
                        acceptable=False

            if acceptable:
                d=engine.math_2d.get_distance(human.world_coords,b.world_coords)
                if d<best_distance:
                    best_distance=d 
                    best_object=b

        return best_object

    
    #---------------------------------------------------------------------------
    def get_objects_within_range(self,WORLD_COORDS,object_list,max_distance):
        '''check distance on objects from an array and returns the ones that are in range'''
        near_objects=[]
        for b in object_list:
            d=engine.math_2d.get_distance(WORLD_COORDS,b.world_coords)
            if d<max_distance:
                near_objects.append(b)
        return near_objects

    #---------------------------------------------------------------------------
    def handle_keydown(self,key,mouse_screen_coords=None):
        '''handle keydown events. called by graphics engine'''
        # these are for one off (not repeating) key presses

        #print('key ',key)
        self.world_menu.handle_input(key)

        if self.player.ai.memory['current_task']=='task_vehicle_crew':
            if self.player.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle.is_airplane:
                if key=='p':
                    self.player.ai.switch_task_exit_vehicle(self.player.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle)
                    self.player.ai.speak('bailing out!')
                    # note - physics needs to be udpdate to handle falling
        else:
            # controls for when you are walking about
            if key=='g':
                self.player.ai.throw([],mouse_screen_coords)
            elif key=='p':
                self.player.ai.prone_state_change()
            elif key=='t':
                self.player.ai.launch_antitank([],mouse_screen_coords)

        # controls for vehicles and walking 
        if key=='r':
            self.player.ai.handle_player_reload()

        if key=='tab':
            self.activate_context_menu()

        if key=='space':
            self.display_weapon_range=not self.display_weapon_range

        if key=='m':
            self.toggle_map()

    #---------------------------------------------------------------------------
    def handle_key_press(self,key,mouse_screen_coords=None):
        '''handle key press'''
        # these are for key presses that can be continuous

        # stop player from moving when dead
        if self.player.ai.blood_pressure>0:
            # key press is when a key is held down
            # key - string  example 'w'
            if self.player.ai.memory['current_task']=='task_vehicle_crew':
                role=self.player.ai.memory['task_vehicle_crew']['vehicle_role']
                vehicle=role.vehicle
                turret=role.turret

                if role.is_driver:

                    if vehicle.is_airplane:
                        # ---- controls for airplanes ------------
                        if key=='w':
                            vehicle.ai.handle_elevator_up()
                        elif key=='s':
                            vehicle.ai.handle_elevator_down()
                            if vehicle.altitude<1:
                                vehicle.ai.brake_power=1
                        elif key=='a':
                            vehicle.ai.handle_aileron_left()
                            vehicle.ai.handle_rudder_left()
                            if vehicle.altitude<1:
                                vehicle.ai.handle_steer_left()
                        elif key=='d':
                            vehicle.ai.handle_aileron_right()
                            vehicle.ai.handle_rudder_right()
                            if vehicle.altitude<1:
                                vehicle.ai.handle_steer_right()
                        elif key=='up':
                            pass
                        elif key=='down':
                            pass
                        elif key=='left':
                            vehicle.ai.handle_throttle_down()
                        elif key=='right':
                            vehicle.ai.handle_throttle_up()
                    else:
                        # ---- controls for ground vehicles ------------

                        if key=='w':
                            vehicle.ai.throttle=1
                            vehicle.ai.brake_power=0
                        elif key=='s':
                            vehicle.ai.brake_power=1
                            vehicle.ai.throttle=0
                        elif key=='a':
                            vehicle.ai.handle_steer_left()
                        elif key=='d':
                            vehicle.ai.handle_steer_right()

                elif role.is_gunner:
                    if key=='w':
                        self.player.ai.memory['task_vehicle_crew']['current_action']='rotate turret'
                        angle=engine.math_2d.get_rotation(turret.screen_coords,mouse_screen_coords)
                        self.player.ai.memory['task_vehicle_crew']['calculated_turret_angle']=angle
                    if key=='s':
                        if turret.ai.coaxial_weapon:
                            # no calculated range for player
                            turret.ai.coaxial_weapon.ai.calculated_range=turret.ai.coaxial_weapon.ai.range
                            turret.ai.handle_fire_coax()
                    if key=='a':
                        turret.ai.handle_rotate_left()
                    elif key=='d':
                        turret.ai.handle_rotate_right()
                    elif key=='f':
                        # no calculated range for player
                        turret.ai.primary_weapon.ai.calculated_range=turret.ai.primary_weapon.ai.range
                        turret.ai.handle_fire()
            else:
                # ---- controls for walking around ------------
                action=False
                speed=self.player.ai.get_calculated_speed()
                if key=='w':
                    self.player.world_coords[1]-=speed*self.time_passed_seconds
                    self.player.rotation_angle=0
                    self.player.reset_image=True
                    action=True
                elif key=='s':
                    self.player.world_coords[1]+=speed*self.time_passed_seconds
                    self.player.rotation_angle=180
                    self.player.reset_image=True
                    action=True
                elif key=='a':
                    self.player.world_coords[0]-=speed*self.time_passed_seconds
                    self.player.rotation_angle=90
                    self.player.reset_image=True
                    action=True
                elif key=='d':
                    self.player.world_coords[0]+=speed*self.time_passed_seconds
                    self.player.rotation_angle=270
                    self.player.reset_image=True
                    action=True
                elif key=='f':
                    # fire the gun
                    if self.player.ai.primary_weapon!=None:
                        self.player.ai.fire_player(self.player.ai.primary_weapon,mouse_screen_coords)
                    action=True

                if action:
                    self.player.ai.fatigue+=self.player.ai.fatigue_add_rate*self.time_passed_seconds
                    self.player.ai.recent_noise_or_move=True
                    self.player.ai.last_noise_or_move_time=self.world_seconds

    #---------------------------------------------------------------------------
    def kill_all_nonplayer_humans(self):
        for b in self.grid_manager.get_objects_from_all_grid_squares(True,False):
            if b.is_player is False:
                b.ai.blood_pressure=0
        engine.log.add_data('note','world.kill_all_nonplayer_humans executed',True)

    #---------------------------------------------------------------------------
    def process_add_remove_queue(self):
        if len(self.add_queue)>0:
            for b in self.add_queue:
                self.add_object(b)
            self.add_queue=[]

        if len(self.remove_queue)>0:
            for b in self.remove_queue:
                self.remove_object(b)
            self.remove_queue=[]

    #---------------------------------------------------------------------------
    def process_exit_queue(self):
        '''process objects that need to leave the map'''

        for b in self.exit_queue:
            message=b.name + ' has exited the world area'
            if b.is_human:
                message+=('\n  - faction: '+b.ai.squad.faction)

                # exit vehicle
            
            if b.is_vehicle:
                # process all the passengers
                pass


            print(message)

            print('!!!! Process Exit Queue Needs a Rewrite !!!!! ')

            # remove from the world
            self.remove_queue.append(b)

            self.exited_object_count+=1

        #clear the queue        
        self.exit_queue=[]

    #---------------------------------------------------------------------------
    def process_reinforcements(self):
        # array of  [time,faction,spawn_point,squad]
        process_queue=[]
        for b in self.reinforcements:
            if b[0]<self.world_seconds:
                process_queue.append(b)
        for b in process_queue:
            self.reinforcements.remove(b)
            engine.log.add_data('error','world.process_reinforcements is disabled ! ',True)

    #---------------------------------------------------------------------------
    def remove_hit_markers(self):
        # if this is slow we could create our own wo_ category for hit markers
        for b in self.grid_manager.get_all_objects():
            if b.is_hit_marker:
                self.remove_queue.append(b)

    #---------------------------------------------------------------------------
    def remove_object(self, world_object):
        ''' remove object from world. '''
        # !! note - objects should add themselves to the remove_queue instead of calling this directly

        world_object.in_world=False

        # remove from grid square
        self.grid_manager.remove_object_from_world_grid(world_object)
        
    #---------------------------------------------------------------------------
    def spawn_hit_markers(self):
        for b in self.grid_manager.get_all_objects():
            if b.is_vehicle or b.is_vehicle_wreck:
                for hit in b.ai.collision_log:
                    marker=engine.world_builder.spawn_object(self,b.world_coords,'hit_marker',True)
                    marker.ai.setup(b,hit)
    #---------------------------------------------------------------------------
    def spawn_player(self):
        '''spawns player'''
        # ! note - this should be done after squads are created
        candidates=[]
        for squad in self.tactical_ai[self.player_spawn_faction].squads:
            candidates+=squad.members

        if len(candidates)>0:
            self.player=random.choice(candidates)
            self.player.is_player=True
            if self.player.ai.memory['current_task']=='task_vehicle_crew':
                # not sure if we have to do anything if in a vehicle 
                pass
            else:
                self.player.ai.memory['current_task']='task_player_control'
            print('You are now '+self.player.name)
            return True
        else:
            engine.log.add_data('error','world.spawn_player but there are no humans left in the world of the correct faction: '+self.player_spawn_faction,True)
            return False

    #---------------------------------------------------------------------------
    def start(self):
        '''performs world tasks necessary for a new world to start'''
        # called by world_builder.load_world()

        # precompute world_area locations
        engine.log.add_data('note','Computing World Area locations..',True)
        for area in self.world_areas:
            area.compute_locations()
        
        # tactical_ai start. create squads, figure out initial coords, orders, etc 
        for ai in self.tactical_ai.values():
            ai.start()

        # spawn player
        self.spawn_player()

    #---------------------------------------------------------------------------
    def toggle_hit_markers(self):
        '''enable/disable hit markers'''
        if self.hit_markers:
            self.hit_markers=False
            self.remove_hit_markers()
            engine.log.add_data('note','Removed hit markers',True)
        else:
            self.hit_markers=True
            self.spawn_hit_markers()
            engine.log.add_data('note','Spawned hit markers',True)


    #---------------------------------------------------------------------------
    def toggle_map(self):
        ''' enable/disable map features '''

        if self.map_enabled:
            self.map_enabled=False
            for b in self.grid_manager.get_all_objects():
                if b.is_map_pointer:
                    self.remove_queue.append(b)
        else:
            self.map_enabled=True
            print('map enabled :','green= world area','blue= squad','green= squad destination')

            for b in self.world_areas:
                engine.world_builder.spawn_map_pointer(self,b.world_coords,'normal')


    #---------------------------------------------------------------------------
    def update(self,time_passed_seconds):
        self.time_passed_seconds=time_passed_seconds

        if self.is_paused is False:
            self.world_seconds+=self.time_passed_seconds
            self.process_reinforcements()

            # cycle the text queue
            self.time_since_last_text_clear+=self.time_passed_seconds
            if self.time_since_last_text_clear>self.text_queue_clear_rate:
                self.time_since_last_text_clear=0
                if len(self.text_queue)>0:
                    self.text_queue.pop(0)

            # update the world objects
            self.grid_manager.update_world_objects()

            # update world areas
            for b in self.world_areas:
                b.update()

            for ai in self.tactical_ai.values():
                ai.update()

            # update world menu -
            self.world_menu.update()

            if self.debug_mode:
                self.update_debug_info()

            if self.display_vehicle_text:
                self.update_vehicle_text()
            
            # check if anything is out of map bounds
            if self.world_seconds-self.last_map_check>self.map_check_interval:
                self.map_check_interval=random.randint(1,10)
                self.last_map_check=self.world_seconds
                self.check_map_bounds()

                # process anything that has exited
                self.process_exit_queue()

            # add/remove objects to/from the world
            self.process_add_remove_queue()

    #------------------------------------------------------------------------------
    def update_debug_info(self):
        self.debug_text_queue = []
        self.debug_text_queue.append(f"Grid Square Count: {len(self.grid_manager.index_map)}")
        self.debug_text_queue.append(f"World Objects: {len(self.grid_manager.get_all_objects())}")
        self.debug_text_queue.append(f"World Objects that Update: {len(self.grid_manager.get_all_wo_update())}")
        self.debug_text_queue.append(f"Exited objects count: {self.exited_object_count}")
        self.debug_text_queue.append(f"Panzerfaust launches: {self.panzerfaust_launches}")
        self.debug_text_queue.append(f"Helmet bounces: {self.helmet_bounces}")
        self.debug_text_queue.append(f"Body armor bounces: {self.body_armor_bounces}")
        self.debug_text_queue.append(f'Medic Heals: {self.medic_heals}')
        self.debug_text_queue.append(f'Mechanic Fixes: {self.mechanic_fixes}')
        self.debug_text_queue.append("----- Player Stats -----")
        self.debug_text_queue.append(f"Player Name: {self.player.name}")
        self.debug_text_queue.append(f"Player memory current task: {self.player.ai.memory['current_task']}")
        self.debug_text_queue.append(f"Player Scale Modifier: {self.player.scale_modifier}")
        self.debug_text_queue.append(f"Player World Coords: {engine.math_2d.get_round_vector_2(self.player.world_coords)}")
        self.debug_text_queue.append(f"Player Screen Coords: {self.player.screen_coords}")
        self.debug_text_queue.append(f"Player altitude: {self.player.altitude}")
        self.debug_text_queue.append(f"Player Fatigue: {round(self.player.ai.fatigue, 1)}")
        self.debug_text_queue.append(f"Player Speed: {self.player.ai.get_calculated_speed()}")
        self.debug_text_queue.append(f"Player building overlap count: {len(self.player.ai.building_list)}")
        self.debug_text_queue.append('----- Faction Stats ------')
        for b in self.tactical_ai.values():
            self.debug_text_queue.append(f"{b.faction} humans: {len(b.allied_humans)}")
            self.debug_text_queue.append(f"{b.faction} vehicles: {len(b.allied_crewed_vehicles)}")


        # world area data
        for b in self.world_areas:
            self.debug_text_queue.append('Area '+b.name+' '+str(b.world_coords)+' is controlled by : '+b.faction)

    #------------------------------------------------------------------------------
    def update_vehicle_text(self):
        '''this is the vehicle HUD text. basically debug text'''
        # at the moment this is turned on from the vehicle context menu 
        
        self.vehicle_text_queue=[]

        if self.player.ai.memory['current_task']=='task_vehicle_crew':
            vehicle_role=self.player.ai.memory['task_vehicle_crew']['vehicle_role']
            vehicle=vehicle_role.vehicle
            self.vehicle_text_queue.append('Vehicle: '+vehicle.name)

            if vehicle_role.is_driver:
                # gauges
                self.vehicle_text_queue.append(f'Engines on: {vehicle.ai.engines_on}')
                self.vehicle_text_queue.append(f'Electrical system on: {vehicle.ai.electrical_system_functioning}')
                current_fuel,max_fuel=vehicle.ai.read_fuel_gauge()
                self.vehicle_text_queue.append(f'Fuel Gauge: {current_fuel}/{max_fuel}')
                self.vehicle_text_queue.append(f'Speed: {round(vehicle.ai.current_speed, 1)}')

                #self.vehicle_text_queue.append(f'max speed: {round(vehicle.ai.max_speed, 1)} current speed: {round(vehicle.ai.current_speed, 1)}')
                #self.vehicle_text_queue.append(f'acceleration: {vehicle.ai.acceleration}')
                #self.vehicle_text_queue.append(f'throttle: {vehicle.ai.throttle}')
                #self.vehicle_text_queue.append(f'brake: {vehicle.ai.brake_power}')
                #self.vehicle_text_queue.append(f'wheel steering: {vehicle.ai.wheel_steering}')

                # airplane specific 
                if vehicle.is_airplane:
                    self.vehicle_text_queue.append(f'altitude: {round(vehicle.altitude, 1)}')
                    self.vehicle_text_queue.append(f'rate of climb: {round(vehicle.ai.rate_of_climb, 1)}')
                    self.vehicle_text_queue.append(f'ailerons: {round(vehicle.ai.ailerons, 1)}')
                    self.vehicle_text_queue.append(f'elevator: {round(vehicle.ai.elevator, 1)}')
                    self.vehicle_text_queue.append(f'rudder: {round(vehicle.ai.rudder, 1)}')
                    self.vehicle_text_queue.append(f'flaps: {round(vehicle.ai.flaps, 1)}')

            if vehicle_role.is_driver:
                for role in vehicle.ai.vehicle_crew:
                    if role.role_occupied:
                        if role.is_gunner:
                            self.vehicle_text_queue.append(f'Gunner {role.human.name}: {role.human.ai.memory['task_vehicle_crew']['current_action']}')


            if vehicle_role.is_gunner:
                turret=vehicle_role.turret
                self.vehicle_text_queue.append(f'Vehicle angle: {vehicle.rotation_angle}')
                self.vehicle_text_queue.append(f'Turret angle: {turret.rotation_angle}')

                if turret.ai.primary_weapon:
                    self.vehicle_text_queue.append('')
                    weapon=turret.ai.primary_weapon
                    self.vehicle_text_queue.append(f'Weapon: {weapon.name}')
                    if weapon.ai.action_jammed:
                        self.vehicle_text_queue.append(' - action jammed')
                    if weapon.ai.damaged:
                        self.vehicle_text_queue.append(' - damaged')
                    ammo_gun,ammo_inventory,magazine_count=self.player.ai.check_ammo(weapon,vehicle)
                    self.vehicle_text_queue.append(f' - ammo {ammo_gun}/{ammo_inventory}')

                if turret.ai.coaxial_weapon:
                    self.vehicle_text_queue.append('')
                    weapon=turret.ai.coaxial_weapon
                    self.vehicle_text_queue.append(f'Weapon: {weapon.name}')
                    if weapon.ai.action_jammed:
                        self.vehicle_text_queue.append(' - action jammed')
                    if weapon.ai.damaged:
                        self.vehicle_text_queue.append(' - damaged')
                    ammo_gun,ammo_inventory,magazine_count=self.player.ai.check_ammo(weapon,vehicle)
                    self.vehicle_text_queue.append(f' - ammo {ammo_gun}/{ammo_inventory}')
