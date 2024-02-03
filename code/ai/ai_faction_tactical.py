
'''
module : ai_faction_tactical.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes : AI that controls all a factions squads on the tactical map 
'''


#import built in modules
import random
import copy 

#import custom packages
import engine.math_2d
import copy
from ai.ai_squad import AISquad

#global variables

class AIFactionTactical(object):
    def __init__(self,WORLD,FACTION):

        # squads waiting to enter the map
        self.squad_spawn_queue=[]

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

        # list of spawn point world_coords
        self.spawn_points=[]

    #---------------------------------------------------------------------------
    # spawns squads in the spawn queue
    def process_spawn_queue(self):
        for b in self.squad_spawn_queue:
            # get a random spawn point
            coords=self.spawn_points[random.randint(0,len(self.spawn_points)-1)]
            # add random offsets
            b.world_coords=[coords[0]+float(random.randint(-200,200)),coords[1]+float(random.randint(-200,200))]
            b.destination=[coords[0]+float(random.randint(-200,200)),coords[1]+float(random.randint(-200,200))]
            b.spawn_on_map()
            b.faction_tactical=self # give the squad a ref back to hq..
            self.squads.append(b)
        self.squad_spawn_queue.clear()

    
    #---------------------------------------------------------------------------
    def split_squad(self,members):
        '''removes members from their current squad and puts them in a new squad'''
        squad=AIS
        sdf

    #---------------------------------------------------------------------------
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
    
    #---------------------------------------------------------------------------
    def update(self):
        time_passed=self.world.graphic_engine.time_passed_seconds
        self.time_since_update+=time_passed

        # spawn any new squads
        if len(self.squad_spawn_queue)>0:
            self.process_spawn_queue()

        # run the update for each squad
        for b in self.squads:
            b.update()

        if self.time_since_update>self.think_rate:
            self.time_since_update=0
            if len(self.squads)>0:
                self.tactical_order()
