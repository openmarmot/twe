"""
soviet_gaz_61 object definition

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


@register_object("soviet_gaz_61")
def create(world, world_coords):
    z = WorldObject(world, ["gaz_61"], AIVehicle)
    z.name = "GAZ 61"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.is_transport = True

    z.ai.max_speed = 592

    driver = VehicleRole("driver", z)
    driver.is_driver = True
    z.ai.vehicle_crew.append(driver)

    for x in range(3):
        passenger = VehicleRole("passenger", z)
        passenger.is_passenger = True
        z.ai.vehicle_crew.append(passenger)

    z.ai.max_offroad_speed = 177.6
    z.ai.rotation_speed = 40.0
    z.collision_radius = 50
    z.bounding_circles.append([[-29.0, 0.0], 20])
    z.bounding_circles.append([[-8.0, 0.0], 20])
    z.bounding_circles.append([[7.0, 0.0], 20])
    z.bounding_circles.append([[29.0, 0.0], 20])
    z.weight = 1200
    z.drag_coefficient = 0.8
    z.frontal_area = 3
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    z.ai.fuel_tanks[0].volume = 60
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[0], "gas_80_octane")
    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "volkswagen_type_82_engine", False)
    )
    z.ai.engines[0].ai.exhaust_position_offset = [65, 10]
    z.ai.batteries.append(
        engine.world_builder.spawn_object(world, world_coords, "battery_vehicle_6v", False)
    )
    z.ai.min_wheels_per_side_front = 1
    z.ai.min_wheels_per_side_rear = 1
    z.ai.max_wheels = 4
    z.ai.max_spare_wheels = 1
    z.ai.front_left_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "volkswagen_wheel", False)
    )
    z.ai.front_right_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "volkswagen_wheel", False)
    )
    z.ai.rear_left_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "volkswagen_wheel", False)
    )
    z.ai.rear_right_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "volkswagen_wheel", False)
    )
    z.ai.spare_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "volkswagen_wheel", False)
    )
    if random.randint(0, 3) == 1:
        z.add_inventory(
            engine.world_builder.spawn_object(world, world_coords, "vodka", False)
        )
        z.add_inventory(
            engine.world_builder.spawn_object(world, world_coords, "vodka", False)
        )
        z.add_inventory(
            engine.world_builder.spawn_object(world, world_coords, "pickle_jar", False)
        )
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "german_fuel_can", False))
    z.add_inventory(engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_medical, False))
    z.add_inventory(
        engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_german_military_equipment, False)
    )
    z.rotation_angle = float(random.randint(0, 359))
    return z
