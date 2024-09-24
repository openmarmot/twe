'''
module : map_object.py
language : Python 3.x
email : andrew@openmarmot.com
notes : this is the compressed map version of a world_object that is suitable for saving and loading
'''

#import built in modules

#import custom packages

#global variables

class MapObject(object):
    '''a world object in its compressed strategic map form'''
    def __init__(self,world_builder_identity,name,world_coords,rotation,inventory):
        self.world_builder_identity=world_builder_identity #string
        self.name=name # string
        self.world_coords=world_coords # [x,y]
        self.rotation=rotation #float
        self.inventory=inventory # array of world_builder_identity