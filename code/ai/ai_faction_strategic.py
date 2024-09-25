
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
    def deploy_squad_to_map(self,squad_name,map_square):
        '''convert a squad to individual members and then add them to a map as a map_object'''
        members=[]
        if 'German' in squad_name:
            members=engine.world_builder.german_squad_data[squad_name]['members'].split(',')
        elif 'Soviet' in squad_name:
            members=engine.world_builder.soviet_squad_data[squad_name]['members'].split(',')
        else:
            engine.log.add_data('error','ai_faction_strategic.deploy_squad_to_map squad_name '+squad_name+' not recognized',True)

        # convert each member to a map_object and add to map
        for b in members:
            map_square.map_objects.append(MapObject(b,'none',[0,0],0,[]))
        

    #---------------------------------------------------------------------------
    def set_initial_units(self,squads):
        # get the most recent data 
        self.update_map_square_data()

        # initial deployment can be deployed on any owned grid ssuare
        # after that reinforcements show up at rail yards

        # just evenly spread everything for now
        while len(squads)>len(self.squares_owned):
            for b in self.squares_owned:
                self.deploy_squad_to_map(squads.pop(),b)

        # plop the rest of them out randomly
        while len(squads)>0:
            self.deploy_squad_to_map(squads.pop(),random.choice(self.squares_owned))

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
                if map_square.hostile_count>0:
                    self.squares_owned_at_risk.append(map_square)

            if map_square.rail_yard or map_square.airport or map_square.town:
                if self.faction==map_square.faction:
                    self.square_objectives_owned.append(map_square)
                else:
                    self.square_objectives_not_owned.append(map_square)

                # check if it borders a enemy square 

