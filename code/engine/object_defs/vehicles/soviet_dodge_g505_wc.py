"""
soviet_dodge_g505_wc object definition

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


@register_object("soviet_dodge_g505_wc")
def create(world, world_coords):
    # note! at the moment this is meant to represent a 6x6 american truck
    #
    # ref : https://truck-encyclopedia.com/ww2/us/Dodge-WC-3-4-tons-series.php
    # ref : https://truck-encyclopedia.com/ww2/us/dodge-WC-62-63-6x6.php
    z = WorldObject(world, ["dodge_g505_wc", "dodge_g505_wc_destroyed"], AIVehicle)
    z.name = "Dodge G505 WC Truck"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.is_transport = True

    driver = VehicleRole("driver", z)
    driver.is_driver = True
    z.ai.vehicle_crew.append(driver)

    for x in range(10):
        passenger = VehicleRole("passenger", z)
        passenger.is_passenger = True
        z.ai.vehicle_crew.append(passenger)

    z.ai.max_speed = 651.2
    z.ai.max_offroad_speed = 177.6
    # z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
    z.ai.rotation_speed = 40.0
    z.collision_radius = 100
    z.bounding_circles.append([[-32.0, 0.0], 25])
    z.bounding_circles.append([[-8.0, 0.0], 25])
    z.bounding_circles.append([[10.0, 0.0], 25])
    z.bounding_circles.append([[35.0, 0.0], 25])
    z.weight = 2380
    z.drag_coefficient = 0.9
    z.frontal_area = 5
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    z.ai.fuel_tanks[0].volume = 114
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[0], "gas_80_octane")
    z.ai.engines.append(
        engine.world_builder.spawn_object(
            world, world_coords, "chrysler_flathead_straight_6_engine", False
        )
    )
    z.ai.engines[0].ai.exhaust_position_offset = [75, 10]
    z.ai.batteries.append(
        engine.world_builder.spawn_object(world, world_coords, "battery_vehicle_6v", False)
    )
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "german_fuel_can", False))
    z.add_inventory(engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_medical, False))
    z.add_inventory(
        engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_consumables, False)
    )
    z.rotation_angle = float(random.randint(0, 359))
    z.ai.min_wheels_per_side_front = 1
    z.ai.min_wheels_per_side_rear = 1
    z.ai.max_wheels = 6
    z.ai.max_spare_wheels = 0
    z.ai.front_left_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "g505_wheel", False)
    )
    z.ai.front_right_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "g505_wheel", False)
    )
    z.ai.rear_left_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "g505_wheel", False)
    )
    z.ai.rear_left_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "g505_wheel", False)
    )
    z.ai.rear_right_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "g505_wheel", False)
    )
    z.ai.rear_right_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "g505_wheel", False)
    )
    return z
