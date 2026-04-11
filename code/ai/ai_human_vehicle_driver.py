"""
repo : https://github.com/openmarmot/twe

notes : vehicle driver code
"""

# import built in modules
import random
import copy
from ai.ai_human_vehicle_crew_action import VehicleCrewAction

# import custom packages
import engine.math_2d
import engine.log
from engine.vehicle_order import VehicleOrder

# import engine.global_exchange_rates


class AIHumanVehicleDriver:
    def __init__(self, owner):
        self.owner = owner

        # distance tuning
        # when a vehicle is < this distance to a target it is considered arrived
        self.vehicle_arrival_distance = 150

    # ---------------------------------------------------------------------------
    def action(self):
        vehicle = self.owner.ai.memory["task_vehicle_crew"]["vehicle_role"].vehicle
        vehicle.ai.throttle = 0
        vehicle.ai.brake_power = 1

        current_action = self.owner.ai.memory["task_vehicle_crew"]["current_action"]
        if current_action == VehicleCrewAction.DRIVING:
            calculated_distance = self.owner.ai.memory["task_vehicle_crew"][
                "calculated_distance_to_target"
            ]
            calculated_vehicle_angle = self.owner.ai.memory["task_vehicle_crew"][
                "calculated_vehicle_angle"
            ]

            # initial throttle settings
            if calculated_distance < 150:
                # apply brakes. bot will only exit when speed is zero
                # note this number should be < the minimum distance to jump out
                # or you can end up with drivers stuck in the vehicle if they slow down fast
                vehicle.ai.throttle = 0
                vehicle.ai.brake_power = 1
            elif calculated_distance < 300:
                vehicle.ai.throttle = 0.5
                vehicle.ai.brake_power = 0
            else:
                vehicle.ai.throttle = 1
                vehicle.ai.brake_power = 0

            # Normalize both angles to [0, 360)
            current_angle = engine.math_2d.get_normalized_angle(vehicle.rotation_angle)
            desired_angle = engine.math_2d.get_normalized_angle(
                calculated_vehicle_angle
            )

            # Compute shortest signed difference (-180 to +180)
            diff = (desired_angle - current_angle + 180) % 360 - 180

            # If close enough, snap to exact angle and neutral steering
            if abs(diff) <= 4:  # Adjusted threshold to match original logic
                vehicle.ai.handle_steer_neutral()
                vehicle.rotation_angle = desired_angle
                vehicle.ai.update_heading()
            else:
                # Steer in the direction of the shortest diff
                if diff > 0:
                    vehicle.ai.handle_steer_left()  # Assuming this increases angle
                    # helps turn faster
                    if vehicle.ai.throttle > 0.5:
                        vehicle.ai.throttle = 0.5
                else:
                    vehicle.ai.handle_steer_right()  # Assuming this decreases angle
                    # helps turn faster
                    if vehicle.ai.throttle > 0.5:
                        vehicle.ai.throttle = 0.5

            return

        if current_action == VehicleCrewAction.ROTATING:
            # rotating in place with minimal movement
            # throttle + brake seems to be working here fairly well

            calculated_vehicle_angle = self.owner.ai.memory["task_vehicle_crew"][
                "calculated_vehicle_angle"
            ]

            if vehicle.ai.current_speed == 0:
                # this throttle boost helps vehicle overcome bad terrain like trees
                # otherwise a 0.2 isn't enough to move against a tree tile and they will get stuck not moving or rotating
                vehicle.ai.throttle = 0.5
                vehicle.ai.brake_power = 1
            elif vehicle.ai.current_speed > 10:
                vehicle.ai.throttle = 0
                vehicle.ai.brake_power = 1
            else:
                vehicle.ai.throttle = 0.2
                vehicle.ai.brake_power = 1

            # Normalize both angles to [0, 360)
            current_angle = engine.math_2d.get_normalized_angle(vehicle.rotation_angle)
            desired_angle = engine.math_2d.get_normalized_angle(
                calculated_vehicle_angle
            )

            # Compute shortest signed difference (-180 to +180)
            diff = (desired_angle - current_angle + 180) % 360 - 180

            # If close enough, snap to exact angle and stop
            if abs(diff) <= 6:  # Adjusted threshold to match original logic
                vehicle.ai.handle_steer_neutral()
                vehicle.rotation_angle = desired_angle
                vehicle.ai.update_heading()
                vehicle.ai.throttle = 0
                vehicle.ai.brake_power = 1
                # this action is now done
                self.owner.ai.memory["task_vehicle_crew"]["current_action"] = (
                    VehicleCrewAction.IDLE
                )
            else:
                # Rotate in the direction of the shortest diff
                if diff > 0:
                    vehicle.ai.handle_steer_left()
                else:
                    vehicle.ai.handle_steer_right()

    # ---------------------------------------------------------------------------
    def think_vehicle_order(self):
        """think about the drivers current vehicle order"""
        order = self.owner.ai.memory["task_vehicle_crew"]["vehicle_order"]
        vehicle = self.owner.ai.memory["task_vehicle_crew"]["vehicle_role"].vehicle
        if order.order_drive_to_coords or order.order_close_with_enemy:
            distance = engine.math_2d.get_distance(
                vehicle.world_coords, order.world_coords
            )
            if (
                distance < self.vehicle_arrival_distance
                and vehicle.ai.current_speed < 10
            ):
                # we have arrived and can delete the order.
                self.owner.ai.memory["task_vehicle_crew"]["current_action"] = (
                    VehicleCrewAction.WAITING
                )
                vehicle.ai.brake_power = 1
                vehicle.ai.throttle = 0

                if order.exit_vehicle_when_finished:
                    if vehicle.ai.is_transport:
                        for role in vehicle.ai.vehicle_crew:
                            if role.role_occupied:
                                role.human.ai.switch_task_exit_vehicle()
                                # this will also clear out any vehicle_orders they had

                # delete the order
                self.owner.ai.memory["task_vehicle_crew"]["vehicle_order"] = None

                return
            # default
            self.think_drive_to_destination(order.world_coords, distance)
            return
        if order.order_tow_object:
            # future
            return

    # ---------------------------------------------------------------------------
    def think_drive_to_destination(self, destination, distance):
        """perform actions necessary to start driving somewhere"""
        vehicle = self.owner.ai.memory["task_vehicle_crew"]["vehicle_role"].vehicle

        rotation = engine.math_2d.get_rotation(vehicle.world_coords, destination)
        self.owner.ai.memory["task_vehicle_crew"]["current_action"] = (
            VehicleCrewAction.DRIVING
        )
        self.owner.ai.memory["task_vehicle_crew"]["calculated_distance_to_target"] = (
            distance
        )
        self.owner.ai.memory["task_vehicle_crew"]["calculated_vehicle_angle"] = rotation
        # turn engines on
        # could do smarter checks here once engines have more stats
        need_start = False
        for b in vehicle.ai.engines:
            if b.ai.engine_on is False:
                need_start = True
                break
        if need_start:
            current_fuel, max_fuel = vehicle.ai.read_fuel_gauge()
            if current_fuel > 0:
                vehicle.ai.handle_start_engines()
            else:
                # there might be some cases where this happens and we should have turned the engine on anyways (some engines don't use fuel)
                if max_fuel == 0:
                    engine.log.add_data(
                        "warn",
                        f"ai_human_vehicle think_drive_to_destination max_fuel==0 for vehicle {vehicle.name}",
                        True,
                    )

                # out of fuel.
                # disable the vehicle for now. in the future we will want to try and get fuel and refuel
                # engine.log.add_data('warn',f'ai_human_vehicle.think_drive_to_destination out of fuel. driver {self.owner.name} vehicle {vehicle.name} marking vehicle disabled',True)
                vehicle.ai.vehicle_disabled = True

    # ---------------------------------------------------------------------------
    def check_rotation_required(self, rotation_required):
        """handle common rotation logic"""
        vehicle = self.owner.ai.memory["task_vehicle_crew"]["vehicle_role"].vehicle
        current_fuel, max_fuel = vehicle.ai.read_fuel_gauge()
        if current_fuel == 0 and max_fuel > 0:
            engine.log.add_data(
                "warn",
                f"ai_human_vehicle.think_vehicle_role_driver waiting for driver {self.owner.name}  to rotate {vehicle.name} and out of fuel, marking vehicle disabled",
                True,
            )
            vehicle.ai.vehicle_disabled = True
            return

        v = vehicle.rotation_angle
        current_angle = engine.math_2d.get_normalized_angle(v)
        desired_angle = engine.math_2d.get_normalized_angle(rotation_required)
        diff = (desired_angle - current_angle + 180) % 360 - 180
        if abs(diff) <= 6:
            # we are close enough
            self.owner.ai.memory["task_vehicle_crew"]["current_action"] = (
                VehicleCrewAction.WAITING
            )
            vehicle.ai.brake_power = 1
            vehicle.ai.throttle = 0
            self.owner.ai.memory["task_vehicle_crew"]["think_interval"] = (
                random.uniform(0.5, 2.0)
            )
            return
        # default
        self.owner.ai.memory["task_vehicle_crew"]["calculated_vehicle_angle"] = (
            rotation_required
        )
        self.owner.ai.memory["task_vehicle_crew"]["current_action"] = (
            VehicleCrewAction.ROTATING
        )
        return

    # ---------------------------------------------------------------------------
    def create_vehicle_order_for_target(self, target_or_coords, offset_distance=60):
        """create vehicle order to get close to target with fire mission"""
        vehicle = self.owner.ai.memory["task_vehicle_crew"]["vehicle_role"].vehicle
        need_vehicle_order = False
        if self.owner.ai.memory["task_vehicle_crew"]["vehicle_order"] is None:
            need_vehicle_order = True
        else:
            if (
                self.owner.ai.memory["task_vehicle_crew"][
                    "vehicle_order"
                ].order_close_with_enemy
                is False
            ):
                need_vehicle_order = True
        # ensuring we only do this once
        if need_vehicle_order:
            vehicle_order = VehicleOrder()
            vehicle_order.order_close_with_enemy = True
            vehicle_order.world_coords = engine.math_2d.calculate_relative_position(
                target_or_coords, offset_distance, [200, 200]
            )
            if vehicle.ai.is_transport:
                vehicle_order.exit_vehicle_when_finished = True
            self.owner.ai.memory["task_vehicle_crew"]["vehicle_order"] = vehicle_order

    # ---------------------------------------------------------------------------
    def think(self):
        vehicle = self.owner.ai.memory["task_vehicle_crew"]["vehicle_role"].vehicle

        commander_role, gunner_role = self.identify_crew_roles(vehicle)

        if self.handle_commander_actions(vehicle, commander_role):
            return

        if self.handle_gunner_actions(vehicle, gunner_role):
            return

        if self.handle_driver_decisions(vehicle, commander_role, gunner_role):
            return

        if self.handle_passenger_loading(vehicle):
            return

        if self.handle_vehicle_orders(vehicle):
            return

        if self.handle_out_of_ammo(vehicle):
            return

        if self.handle_squad_leader_distance(vehicle):
            return

        self.handle_default_behavior(vehicle)

    def identify_crew_roles(self, vehicle):
        commander_role = None
        gunner_role = None

        for role in vehicle.ai.vehicle_crew:
            if role.role_occupied:
                if role.is_commander:
                    commander_role = role
                if role.is_gunner:
                    if (
                        role.turret
                        and role.turret.ai
                        and getattr(role.turret.ai, "primary_turret", False)
                    ):
                        gunner_role = role

        return commander_role, gunner_role

    def handle_commander_actions(self, vehicle, commander_role):
        if not commander_role:
            return False

        current_action = commander_role.human.ai.memory["task_vehicle_crew"][
            "current_action"
        ]

        if current_action == VehicleCrewAction.WAITING_FOR_ROTATE:
            rotation_required = commander_role.human.ai.memory["task_vehicle_crew"][
                "calculated_vehicle_angle"
            ]
            v = vehicle.rotation_angle
            current_angle = engine.math_2d.get_normalized_angle(v)
            desired_angle = engine.math_2d.get_normalized_angle(rotation_required)
            diff = (desired_angle - current_angle + 180) % 360 - 180
            if abs(diff) <= 6:
                self.owner.ai.memory["task_vehicle_crew"]["current_action"] = (
                    VehicleCrewAction.WAITING
                )
                vehicle.ai.brake_power = 1
                vehicle.ai.throttle = 0
                self.owner.ai.memory["task_vehicle_crew"]["think_interval"] = (
                    random.uniform(0.5, 2.0)
                )
                return True
            self.owner.ai.memory["task_vehicle_crew"]["calculated_vehicle_angle"] = (
                rotation_required
            )
            self.owner.ai.memory["task_vehicle_crew"]["current_action"] = (
                VehicleCrewAction.ROTATING
            )
            return True

        return False

    def handle_gunner_actions(self, vehicle, gunner_role):
        if not gunner_role:
            return False

        current_action = gunner_role.human.ai.memory["task_vehicle_crew"][
            "current_action"
        ]

        if gunner_role.turret.ai.primary_weapon:
            if current_action in (
                VehicleCrewAction.RELOADING_PRIMARY,
                VehicleCrewAction.RELOADING_COAX,
                VehicleCrewAction.ENGAGING,
                VehicleCrewAction.CLEARING_JAM,
            ):
                self.owner.ai.memory["task_vehicle_crew"]["current_action"] = (
                    VehicleCrewAction.WAITING
                )
                vehicle.ai.brake_power = 1
                vehicle.ai.throttle = 0
                self.owner.ai.memory["task_vehicle_crew"]["think_interval"] = (
                    random.uniform(1, 5.0)
                )
                return True
        else:
            engine.log.add_data(
                "error",
                f"turret {gunner_role.turret.name} does not have a primary weapon",
                True,
            )
            return True

        if current_action == VehicleCrewAction.WAITING_FOR_ROTATE:
            target = gunner_role.human.ai.memory["task_vehicle_crew"]["target"]
            if target is not None:
                rotation_required = engine.math_2d.get_rotation(
                    vehicle.world_coords, target.world_coords
                )
                self.check_rotation_required(rotation_required)
                return True

        if current_action == VehicleCrewAction.WAITING_FOR_ROTATE_FIRE_MISSION:
            if gunner_role.human.ai.memory["task_vehicle_crew"]["fire_missions"]:
                fire_mission = gunner_role.human.ai.memory["task_vehicle_crew"][
                    "fire_missions"
                ][0]
                rotation_required = engine.math_2d.get_rotation(
                    vehicle.world_coords, fire_mission.world_coords
                )
                self.check_rotation_required(rotation_required)
                return True

        if current_action == VehicleCrewAction.WAITING_FOR_POSITION_FIRE_MISSION:
            if gunner_role.human.ai.memory["task_vehicle_crew"]["fire_missions"]:
                fire_mission = gunner_role.human.ai.memory["task_vehicle_crew"][
                    "fire_missions"
                ][0]
                self.create_vehicle_order_for_target(fire_mission.world_coords)

        if current_action == VehicleCrewAction.WAITING_FOR_CLOSE_DISTANCE:
            target = gunner_role.human.ai.memory["task_vehicle_crew"]["target"]
            if target is not None:
                self.create_vehicle_order_for_target(target.world_coords)
            else:
                engine.log.add_data(
                    "debug",
                    f"driver: gunner waiting for close distance but target is None",
                    False,
                )

        return False

    def handle_driver_decisions(self, vehicle, commander_role, gunner_role):
        if commander_role or gunner_role:
            return False

        has_targets = (
            len(self.owner.ai.human_targets) > 0
            or len(self.owner.ai.vehicle_targets) > 0
        )

        if not has_targets:
            return False

        if self.owner.ai.morale_check() is False:
            self.owner.ai.speak("I'm out! This vehicle is useless without a gunner!")
            self.owner.ai.switch_task_exit_vehicle()
            return True

        for role in vehicle.ai.vehicle_crew:
            if role.role_occupied is False:
                if role.is_gunner and role.turret:
                    self.owner.ai.switch_task_vehicle_crew(vehicle, None)
                    return True

        target = None
        if self.owner.ai.human_targets:
            target = self.owner.ai.human_targets[0]
        elif self.owner.ai.vehicle_targets:
            target = self.owner.ai.vehicle_targets[0]

        if target:
            distance_to_target = engine.math_2d.get_distance(
                vehicle.world_coords, target.world_coords
            )
            if distance_to_target < 1500:
                self.owner.ai.speak("Too close! Jumping out!")
                self.owner.ai.switch_task_exit_vehicle()
                return True

        if vehicle.ai.is_transport or vehicle.ai.vehicle_out_of_ammo:
            self.owner.ai.switch_task_exit_vehicle()
            return True

        spawn_coords = self.owner.ai.squad.faction_tactical.spawn_location
        vehicle_order = VehicleOrder()
        vehicle_order.order_drive_to_coords = True
        vehicle_order.world_coords = engine.math_2d.randomize_coordinates(
            spawn_coords, 100
        )
        vehicle_order.exit_vehicle_when_finished = True
        self.owner.ai.memory["task_vehicle_crew"]["vehicle_order"] = vehicle_order
        return True

    def handle_passenger_loading(self, vehicle):
        if vehicle.ai.check_if_vehicle_is_full():
            return False

        for b in self.owner.ai.squad.faction_tactical.allied_humans:
            if "task_enter_vehicle" in b.ai.memory:
                if vehicle is b.ai.memory["task_enter_vehicle"]["vehicle"]:
                    self.owner.ai.memory["task_vehicle_crew"]["think_interval"] = (
                        random.uniform(0.8, 1)
                    )
                    vehicle.ai.brake_power = 1
                    vehicle.ai.throttle = 0
                    self.owner.ai.memory["task_vehicle_crew"]["current_action"] = (
                        VehicleCrewAction.WAITING_FOR_PASSENGERS
                    )
                    return True

        return False

    def handle_vehicle_orders(self, vehicle):
        if self.owner.ai.memory["task_vehicle_crew"]["vehicle_order"] is not None:
            self.think_vehicle_order()
            return True

        for role in vehicle.ai.vehicle_crew:
            if role.role_occupied:
                if (
                    role.human.ai.memory["task_vehicle_crew"]["vehicle_order"]
                    is not None
                ):
                    self.owner.ai.memory["task_vehicle_crew"]["vehicle_order"] = (
                        role.human.ai.memory["task_vehicle_crew"]["vehicle_order"]
                    )
                    role.human.ai.memory["task_vehicle_crew"]["vehicle_order"] = None
                    return True

        return False

    def handle_out_of_ammo(self, vehicle):
        if not (vehicle.ai.vehicle_out_of_ammo and vehicle.ai.is_transport == False):
            return False

        spawn_coords = self.owner.ai.squad.faction_tactical.spawn_location
        distance_to_spawn = engine.math_2d.get_distance(
            vehicle.world_coords, spawn_coords
        )

        if distance_to_spawn < 300:
            for role in vehicle.ai.vehicle_crew:
                if role.role_occupied:
                    role.human.ai.switch_task_exit_vehicle()
        else:
            vehicle_order = VehicleOrder()
            vehicle_order.order_drive_to_coords = True
            vehicle_order.world_coords = engine.math_2d.randomize_coordinates(
                spawn_coords, 100
            )
            vehicle_order.exit_vehicle_when_finished = True
            self.owner.ai.memory["task_vehicle_crew"]["vehicle_order"] = vehicle_order

        return True

    def handle_squad_leader_distance(self, vehicle):
        if self.owner.ai.squad.squad_leader is None:
            return False

        distance_to_squad_lead = engine.math_2d.get_distance(
            self.owner.world_coords, self.owner.ai.squad.squad_leader.world_coords
        )

        if distance_to_squad_lead <= 300:
            return False

        vehicle_order = VehicleOrder()
        vehicle_order.order_drive_to_coords = True
        vehicle_order.world_coords = copy.copy(
            self.owner.ai.squad.squad_leader.world_coords
        )
        if vehicle.ai.is_transport:
            vehicle_order.exit_vehicle_when_finished = True
        self.owner.ai.memory["task_vehicle_crew"]["vehicle_order"] = vehicle_order
        return True

    def handle_default_behavior(self, vehicle):
        self.owner.ai.memory["task_vehicle_crew"]["current_action"] = (
            VehicleCrewAction.WAITING_AT_DESTINATION
        )
        vehicle.ai.brake_power = 1
        vehicle.ai.throttle = 0

        if not vehicle.ai.is_transport:
            return

        crew_squad_lead = False
        for role in vehicle.ai.vehicle_crew:
            if role.role_occupied:
                if role.human.ai.squad.squad_leader == role.human:
                    crew_squad_lead = True
                    break

        if crew_squad_lead:
            return

        for role in vehicle.ai.vehicle_crew:
            if role.role_occupied:
                role.human.ai.switch_task_exit_vehicle()
