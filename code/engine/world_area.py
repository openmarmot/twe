
'''
module : world_area.py
language : Python 3.x
email : andrew@openmarmot.com
notes : kind of a control point, a map feature that the factions will want to attack or defend 
'''


#import built in modules
import random 

#import custom packages
import engine.math_2d

#global variables

class WorldArea(object):
    def __init__(self,WORLD):

        # created by world_builder.generate_world_area

        # should world area have a list of the objects in it ???

        self.name='none'

        # the ever present WORLD reference
        self.world=WORLD

        # radius? circumference?
        # this is used to determine the sphere of coverage for what is considered 'in' the area
        self.size=1000

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
        self.type='none'

        # True if more than one faction is present
        self.is_contested=False

        self.time_since_control_update=0

        self.control_update_interval=0

    #---------------------------------------------------------------------------
    def update(self):
        time_passed=self.world.time_passed_seconds
        self.time_since_control_update+=time_passed

        if self.time_since_control_update>5:
            self.update_control()
            self.time_since_control_update=0
            self.control_update_interval=random.randint(5,25)
        

    #---------------------------------------------------------------------------
    def update_control(self):
        ''' determine who is in control of the world area '''
        self.german_count=0
        self.soviet_count=0
        self.american_count=0
        self.civilian_count=0

        for b in self.world.wo_objects_human:
            d=engine.math_2d.get_distance(self.world_coords,b.world_coords)
            if d < self.size:
                if b.is_german:
                    self.german_count+=1
                elif b.is_soviet:
                    self.soviet_count+=1
                elif b.is_american:
                    self.american_count+=1
                elif b.is_civilian:
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