
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
    def advance_turn(self):
        '''take a strategic map turn'''

        self.update_map_square_data()

        # buy units with income
        self.buy_and_place_units(100)
        

        # something else?

        # move existing units 
        if self.faction!='civilian':
            self.move_units()

    #---------------------------------------------------------------------------
    def buy_and_place_units(self,funds):
        '''buy and place units at the beginning of a turn'''

        squad_options=getattr(engine.world_builder,f"{self.faction}_squad_data")

        squad_names=list(squad_options.keys())

        if len(squad_names)>0:
            # just randomly grab some squads for now
            cost=0
            squads=[]
            while cost<funds:
                squad=random.choice(squad_names)
                cost+=squad_options[squad]['cost']
                squads.append(squad)

            # after the initial turn troops can only appear at a rail head
            rail_yards=[]
            for b in self.square_objectives_owned:
                if b.rail_yard:
                    rail_yards.append(b)

            if len(rail_yards)>0:
                # plop the rest of them out randomly
                while len(squads)>0:
                    map=random.choice(rail_yards)
                    map.map_objects+=engine.world_builder.get_squad_map_objects(squads.pop())
            else:
                # not sure what to do here yet. having no rail yards means the faction loses i guess
                engine.log.add_data('error','no rail yards for'+self.faction,True)
        else:
            # missing squad lists
            engine.log.add_data('warn','ai_faction_strategic.buy_and_place_units, faction '+self.faction+' has no squad data',True)




    #---------------------------------------------------------------------------
    def evaluate_neighbor(self,current_square, neighbor):
        '''evaluate a neighboring map square'''
        if neighbor is None:
            return -1, 0  # Can't move there

        # Troop counts on the neighbor square
        enemy_troop_count = (neighbor.german_count + neighbor.soviet_count + neighbor.american_count) - getattr(neighbor, f"{self.faction}_count")
        our_troop_count = getattr(neighbor, f"{self.faction}_count")
        moving_troops = getattr(current_square, f"{self.faction}_count")
        total_our_troops_after_moving = our_troop_count + moving_troops

        # Check for resources
        resource_present = neighbor.rail_yard or neighbor.airport or neighbor.town

        priority_score = 0
        moving_troops_needed = 0

        if resource_present:
            priority_score+=0.8
            if enemy_troop_count == 0 and our_troop_count == 0:
                # Priority 1: Unoccupied resource
                priority_score += 3
                moving_troops_needed = int(moving_troops*0.5)
            elif enemy_troop_count==0 and our_troop_count>0:
                priority_score+=0.5
                moving_troops_needed = int(moving_troops*0.5)

            else:
                # Troops needed to outnumber enemy troops
                required_troops_to_outnumber = enemy_troop_count - our_troop_count + 1
                if moving_troops + our_troop_count >= enemy_troop_count + 1:
                    # Priority 2: Outnumber enemy troops
                    moving_troops_needed = min(required_troops_to_outnumber, moving_troops)
                    priority_score += 2

        else:
            # Not a resource square
            priority_score = 0
            moving_troops_needed=int(moving_troops*.75)
            if enemy_troop_count>0 and moving_troops>enemy_troop_count:
                priority_score+=0.5

        # Avoid moving to squares where we would be outnumbered
        if total_our_troops_after_moving < enemy_troop_count:
            priority_score -= -1

        # Add bonus for preferred direction
        if self.faction == 'german' and neighbor == current_square.east:
            priority_score += 1.5
        if self.faction == 'soviet' and neighbor == current_square.west:
            priority_score += 1.5

        return priority_score, moving_troops_needed
    
    #---------------------------------------------------------------------------
    def move_units(self):
        movement_orders = []

        # figure out the best movements
        for square in self.squares_owned:

            faction_count = getattr(square, f"{self.faction}_count")
            if faction_count > 0:
                neighbors = {
                    'north': square.north,
                    'south': square.south,
                    'east': square.east,
                    'west': square.west
                }
                best_score = -1
                best_move = None
                moving_troops_needed = 0

                # Evaluate all neighbors
                for direction, neighbor in neighbors.items():
                    priority_score, troops_needed = self.evaluate_neighbor(square, neighbor)
                    if priority_score > best_score:
                        best_score = priority_score
                        best_move = neighbor
                        moving_troops_needed = troops_needed

                # Create movement order if a valid move is found
                if best_score > 0 and moving_troops_needed > 0:
                    movement_orders.append({
                        'from': square,
                        'to': best_move,
                        'troops': moving_troops_needed
                    })
                    # Update the current square's troop count
                    setattr(square, f"{self.faction}_count", faction_count - moving_troops_needed)

        # Apply movement orders
        for order in movement_orders:
            from_square = order['from']
            to_square = order['to']
            troops_needed = order['troops']

            # get the troops
            troops_to_move=[]
            for b in from_square.map_objects:
                if b.world_builder_identity.startswith(self.faction) and len(troops_to_move)<troops_needed:
                    troops_to_move.append(b)

            # move the troops
            for b in troops_to_move:
                to_square.map_objects.append(b)
                from_square.map_objects.remove(b)


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

