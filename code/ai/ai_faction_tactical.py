
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
        # format for this is [[spawn_coordinates,squad]]
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

    #---------------------------------------------------------------------------
    # spawns squads in the spawn queue
    def process_spawn_queue(self):
        # spawn queue is a array of arrays [[spawn_location,squad]]
        for b in self.squad_spawn_queue:
            coords=b[0]
            # add random offsets
            b[1].world_coords=[coords[0]+float(random.randint(-200,200)),coords[1]+float(random.randint(-200,200))]
            b[1].destination=[coords[0]+float(random.randint(-200,200)),coords[1]+float(random.randint(-200,200))]
            b[1].spawn_on_map()
            b[1].faction_tactical=self # give the squad a ref back to hq..
            self.squads.append(b[1])
        self.squad_spawn_queue.clear()
    
    #---------------------------------------------------------------------------
    def split_squad(self,members):
        '''removes members from their current squad and puts them in a new squad'''
        if len(members)>0:

            # members - list of humans that you want to put in a new squad. 
            squad=AISquad(self.world)
            squad.faction=self.faction
            squad.faction_tactical=self
            
            for b in members:
                # note! this will remove the members from their old squad if they had one
                squad.add_to_squad(b)

            # run a think cycle to set squad variables correctly
            squad.handle_ai_think()

            # add to the list of squads we are keeping track of
            self.squads.append(squad)
        else:
            print('debug : attempt to split a squad with zero new members')

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
        unassigned_squads=[]

        # only count the squads that have members
        # note that squads that have all memberes dead/gone don't get deleted at the moment
        for b in self.squads:
            if len(b.members)>0:
                unassigned_squads.append(b)
        
        for b in unassigned_squads:
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
