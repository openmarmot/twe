
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
    def __init__(self,strategic_map,faction):

        # faction - german/soviet/american/civilian
        self.faction=faction

        # ref to the strategic map
        self.strategic_map=strategic_map

        # square data
        self.squares_owned=[]
        self.squares_owned_at_risk=[]
        self.square_objectives=[]
        self.square_objectives_owned=[]
        self.square_objectives_not_owned=[]

    #---------------------------------------------------------------------------
    def set_initial_units(self):
        self.update_map_square_data()

        # determine what squares if any are at risk

        # determine a deployment strategy

        # initial deployment can be deployed on any owned grid ssuare
        # after that reinforcements show up at rail yards

        

    #---------------------------------------------------------------------------
    def update_map_square_data(self):
        # zero out everything
        self.squares_owned=[]
        self.squares_owned_at_risk=[]
        self.square_objectives=[]
        self.square_objectives_owned=[]
        self.square_objectives_not_owned=[]

        for map_square in self.strategic_map.map_squares:
            if self.faction==map_square.faction:
                self.squares_owned.append(map_square)
                if map_square.

                # check if it borders a enemy square 

