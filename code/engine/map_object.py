'''
repo : https://github.com/openmarmot/twe

notes : this is the compressed map version of a world_object that is suitable for saving and loading
'''

#import built in modules

#import custom packages

#global variables

class MapObject():
    '''a world object in its compressed strategic map form'''
    def __init__(self,world_builder_identity,name,world_coords,rotation,inventory):
        self.world_builder_identity=world_builder_identity #string
        # note - if name is left as '' on initial creation of the map_object, it will get the name from world_builder.spawn_object when spawned
        self.name=name # string
        self.world_coords=world_coords # [x,y]
        self.rotation=rotation #float
        self.inventory=inventory # array of world_builder_identity strings