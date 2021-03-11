
'''
module : module_template.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules

#import custom packages

# module specific variables
module_version='0.0' #module software version
module_last_update_date='March 10 2021' #date of last update

#global variables



class WorldObject(object):

    def __init__(self, world):

        self.world = world
        self.name = None
        self.image_name = 'none'
        # updated by the object AI
        self.world_coords=[0.,0.]
        # note these are only updated by the graphic engine when the obj is on screen
        self.screen_coords=[0.,0.]
        self.speed = 0.
        self.rotation_angle=0.
        self.render_level=1
        self.render=True

        # these are used by other objects to determine how this object can be interacted with
        # might just make this a string or something but bools are fast and easy to use 
        self.is_player=False
        self.is_vehicle=False
        self.is_gun=False
        self.is_crate=False
        self.ai=None

        #collision (bool) - used by world class
        # true - obj will be added to collision list
        # false - obj will not be added to collision list, nothing can collide with it
        self.collision=True
        # radius of collision circle in world coords
        self.collision_radius=5
        
        # list of other wo_objects contained within this one
        self.inventory=[]

        # is this used? pretty sure its not 
        self.id = 0

    #add_inventory

    #remove_inventory

    def wo_start(self):
        self.world.add_object(self)

    def wo_stop(self):
        self.world.remove_object(self)

    def update(self, time_passed):
        if self.ai!=None:
            self.ai.update(time_passed)

    def render_pass_2(self):
        ''' only override if the object needs special additional rendering'''
        pass
