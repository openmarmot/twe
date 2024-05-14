
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
import engine.math_2d

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
    def get_area_enemy_count(self,area):
        '''get a enemy count for a world_area'''
        if self.faction=='german':
            return area.soviet_count+area.american_count
        elif self.faction=='soviet':
            return area.german_count+area.american_count
        elif self.faction=='american':
            return area.german_count+area.soviet_count
        else:
            print('debug: ai_faction_tactical.get_area_enemy_count - faction not handled: ',self.faction)

    #---------------------------------------------------------------------------
    def get_area_friendly_count(self,area):
        '''get a friendly count for a world_area'''
        if self.faction=='german':
            return area.german_count
        elif self.faction=='soviet':
            return area.soviet_count
        elif self.faction=='american':
            return area.american_count
        else:
            print('debug: ai_faction_tactical.get_area_enemy_count - faction not handled: ',self.faction)

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

            # add to the list of squads we are keeping track of
            self.squads.append(squad)
        else:
            print('debug : attempt to split a squad with zero new members')

    #---------------------------------------------------------------------------
    def tactical_order(self):

        idle_squads=[] # these are squads that are near their current squad destination
        busy_squads=[]

        for b in self.squads:
            if len(b.members)>0:
                if b.squad_leader!=None:
                    d=engine.math_2d.get_distance(b.destination,b.squad_leader.world_coords)
                    
                    # this probably could be a ai_state check instead of a pure distance meansurement
                    if d<600:
                        idle_squads.append(b)
                    else:
                        busy_squads.append(b)

        contested_areas=[]
        enemy_areas=[]
        empty_areas=[]
        controlled_areas=[]

        # categorize zones
        for b in self.world.world_areas:
            if b.is_contested:
                contested_areas.append(b)
            elif b.faction=='none':
                empty_areas.append(b)
            elif b.faction==self.faction:
                controlled_areas.append(b)
            else :
                # only option left is enemy controlled
                enemy_areas.append(b)

        # contested zones are top priority
        if len(contested_areas)>0:

            most_troops=None
            troops=0
            for b in contested_areas:
                count=self.get_area_friendly_count(b)
                if count>troops:
                    most_troops=b
                    troops=count
            least_troops=most_troops
            for b in contested_areas:
                count=self.get_area_friendly_count(b)
                if count<troops:
                    least_troops=b
                    troops=count  

            # make a tactics decision !
            choice=random.randint(1,3)
            
            # overwhelming force !!
            if choice==1:
                troop_count=0
                for b in idle_squads:
                    b.destination=most_troops.world_coords
                    troop_count+=len(b.members)

                # check if we have numerical superiority
                if (self.get_area_friendly_count(most_troops)+troop_count)<self.get_area_enemy_count(most_troops):
                    # lets send in the busy squads as well. this is a dangerous decision.
                    for b in busy_squads:
                        b.destination=most_troops.world_coords
            
            # shore up the weakest area
            elif choice==2:
                for b in idle_squads:
                    b.destination=least_troops.world_coords

            # do nothing
            elif choice==3:
                pass
        
        elif len(enemy_areas)>0:
            most_enemies=None
            troops=0
            for b in enemy_areas:
                count=self.get_area_enemy_count(b)
                if count>troops:
                    most_enemies=b
                    troops=count
            least_enemies=most_enemies
            for b in enemy_areas:
                count=self.get_area_enemy_count(b)
                if count<troops:
                    least_enemies=b
                    troops=count  

            # make a tactics decision !
            choice=random.randint(1,3)
            
            # overwhelm the weak area !!
            if choice==1:
                troop_count=0
                for b in idle_squads:
                    b.destination=least_enemies.world_coords
                    troop_count+=len(b.members)

                # check if we have numerical superiority
                if (self.get_area_friendly_count(least_enemies)+troop_count)<self.get_area_enemy_count(least_enemies):
                    # lets send in the busy squads as well. this is a dangerous decision.
                    for b in busy_squads:
                        b.destination=least_enemies.world_coords
            
            # smaller attach on the weak area
            elif choice==2:
                for b in idle_squads:
                    b.destination=least_enemies.world_coords

            # do nothing
            elif choice==3:
                pass
        
        else:
            # no contested areas, no enemy held areas

            # just send the idle squads all over

            for b in self.world.world_areas:
                if len(idle_squads)>0:
                    idle_squads.pop().destination=b.world_coords

    
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
            if self.faction=='civilian':
                #not sure if civilians will eventually have tactical orders or not
                pass
            else:
                if len(self.squads)>0:
                    self.tactical_order()
