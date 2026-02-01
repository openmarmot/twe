'''
repo : https://github.com/openmarmot/twe

notes : vehicle commander code
'''

#import built in modules
import random

import math

#import custom packages
import engine.math_2d
import engine.world_builder
import engine.log
from engine.vehicle_order import VehicleOrder
from engine.tactical_order import TacticalOrder
from engine.fire_mission import FireMission

#import engine.global_exchange_rates

class AIHumanVehicleCommander():
    '''vehicle commander role AI'''
    def __init__(self, owner):
        self.owner=owner

    #---------------------------------------------------------------------------
    def think(self):
        '''commander role'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        self.owner.ai.memory['task_vehicle_crew']['current_action']='Pondering'

        # determine what the primary weapon is and primary gunner is
        primary_gunner_role=None
        indirect_gunner_role=None
        for role in vehicle.ai.vehicle_crew:
            if role.is_gunner and role.role_occupied:
                if role.turret:
                    if role.turret.ai.primary_turret:
                        if role.turret.ai.primary_weapon.ai.direct_fire:
                            primary_gunner_role=role
                        if role.turret.ai.primary_weapon.ai.indirect_fire:
                            indirect_gunner_role=role

        if primary_gunner_role:
            self.think_primary_gunner_role(vehicle,primary_gunner_role)

        if indirect_gunner_role:
            self.think_indirect_gunner_role(vehicle,indirect_gunner_role)

    #---------------------------------------------------------------------------
    def get_indirect_fire_targets(self,vehicle,scan_radius=2000):
        '''get list of valid indirect fire targets sorted by density'''
        valid_targets = []
        nearby_targets = []

        # scan for valid targets within radius
        for target in self.owner.ai.human_targets:
            distance = engine.math_2d.get_distance(vehicle.world_coords, target.world_coords)
            if distance <= scan_radius:
                # prioritize humans that are far away
                if distance > 1000:
                    valid_targets.append(target)
                else:
                    nearby_targets.append(target)

        for target in self.owner.ai.vehicle_targets:
            # check if vehicle is valid (has crew and not disabled)
            if target.ai.check_if_vehicle_is_occupied() and not target.ai.vehicle_disabled:
                distance = engine.math_2d.get_distance(vehicle.world_coords, target.world_coords)
                if distance <= scan_radius:
                    # only target light vehicles with weak top armor
                    top_armor = target.ai.passenger_compartment_armor['top'][0]
                    if top_armor < 10:
                        valid_targets.append(target)
                    else:
                        nearby_targets.append(target)

        # combine and sort by density (count in 500 unit clusters)
        # first pass: count densities in 500 unit buckets
        density_map = {}
        all_targets = valid_targets + nearby_targets

        for target in all_targets:
            key = (int(target.world_coords[0] // 500), int(target.world_coords[1] // 500))
            if key not in density_map:
                density_map[key] = 0
            density_map[key] += 1

        # second pass: sort by density (highest first), then by distance (closest first)
        targets_with_score = []
        for target in all_targets:
            key = (int(target.world_coords[0] // 500), int(target.world_coords[1] // 500))
            distance = engine.math_2d.get_distance(vehicle.world_coords, target.world_coords)
            density = density_map.get(key, 1)
            score = density * 1000 - distance
            targets_with_score.append((score, target))

        # sort descending by score
        targets_with_score.sort(reverse=True)

        # extract sorted targets
        return [target for score, target in targets_with_score]

    #---------------------------------------------------------------------------
    def calculate_indirect_target_coords(self,target,scatter_radius=500):
        '''add random scatter to target coordinates for indirect fire'''
        distance = engine.math_2d.get_distance(target.world_coords, [0,0])

        # create random offset within scatter radius
        angle = random.uniform(0, 2 * math.pi)
        offset = random.uniform(0, scatter_radius)

        offset_x = offset * math.cos(angle)
        offset_y = offset * math.sin(angle)

        # calculate center of mass of cluster to prioritize
        cluster_count = 1
        for other_target in self.owner.ai.human_targets:
            if other_target.ai.blood_pressure >= 1 and other_target != target:
                dist = engine.math_2d.get_distance(target.world_coords, other_target.world_coords)
                if dist < 1000:
                    cluster_count += 1

        # more scatter for larger clusters (more realistic for area fire)
        adjusted_scatter = scatter_radius * (0.5 + cluster_count * 0.2)
        offset = random.uniform(0, adjusted_scatter)
        offset_x = offset * math.cos(angle)
        offset_y = offset * math.sin(angle)

        target_coords = [
            target.world_coords[0] + offset_x,
            target.world_coords[1] + offset_y
        ]

        return target_coords

    #---------------------------------------------------------------------------
    def calculate_mission_ttl(self,target):
        '''calculate mission expiration time based on target movement'''
        # random base TTL: 30-180 seconds
        base_ttl = random.uniform(30, 180)

        # reduce TTL if target is moving
        if target.is_vehicle and target.ai.current_speed > 0:
            ttl_multiplier = 0.5
            ttl_adjustment = random.uniform(-30, 0)
            ttl = base_ttl * ttl_multiplier + ttl_adjustment
        elif target.is_human and target.ai.in_vehicle():
            vehicle=target.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
            if vehicle.ai.current_speed>0:
                ttl_multiplier = 0.7
                ttl_adjustment = random.uniform(-20, 0)
                ttl = base_ttl * ttl_multiplier + ttl_adjustment
            else:
                ttl = base_ttl + random.uniform(-30, 0)
        else:
            ttl = base_ttl

        # clamp TTL between 15 and 300 seconds
        ttl = max(15, min(300, ttl))

        return self.owner.world.world_seconds + ttl

    #---------------------------------------------------------------------------
    def think_indirect_gunner_role(self,vehicle,indirect_gunner_role):
        '''think of commander actions related to indirect gunner role'''

        # check if fire_missions list exists in memory
        if 'fire_missions' not in indirect_gunner_role.human.ai.memory['task_vehicle_crew']:
            indirect_gunner_role.human.ai.memory['task_vehicle_crew']['fire_missions'] = []

        # always check existing fire mission for validity
        fire_missions = indirect_gunner_role.human.ai.memory['task_vehicle_crew']['fire_missions']

        if fire_missions:
            fire_mission = fire_missions[0]

            # check if mission is complete
            if fire_mission.rounds_fired > fire_mission.rounds_requested:
                fire_missions.pop(0)
                return

            # check if mission is expired
            if self.owner.world.world_seconds > fire_mission.expiration_time:
                fire_missions.pop(0)
                return

            # check if target is still valid (alive)
            if fire_mission.target_obj is not None:
                if fire_mission.target_obj.ai.blood_pressure < 1:
                    fire_missions.pop(0)
                    return

                if fire_mission.target_obj.is_vehicle:
                    if not fire_mission.target_obj.ai.check_if_vehicle_is_occupied():
                        fire_missions.pop(0)
                        return

                # check if target moved beyond acceptable distance
                old_dist = engine.math_2d.get_distance(fire_mission.world_coords,
                                                       fire_mission.target_obj.world_coords)
                if old_dist > 1500:
                    fire_missions.pop(0)
                    return

        # mission is invalid or doesn't exist: find new targets
        valid_targets = self.get_indirect_fire_targets(vehicle)

        if not valid_targets:
            return  # no valid targets found

        # select best target by density (first in sorted list)
        best_target = valid_targets[0]

        # calculate target coordinates with scatter
        target_coords = self.calculate_indirect_target_coords(best_target)

        # calculate TTL
        ttl = self.calculate_mission_ttl(best_target)

        # create new FireMission
        new_mission = FireMission(target_coords, ttl, best_target)

        # add to gunner's fire_missions list
        fire_missions.append(new_mission)

        # optional speech
        if random.randint(0, 10) == 0:
            self.owner.ai.speak('Gunner, fire mission assigned to ')

    #---------------------------------------------------------------------------
    def think_primary_gunner_role(self,vehicle,primary_gunner_role):
        '''think of commander actions related to primary_gunner_role'''
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
            if primary_gunner_role.human.ai.memory['task_vehicle_crew']['target'] != biggest_threat:

                engage_primary,engage_primary_reason=self.owner.ai.calculate_engagement(
                    primary_gunner_role.turret.ai.primary_weapon,biggest_threat)
                if engage_primary and primary_gunner_role.human.ai.memory['task_vehicle_crew']['target'] != biggest_threat:
                    # tell the gunner to engage
                    primary_gunner_role.human.ai.memory['task_vehicle_crew']['target']=biggest_threat
                    self.owner.ai.speak(f'Gunner, prioritize the {biggest_threat.name} ')

            # check if we should re-orientate the vehicle to face the biggest threat
            # only do this for heavy armor vehicles
            if biggest_threat.ai.vehicle_armor['front'][0]>30:

                # first check if the turret has 360 degree rotation.
                # if it doesn't the vehicle will naturally orientate towards the vehicle
                if primary_gunner_role.turret.ai.rotation_range[1]==360:
                    rotation_required=engine.math_2d.get_rotation(vehicle.world_coords,biggest_threat.world_coords)
                    v=vehicle.rotation_angle
                    rotation_fuzzyness=5
                    # rotate if we are NOT currently roughly facing the target
                    if rotation_required > v - rotation_fuzzyness or rotation_required < v + rotation_fuzzyness:
                        # we will just save the angle and the driver will grab it
                        self.owner.ai.memory['task_vehicle_crew']['calculated_vehicle_angle']=rotation_required
                        self.owner.ai.memory['task_vehicle_crew']['current_action']='Waiting for driver to rotate the vehicle'
                        #engine.log.add_data('debug',f'commander {self.owner.name} decision: - rotate {vehicle.name} due to {biggest_threat.name}',True)

            # lets push out a rethink a bit so we aren't immediately changing the order
            self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(15,25)

            return
