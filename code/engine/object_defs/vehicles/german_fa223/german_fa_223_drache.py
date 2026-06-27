"""
german_fa_223_drache object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_vehicle import AIVehicle
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_fa_223_drache")
def create(world, world_coords):
    z = WorldObject(world, ["fa_223_drache", "fa_223_drache"], AIVehicle)
    z.name = "Focke Achgelis 223 Drache"

    driver = VehicleRole("driver", z)
    driver.is_driver = True
    z.ai.vehicle_crew.append(driver)

    z.ai.max_speed = 4736
    z.ai.max_offroad_speed = 177.6
    z.ai.stall_speed = 100
    z.ai.rotation_speed = 50
    z.ai.acceleration = 100
    z.ai.max_rate_of_climb = 3
    z.ai.throttle_zero = False
    z.collision_radius = 200
    z.is_airplane = True
    z.is_vehicle = True
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 4300
    z.drag_coefficient = 0.8
    z.frontal_area = 6
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    z.ai.fuel_tanks[0].volume = 415
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[0], "gas_80_octane")
    z.ai.engines.append(engine.world_builder.spawn_object(world, world_coords, "jumo_211", False))
    z.ai.engines[0].ai.exhaust_position_offset = [-10, 65]
    z.ai.batteries.append(
        engine.world_builder.spawn_object(world, world_coords, "battery_vehicle_24v", False)
    )
    left_rotor = engine.world_builder.spawn_object(world, world_coords, "fa_223_rotor", True)
    left_rotor.ai.engine = z.ai.engines[0]
    left_rotor.ai.position_offset = [-50, -180]
    left_rotor.ai.rotor_rotation = 0
    left_rotor.ai.vehicle = z
    z.ai.rotors.append(left_rotor)
    right_rotor = engine.world_builder.spawn_object(world, world_coords, "fa_223_rotor", True)
    right_rotor.ai.engine = z.ai.engines[0]
    right_rotor.ai.position_offset = [-50, 180]
    right_rotor.ai.rotor_rotation = 60
    right_rotor.ai.vehicle = z
    z.ai.rotors.append(right_rotor)
    return z
