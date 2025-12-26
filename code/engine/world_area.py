
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : kind of a control point, a map feature that the factions will want to attack or defend 
'''


#import built in modules
import random 

#import custom packages
import engine.math_2d

#global variables

class WorldArea():
    def __init__(self,WORLD):

        # created by world_builder.generate_world_area

        # should world area have a list of the objects in it ???

        self.name='none'

        # the ever present WORLD reference
        self.world=WORLD

        # radius? circumference?
        # this is used to determine the sphere of coverage for what is considered 'in' the area
        self.size=2000

        # center of the area
        self.world_coords=[0,0]

        # faction : german/soviet/american/none
        #  basically who is currently in control 
        self.faction='none'

        self.german_count=0
        self.soviet_count=0
        self.american_count=0
        self.civilian_count=0

        # helps AI determine how to interact with it
        # town / fuel_dump / 
        self.area_type='none'

        # True if more than one faction is present
        self.is_contested=False

        self.time_since_control_update=0

        self.control_update_interval=0

        # locations are used when a vehicle or squad travels to a world area
        # this keeps vehicles from all being on top of each other
        self.locations=[]
        self.used_locations=[]

    #---------------------------------------------------------------------------
    def compute_locations(self):
        '''compute locations, avoiding existing objects'''
        # note this is called by world.start and is pre-computed before the game starts
        
        # build a list of coordinates to avoid. avoid all objects roughly near the world area
        coords_to_avoid=[]
        grids=self.world.grid_manager.get_grid_squares_near_world_coords(self.world_coords,self.size)
        for grid in grids:
            for wo_object in grid.wo_objects:
                coords_to_avoid.append(wo_object.world_coords)

        seperation=100
        count=100 # this should be plenty. locations are mostly used at a squad or vehicle level
        #self.locations=engine.math_2d.get_random_constrained_coords(self.world_coords,
        #    self.size,seperation,count,coords_to_avoid,600)
        
        self.locations=engine.math_2d.get_random_constrained_coords_v2(self.world_coords,
            self.size,seperation,count,coords_to_avoid,600)
        
    #---------------------------------------------------------------------------
    def get_location(self):
        '''get a random unused location'''

        if len(self.locations)==0:
            # reset 
            self.locations=self.used_locations
            self.used_locations=[]

        location=self.locations.pop(random.randint(0, len(self.locations) - 1))
        self.used_locations.append(location)
        return location

    #---------------------------------------------------------------------------
    def update(self):
        time_passed=self.world.time_passed_seconds
        self.time_since_control_update+=time_passed

        if self.time_since_control_update>self.control_update_interval:
            self.update_control()
            self.time_since_control_update=0
            self.control_update_interval=random.randint(5,13)
        

    #---------------------------------------------------------------------------
    def update_control(self):
        ''' determine who is in control of the world area '''
        self.german_count=0
        self.soviet_count=0
        self.american_count=0
        self.civilian_count=0
        
        # get the humans from the grid squares that cover the world_area bounds
        for b in self.world.grid_manager.get_objects_from_grid_squares_near_world_coords(self.world_coords,self.size,True,False):
            d=engine.math_2d.get_distance(self.world_coords,b.world_coords)
            if d < self.size:
                if b.ai.squad.faction_tactical.faction=='german':
                    self.german_count+=1
                elif b.ai.squad.faction_tactical.faction=='soviet':
                    self.soviet_count+=1
                elif b.ai.squad.faction_tactical.faction=='american':
                    self.american_count+=1
                elif b.ai.squad.faction_tactical.faction=='civilian':
                    self.civilian_count+=1
                else:
                    print('debug: world_area.update_control unidentified human object')

        # determine who controls it
        # todo - need to understand if it is a free for all or if soviets and americans are allied
        if self.german_count>self.soviet_count and self.german_count>self.american_count:
            self.faction='german'
        elif self.soviet_count>self.german_count and self.soviet_count>self.american_count:
            self.faction='soviet'
        elif self.american_count>self.german_count and self.american_count>self.soviet_count:
            self.faction='american'
        else:
            self.faction='none'

        if self.german_count>0 and self.soviet_count>0:
            self.is_contested=True
        elif self.german_count>0 and self.american_count>0:
            self.is_contested=True
        elif self.soviet_count>0 and self.american_count>0:
            # need to check if they are allies or not
            self.is_contested=True
        else:
            self.is_contested=False