
'''
module : module_template.py
version : see module_version variable
Language : Python 3.x
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

        # string that tells world_builder how to spawn this object
        # used for saving/loading objects
        self.world_builder_identity=''
        
        # list of images, the AI will set image_index to the current one
        #   that should be used
        # human [default(standing?),walking,fighting,dead]
        # building [outside, inside]
        self.image_list=IMAGE_LIST
        # the index of the image in the list that should be rendered
        self.image_index=0

        # the actual rotated image object. set by graphics_engine 
        self.image=None 

        # image width, height. set by graphics_engine
        self.image_size=None

        # tell graphicsEngine to reset the image (need to rotate, etc)
        self.reset_image=True

        # updated by the object AI
        self.world_coords=None

        # updated automatically by the graphic engine when 
        #   the object is renderable 
        self.screen_coords=[0.,0.]

        self.speed = 0.
        self.rotation_speed=0.
        # rotation_angle - mainly used to rotate the object sprite. in degrees
        self.rotation_angle=0.
        # heading is a direction vector used by some objects
        # can be set with math_2d.get_heading_vector
        self.heading=[0,0]

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
        self.is_human=False
        self.is_zombie=False
        self.is_civilian=False
        self.is_soldier=False
        self.is_vehicle=False
        self.is_gun=False
        self.is_grenade=False
        self.is_handheld_antitank=False
        self.is_gun_mag_carrier=False
        self.is_container=False
        self.is_projectile=False
        self.is_consumable=False
        self.is_german=False
        self.is_soviet=False
        self.is_american=False
        self.is_gas=False
        self.is_diesel=False
        self.is_building=False
        self.is_map_pointer=False

        # AI where any unique code for the object is held
        # note that 'AI' is a class that is passed in
        self.ai=AI(self)

        #collision (bool) - used by world class
        # true - obj will be added to collision list
        # false - obj will not be added to collision list, nothing can collide with it
        self.collision=True
        # radius of collision circle in world coords
        self.collision_radius=5
        


        # is this used? pretty sure its not 
        self.id = 0

    #add_inventory
    def add_inventory(self, ITEM):
        self.ai.handle_event('add_inventory',ITEM)

    #remove_inventory
    def remove_inventory(self, ITEM):
        self.ai.handle_event('remove_inventory',ITEM)

    def wo_start(self):
        self.world.add_object(self)

    def wo_stop(self):
        self.world.remove_object(self)

    def update(self):
            self.ai.update()

    def render_pass_2(self):
        ''' only override if the object needs special additional rendering'''
        pass
