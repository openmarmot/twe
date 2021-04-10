
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

# module specific variables
module_version='0.0' #module software version
module_last_update_date='April 05 2021' #date of last update

#global variables


class World(object):
    #---------------------------------------------------------------------------
    def __init__(self,SCREEN_SIZE):

        self.wo_objects=[]
        self.wo_objects_collision=[]
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

    #---------------------------------------------------------------------------
    def remove_object(self, worldobject):
        if worldobject in self.wo_objects:
            self.wo_objects.remove(worldobject)
        if worldobject.collision and worldobject in self.wo_objects_collision:
            self.wo_objects_collision.remove(worldobject)

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

    #---------------------------------------------------------------------------
    def render(self):
        self.graphic_engine.render()


 #   def get_close_entity(self, name, location, e_range=100):
#
#        location = Vector2(*location)
#
#
 #       for entity in self.entities.values():
#
 #           if entity.name == name:
  #              distance = location.get_distance_to(entity.location)
   #             if distance < e_range:
    #                return entity
     #   return None
