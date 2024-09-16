
'''
module : ai_faction_strategic.py
language : Python 3.x
email : andrew@openmarmot.com
notes : AI that controls all a factions units on the strategic map 
'''


#import built in modules
import random
import copy 

#import custom packages
import engine.math_2d
import engine.world_builder 

#global variables

class AIFactionStrategic(object):
    def __init__(self,world,faction):

        # faction - german/soviet/american/civilian
        self.faction=faction

    #---------------------------------------------------------------------------
    def set_initial_units(self):

        # things we should already know :
        # - which column? or squares are ours
        # - which squares are the enemy
        # - how many points we have to spend

        # determine what squares if any are at risk

        # determine a deployment strategy

        # initial deployment can be deployed on any owned grid ssuare
        # after that reinforcements show up at rail yards

        pass