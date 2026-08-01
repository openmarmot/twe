"""
repo : https://github.com/openmarmot/twe

notes : vehicle commander code
"""

# import built in modules
import random
from ai.ai_human_vehicle_crew_action import VehicleCrewAction

import math

# import custom packages
import engine.math_2d
import engine.log
import engine.penetration_calculator
from engine.vehicle_order import VehicleOrder
from engine.tactical_order import TacticalOrder
from engine.fire_mission import FireMission

# import engine.global_exchange_rates


class AIHumanVehicleCommander:
    """vehicle commander role AI"""

    def __init__(self, owner):
        self.owner = owner

    # ---------------------------------------------------------------------------
    def think(self):
        """commander role"""
        vehicle_role = self.owner.ai.memory["task_vehicle_crew"]["vehicle_role"]
        vehicle = vehicle_role.vehicle
        # dual-role commander/gunner shares task_vehicle_crew memory with gunner code.
        # never reset current_action in that case - it would clobber ENGAGING / reload / etc.
        dual_role_gunner = vehicle_role.is_gunner
        if not dual_role_gunner:
            self.owner.ai.memory["task_vehicle_crew"]["current_action"] = (
                VehicleCrewAction.MONITORING
            )

        # determine what the primary weapon is and primary gunner is
        primary_gunner_role = None
        indirect_gunner_role = None
        for role in vehicle.ai.vehicle_crew:
            if role.is_gunner and role.role_occupied:
                if role.turret:
                    if role.turret.ai.primary_turret:
                        if role.turret.ai.primary_weapon.ai.direct_fire:
                            primary_gunner_role = role
                        if role.turret.ai.primary_weapon.ai.indirect_fire:
                            indirect_gunner_role = role

        # self-preservation check - runs before any gunner-directed movement or fire mission logic.
        # If we ordered a retreat, skip the gunner role handlers so they don't immediately
        # countermand it by requesting new fire missions or positioning moves.
        if self.think_vehicle_position(vehicle):
            return

        if primary_gunner_role:
            self.think_primary_gunner_role(vehicle, primary_gunner_role)

        if indirect_gunner_role:
            self.think_indirect_gunner_role(vehicle, indirect_gunner_role)

    # ---------------------------------------------------------------------------
    def get_indirect_fire_targets(self, vehicle):
        """get best indirect fire target - trusts evaluate_targets for filtering, vehicles first"""
        vehicle_coords = vehicle.world_coords

        # VEHICLE PRIORITY: process vehicles first to avoid redundant human distance checks
        valid_targets = []

        for target in self.owner.ai.vehicle_targets:
            # evaluate_targets already filtered (alive, hostile, visible)
            # commander adds own filter for vehicle status + armor

            if not target.ai.vehicle_disabled:
                top_armor = target.ai.passenger_compartment_armor["top"][0]
                if top_armor < 10:
                    if target.ai.check_if_vehicle_is_occupied():
                        distance = engine.math_2d.get_distance(
                            vehicle_coords, target.world_coords
                        )
                        if distance > 1000:
                            valid_targets.append({"obj": target, "distance": distance})

        # VEHICLE CHECK: return if we have valid vehicles
        if valid_targets:
            if len(valid_targets) < 5:
                valid_targets.sort(key=lambda t: t["distance"])
                return [t["obj"] for t in valid_targets[:1]]

            # Find best vehicle (closest)
            best_vehicle = min(valid_targets, key=lambda t: t["distance"])
            return [best_vehicle["obj"]]

        # FALLBACK: HUMAN PRIORITY (only if no good vehicles)
        for target in self.owner.ai.human_targets:
            # evaluate_targets already filtered (alive, hostile, visible)
            # commander only filters by distance > 1000 for priority
            distance = engine.math_2d.get_distance(vehicle_coords, target.world_coords)
            if distance > 1000:
                valid_targets.append({"obj": target, "distance": distance})

        # HUMAN CLUSTERING: group by density
        if not valid_targets:
            return []

        # DENSITY MAP (500-unit buckets) - only for humans
        density_map = {}
        for human in valid_targets:
            key = (
                int(human["obj"].world_coords[0] // 500),
                int(human["obj"].world_coords[1] // 500),
            )
            density_map[key] = density_map.get(key, 0) + 1

        # find best cluster with most humans
        best_cluster_key = max(density_map.items(), key=lambda kv: kv[1])[0]

        # get humans in best cluster
        best_cluster_humans = [
            h
            for h in valid_targets
            if (
                int(h["obj"].world_coords[0] // 500),
                int(h["obj"].world_coords[1] // 500),
            )
            == best_cluster_key
        ]

        # sort cluster by distance
        best_cluster_humans.sort(key=lambda t: t["distance"])

        return [best_cluster_humans[0]["obj"]]

    # ---------------------------------------------------------------------------
    def calculate_indirect_target_coords(self, target, scatter_radius=500):
        """add random scatter to target coordinates for indirect fire"""
        # count humans in cluster (within 1000 units)
        cluster_count = 1
        for other_target in self.owner.ai.human_targets:
            if other_target.ai.blood_pressure >= 1 and other_target != target:
                dist = engine.math_2d.get_distance(
                    target.world_coords, other_target.world_coords
                )
                if dist < 1000:
                    cluster_count += 1

        # more scatter for larger clusters (more realistic for area fire)
        adjusted_scatter = scatter_radius * (0.5 + cluster_count * 0.2)
        angle = random.uniform(0, 2 * math.pi)
        offset = random.uniform(0, adjusted_scatter)
        offset_x = offset * math.cos(angle)
        offset_y = offset * math.sin(angle)

        target_coords = [
            target.world_coords[0] + offset_x,
            target.world_coords[1] + offset_y,
        ]

        return target_coords

    # ---------------------------------------------------------------------------
    def calculate_mission_ttl(self, target):
        """calculate mission expiration time based on target movement"""
        # random base TTL: 30-180 seconds
        base_ttl = random.uniform(30, 180)

        # reduce TTL if target is moving
        if target.is_vehicle and target.ai.current_speed > 0:
            ttl_multiplier = 0.5
            ttl_adjustment = random.uniform(-30, 0)
            ttl = base_ttl * ttl_multiplier + ttl_adjustment
        elif target.is_human and target.ai.in_vehicle():
            vehicle = target.ai.memory["task_vehicle_crew"]["vehicle_role"].vehicle
            if vehicle.ai.current_speed > 0:
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

    # ---------------------------------------------------------------------------
    def think_indirect_gunner_role(self, vehicle, indirect_gunner_role):
        """think of commander actions related to indirect gunner role"""

        # this seems pretty computation heavy. need to consider how often this is running

        # check if fire_missions list exists in memory
        if (
            "fire_missions"
            not in indirect_gunner_role.human.ai.memory["task_vehicle_crew"]
        ):
            indirect_gunner_role.human.ai.memory["task_vehicle_crew"][
                "fire_missions"
            ] = []

        # always check existing fire mission for validity
        fire_missions = indirect_gunner_role.human.ai.memory["task_vehicle_crew"][
            "fire_missions"
        ]

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
                if fire_mission.target_obj.is_human:
                    if fire_mission.target_obj.ai.blood_pressure < 1:
                        fire_missions.pop(0)
                        return

                if fire_mission.target_obj.is_vehicle:
                    if not fire_mission.target_obj.ai.check_if_vehicle_is_occupied():
                        fire_missions.pop(0)
                        return

                # check if target moved beyond acceptable distance
                if fire_mission.target_obj is not None:
                    old_dist = engine.math_2d.get_distance(
                        fire_mission.world_coords, fire_mission.target_obj.world_coords
                    )
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
            self.owner.ai.speak("Gunner, fire mission assigned to ")

    # ---------------------------------------------------------------------------
    def think_primary_gunner_role(self, vehicle, primary_gunner_role):
        """think of commander actions related to primary_gunner_role"""
        max_threat_score = 0
        biggest_threat = None
        our_front_armor = vehicle.ai.vehicle_armor["front"][0]

        for v in self.owner.ai.vehicle_targets:
            armor = v.ai.vehicle_armor["front"][0]

            if len(v.ai.turrets) == 0:
                penetration = 0
            else:
                distance = engine.math_2d.get_distance(
                    vehicle.world_coords, v.world_coords
                )
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
            gunner_mem = primary_gunner_role.human.ai.memory["task_vehicle_crew"]
            # dual-role: commander is also this gunner (T-34-76 etc). Shared memory means
            # hull-rotate WAITING_FOR_ROTATE and long think_interval would block shooting.
            is_dual_role = primary_gunner_role.human == self.owner

            # check if we are already engaging the target
            if gunner_mem["target"] != biggest_threat:
                engage_primary, engage_primary_reason = (
                    self.owner.ai.calculate_engagement(
                        primary_gunner_role.turret.ai.primary_weapon, biggest_threat
                    )
                )
                if engage_primary and gunner_mem["target"] != biggest_threat:
                    # tell the gunner to engage
                    gunner_mem["target"] = biggest_threat
                    if not is_dual_role:
                        self.owner.ai.speak(
                            f"Gunner, prioritize the {biggest_threat.name} "
                        )

            # hull reorientation for armor facing - dedicated commander only.
            # dual-role must keep gunner current_action / think_interval intact so the
            # 360 turret can engage immediately instead of parking in WAITING_FOR_ROTATE.
            # note - separate 360 gunners are not blocked by this; hull face still helps
            # (best armor + smaller silhouette) when the trade is one we can accept.
            if not is_dual_role:
                if biggest_threat.ai.vehicle_armor["front"][0] > 30:
                    # first check if the turret has 360 degree rotation.
                    # if it doesn't the vehicle will naturally orientate towards the vehicle
                    if primary_gunner_role.turret.ai.rotation_range[1] == 360:
                        # only hull-face when we can pen their front at current range.
                        # if we cannot, driver/gunner reposition for angle/range instead
                        # of sitting nose-on in a losing long-range trade.
                        hull_face = self.can_pen_target_front(
                            primary_gunner_role.turret.ai.primary_weapon,
                            vehicle,
                            biggest_threat,
                        )
                        if hull_face:
                            rotation_required = engine.math_2d.get_rotation(
                                vehicle.world_coords, biggest_threat.world_coords
                            )
                            v = vehicle.rotation_angle
                            rotation_fuzzyness = 5
                            # rotate if we are NOT currently roughly facing the target
                            current_angle = engine.math_2d.get_normalized_angle(v)
                            desired_angle = engine.math_2d.get_normalized_angle(
                                rotation_required
                            )
                            diff = (desired_angle - current_angle + 180) % 360 - 180
                            if abs(diff) > rotation_fuzzyness:
                                # we will just save the angle and the driver will grab it
                                self.owner.ai.memory["task_vehicle_crew"][
                                    "calculated_vehicle_angle"
                                ] = rotation_required
                                self.owner.ai.memory["task_vehicle_crew"][
                                    "current_action"
                                ] = VehicleCrewAction.WAITING_FOR_ROTATE

                # push rethink so we aren't immediately changing the order
                self.owner.ai.memory["task_vehicle_crew"]["think_interval"] = (
                    random.uniform(15, 25)
                )

            return

    # ---------------------------------------------------------------------------
    def can_pen_target_front(self, weapon, vehicle, target):
        """True if loaded AP would pen target front armor at current range (ideal hit)."""
        if weapon is None or weapon.ai.magazine is None:
            return False
        if len(weapon.ai.magazine.ai.projectiles) == 0:
            return False
        if not target.is_vehicle:
            return True

        distance = engine.math_2d.get_distance(
            vehicle.world_coords, target.world_coords
        )
        projectile = weapon.ai.magazine.ai.projectiles[0]
        penetration, _, _, _ = engine.penetration_calculator.calculate_penetration(
            projectile,
            distance,
            "steel",
            target.ai.passenger_compartment_armor["front"],
            "front",
            180,
        )
        return penetration

    # ---------------------------------------------------------------------------
    def think_vehicle_position(self, vehicle):
        """self-preservation: assess nearby threats using sorted target lists and order retreat to spawn if vehicle is too vulnerable.

        Returns True if a retreat order was issued (caller should skip the rest of commander think).
        Returns False if no action was taken.
        """
        # human_targets and vehicle_targets are already sorted closest-first by evaluate_targets
        human_targets = self.owner.ai.human_targets
        vehicle_targets = self.owner.ai.vehicle_targets

        if not human_targets and not vehicle_targets:
            return False

        # our vehicle characteristics for threat assessment
        front_armor = vehicle.ai.vehicle_armor.get("front", [0])[0] if hasattr(vehicle.ai, "vehicle_armor") else 0
        passenger_armor = getattr(vehicle.ai, "passenger_compartment_armor", {})
        top_armor = passenger_armor.get("top", [0])[0] if isinstance(passenger_armor, dict) else 0
        is_open_top = getattr(vehicle.ai, "open_top", False)

        # does this vehicle have any direct-fire main armament? (mortar carriers like 251/2 do not)
        has_direct_fire_armament = False
        for role in vehicle.ai.vehicle_crew:
            if role.is_gunner and role.role_occupied and role.turret and role.turret.ai.primary_weapon:
                if role.turret.ai.primary_weapon.ai.direct_fire:
                    has_direct_fire_armament = True
                    break

        # base vulnerability: soft skin, open top, or pure support vehicle (no way to fight back at close range)
        is_vulnerable = (front_armor < 25) or (top_armor < 10) or is_open_top or (not has_direct_fire_armament)

        if not is_vulnerable:
            # we have decent protection and/or direct fire - let primary gunner logic decide engagement
            return False

        # --- threat scoring (humans first per request, then first ~4 vehicles) ---
        threat_score = 0

        # human targets - very close infantry is lethal to open/soft vehicles even without penetration
        for target in human_targets[:3]:
            distance = engine.math_2d.get_distance(vehicle.world_coords, target.world_coords)
            if distance < 600:
                threat_score += 35
            elif distance < 1200:
                threat_score += 20
            elif distance < 1800:
                threat_score += 8

        # vehicle targets - first 4 closest (use similar penetration logic to think_primary_gunner_role)
        for target in vehicle_targets[:4]:
            distance = engine.math_2d.get_distance(vehicle.world_coords, target.world_coords)
            if distance > 2200:
                continue

            penetration = 0
            if len(getattr(target.ai, "turrets", [])) > 0:
                try:
                    penetration = target.ai.get_primary_gun_penetration(distance)
                except (AttributeError, TypeError, KeyError):
                    penetration = 0

            # high threat if they can hurt us or are dangerously close
            if penetration >= front_armor * 0.5 or distance < 900:
                threat_score += 28 if distance < 700 else 18
            elif penetration > 0:
                threat_score += 10
            elif distance < 1100:
                # even unpenning vehicles are dangerous if very close (ramming, MG, etc.)
                threat_score += 6

        if threat_score < 25:
            return False

        # morale check - low morale makes retreat much more likely
        flee_modifier = 0
        if self.owner.ai.morale_check() is False:
            flee_modifier = 25
        elif self.owner.ai.morale < 60:
            flee_modifier = 15

        effective_threat = threat_score + flee_modifier

        # final gate: only retreat on clearly high threat for this vulnerable vehicle
        if effective_threat < 40:
            return False

        # --- issue retreat order toward spawn with +/- 400 randomness ---
        spawn_location = self.owner.ai.squad.faction_tactical.spawn_location
        if spawn_location is None:
            return False

        retreat_coords = engine.math_2d.randomize_coordinates(spawn_location, 400)

        vehicle_order = VehicleOrder()
        vehicle_order.order_drive_to_coords = True
        vehicle_order.world_coords = retreat_coords
        # keep the crew in the vehicle on arrival (we are retreating to safety, not dropping off)
        vehicle_order.exit_vehicle_when_finished = False
        vehicle_order.is_retreat = True

        self.owner.ai.memory["task_vehicle_crew"]["vehicle_order"] = vehicle_order

        self.owner.ai.speak("Driver, fall back!")
        self.owner.ai.add_journal_entry(
            f"Retreating {vehicle.name} due to threat (score {int(effective_threat)})"
        )

        # cancel any active indirect fire missions so we stop trying to close for positioning
        for role in vehicle.ai.vehicle_crew:
            if role.role_occupied:
                vcrew_mem = role.human.ai.memory.get("task_vehicle_crew", {})
                if "fire_missions" in vcrew_mem:
                    vcrew_mem["fire_missions"] = []

        # slow commander re-evaluation while we are moving out
        self.owner.ai.memory["task_vehicle_crew"]["think_interval"] = random.uniform(6.0, 12.0)

        return True
