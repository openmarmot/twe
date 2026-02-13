
'''
repo : https://github.com/openmarmot/twe

notes : AI that controls all a factions squads on the tactical map 
'''


#import built in modules
import random
import copy 
from itertools import cycle

#import custom packages
import engine.squad_builder
import engine.math_2d
from ai.ai_squad import AISquad
import engine.world_builder
from engine.tactical_order import TacticalOrder
from engine.vehicle_order import VehicleOrder
from engine.fire_mission import FireMission

#global variables

class AIFactionTactical():
    def __init__(self,world,faction,allied_factions,hostile_factions,radio_frequency):


        # squads in the faction who are present on this map
        self.squads=[] 

        self.spawn_location=[0,0]

        # general map goal (attack/defend/scout ?)

        self.world=world

        # should be higher than think_rate to get an immediate think
        self.time_since_update=70

        # how often you the class thinks
        # before they get re-tasked by faction_tactical
        self.think_rate=3

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

        self.initial_fire_missions=0
        self.indirect_fire_vehicles=[]

        self.allied_humans=[]
        self.hostile_humans=[]
        self.allied_crewed_vehicles=[]

        # world areas under control at the start of the scenario
        self.initial_controlled_world_areas=[]

    #---------------------------------------------------------------------------
    def assign_initial_fire_missions(self):
        '''assign initial fire missons'''

        # this is kind of awful but we don't really have a better way of assigning these 
        # as we don't know who ends up being a indirect gunner

        hostile_world_areas=[]
        for b in self.world.world_areas:
            if self.faction=='german':
                if b.faction=='soviet':
                    hostile_world_areas.append(b)
            elif self.faction=='soviet':
                if b.faction=='german':
                    hostile_world_areas.append(b)

        if hostile_world_areas:
            for v in self.indirect_fire_vehicles:
                for role in v.ai.vehicle_crew:
                    if role.role_occupied and role.is_gunner:
                        if role.turret.ai.primary_weapon.ai.indirect_fire:
                            # random for now
                            random_world_area=random.choice(hostile_world_areas)
                            for _ in range(3):
                                f=FireMission(random_world_area.get_location(),self.world.world_seconds+300,None)
                                f.rounds_requested=5
                                role.human.ai.memory['task_vehicle_crew']['fire_missions'].append(f)
                            self.initial_fire_missions-=1

        if self.initial_fire_missions<1:
            # reset think rate to normal
            self.think_rate=30

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
        squad_number=0
        for b in squad_lists:
            squad=AISquad(self.world)
            squad.faction=self.faction
            squad.faction_tactical=self
            squad.name=f"squad{squad_number}"
            squad_number+=1
            for c in b:
                squad.add_to_squad(c)
            
            # set the initial squad leader
            if len(squad.members)>0:
                squad.squad_leader=squad.members[0]
            else:
                # some squads end up vehicle only due to the current squad creation algo.
                #print(f'squad error. member count:{len(squad.members)}, vehicle count:{len(squad.vehicles)}')

                # set the spawn location so the vehicles end up in the right area
                self.set_squad_starting_position(squad,self.spawn_location)

                # lets just skip adding those squads to ai tactical so the squad isn't saved
                # they will just be extra vehicles that the ai can use if it wants
                continue
                
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
            print('debug: ai_faction_tactical.get_area_friendly_count - faction not handled: ',self.faction)

    #---------------------------------------------------------------------------
    def identify_indirect_fire_vehicles(self):
        '''identify friendly vehicles with indirect fire weapons'''
        self.indirect_fire_vehicles=[]
        self.initial_fire_missions=0

        for squad in self.squads:
            # compiles list of indirect fire vehicles
            for v in squad.vehicles:
                for t in v.ai.turrets:
                    if t.ai.primary_weapon.ai.indirect_fire:
                        self.indirect_fire_vehicles.append(v)
                        self.initial_fire_missions+=1
                        break


            # we want to think more often if we have fire missions that we can hand out
            if self.initial_fire_missions>0:
                self.think_rate=3
            else:
                self.think_rate=30

    #---------------------------------------------------------------------------
    def process_radio_messages(self):
        '''Process incoming radio messages from HQ'''

        for message in self.radio.ai.receive_queue:
            if message.startswith('HQ'):
                message=message.split(',')
                self.radio.ai.send_message(f"{message[1]},HQ,Message Received, ")

        # clear queue
        self.radio.ai.receive_queue=[]

    #---------------------------------------------------------------------------
    def send_radio_comms_check(self):
        '''Send comms check message to HQ'''

        self.radio.ai.send_message('HQ,ALL,Sending a comms check, ')

    #---------------------------------------------------------------------------
    def set_initial_orders_and_positions(self):
        '''hand out the initial tactical orders to the squad leads'''

        # Configuration
        min_squads_per_area=2
        max_squads_per_area=5

        # Sort all squads by type first
        motorized_squads=[s for s in self.squads if len(s.vehicles)>0]
        foot_squads=[s for s in self.squads if len(s.vehicles)==0]
        random.shuffle(motorized_squads)
        random.shuffle(foot_squads)

        # --- Handle initial controlled world areas (defending in place) ---
        if self.initial_controlled_world_areas:
            areas=copy.copy(self.initial_controlled_world_areas)
            random.shuffle(areas)

            for area in areas:
                # Assign 1 motorized squad if available
                if motorized_squads:
                    squad=motorized_squads.pop(0)
                    location=area.get_location()
                    threat_direction=self.get_threat_direction(location)
                    self.set_squad_defend_order(squad,area,location,threat_direction)
                    self.set_squad_starting_position(squad,location,threat_direction)

                # Assign 1 foot squad if available
                if foot_squads:
                    squad=foot_squads.pop(0)
                    location=area.get_location()
                    threat_direction=self.get_threat_direction(location)
                    self.set_squad_defend_order(squad,area,location,threat_direction)
                    self.set_squad_starting_position(squad,location,threat_direction)

        # --- Handle remaining squads (spawn at spawn_location, travel to area) ---
        remaining_squads=motorized_squads+foot_squads
        if remaining_squads:
            # Re-separate for grouped assignment
            motorized_squads=[s for s in remaining_squads if len(s.vehicles)>0]
            foot_squads=[s for s in remaining_squads if len(s.vehicles)==0]

            # Setup spawn grid
            squad_spacing=250
            squad_grid=engine.math_2d.get_grid_coords(
                self.spawn_location,squad_spacing,len(remaining_squads))

            # Area setup
            areas=self.world.world_areas[:]
            random.shuffle(areas)
            area_assignments={area:[] for area in areas}

            # Phase 1: Assign same-type squads to each area (up to min_squads_per_area)
            for area in areas:
                for squad_list in [motorized_squads,foot_squads]:
                    if len(area_assignments[area])>=min_squads_per_area:
                        break
                    while squad_list and len(area_assignments[area])<min_squads_per_area:
                        area_assignments[area].append(squad_list.pop(0))

            # Phase 2: Distribute overflow up to max_squads_per_area
            overflow=motorized_squads+foot_squads
            if overflow:
                area_cycle=cycle(areas)
                while overflow:
                    area=next(area_cycle)
                    if len(area_assignments[area])<max_squads_per_area:
                        area_assignments[area].append(overflow.pop(0))
                    elif all(len(area_assignments[a])>=max_squads_per_area for a in areas):
                        # All areas at max - just assign to random (no hard limit)
                        area_assignments[random.choice(areas)].append(overflow.pop(0))

            # Issue orders and set positions
            for world_area,squads in area_assignments.items():
                for squad in squads:
                    spawn_location=squad_grid.pop()
                    destination=world_area.get_location()
                    threat_direction=self.get_threat_direction(destination)
                    self.set_squad_defend_order(squad,world_area,destination,threat_direction)
                    self.set_squad_starting_position(squad,spawn_location,threat_direction)

    #---------------------------------------------------------------------------
    def get_threat_direction(self,from_coords):
        '''calculate the direction enemies are expected to come from'''
        # returns rotation angle in degrees toward nearest hostile spawn
        enemy_spawn=None
        if self.faction=='german':
            if 'soviet' in self.world.tactical_ai:
                enemy_spawn=self.world.tactical_ai['soviet'].spawn_location
        elif self.faction=='soviet':
            if 'german' in self.world.tactical_ai:
                enemy_spawn=self.world.tactical_ai['german'].spawn_location
        
        if enemy_spawn:
            return engine.math_2d.get_rotation(from_coords,enemy_spawn)
        return None

    #---------------------------------------------------------------------------
    def set_squad_defend_order(self,squad,world_area,world_area_location,threat_direction=None):
        '''Set squad defend order to specified location'''

        if squad.squad_leader:
            order=TacticalOrder()
            order.order_defend_area=True
            order.world_area=world_area
            order.world_coords=world_area_location
            order.threat_direction=threat_direction
            squad.squad_leader.ai.switch_task_squad_leader(order)

    #---------------------------------------------------------------------------
    def set_squad_starting_position(self,squad,position,threat_direction=None):
        '''Set squad starting positions on the battlefield'''

        # set the member positions
        member_grid=engine.math_2d.get_grid_coords(position,20,len(squad.members))
        member_vehicle_assignments=[]
        for c in squad.members:
            c.world_coords=member_grid.pop()
            member_vehicle_assignments.append(c)
            # set infantry facing toward threat if known
            if threat_direction is not None:
                c.rotation_angle=threat_direction
                c.reset_image=True

        # - handle squad attached vehicles -
            
        # set an initial vehicle order. after this vehicle orders will be 
        # created by ai_human dynamically based on what the ai is trying to do
        vehicle_order=None
        if squad.squad_leader:
            if squad.squad_leader.ai.memory['task_squad_leader']['orders']:
                vehicle_order=VehicleOrder()
                vehicle_order.order_drive_to_coords=True
                vehicle_order.world_coords=squad.squad_leader.ai.memory['task_squad_leader']['orders'][0].world_coords

        for vehicle in squad.vehicles:
            vehicle.world_coords=position
            # set initial rotation toward threat direction if known
            if threat_direction is not None:
                vehicle.rotation_angle=threat_direction
                vehicle.reset_image=True
            elif self.faction=='german':
                vehicle.rotation_angle=270
            elif self.faction=='soviet':
                vehicle.rotation_angle=90
            
            # assign vehicle crew
            crew_count=len(vehicle.ai.vehicle_crew)
            while len(member_vehicle_assignments)>0 and crew_count>0:
                crew_count-=1
                member_vehicle_assignments.pop().ai.switch_task_enter_vehicle(vehicle,vehicle_order)  

    #---------------------------------------------------------------------------
    def split_squad(self,members):
        '''removes members from their current squad and puts them in a new squad'''
        if len(members)>0:

            # members - list of humans that you want to put in a new squad. 
            squad=AISquad(self.world)
            squad.faction=self.faction
            squad.faction_tactical=self
            squad_number = len(self.squads) 
            squad.name = f"squad_split_{squad_number}" # for now just to keep track of these
            
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
        # controlled_world_areas : list of world_areas controlled by your team
        # create squads 
        self.create_squads()

        # tune radios to the correct channel
        self.tune_radios()
        
        # civilians get positions set by map gen 
        if self.faction != "civilian":
            # create initial tactical orders
            # also sets squad spawn positions
            self.set_initial_orders_and_positions()

            # build indirect fire data
            self.identify_indirect_fire_vehicles()

        # update human lists and give out tactical orders right away
        self.update_human_lists()       

    #---------------------------------------------------------------------------
    def tune_radios(self):
        '''tune any radios that squad members or squad vehicles have to the faction radio_frequency'''
        for squad in self.squads:
            # tune radios in squad members' inventories
            for member in squad.members:
                if member.ai.large_pickup is not None:
                    if member.ai.large_pickup.is_radio:
                        member.ai.large_pickup.ai.current_frequency = self.radio_frequency
            # tune radios in squad vehicles
            for vehicle in squad.vehicles:
                # check dedicated radio slot
                if vehicle.ai.radio is not None:
                    vehicle.ai.radio.ai.current_frequency = self.radio_frequency

    #---------------------------------------------------------------------------
    def update(self):
        '''Update tactical AI faction processing'''

        time_passed=self.world.time_passed_seconds
        self.time_since_update+=time_passed


        self.process_radio_messages()

        if self.time_since_update>self.think_rate:

            self.time_since_update=0
            # randomize think_rate a bit 
            #self.think_rate=random.randint(60,90)

            self.update_human_lists()

            if self.initial_fire_missions>0:
                self.assign_initial_fire_missions()


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
