
'''
module : engine.world.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
The world class should handle all of the world logic and world objects.
It should not have any specific graphic engine code (pygame, etc)
'''

#import built in modules
import random
import copy
#from unittest import result  # no idea why this was here. disabled 8/2023


#import custom packages
from engine.graphics_2d_pygame import Graphics_2D_Pygame
from engine.world_menu import World_Menu
import engine.math_2d
import engine.world_builder
from ai.ai_faction_tactical import AIFactionTactical


#global variables


class World(object):
    #---------------------------------------------------------------------------
    def __init__(self,SCREEN_SIZE):
        
        # tactical AIs
        self.german_ai=AIFactionTactical(self,'german')
        self.soviet_ai=AIFactionTactical(self,'soviet')
        self.american_ai=AIFactionTactical(self,'american')
        self.civilian_ai=AIFactionTactical(self,'civilian')

        # off man reinforcements
        # array of  [time,faction,[spawn_point,squad]]
        self.reinforcements=[]

        # world objects that need to exit the map 
        self.exit_queue=[]

        # objects to be added to the world
        self.add_queue=[]

        # objects to be removed from the world
        self.remove_queue=[]

        # object lists 
        self.wo_objects=[]
        # not sure this one is used
        self.wo_objects_collision=[]
        self.wo_objects_human=[]
        self.wo_objects_guns=[]
        self.wo_objects_gun_magazines=[]
        self.wo_objects_german=[]
        self.wo_objects_soviet=[]
        self.wo_objects_american=[]
        self.wo_objects_civilian=[]
        self.wo_objects_vehicle=[]
        self.wo_objects_grenade=[]
        self.wo_objects_consumable=[]
        self.wo_objects_building=[]
        self.wo_objects_map_pointer=[]
        self.wo_objects_handheld_antitank=[]
        self.wo_objects_melee=[]
        self.wo_objects_airplane=[]
        self.wo_objects_medical=[]
        self.wo_objects_ammo_container=[]
        self.wo_objects_container=[]
        self.wo_objects_furniture=[]
        self.wo_objects_cleanup=[]

        #world areas
        self.world_areas=[]

        # spawn locations
        self.spawn_center=[0.,0.]
        self.spawn_north=[0.,-4000.]
        self.spawn_south=[0.,4000.]
        self.spawn_west=[-4000.,0.]
        self.spawn_east=[4000.,0.]
        self.spawn_far_east=[10000.,0.]

        # size of the map in every direction from 0,0
        self.map_size=100000
        self.map_check_interval=5
        self.last_map_check=0
        self.exited_object_count=0

        self.graphic_engine=Graphics_2D_Pygame(SCREEN_SIZE,self)
        self.world_menu=World_Menu(self)

        self.player=None

        # a way to pause the action
        self.is_paused=False

        # debug text and other stuff checks this condition
        self.debug_mode=False

        # display vehicle text. set by world menu
        self.display_vehicle_text=False
        self.vehicle_text_queue=[]

        # debug info queue
        self.debug_text_queue=[]

        #bool
        self.map_enabled=False

        # checked by ai_gun.fire() and world_builder.spawn_shrapnel_cloud
        # True== get hurt, False== don't get hurt
        self.friendly_fire=False # complete friendly fire
        self.friendly_fire_squad=False # only at the squad level
        self.friendly_fire_explosive=True # grenade shrap clouds
        self.friendly_fire_explosive_squad=True # only at the squad level


        # physics stuff 

        # air density in kg/m^3. good default is 1.225
        self.air_density=1.225

        # seconds that the world has existed for 
        # can be used by other classes for time keeping
        self.world_seconds=0


        # number of objects over which the world starts to cleanup un-needed objects
        self.cleanup_threshold=4000

    #---------------------------------------------------------------------------
    def activate_context_menu(self):
        '''called when player hits tab, activates a menu based on the context'''

        if self.world_menu.active_menu=='none':

            in_vehicle=None
            vlist=self.wo_objects_vehicle+self.wo_objects_airplane
            for b in vlist:
                if self.player in b.ai.passengers:
                    in_vehicle=b
            
            if in_vehicle==None:
                self.world_menu.activate_menu(self.player)
            else:
                self.world_menu.activate_menu(in_vehicle)
        else:
            self.world_menu.deactivate_menu()


    #---------------------------------------------------------------------------
    def add_object(self, WORLD_OBJECT):
        '''add object to the world'''
        # !! NOTE this should not be called by objects directly. use the add_queue instead

        # reset the image so that the graphics engine can make sure it matches the current view scale
        WORLD_OBJECT.reset_image=True

        if WORLD_OBJECT not in self.wo_objects:
            
            # set or reset spawn time in world_seconds
            WORLD_OBJECT.spawn_time=self.world_seconds

            self.wo_objects.append(WORLD_OBJECT)
            if WORLD_OBJECT.collision:
                self.wo_objects_collision.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_human:
                self.wo_objects_human.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_gun:
                self.wo_objects_guns.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_german:
                self.wo_objects_german.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_soviet:
                self.wo_objects_soviet.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_american:
                self.wo_objects_american.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_vehicle:
                self.wo_objects_vehicle.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_grenade:
                self.wo_objects_grenade.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_consumable:
                self.wo_objects_consumable.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_building:
                self.wo_objects_building.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_map_pointer:
                self.wo_objects_map_pointer.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_handheld_antitank:
                self.wo_objects_handheld_antitank.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_airplane:
                self.wo_objects_airplane.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_civilian:
                self.wo_objects_civilian.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_melee:
                self.wo_objects_melee.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_medical:
                self.wo_objects_medical.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_container:
                self.wo_objects_container.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_ammo_container:
                self.wo_objects_ammo_container.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_furniture:
                self.wo_objects_furniture.append(WORLD_OBJECT)
            if WORLD_OBJECT.is_gun_magazine:
                self.wo_objects_gun_magazines.append(WORLD_OBJECT)
            if WORLD_OBJECT.can_be_deleted:
                self.wo_objects_cleanup.append(WORLD_OBJECT)
        else:
            print('Error!! '+ WORLD_OBJECT.name+' already in world.wo_objects. Add fails !!')
        
    #---------------------------------------------------------------------------
    def check_collision_return_object(self,collider,ignore_list, objects,consider_prone=False):
        ''' collision check. returns colliding object or None'''
        # note - this no longer hands out collision events 

        # collider - worldobject doing the colliding
        # ignore_list - list of objects to ignore
        # objects - array of objects to check collision against


        collided=engine.math_2d.checkCollisionCircleOneResult(collider,objects,ignore_list)
        if collided !=None:
            if collided.is_human:
                if collided.ai.in_vehicle:
                    collided=collided.ai.vehicle
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
        check_objects=self.wo_objects_human+self.wo_objects_vehicle
        for b in check_objects:
            if b.world_coords[0]>self.map_size or b.world_coords[0]<-self.map_size \
                or b.world_coords[1]>self.map_size or b.world_coords[1]<-self.map_size:
                self.exit_queue.append(b)


    #---------------------------------------------------------------------------
    def check_object_exists(self,object):
        '''returns a bool as to whether the object is in the world'''

        if object in self.wo_objects:
            if object in self.remove_queue:
                print('debug : check object on object in remove_queue')
                return False
            elif object in self.exit_queue:
                print('debug : check object on object in exit_queue')
                return False
            else:
                return True
        else:
            return False
            

    #------------------------------------------------------------------------------
    def cleanup(self):
        '''cleanup routine for when performance is hurting'''

        # find the oldest time (which is the lowest number, as spawn_time counts up from zero)
        oldest_time=10000
        for b in self.wo_objects_cleanup:
            if b.spawn_time<oldest_time:
                oldest_time=b.spawn_time
                #oldest_object=b
        
        # remove objects that are in the same approximate spawn time
        remove_list=[]
        for b in self.wo_objects_cleanup:
            if b.spawn_time>oldest_time-1 and b.spawn_time<oldest_time+1:
                remove_list.append(b)

        print('Cleanup function removing '+str(len(remove_list))+' objects')
        self.remove_queue+=remove_list
    #---------------------------------------------------------------------------
    def generate_ignore_list(self,OBJ):
        ''' generates a ignore list for collision checking'''
        # OBJ - the world object that needs the ignore list
        # this is for objects that use ai_human
        ignore_list=[OBJ]

        if OBJ.is_human:
            if self.friendly_fire==False:
                if OBJ.is_german:
                        ignore_list+=self.wo_objects_german
                elif OBJ.is_soviet:
                    ignore_list+=self.wo_objects_soviet
                elif OBJ.is_american:
                    ignore_list+=self.wo_objects_american
            elif self.friendly_fire_squad==False:
                # just add the squad
                ignore_list+=OBJ.ai.squad.members

            if OBJ.is_player:
                pass
            elif OBJ.is_soldier:
                pass
            if OBJ.ai.in_vehicle:
                # add the vehicle otherwise it tends to get hit
                ignore_list.append(OBJ.ai.vehicle)
                for b in OBJ.ai.vehicle.turrets:
                    ignore_list.append(b)

            if OBJ.ai.in_building:
                # add possible buildings the equipper is in.
                # assuming they are shooting out windows so should not hit the building
                ignore_list+=OBJ.ai.building_list
        elif OBJ.is_turret:
            ignore_list.append(OBJ.ai.vehicle)

        return ignore_list

    #---------------------------------------------------------------------------
    def get_closest_gun(self, WORLD_COORDS):
        ''' returns the closest gun. spawns one if there are none '''
        best_object=self.get_closest_object(WORLD_COORDS,self.wo_objects_guns,5000)
        if best_object==None:
            # spawn a new gun and return it

            # first lets get a random building
            b=self.get_random_object(self.wo_objects_building)

            # randomize the coords a bit 
            w=[b.world_coords[0]+float(random.randint(-20,20)),b.world_coords[1]+float(random.randint(-20,20))]

            # spawn a ppk
            engine.world_builder.spawn_object(self,w,'ppk',True)
            # hmm we don't have the object reference, so lets just run this method again
            # does this make sense? am i insane? HA HA HAHAHAHA
            return self.get_closest_gun(WORLD_COORDS)
        else : 
            return best_object

    #---------------------------------------------------------------------------
    def get_closest_object(self, WORLD_COORDS,OBJECT_LIST,MAX_DISTANCE):
        ''' can be used on its own or referenced like get_closest_gun() does'''
        best_distance=MAX_DISTANCE
        best_object=None
        for b in OBJECT_LIST:
            d=engine.math_2d.get_distance(WORLD_COORDS,b.world_coords)
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
        for b in self.wo_objects_vehicle:
            acceptable=True

            # don't return airplanes if not a pilot
            if b.is_airplane and human.ai.is_pilot==False:
                acceptable=False

            if b.ai.driver!=None:
                if b.ai.driver.ai.squad.faction!=human.ai.squad.faction:
                    acceptable=False

            # check if its full first
            if acceptable and len(b.ai.passengers)<b.ai.max_occupants:
                d=engine.math_2d.get_distance(human.world_coords,b.world_coords)
                if d<best_distance:
                    best_distance=d 
                    best_object=b

        return best_object

    #---------------------------------------------------------------------------
    def get_random_object(self,OBJECT_LIST):
        ''' return a random object from a list '''
        i=random.randint(0,len(OBJECT_LIST)-1)
        return OBJECT_LIST[i]
    
    #---------------------------------------------------------------------------
    def get_objects_within_range(self,WORLD_COORDS,OBJECT_LIST,MAX_DISTANCE):
        '''check distance on objects from an array and returns the ones that are in range'''
        near_objects=[]
        for b in OBJECT_LIST:
            d=engine.math_2d.get_distance(WORLD_COORDS,b.world_coords)
            if d<MAX_DISTANCE:
                near_objects.append(b)
        return near_objects

    #---------------------------------------------------------------------------
    def handle_keydown(self,KEY):
        '''handle keydown events. called by graphics engine'''
        # these are for one off (not repeating) key presses
        #KEY is a key number

        # for now just figure out if we are routing it to 
        # the menu or the player

        #print('key ',KEY)
        if KEY==96:
            self.world_menu.handle_input("tilde")
        elif KEY==91: # [
            self.graphic_engine.zoom_out()
        elif KEY==93: # ]
            self.graphic_engine.zoom_in()
        elif KEY==48:
            self.world_menu.handle_input("0")
        elif KEY==49:
            self.world_menu.handle_input("1")
        elif KEY==50:
            self.world_menu.handle_input("2")
        elif KEY==51:
            self.world_menu.handle_input("3")
        elif KEY==52:
            self.world_menu.handle_input("4")
        elif KEY==53:
            self.world_menu.handle_input("5")
        elif KEY==54:
            self.world_menu.handle_input("6")
        elif KEY==55:
            self.world_menu.handle_input("7")
        elif KEY==56:
            self.world_menu.handle_input("8")
        elif KEY==57:
            self.world_menu.handle_input("9")
        elif KEY==27:
            self.world_menu.handle_input("esc")
        elif KEY==9: #tab
            self.activate_context_menu()
        elif KEY==112: #p
            self.player.ai.handle_keydown('p')
        elif KEY==116: #t
            self.player.ai.handle_keydown('t')
        elif KEY==103: #g
            self.player.ai.handle_keydown('g')
        elif KEY==98: #b
            self.player.ai.handle_keydown('b')
        elif KEY==114: #r
            self.player.ai.handle_keydown('r')

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
                message+=('\n  - ai_state: '+b.ai.ai_state)
                message+=('\n  - ai_goal: '+b.ai.ai_goal)
                message+=('\n  - ai_vehicle_goal: '+b.ai.ai_vehicle_goal)

                # exit vehicle
                if b.ai.in_vehicle:
                    b.ai.handle_exit_vehicle()

                # remove from squad 
                b.ai.squad.members.remove(b)

            elif b.is_vehicle:
                # tell all the passengers to get out
                # kind of a fail safe as they are likely already in the list
                if len(b.ai.passengers)>0:
                    temp=copy.copy(b.ai.passengers)
                    for c in temp:
                        c.ai.handle_exit_vehicle()


            print(message)

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
            print('spawning reinforcements',b[1])
            if b[1]=='german':
                engine.world_builder.create_standard_squad(self,self.german_ai,b[2],b[3])
            elif b[1]=='american':
                engine.world_builder.create_standard_squad(self,self.american_ai,b[2],b[3])
            elif b[1]=='soviet':
                engine.world_builder.create_standard_squad(self,self.soviet_ai,b[2],b[3])
            elif b[1]=='civilian':
                engine.world_builder.create_standard_squad(self,self.civilian_ai,b[2],b[3])
            else:
                print('Error - faction not recognized in process_reinforements: ',b[1])

    #---------------------------------------------------------------------------
    def random_player_spawn(self):
        if len(self.wo_objects_human)>0:
            b=random.randint(0,len(self.wo_objects_human)-1)
            self.player=self.wo_objects_human[b]
            self.player.is_player=True
            print('You are now '+self.player.name)
        else:
            print('player spawn error : no humans left on the map')
            # maybe spawn a new civilian ??

    #---------------------------------------------------------------------------
    def remove_object(self, WORLD_OBJECT):
        ''' remove object from world. '''
        # !! note - objects should add themselves to the remove_queue instead of calling this directly

        if WORLD_OBJECT in self.wo_objects:
            self.wo_objects.remove(WORLD_OBJECT)
            if WORLD_OBJECT.collision and WORLD_OBJECT in self.wo_objects_collision:
                self.wo_objects_collision.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_human:
                self.wo_objects_human.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_gun:
                self.wo_objects_guns.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_german:
                self.wo_objects_german.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_soviet:
                self.wo_objects_soviet.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_american:
                self.wo_objects_american.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_vehicle:
                self.wo_objects_vehicle.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_grenade:
                self.wo_objects_grenade.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_consumable:
                self.wo_objects_consumable.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_building:
                self.wo_objects_building.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_map_pointer:
                self.wo_objects_map_pointer.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_handheld_antitank:
                self.wo_objects_handheld_antitank.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_airplane:
                self.wo_objects_airplane.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_civilian:
                self.wo_objects_civilian.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_melee:
                self.wo_objects_melee.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_medical:
                self.wo_objects_medical.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_container:
                self.wo_objects_container.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_ammo_container:
                self.wo_objects_ammo_container.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_furniture:
                self.wo_objects_furniture.remove(WORLD_OBJECT)
            if WORLD_OBJECT.can_be_deleted:
                self.wo_objects_cleanup.remove(WORLD_OBJECT)
            if WORLD_OBJECT.is_gun_magazine:
                self.wo_objects_gun_magazines.remove(WORLD_OBJECT)
        else:
            print('Error!! '+ WORLD_OBJECT.name+' not in world.wo_objects. Remove fails !!')
        

    #---------------------------------------------------------------------------
    def render(self):
        self.graphic_engine.render()


    #---------------------------------------------------------------------------
    def select_with_mouse(self, mouse_screen_coords):
        '''
        return a object that is 'under' the mouse cursor

        called by graphics_2d_pygame on mouse down event currently 
        '''
        
        possible_objects=[]
        check_objects=[]

        # this has been reworked to favor selecting items over humans/vehicles/storage

        temp=None

        # add all rendered objects to an array
        for b in self.graphic_engine.renderlists:
            for c in b:
                # filter out a couple things we don't want to click on
                if c.is_player==False and c!=self.player.ai.large_pickup and c!=self.player.ai.vehicle and c.is_turret==False:
                    possible_objects.append(c)

        #-- first pass - filter for desirable objects
        for b in possible_objects:
            if (b.is_gun or b.is_consumable or b.is_handheld_antitank or b.is_throwable or b.is_gun_magazine):
                check_objects.append(b)

        if len(check_objects)>0:
            temp=engine.math_2d.checkCollisionCircleMouse(mouse_screen_coords,check_objects)

        #-- second pass - check for less desirable objects
        if temp==None:
            # first remove the objects we already checked
            for b in check_objects:
                possible_objects.remove(b)
            check_objects=[]

            # build a list of less desirable objects
            for b in possible_objects:
                if (b.is_human or b.is_container or b.is_vehicle or b.is_airplane
                    or b.is_ammo_container or b.is_furniture or b.is_large_human_pickup):
                    check_objects.append(b)
            if len(check_objects)>0:
                temp=engine.math_2d.checkCollisionCircleMouse(mouse_screen_coords,check_objects)

        #-- third pass - check everything that is left
        if temp==None:
            # first remove the objects we already checked
            for b in check_objects:
                possible_objects.remove(b)
            check_objects=[]

            # check everything that is left
            if len(possible_objects)>0:
                temp=engine.math_2d.checkCollisionCircleMouse(mouse_screen_coords,possible_objects)

        if temp != None:
            self.world_menu.activate_menu(temp)

    #---------------------------------------------------------------------------
    def spawn_player(self, FACTION):
        spawned=False
        if FACTION=='german':
            if len(self.wo_objects_german)>0:
                b=random.randint(0,len(self.wo_objects_german)-1)
                self.player=self.wo_objects_german[b]
                spawned=True
        elif FACTION=='soviet':
            if len(self.wo_objects_soviet)>0:
                b=random.randint(0,len(self.wo_objects_soviet)-1)
                self.player=self.wo_objects_soviet[b]
                spawned=True
        elif FACTION=='american':
            if len(self.wo_objects_american)>0:
                b=random.randint(0,len(self.wo_objects_american)-1)
                self.player=self.wo_objects_american[b]
                spawned=True
        elif FACTION=='civilian':
            if len(self.wo_objects_civilian)>0:
                b=random.randint(0,len(self.wo_objects_civilian)-1)
                self.player=self.wo_objects_civilian[b]
                spawned=True

        if spawned:
            self.player.is_player=True
            print('You are now '+self.player.name)
        else:
            print('ERROR : player spawn failed')


    #---------------------------------------------------------------------------
    def toggle_map(self):
        ''' enable/disable map features '''

        if self.map_enabled:
            self.map_enabled=False
            # because removing items from the same list you are 
            # iterating through causes odd issues. working with a copy is much 
            # better
            temp=copy.copy(self.wo_objects_map_pointer)
            
            # remove map objects
            self.remove_queue+=temp
        else:
            self.map_enabled=True
            print('map enabled :','green= world area','blue= squad','green= squad destination')

            for b in self.world_areas:
                engine.world_builder.spawn_map_pointer(self,b.world_coords,'normal')

            engine.world_builder.spawn_map_pointer(self,self.player.ai.squad.world_coords,'blue')
            engine.world_builder.spawn_map_pointer(self,self.player.ai.squad.destination,'orange')

    #---------------------------------------------------------------------------
    def load_map(self):
        pass

    #---------------------------------------------------------------------------
    def unload_map(self):
        pass


    #---------------------------------------------------------------------------
    def update(self):
        self.graphic_engine.update()

        if self.is_paused==False:
            self.world_seconds+=self.graphic_engine.time_passed_seconds
            self.process_reinforcements()

            for b in self.wo_objects:
                b.update()

            # update world areas
            for b in self.world_areas:
                b.update()

            # update tactical AIs
            self.german_ai.update()
            self.soviet_ai.update()
            self.american_ai.update()
            self.civilian_ai.update()

            # update world menu -
            self.world_menu.update()

            if self.debug_mode:
                self.update_debug_info()

            if self.display_vehicle_text:
                self.update_vehicle_text()

            # check if we need to start cleaning up old objects for performance
            if len(self.wo_objects_cleanup)>self.cleanup_threshold:
                self.cleanup()
            
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
        self.debug_text_queue=[]
        self.debug_text_queue.append('FPS: '+str(int(self.graphic_engine.clock.get_fps())))
        self.debug_text_queue.append('World scale: '+str(self.graphic_engine.scale))
        self.debug_text_queue.append('World Objects: '+ str(len(self.wo_objects)))
        self.debug_text_queue.append('Rendered Objects: '+ str(self.graphic_engine.renderCount))
        self.debug_text_queue.append('wo_objects_cleanup: '+ str(len(self.wo_objects_cleanup)))
        self.debug_text_queue.append('Exited objects count: '+ str(self.exited_object_count))
        self.debug_text_queue.append('Vehicles: '+ str(len(self.wo_objects_vehicle)))
        self.debug_text_queue.append('Germans: '+ '[units: '+str(len(self.wo_objects_german))+'] [squads: '+ str(len(self.german_ai.squads))+']')
        self.debug_text_queue.append('Soviets: '+ '[units: '+str(len(self.wo_objects_soviet))+'] [squads: '+ str(len(self.soviet_ai.squads))+']')
        self.debug_text_queue.append('Americans: '+ '[units: '+str(len(self.wo_objects_american))+'] [squads: '+ str(len(self.american_ai.squads))+']')
        self.debug_text_queue.append('Civilians: '+ '[units: '+str(len(self.wo_objects_civilian))+'] [squads: '+ str(len(self.civilian_ai.squads))+']')
        self.debug_text_queue.append('----- Player Stats -----')
        self.debug_text_queue.append('Player Name: '+self.player.name)
        self.debug_text_queue.append('Player Scale Modifier: '+str(self.player.scale_modifier))
        self.debug_text_queue.append('Player World Coords: '+str(engine.math_2d.get_round_vector_2(self.player.world_coords)))
        self.debug_text_queue.append('Player altitude: ' + str(self.player.altitude))
        self.debug_text_queue.append('Player Fatigue: '+str(round(self.player.ai.fatigue,1)))
        self.debug_text_queue.append('Player Speed: '+str(self.player.ai.get_calculated_speed()))
        self.debug_text_queue.append('Player building overlap count: '+str(len(self.player.ai.building_list)))


        # world area data
        for b in self.world_areas:
            self.debug_text_queue.append('Area '+b.name+' is controlled by : '+b.faction)

    #------------------------------------------------------------------------------
    def update_vehicle_text(self):
        self.vehicle_text_queue=[]

        if self.player.ai.in_vehicle:
            self.vehicle_text_queue.append('Vehicle: '+self.player.ai.vehicle.name)

            for b in self.player.ai.vehicle.ai.engines:
                self.vehicle_text_queue.append('Engine: ' + b.name + ' ' + str(b.ai.engine_on))

            for b in self.player.ai.vehicle.ai.fuel_tanks:
                fuel=0
                if len(b.ai.inventory)>0:
                    if 'gas' in b.ai.inventory[0].name:
                        fuel=b.ai.inventory[0].volume
                fuel_text=str(b.volume) + '|' + str(round(fuel,2))
                self.vehicle_text_queue.append('Fuel Tank: ' + b.name + ' ' + fuel_text)

            self.vehicle_text_queue.append('max speed | current speed: '+str(round(self.player.ai.vehicle.ai.max_speed,1))+
                ' | '+str(round(self.player.ai.vehicle.ai.current_speed,1)))
            self.vehicle_text_queue.append('acceleration: '+str(self.player.ai.vehicle.ai.acceleration))
            self.vehicle_text_queue.append('throttle: '+str(self.player.ai.vehicle.ai.throttle))
            self.vehicle_text_queue.append('brake: '+str(self.player.ai.vehicle.ai.brake_power))
            self.vehicle_text_queue.append('wheel steering: '+str(self.player.ai.vehicle.ai.wheel_steering))

            # airplane specific 
            if self.player.ai.vehicle.is_airplane:
                self.vehicle_text_queue.append('altitude: '+str(round(self.player.ai.vehicle.altitude,1)))
                self.vehicle_text_queue.append('rate of climb: '+str(round(self.player.ai.vehicle.ai.rate_of_climb,1)))
                self.vehicle_text_queue.append('ailerons: '+str(round(self.player.ai.vehicle.ai.ailerons,1)))
                self.vehicle_text_queue.append('elevator: '+str(round(self.player.ai.vehicle.ai.elevator,1)))
                self.vehicle_text_queue.append('rudder: '+str(round(self.player.ai.vehicle.ai.rudder,1)))
                self.vehicle_text_queue.append('flaps: '+str(round(self.player.ai.vehicle.ai.flaps,1)))










