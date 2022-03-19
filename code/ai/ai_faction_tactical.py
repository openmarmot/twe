
'''
module : ai_faction_tactical.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes : AI that controls all a factions squads on the tactical map 
'''


#import built in modules
import random 

#import custom packages
import engine.math_2d
import copy

# module specific variables
module_version='0.0' #module software version
module_last_update_date='June 02 2021' #date of last update


#global variables

class AIFactionTactical(object):
    def __init__(self,WORLD,FACTION):

        # squads in the faction who are present on this map
        self.squads=[] 

        # current ai state
        self.ai_state='none'

        # current ai goal
        self.ai_goal='none'

        # general map goal (attack/defend/scout ?)

        self.world=WORLD

        # should be higher than think_rate to get an immediate think
        self.time_since_update=70

        # how often you the class thinks
        # want this to be a highish number to give squads time to make independent decisions
        # before they get re-tasked by faction_tactical
        self.think_rate=60

        # faction - german/soviet/american/civilian
        self.faction=FACTION

        # world_coords of the spawn point for this faction
        # in the future should support multiple spawn points
        self.spawn_point=None

    # spawn all squads. used at the start of the game
    def spawn_all(self):
        self.spawn_squads(self.squads)

    # spawns a list of squads
    def spawn_squads(self,SQUADS):
        for b in SQUADS:
            b.world_coords=[self.spawn_point[0]+float(random.randint(-200,200)),self.spawn_point[1]+float(random.randint(-200,200))]
            b.destination=[self.spawn_point[0]+float(random.randint(-200,200)),self.spawn_point[1]+float(random.randint(-200,200))]
            
            b.spawn_on_map()

    def update(self):
        time_passed=self.world.graphic_engine.time_passed_seconds
        self.time_since_update+=time_passed
        # run the update for each squad
        for b in self.squads:
            b.update()

        if self.time_since_update>self.think_rate:
            self.time_since_update=0
            if len(self.squads)>0:
                self.tactical_order()

    def tactical_order(self):
        attack_queue=[] # areas that are owned by the enemy
        defend_queue=[] # areas that are neutral
        reinforce_queue=[] # areas that are contested

        # populate queues 
        for b in self.world.world_areas:
            if b.faction=='none':
                defend_queue.append(b)
            elif b.faction==self.faction:
                # we already have this one. not sure what to do here
                pass
            else :
                # i guess that means the owner isn't us 
                attack_queue.append(b)
            if b.is_contested:
                reinforce_queue.append(b)

        # hand out orders 
        assign_orders=True
        unassigned_squads=copy.copy(self.squads)

        while assign_orders:
            b=unassigned_squads.pop()

            # order of importance is reinforce, attack, defend 

            if len(reinforce_queue)>0:
                b.destination=reinforce_queue.pop().world_coords
            elif len(attack_queue)>0:
                b.destination=attack_queue.pop().world_coords
            elif len(defend_queue)>0:
                b.destination=defend_queue.pop().world_coords
            else :
                # seems like all the queues are empty
                # just send them somewhere random
                b.destination=self.world.world_areas[random.randint(0,len(self.world.world_areas)-1)].world_coords

            if len(unassigned_squads)<1:
                assign_orders=False
