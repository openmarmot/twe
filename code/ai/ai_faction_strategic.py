
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
import engine.log
from engine.map_object import MapObject

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
    def set_initial_units(self,squads):
        # get the most recent data 
        self.update_map_square_data()

        # initial deployment can be deployed on any owned grid ssuare
        # after that reinforcements show up at rail yards

        # just evenly spread everything for now
        while len(squads)>len(self.squares_owned):
            for b in self.squares_owned:
                b.map_objects+=engine.world_builder.get_squad_map_objects(squads.pop())

        # plop the rest of them out randomly
        while len(squads)>0:
            map=random.choice(self.squares_owned)
            map.map_objects+=engine.world_builder.get_squad_map_objects(squads.pop())


    #---------------------------------------------------------------------------
    def update_map_square_data(self):
        # zero out everything
        self.squares_owned=[]
        self.squares_owned_at_risk=[]
        self.square_objectives=[]
        self.square_objectives_owned=[]
        self.square_objectives_not_owned=[]

        for map_square in self.strategic_map.map_squares:
            if self.faction==map_square.map_control:
                self.squares_owned.append(map_square)
                if map_square.hostile_count>0:
                    self.squares_owned_at_risk.append(map_square)

            if map_square.rail_yard or map_square.airport or map_square.town:
                if self.faction==map_square.map_control:
                    self.square_objectives_owned.append(map_square)
                else:
                    self.square_objectives_not_owned.append(map_square)

                # check if it borders a enemy square 

