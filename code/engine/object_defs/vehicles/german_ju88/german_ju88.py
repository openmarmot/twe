"""
german_ju88 object definition

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


@register_object("german_ju88")
def create(world, world_coords):
    z = WorldObject(world, ["ju88-winter-weathered", "ju88-winter-weathered"], AIVehicle)
    z.name = "Junkers Ju88"

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
    mg = engine.world_builder.spawn_object(world, world_coords, "mg15", False)
    z.add_inventory(mg)
    z.ai.primary_weapon = mg
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg15_drum_magazine", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg15_drum_magazine", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg15_drum_magazine", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg15_drum_magazine", False))
    z.is_airplane = True
    z.is_vehicle = True
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 9800
    z.drag_coefficient = 0.8
    z.frontal_area = 6
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    z.ai.fuel_tanks[0].volume = 415
    z.ai.fuel_tanks[1].volume = 415
    z.ai.fuel_tanks[2].volume = 425
    z.ai.fuel_tanks[3].volume = 425
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[0], "gas_80_octane")
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[1], "gas_80_octane")
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[2], "gas_80_octane")
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[3], "gas_80_octane")
    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "jumo_211", False)
    )
    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "jumo_211", False)
    )
    z.ai.engines[0].ai.exhaust_position_offset = [-10, 65]
    z.ai.engines[1].ai.exhaust_position_offset = [-10, -75]
    z.ai.batteries.append(
        engine.world_builder.spawn_object(world, world_coords, "battery_vehicle_24v", False)
    )
    return z