'''
repo : https://github.com/openmarmot/twe

notes : vehicle commander code
'''

#import built in modules
import random
import copy

#import custom packages
import engine.math_2d
import engine.world_builder
import engine.log
from engine.vehicle_order import VehicleOrder
from engine.tactical_order import TacticalOrder

#import engine.global_exchange_rates

class AIHumanVehicleCommander():
    def __init__(self, owner):
        self.owner=owner

    #---------------------------------------------------------------------------
    def think(self):
        '''commander role'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        self.owner.ai.memory['task_vehicle_crew']['current_action']='Pondering'

        # determine what the primary weapon is and primary gunner is
        primary_gunner=None
        for role in vehicle.ai.vehicle_crew:
            if role.is_gunner and role.role_occupied:
                if role.turret:
                    if role.turret.ai.primary_turret:
                        if role.turret.ai.primary_weapon.ai.direct_fire:
                            primary_gunner=role
                            break

        # for now we have no actions if we don't have a primary gunner
        if primary_gunner is None:
            return

        max_threat_score = 0
        biggest_threat = None
        our_front_armor = vehicle.ai.vehicle_armor['front'][0]

        for v in self.owner.ai.vehicle_targets:
            armor = v.ai.vehicle_armor['front'][0]

            if len(v.ai.turrets) == 0:
                penetration = 0
            else:
                distance = engine.math_2d.get_distance(vehicle.world_coords, v.world_coords)
                penetration = v.ai.get_primary_gun_penetration(distance)

            # weight penetration more heavily - a vehicle with a big gun is more dangerous
            threat_score = armor + (penetration * 2)

            # filter vehicles that cannot penetrate our armor
            # if they have no penetration capability, only consider them if heavily armored
            # (armored vehicles without loaded guns are still potential threats)
            if penetration > 0 and penetration < our_front_armor:
                if armor < 30:
                    continue

            # minimum threshold to filter out soft-skinned vehicles with no guns
            if threat_score < 10:
                continue

            if threat_score > max_threat_score:
                max_threat_score = threat_score
                biggest_threat = v

        if biggest_threat:
            
            # check if we are already engaging the target
            if primary_gunner.human.ai.memory['task_vehicle_crew']['target'] != biggest_threat:

                engage_primary,engage_primary_reason=self.owner.ai.calculate_engagement(primary_gunner.turret.ai.primary_weapon,biggest_threat)
                if engage_primary and primary_gunner.human.ai.memory['task_vehicle_crew']['target']!=biggest_threat :
                    # tell the gunner to engage
                    primary_gunner.human.ai.memory['task_vehicle_crew']['target']=biggest_threat
                    self.owner.ai.speak(f'Gunner, prioritize the {biggest_threat.name} ')

            # check if we should re-orientate the vehicle to face the biggest threat
            # only do this for heavy armor vehicles
            if biggest_threat.ai.vehicle_armor['front'][0]>30:

                # first check if the turret has 360 degree rotation.
                # if it doesn't the vehicle will naturally orientate towards the vehicle
                if primary_gunner.turret.ai.rotation_range[1]==360:
                    rotation_required=engine.math_2d.get_rotation(vehicle.world_coords,biggest_threat.world_coords)
                    v=vehicle.rotation_angle
                    rotation_fuzzyness=5
                    # rotate if we are NOT currently roughly facing the target
                    if not (rotation_required>v-rotation_fuzzyness and rotation_required<v+rotation_fuzzyness):
                        # we will just save the angle and the driver will grab it
                        self.owner.ai.memory['task_vehicle_crew']['calculated_vehicle_angle']=rotation_required
                        self.owner.ai.memory['task_vehicle_crew']['current_action']='Waiting for driver to rotate the vehicle'
                        #engine.log.add_data('debug',f'commander {self.owner.name} decision: - rotate {vehicle.name} due to {biggest_threat.name}',True)

            # lets push out a rethink a bit so we aren't immediately changing the order
            self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(15,25)

            return
