
'''
module : engine.world.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
The world class should handle all of the world logic and world objects.
It should not have any specific graphic engine code (pygame, etc)
'''




#import custom packages
from engine.graphics_2d_pygame import Graphics_2D_Pygame
from engine.world_menu import World_Menu
import engine.math_2d
import engine.world_builder

# module specific variables
module_version='0.0' #module software version
module_last_update_date='April 05 2021' #date of last update

#global variables


class World(object):
    #---------------------------------------------------------------------------
    def __init__(self,SCREEN_SIZE):


        # object lists 
        self.wo_objects=[]
        self.wo_objects_collision=[]
        self.wo_objects_human=[]
        self.wo_objects_guns=[]


        self.entity_id = 0
        self.graphic_engine=Graphics_2D_Pygame(SCREEN_SIZE,self)
        self.world_menu=World_Menu(self)
        self.player=None

    #---------------------------------------------------------------------------
    def add_object(self, worldobject):
        #maybe should check if the object is already in there to prevent duplicates
        self.wo_objects.append(worldobject)
        if worldobject.collision:
            self.wo_objects_collision.append(worldobject)
        if worldobject.is_human:
            self.wo_objects_human.append(worldobject)
        if worldobject.is_gun:
            self.wo_objects_guns.append(worldobject)

    #---------------------------------------------------------------------------
    def check_collision_bool(self,COLLIDER,IGNORE_LIST, CHECK_ALL,CHECK_HUMAN):
        ''' collision check. returns bool as to whether there was a collision.'''
        # COLLIDER - worldobject doing the colliding
        # IGNORE LIST - list of objects to ignore
        collided=False

        if CHECK_ALL :
            # this should maybe be wo_objects_collision - not really using that atm though
            temp=engine.math_2d.checkCollisionSquareOneResult(COLLIDER,self.wo_objects,IGNORE_LIST)
            if temp !=None:
                print('Collision with '+temp.name )
                temp.ai.handle_event("collision",COLLIDER)
                collided=True
        else :
            if CHECK_HUMAN :
                temp=engine.math_2d.checkCollisionSquareOneResult(COLLIDER,self.wo_objects_human,IGNORE_LIST)
                if temp !=None:
                    print('Collision with '+temp.name )
                    temp.ai.handle_event("collision",COLLIDER)
                    collided=True

        return collided

    #---------------------------------------------------------------------------
    def get_closest_gun(self, WORLD_COORDS):
        best_distance=100000
        best_object=None
        for b in self.wo_objects_guns:
            d=engine.math_2d.get_distance(WORLD_COORDS,b.world_coords)
            if d<best_distance:
                best_distance=d 
                best_object=b
        if best_object==None:
            # spawn a new gun and return it
            engine.world_builder.spawn_gun(world,[WORLD_COORDS[0]+float(random.randint(-200,200)),WORLD_COORDS[1]+float(random.randint(-200,200))],'mp40')
            # hmm we don't have the object reference, so lets just run this method again
            # does this make sense? am i insane? HA HA HAHAHAHA
            print('warning mind bender insane o loop activated in world.get_closest_gun')
            return self.get_closest_gun(WORLD_COORDS)
        else : 
            return best_object
    #---------------------------------------------------------------------------
    def remove_object(self, worldobject):
        if worldobject in self.wo_objects:
            self.wo_objects.remove(worldobject)
        if worldobject.collision and worldobject in self.wo_objects_collision:
            self.wo_objects_collision.remove(worldobject)
        if worldobject.is_human:
            self.wo_objects_human.remove(worldobject)
        if worldobject.is_gun:
            self.wo_objects_guns.remove(worldobject)

    #---------------------------------------------------------------------------
    def render(self):
        self.graphic_engine.render()


    #---------------------------------------------------------------------------
    def load_map(self):
        pass

    #---------------------------------------------------------------------------
    def unload_map(self):
        pass

#    def get(self, entity_id):
#
#        if entity_id in self.wo_objects:
#            return self.wo_objects[entity_id]
#        else:
#            return None

    #---------------------------------------------------------------------------
    def update(self):
        self.graphic_engine.update()

        for b in self.wo_objects:
            b.update()





