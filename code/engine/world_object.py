
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
module_last_update_date='March 27 2021' #date of last update

#global variables



class WorldObject(object):

    def __init__(self, world,IMAGE_LIST,AI):

        self.world = world
        self.name = None
        
        # list of images, the AI will set image_index to the current one
        #   that should be used
        # human [default(standing?),walking,fighting,dead]
        # building [outside, inside]
        self.image_list=IMAGE_LIST
        # the index of the image in the list that should be rendered
        self.image_index=0



        # updated by the object AI
        self.world_coords=[0.,0.]

        # updated automatically by the graphic engine when 
        #   the object is renderable 
        self.screen_coords=[0.,0.]

        self.speed = 0.
        self.rotation_angle=0.

        # render level kind of a 'z' layer
        # 0 - ground cover
        # 1 - man made ground cover (cement, building insides)
        # 2 - objects laying on the ground (weapons,etc)
        # 3 - objects walking on the ground (humans, animals, vehicles)
        # 4 - objects above ground (birds, planes, clouds, etc)
        self.render_level=1

        # not sure this is used at the moment
        self.render=True

        # these are used by other objects to determine how this object can be interacted with
        # might just make this a string or something but bools are fast and easy to use 
        self.is_player=False
        self.is_vehicle=False
        self.is_gun=False
        self.is_crate=False

        # AI where any unique code for the object is held
        # note that 'AI' is a class that is passed in
        self.ai=AI(self)

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
    def add_inventory(self, ITEM):
        self.inventory.append(ITEM)

    #remove_inventory
    def remove_inventory(self, ITEM):
        self.inventory.remove(ITEM)

    def wo_start(self):
        self.world.add_object(self)

    def wo_stop(self):
        self.world.remove_object(self)

    def update(self, time_passed):
            self.ai.update(time_passed)

    def render_pass_2(self):
        ''' only override if the object needs special additional rendering'''
        pass
