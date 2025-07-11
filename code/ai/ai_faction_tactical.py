
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
from engine.tactical_order import TacticalOrder
from engine.vehicle_order import VehicleOrder

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
        for b in self.world.grid_manager.get_objects_from_all_grid_squares(True,True):
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
            
            # set the initial squad leader
            if len(squad.members)>0:
                squad.squad_leader=squad.members[0]
            else:
                print(f'squad error. member count:{len(squad.members)}, vehicle count:{len(squad.vehicles)}')
                for v in squad.vehicles:
                    print(v.name)
                

            self.squads.append(squad)



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
        # create squads 
        self.create_squads()
        
        # create initial tactical orders
        self.set_initial_orders()
        
        # this should be done after initial orders so that any enter vehicle commands 
        # aren't overridden for commanders 
        # set squad and object starting positions
        self.set_starting_positions()

        # update human lists and give out tactical orders right away
        self.update_human_lists()

    #---------------------------------------------------------------------------
    def set_initial_orders(self):
        '''hand out the initial tactical orders to the squad leads'''
        for squad in self.squads:
            if squad.squad_leader:
                order=TacticalOrder()
                order.order_defend_area=True
                random_world_area=random.choice(self.world.world_areas)
                order.world_area=random_world_area
                order.world_coords=engine.math_2d.randomize_coordinates(random_world_area.world_coords,300)
                squad.squad_leader.ai.switch_task_squad_leader(order)

    #---------------------------------------------------------------------------
    def set_starting_positions(self):
        '''set the starting positions of the squads, squad members, and vehicles'''
        # reset spawn locations.
        # civilians have world_coords set when they are generated, but after that they should be reset
        if self.faction=='civilian':
            pass
        else:
            squad_grid=engine.math_2d.get_grid_coords(self.spawn_location,150,len(self.squads))

            for b in self.squads:

                # initially set the squad destination to be th espawn location
                squad_coords=squad_grid.pop()

                # set the member positions
                member_grid=engine.math_2d.get_grid_coords(squad_coords,20,len(b.members))
                member_vehicle_assignments=[]
                for c in b.members:
                    c.world_coords=member_grid.pop()
                    member_vehicle_assignments.append(c)
                    # randomize position a bit
                    #engine.math_2d.randomize_position_and_rotation(c,170)

                # - handle squad attached vehicles -
                    
                # set an initial vehicle order. after this vehicle orders will be 
                # created by ai_human dynamically based on what the ai is trying to do
                if b.squad_leader:
                    vehicle_order=VehicleOrder()
                    vehicle_order.order_drive_to_coords=True
                    vehicle_order.world_coords=b.squad_leader.ai.memory['task_squad_leader']['orders'][0].world_coords
                else:
                    vehicle_order=None

                for vehicle in b.vehicles:
                    vehicle.world_coords=squad_coords
                    # set initial rotation
                    if self.faction=='german':
                        vehicle.rotation_angle=270
                    elif self.faction=='soviet':
                        vehicle.rotation_angle=90
                    
                    # assign vehicle crew
                    crew_count=len(vehicle.ai.vehicle_crew)
                    while len(member_vehicle_assignments)>0 and crew_count>0:
                        crew_count-=1
                        member_vehicle_assignments.pop().ai.switch_task_enter_vehicle(vehicle,vehicle_order)

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


    #---------------------------------------------------------------------------
    def update_human_lists(self):
        '''updates lists of humans that ai_faction_tactical keeps'''
        self.allied_humans=[]
        self.hostile_humans=[]
        self.allied_crewed_vehicles=[]

        for b in self.world.grid_manager.get_objects_from_all_grid_squares(True,False):
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
