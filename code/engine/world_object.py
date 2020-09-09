
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
module_last_update_date='June 13 2016' #date of last update

#global variables



class WorldObject(object):

    def __init__(self, world):

        self.world = world
        self.name = None
        self.image_name = 'none'
        self.world_coords=[0.,0.]
        self.screen_coords=[0.,0.]
        self.speed = 0.
        self.rotation_angle=0.
        self.render_level=1
        self.render=True
        self.is_player=False
        self.ai=None
        
        # list of other wo_objects
        self.inventory=[]

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
