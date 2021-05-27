
'''
module : world_area.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes : kind of a control point, a map feature that the factions will want to attack or defend 
'''


#import built in modules
import random 

#import custom packages
import engine.math_2d
# module specific variables
module_version='0.0' #module software version
module_last_update_date='May 26 2021' #date of last update


#global variables

class WorldArea(object):
    def __init__(self,WORLD):

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

        # True if more than one faction is present
        self.is_contested=False

        self.time_since_control_update=0

    #---------------------------------------------------------------------------
    def update(self):
        time_passed=self.world.graphic_engine.time_passed_seconds
        self.time_since_control_update+=time_passed

        if self.time_since_control_update>5:
            self.update_control()
        

    #---------------------------------------------------------------------------
    def update_control(self):
        ''' determine who is in control of the world area '''
        german_count=0
        soviet_count=0
        american_count=0

        for b in self.world.wo_objects_human:
            d=engine.math_2d.get_distance(self.world_coords,b.world_coords)
            if d < self.size:
                if b.is_german:
                    german_count+=1
                elif b.is_soviet:
                    soviet_count+=1
                elif b.is_american:
                    american_count+=1

        # todo - determine who controls it
