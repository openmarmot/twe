
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


# module specific variables
module_version='0.0' #module software version
module_last_update_date='September 08 2020' #date of last update

#global variables


class World(object):
    #---------------------------------------------------------------------------
    def __init__(self,graphic_engine):

        self.wo_objects=[]
        self.entity_id = 0
        self.graphic_engine=graphic_engine
        self.graphic_engine.world=self
        self.player=None

    #---------------------------------------------------------------------------
    def add_object(self, worldobject):
        if(worldobject.render):
            self.graphic_engine.add_object(worldobject)

        self.wo_objects.append(worldobject)

    #---------------------------------------------------------------------------
    def remove_object(self, worldobject):
        self.graphic_engine.remove_object(worldobject)

        if worldobject in self.wo_objects:
            self.wo_objects.remove(worldobject)

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
            b.update(self.graphic_engine.time_passed_seconds)

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
