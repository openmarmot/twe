
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
'''

#import built in modules
import copy

#import custom packages
import engine.math_2d

#global variables


class WorldObject(object):

    def __init__(self, world,IMAGE_LIST,AI):

        self.world = world
        self.name = None

        # this gets set every time a object is added to the world
        # in world.world_seconds
        self.spawn_time=None

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
        # image center. calculated by graphics_engine
        self.image_center=None

        # tell graphicsEngine to reset the image (need to rotate, etc)
        self.reset_image=True

        # objects that fly set their own scale relative to their elevation and the global scale
        # should probably never be negative unless if we start simulating uh holes in the ground
        self.scale_modifier=0


        # if the object scale (world scale + scale_modifier) is under 
        # this it won't be rendered
        self.minimum_visible_scale=0.1

        # updated by the object AI
        self.world_coords=[0,0]
        self.last_world_coords=[0,0] # used to check for movement
        
        # altitude above ground in meters
        self.altitude=0

        # - physics stuff -
        # for containers this is the max volume / max capacity
        # for liquids and most other things this is the current actual volume
        self.volume=0 # liters.
        self.weight=0 #kilograms
        self.drag_coefficient=0.8
        self.frontal_area=0 # square meters

        # updated automatically by the graphic engine when 
        #   the object is renderable 
        self.screen_coords=[0.,0.]

        # rotation_angle - mainly used to rotate the object sprite. in degrees
        self.rotation_angle=0.

        # heading is a direction vector used by some objects
        # can be set with math_2d.get_heading_vector
        self.heading=[0,0]

        
        # checked by graphics_2d_pygame.update_render_info 
        # to determine whether to render the object or not
        # this is used RARELY for special effects like passengers of vehicles
        self.render=True

        # ---- descriptor bools ----------------------------
        
        # for objects with no logic. update() will not be called
        self.no_update=False

        # objects that should not be saved
        self.no_save=False


        # whether the object has been added to the world with world.add_object
        # objects that are in a container are generally not in world
        # however things like humans always are
        # this is used for rendering and grid square placement
        self.in_world=False


        # these are used by other objects to determine how this object can be interacted with
        # might just make this a string or something but bools are fast and easy to use 
        self.is_player=False
        self.is_human=False # something that has ai_human
        
        # note - more specific vehicle categories done in the ai_vehicle class
        self.is_vehicle=False
        self.is_airplane=False
        self.is_gun=False
        self.is_gun_magazine=False # something that has ai_magazine 
        self.is_grenade=False
        self.is_handheld_antitank=False
        self.is_throwable=False #something that can be thrown 
        self.is_radio=False
        self.is_large_human_pickup=False # fills a large pickup slot
        self.is_container=False # object that stores other objects
        self.is_ammo_container=False # contains ammo. note this should go away
        self.is_projectile=False
        self.is_consumable=False
        self.is_medical=False # general medical objects. bandage / pain pills / etc
        self.is_particle_effect=False # smoke/whatever. used to set a higher z level
        self.is_turret=False
        self.is_rotor=False
        self.is_towable=False # indicates whether a object can be towed by a vehicle
        
        self.is_building=False
        self.is_map_pointer=False
        self.is_furniture=False
        self.is_ground_texture=False

        self.is_body=False # dead human
        self.is_vehicle_wreck=False # dead vehicle wreck

        self.is_hit_marker=False

        # state of matter
        self.is_liquid=False
        self.is_solid=True
        self.is_gas=False

        # stuff that i don't think is used at the moment
        self.is_melee=False # melee close combat weapon like a dagger 
        self.is_gun_mag_carrier=False



        # wearables are clothing, helmets, etc 
        self.is_wearable=False
        
        # ---- \ descriptor bools ----------------------------

        # how this object should be offset if it is carried by a human
        self.large_pickup_offset=[10,0]

        # AI where any unique code for the object is held
        # note that 'AI' is a class that is passed in
        self.ai=AI(self)

        #collision (bool) - used by world class
        # true - obj will be added to collision list
        # false - obj will not be added to collision list, nothing can collide with it
        self.collision=True
        # radius of collision circle in world coords
        self.collision_radius=5
        

        # render level kind of a 'z' layer
        # see graphics_2d_pygame for the current list of levels
        self.render_level=None
        self.static_render_level=False
        # doesn't do much here, should also be called after all variables are set by the spawner
        self.reset_render_level()

        # is this used? pretty sure its not 
        self.id = 0

        # the world_grid_square the object is in
        self.grid_square=None

    #---------------------------------------------------------------------------
    def add_inventory(self, ITEM):
        self.ai.handle_event('add_inventory',ITEM)

    #---------------------------------------------------------------------------
    def remove_inventory(self, ITEM):
        self.ai.handle_event('remove_inventory',ITEM)
    
    #---------------------------------------------------------------------------
    def reset_render_level(self):
        '''reset render level to defaults based on object type '''

        if self.static_render_level:
            return

        if self.is_ground_texture:
            self.render_level=0
        elif self.is_building:
            self.render_level=1
        elif self.is_gun:
            self.render_level=2
        elif self.is_vehicle:
            self.render_level=3
        elif self.is_container:
            self.render_level=3
        elif self.is_rotor:
            self.render_level=4
        elif self.is_particle_effect:
            self.render_level=4
        elif self.is_turret:
            self.render_level=4
        elif self.is_human:
            self.render_level=5
        elif self.is_hit_marker:
            self.render_level=6
        else:
            self.render_level=2
            
    #---------------------------------------------------------------------------
    def update(self):
        self.ai.update()
        self.update_scale()
        self.update_physics()
        self.update_grid_square()

    #---------------------------------------------------------------------------
    def update_grid_square(self):
        '''updates the grid square if movement is detected'''
        # grid square controls rendering and collision, we do not want to be there if 
        # we are technically not in the world
        if self.in_world:
            if self.last_world_coords!=self.world_coords:
                self.last_world_coords=copy.copy(self.world_coords)
                self.world.grid_manager.update_wo_object_square(self)

    #---------------------------------------------------------------------------
    def update_physics(self):

        # gravity 
        if self.altitude>0:
            self.render_level=6
            self.altitude+=(engine.math_2d.GRAVITY*self.world.time_passed_seconds)
            if self.altitude<=0:
                self.altitude=0
                self.reset_render_level()

    #---------------------------------------------------------------------------
    def update_scale(self):
        '''update scale of object relative to world'''

        if self.altitude==0:
            self.scale_modifier=0
        else:
            new_modifier=round(0.001*self.altitude,2)
            if new_modifier!=self.scale_modifier:
                self.scale_modifier=new_modifier
                self.reset_image=True

                # if player or vehicle with player in it ..
                # theoretically also change the global scale by the amount that it changed
                # and reset every obj. otherwise the player relative scale will change   
                             
    #---------------------------------------------------------------------------
    def wo_start(self):
        '''add object to world'''
        self.world.add_queue.append(self)

    #---------------------------------------------------------------------------
    def wo_stop(self):
        ''' remove object from world'''
        self.world.remove_queue.append(self)
