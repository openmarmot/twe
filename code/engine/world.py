
'''
module : engine.world.py
version : see module_version variable
Language : Python 3.x
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
from engine.penetration_calculator import Penetration_Calculator
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


        # object lists 
        self.wo_objects=[]
        # not sure this one is used
        self.wo_objects_collision=[]
        self.wo_objects_human=[]
        self.wo_objects_guns=[]
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
        self.wo_objects_liquid_container=[]
        self.wo_objects_object_container=[]

        #world areas
        self.world_areas=[]

        # spawn locations
        self.spawn_center=[0.,0.]
        self.spawn_north=[0.,-4000.]
        self.spawn_south=[0.,4000.]
        self.spawn_west=[-4000.,0.]
        self.spawn_east=[4000.,0.]


        self.graphic_engine=Graphics_2D_Pygame(SCREEN_SIZE,self)
        self.world_menu=World_Menu(self)
        self.penetration_calculator=Penetration_Calculator()

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

        # max distance at which you can select something (open a context menu)
        self.max_menu_distance=90

        # checked by ai_gun.fire() and world_builder.spawn_shrapnel_cloud
        # True== get hurt, False== don't get hurt
        self.friendly_fire=True # complete friendly fire
        self.friendly_fire_squad=False # only at the squad level
        self.friendly_fire_explosive=True # grenade shrap clouds
        self.friendly_fire_explosive_squad=True # only at the squad level

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

        # reset the image so that the graphics engine can make sure it matches the current view scale
        WORLD_OBJECT.reset_image=True

        #maybe should check if the object is already in there to prevent duplicates
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
        if WORLD_OBJECT.is_object_container:
            self.wo_objects_object_container.append(WORLD_OBJECT)
        if WORLD_OBJECT.is_liquid_container:
            self.wo_objects_liquid_container.append(WORLD_OBJECT)
        if WORLD_OBJECT.is_ammo_container:
            self.wo_objects_ammo_container.append(WORLD_OBJECT)
        
    #---------------------------------------------------------------------------
    def check_collision_bool(self,COLLIDER,IGNORE_LIST, CHECK_ALL,CHECK_HUMAN):
        ''' collision check. returns bool as to whether there was a collision.'''
        # COLLIDER - worldobject doing the colliding
        # IGNORE LIST - list of objects to ignore
        collided=False

        if CHECK_ALL :
            # in this case all is humans+vehicles+buidings
            objects=self.wo_objects_human+self.wo_objects_building+self.wo_objects_vehicle
            #temp=engine.math_2d.checkCollisionSquareOneResult(COLLIDER,objects,IGNORE_LIST)
            temp=engine.math_2d.checkCollisionCircleOneResult(COLLIDER,objects,IGNORE_LIST)
            if temp !=None:
                #print('Collision with '+temp.name )
                temp.ai.handle_event("collision",COLLIDER)
                collided=True
        else :
            if CHECK_HUMAN :
                temp=engine.math_2d.checkCollisionCircleOneResult(COLLIDER,self.wo_objects_human,IGNORE_LIST)
                if temp !=None:
                    #print('Collision with '+temp.name )
                    temp.ai.handle_event("collision",COLLIDER)
                    collided=True

        return collided


    #---------------------------------------------------------------------------
    def check_collision_return_object(self,COLLIDER,IGNORE_LIST, CHECK_ALL,CHECK_HUMAN):
        ''' collision check. returns colliding object or None'''
        # COLLIDER - worldobject doing the colliding
        # IGNORE LIST - list of objects to ignore
        collided=None

        if CHECK_ALL :
            # in this case all is humans+vehicles+buidings
            objects=self.wo_objects_human+self.wo_objects_building+self.wo_objects_vehicle
            #temp=engine.math_2d.checkCollisionSquareOneResult(COLLIDER,objects,IGNORE_LIST)
            temp=engine.math_2d.checkCollisionCircleOneResult(COLLIDER,objects,IGNORE_LIST)
            if temp !=None:
                #print('Collision with '+temp.name )
                temp.ai.handle_event("collision",COLLIDER)
                collided=temp
        else :
            if CHECK_HUMAN :
                temp=engine.math_2d.checkCollisionCircleOneResult(COLLIDER,self.wo_objects_human,IGNORE_LIST)
                if temp !=None:
                    #print('Collision with '+temp.name )
                    temp.ai.handle_event("collision",COLLIDER)
                    collided=temp

        return collided


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
    def get_random_object(self,OBJECT_LIST):
        ''' return a random object from a list '''
        i=random.randint(0,len(OBJECT_LIST)-1)
        return OBJECT_LIST[i]

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
        if WORLD_OBJECT in self.wo_objects:
            self.wo_objects.remove(WORLD_OBJECT)
        else:
            print('Error!! '+ WORLD_OBJECT.name+' not in world.wo_objects. Remove fails !!')
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
        if WORLD_OBJECT.is_object_container:
            self.wo_objects_object_container.remove(WORLD_OBJECT)
        if WORLD_OBJECT.is_liquid_container:
            self.wo_objects_liquid_container.remove(WORLD_OBJECT)
        if WORLD_OBJECT.is_ammo_container:
            self.wo_objects_ammo_container.remove(WORLD_OBJECT)

    #---------------------------------------------------------------------------
    def render(self):
        self.graphic_engine.render()


    #---------------------------------------------------------------------------
    def select_with_mouse(self, mouse_screen_coords):
        '''
        return a object that is 'under' the mouse cursor
        radius of 10 or so seems fine

        called by graphics_2d_pygame on mouse down event currently 
        '''
        
        radius=10
        possible_objects=[]

        # this has been reworked to favor selecting items over humans/vehicles/storage

        temp=None

        for b in self.graphic_engine.renderlists:
            for c in b:
                if (c.is_gun or c.is_consumable or c.is_handheld_antitank or c.is_grenade):
                    possible_objects.append(c)

        if len(possible_objects)>0:
            temp=engine.math_2d.checkCollisionCircleMouse(mouse_screen_coords,radius,possible_objects)

        # if there were no guns/consumables/etc or there were but they weren't under the mouse..
        if temp==None:
            for b in self.graphic_engine.renderlists:
                for c in b:
                    if (c.is_human or c.is_object_container or c.is_vehicle or c.is_airplane
                    or c.is_liquid_container or c.is_ammo_container):
                        possible_objects.append(c)
            if len(possible_objects)>0:
                temp=engine.math_2d.checkCollisionCircleMouse(mouse_screen_coords,radius,possible_objects)
        
        if temp != None:
            d=engine.math_2d.get_distance(self.player.world_coords,temp.world_coords)
            if d<self.max_menu_distance or self.debug_mode:
                self.world_menu.activate_menu(temp)
            else:
                print('too far!!')
                print('distance is ',d)
                self.player.ai.destination=copy.copy(temp.world_coords)
                self.player.ai.ai_state='start_moving'
                self.player.ai.ai_goal='player_move'
                self.player.ai.time_since_player_interact+=self.player.ai.time_before_afk+60
                self.player.ai.time_since_ai_transition=0

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
            for b in temp:
                self.remove_object(b)
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

            if self.debug_mode:
                self.update_debug_info()

            if self.display_vehicle_text:
                self.update_vehicle_text()

    #------------------------------------------------------------------------------
    def update_debug_info(self):
        self.debug_text_queue=[]
        self.debug_text_queue.append('FPS: '+str(int(self.graphic_engine.clock.get_fps())))
        self.debug_text_queue.append('World Objects: '+ str(len(self.wo_objects)))
        self.debug_text_queue.append('Rendered Objects: '+ str(self.graphic_engine.renderCount))
        self.debug_text_queue.append('Germans: '+ '[units: '+str(len(self.wo_objects_german))+'] [squads: '+ str(len(self.german_ai.squads))+']')
        self.debug_text_queue.append('Soviets: '+ '[units: '+str(len(self.wo_objects_soviet))+'] [squads: '+ str(len(self.soviet_ai.squads))+']')
        self.debug_text_queue.append('Americans: '+ '[units: '+str(len(self.wo_objects_american))+'] [squads: '+ str(len(self.american_ai.squads))+']')
        self.debug_text_queue.append('Civilians: '+ '[units: '+str(len(self.wo_objects_civilian))+'] [squads: '+ str(len(self.civilian_ai.squads))+']')
        self.debug_text_queue.append('Player World Coords: '+str(self.player.world_coords))
        self.debug_text_queue.append('Player Fatigue: '+str(self.player.ai.fatigue))
        self.debug_text_queue.append('Player Speed: '+str(self.player.ai.get_calculated_speed()))

        # world area data
        for b in self.world_areas:
            self.debug_text_queue.append('Area '+b.name+' is controlled by : '+b.faction)

    #------------------------------------------------------------------------------
    def update_vehicle_text(self):
        self.vehicle_text_queue=[]

        if self.player.ai.in_vehicle:
            self.vehicle_text_queue.append('Vehicle: '+self.player.ai.vehicle.name)
            self.vehicle_text_queue.append('Engine On: '+str(self.player.ai.vehicle.ai.engine_on))
            self.vehicle_text_queue.append('speed: '+str(round(self.player.ai.vehicle.ai.vehicle_speed,1)))
            self.vehicle_text_queue.append('acceleration: '+str(round(self.player.ai.vehicle.ai.acceleration,1)))
            self.vehicle_text_queue.append('throttle: '+str(round(self.player.ai.vehicle.ai.throttle,1)))
            self.vehicle_text_queue.append('brake: '+str(round(self.player.ai.vehicle.ai.brake_power,1)))
            self.vehicle_text_queue.append('fuel: '+str(round(self.player.ai.vehicle.ai.fuel,2)))








