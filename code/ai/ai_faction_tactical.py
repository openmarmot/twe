
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : AI that controls all a factions squads on the tactical map 
'''


#import built in modules
import random
import copy 

#import custom packages
import engine.squad_builder
import engine.math_2d
import copy
from ai.ai_squad import AISquad
import engine.world_builder 

#global variables

class AIFactionTactical():
    def __init__(self,world,faction,allied_factions,hostile_factions,spawn_location,radio_frequency):


        # squads in the faction who are present on this map
        self.squads=[] 

        self.spawn_location=spawn_location

        # general map goal (attack/defend/scout ?)

        self.world=world

        # should be higher than think_rate to get an immediate think
        self.time_since_update=70

        # how often you the class thinks
        # want this to be a highish number to give squads time to make independent decisions
        # before they get re-tasked by faction_tactical
        self.think_rate=60

        # faction - german/soviet/american/civilian
        self.faction=faction

        # allied faction list [string,string]
        self.allied_factions=allied_factions

        # hostile faction list [string,string]
        self.hostile_factions=hostile_factions

        # radio frequency
        self.radio_frequency=radio_frequency

        # radio - needed to get and send radio transmissions
        self.radio=engine.world_builder.spawn_object(world,[0,0],'radio_feldfu_b',False)
        self.radio.ai.current_frequency=self.radio_frequency
        self.radio.ai.turn_power_on()
        # no need to radio.update at the moment.



        self.allied_humans=[]
        self.hostile_humans=[]
        self.allied_crewed_vehicles=[]


    #---------------------------------------------------------------------------
    def create_squads(self):
        '''sort a list of humans into squads and initialize them'''

        # create a list of squad objects
        squad_objects=[]
        for b in self.world.wo_objects:
            if b.world_builder_identity.startswith(self.faction):
                if b.is_human or b.is_vehicle:
                    squad_objects.append(b)

        # sort this into squad lists
        squad_lists=engine.squad_builder.create_squads(squad_objects)

        # create the squads
        for b in squad_lists:
            squad=AISquad(self.world)
            squad.faction=self.faction
            squad.faction_tactical=self
            for c in b:
                squad.add_to_squad(c)

            self.squads.append(squad)

        if False:
            for squad in self.squads:
                print('---------')
                print(', '.join(obj.world_builder_identity for obj in squad.members))
                print(', '.join(obj.world_builder_identity for obj in squad.vehicles))
                print('---------')

    #---------------------------------------------------------------------------
    def get_area_enemy_count(self,area):
        '''get a enemy count for a world_area'''
        if self.faction=='german':
            return area.soviet_count+area.american_count
        if self.faction=='soviet':
            return area.german_count+area.american_count
        if self.faction=='american':
            return area.german_count+area.soviet_count
        if self.faction=='civilian':
            return 0
        else:
            print('debug: ai_faction_tactical.get_area_enemy_count - faction not handled: ',self.faction)
            return 0

    #---------------------------------------------------------------------------
    def get_area_friendly_count(self,area):
        '''get a friendly count for a world_area'''
        if self.faction=='german':
            return area.german_count
        elif self.faction=='soviet':
            return area.soviet_count
        elif self.faction=='american':
            return area.american_count
        elif self.faction=='civilian':
            return 0
        else:
            print('debug: ai_faction_tactical.get_area_enemy_count - faction not handled: ',self.faction)

    #---------------------------------------------------------------------------
    def send_radio_comms_check(self):
        self.radio.ai.send_message('This is '+self.faction+' HQ. Sending a comms check')
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
    def start(self):
        '''do all ai_faction_tactical starting tasks needed after world creation'''
        print(f'faction start: {self.faction}')
        # create squads 
        self.create_squads()
        print(f'faction squads: {len(self.squads)}')
        # set squad and object starting positions
        self.set_starting_positions()

        # create initial tactical orders
        # note - this might have to wait -- squads will not have appointed squad leads yet

        # update human lists and give out tactical orders right away
        self.update_human_lists()
        self.tactical_order()

    #---------------------------------------------------------------------------
    def set_starting_positions(self):
        '''set the starting positions of the squads, squad members, and vehicles'''
        # reset spawn locations.
        # civilians have world_coords set when they are generated, but after that they should be reset
        if self.faction=='civilian':
            for b in self.squads:
                # civilians start all over, so just making sure they are idle right away
                b.destination=copy.copy(b.members[0].world_coords)
        else:
            squad_grid=engine.math_2d.get_grid_coords(self.spawn_location,150,len(self.squads))

            for b in self.squads:

                # initially set the squad destination to be th espawn location
                b.destination=squad_grid.pop()

                # set the member positions
                member_grid=engine.math_2d.get_grid_coords(b.destination,20,len(b.members))
                member_vehicle_assignments=[]
                for c in b.members:
                    c.world_coords=member_grid.pop()
                    member_vehicle_assignments.append(c)
                    # randomize position a bit
                    #engine.math_2d.randomize_position_and_rotation(c,170)

                # handle squad attached vehicles
                for vehicle in b.vehicles:
                    vehicle.world_coords=copy.copy(b.destination)
                    # set initial rotation
                    if self.faction=='german':
                        vehicle.rotation_angle=270
                    elif self.faction=='soviet':
                        vehicle.rotation_angle=90
                    
                    # assign vehicle crew
                    crew_count=len(vehicle.ai.vehicle_crew)
                    while len(member_vehicle_assignments)>0 and crew_count>0:
                        crew_count-=1
                        member_vehicle_assignments.pop().ai.switch_task_enter_vehicle(vehicle,vehicle.world_coords)

    #---------------------------------------------------------------------------
    def tactical_order(self):
        
        idle_squads=[] # these are squads that are near their current squad destination
        busy_squads=[]

        for b in self.squads:
            if len(b.members)>0:
                leader_dist=0
                squad_spread=0
                if b.squad_leader!=None:
                    leader_dist=engine.math_2d.get_distance(b.destination,b.squad_leader.world_coords)

                    # check spread
                    for member in b.members:
                        d=engine.math_2d.get_distance(b.squad_leader.world_coords,member.world_coords)
                        if d>squad_spread:
                            squad_spread=d
                    
                if squad_spread>1000:
                    # squads that are too spread shouldn't be considered busy because we can't get an accurate read on their position
                    # if this isn't here then squads can get stuck waiting for a seperated leader
                    idle_squads.append(b)
                else:
                    # this probably could be a ai_state check instead of a pure distance meansurement
                    if leader_dist<600:
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

            if most_troops!=None and least_troops!=None:
                # make a tactics decision !
                choice=random.randint(1,3)
                
                # overwhelming force !!
                if choice==1:
                    troop_count=0
                    for b in idle_squads:
                        b.destination=engine.math_2d.randomize_coordinates(most_troops.world_coords,200)
                        troop_count+=len(b.members)

                    # check if we have numerical superiority
                    if (self.get_area_friendly_count(most_troops)+troop_count)<self.get_area_enemy_count(most_troops):
                        # lets send in the busy squads as well. this is a dangerous decision.
                        for b in busy_squads:
                            b.destination=engine.math_2d.randomize_coordinates(most_troops.world_coords,200)
                
                # shore up the weakest area
                elif choice==2:
                    for b in idle_squads:
                        b.destination=engine.math_2d.randomize_coordinates(least_troops.world_coords,200)

                # do nothing
                elif choice==3:
                    pass
            else:
                # hmm something went wrong. just send idle troops everywhere!
                self.tactical_order_random_world_area(idle_squads)
        
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

            if most_enemies!=None and least_enemies!=None:
                # make a tactics decision !
                choice=random.randint(1,3)
                
                # overwhelm the weak area !!
                if choice==1:
                    troop_count=0
                    for b in idle_squads:
                        b.destination=engine.math_2d.randomize_coordinates(least_enemies.world_coords,200)
                        troop_count+=len(b.members)

                    # check if we have numerical superiority
                    if (self.get_area_friendly_count(least_enemies)+troop_count)<self.get_area_enemy_count(least_enemies):
                        # lets send in the busy squads as well. this is a dangerous decision.
                        for b in busy_squads:
                            b.destination=engine.math_2d.randomize_coordinates(least_enemies.world_coords,200)
                
                # smaller attack on the weak area
                elif choice==2:
                    for b in idle_squads:
                        b.destination=engine.math_2d.randomize_coordinates(least_enemies.world_coords,200)

                # do nothing
                elif choice==3:
                    pass
            else:
                # hmm something went wrong. just send idle troops everywhere!
                self.tactical_order_random_world_area(idle_squads)
        
        else:
            # no contested areas, no enemy held areas
            # just send the idle squads all over
            self.tactical_order_random_world_area(idle_squads)

    #---------------------------------------------------------------------------
    def tactical_order_random_world_area(self,squads):
        '''send the squads to a random world area'''
        for b in squads:
            b.destination=engine.math_2d.randomize_coordinates(random.choice(self.world.world_areas).world_coords,200)
    
    #---------------------------------------------------------------------------
    def update(self):
        time_passed=self.world.time_passed_seconds
        self.time_since_update+=time_passed

        # run the update for each squad
        for b in self.squads:
            b.update()

        if self.time_since_update>self.think_rate:
            self.time_since_update=0
            # randomize think_rate a bit 
            self.think_rate=random.randint(60,90)

            self.update_human_lists()

            # tactial order
            if len(self.squads)>0:
                self.tactical_order()

    #---------------------------------------------------------------------------
    def update_human_lists(self):
        '''updates lists of humans that ai_faction_tactical keeps'''
        self.allied_humans=[]
        self.hostile_humans=[]
        self.allied_crewed_vehicles=[]

        for b in self.world.wo_objects_human:
            if b.ai.squad!=None:
                if b.ai.squad.faction==self.faction or b.ai.squad.faction in self.allied_factions:
                    self.allied_humans.append(b)

                    # if they are in a vehicle add it to the list
                    if 'task_vehicle_crew' in b.ai.memory:
                        if b.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle not in self.allied_crewed_vehicles:
                            self.allied_crewed_vehicles.append(b.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle)
                else:
                    if b.ai.squad.faction in self.hostile_factions:
                        self.hostile_humans.append(b)
