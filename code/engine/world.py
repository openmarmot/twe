
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


#import custom packages
from engine.graphics_2d_pygame import Graphics_2D_Pygame
from engine.world_menu import World_Menu
from engine.penetration_calculator import Penetration_Calculator
import engine.math_2d
import engine.world_builder
from ai.ai_faction_tactical import AIFactionTactical

# module specific variables
module_version='0.0' #module software version
module_last_update_date='June 17 2021' #date of last update

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

        #bool
        self.map_enabled=False

    #---------------------------------------------------------------------------
    def add_object(self, WORLD_OBJECT):
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
    def get_closest_ammo_source(self, WORLD_OBJECT):
        ''' returns the world object that is the closest ammo source '''
        # WORLD_OBJECT - the object that needs ammo 

        # sources of ammo are : 
        # 1 - your squad mates
        # 2 - vehicles 
        # 3 - ?? (non squad but same side?)

        best_squad_mate=None 
        if WORLD_OBJECT.ai.squad != None:
            if len(WORLD_OBJECT.ai.squad.members)>0:
                best_squad_mate=self.get_closest_object(WORLD_OBJECT.world_coords,WORLD_OBJECT.ai.squad.members)

        if best_squad_mate != None:
            return best_squad_mate
        else:
            # no squad mates for whatever reason
            # just go to a building for now - eventually replace with ammo crate 
            if len(self.wo_objects_building)>0:
                best_building=self.get_closest_object(WORLD_OBJECT.world_coords,self.wo_objects_building)
                return best_building
            else:
                print("Error: no suitable ammo sources")
                # ehh just return a gun or whatever 
                return self.get_closest_gun(WORLD_OBJECT.world_coords)

    #---------------------------------------------------------------------------
    def get_closest_gun(self, WORLD_COORDS):
        ''' returns the closest gun. spawns one if there are none '''
        best_object=self.get_closest_object(WORLD_COORDS,self.wo_objects_guns)
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
    def get_closest_object(self, WORLD_COORDS,OBJECT_LIST):
        ''' can be used on its own or referenced like get_closest_gun() does'''
        best_distance=100000
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

    #---------------------------------------------------------------------------
    def render(self):
        self.graphic_engine.render()


    #---------------------------------------------------------------------------
    def select_with_mouse(self, radius):
        '''
        return a object that is 'under' the mouse cursor
        radius of 10 or so seems fine

        called by graphics_2d_pygame on mouse down event .. currently 
        '''
        mouse=self.graphic_engine.get_mouse_screen_coords()
        possible_objects=[]

        for b in self.graphic_engine.renderlists:
            for c in b:
                # could check is_gun, is_human etc here to narrow down
                if c.is_human or c.is_container or c.is_gun or c.is_consumable or c.is_vehicle or c.is_handheld_antitank:
                    possible_objects.append(c)

        
        return engine.math_2d.checkCollisionCircleMouse(mouse,radius,possible_objects)

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

            for b in self.world_areas:
                engine.world_builder.spawn_map_pointer(self,b.world_coords,'normal')

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






