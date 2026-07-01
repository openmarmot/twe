"""
soviet_zis_5 object definition

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


@register_object("soviet_zis_5")
def create(world, world_coords):
    # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
    z = WorldObject(world, ["zis_5"], AIVehicle)
    z.name = "Zis 5 Truck"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.is_transport = True
    z.ai.open_top = True
    # driver and assistant driver positions are the same for all variants
    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)
    role = VehicleRole("passenger", z)
    z.ai.vehicle_crew.append(role)

    passenger_positions = [
        [2.0, -22.0],
        [20.0, -22.0],
        [40.0, -22.0],
        [61.0, -22.0],
        [21.0, 0.0],
        [40.0, 19.0],
        [20.0, 19.0],
        [0.0, 19.0],
        [1.0, -1.0],
        [62.0, 0.0],
        [61.0, 20.0],
        [40.0, 0.0],
    ]
    for x in range(12):
        role = VehicleRole("passenger", z)
        role.is_passenger = True
        role.seat_visible = True
        role.seat_offset = passenger_positions.pop()
        z.ai.vehicle_crew.append(role)

    z.ai.vehicle_armor["top"] = [1, 0, 0]
    z.ai.vehicle_armor["bottom"] = [1, 0, 0]
    z.ai.vehicle_armor["left"] = [1, 0, 0]
    z.ai.vehicle_armor["right"] = [1, 0, 0]
    z.ai.vehicle_armor["front"] = [1, 0, 0]
    z.ai.vehicle_armor["rear"] = [1, 0, 0]
    z.ai.passenger_compartment_armor["top"] = [0, 0, 0]
    z.ai.passenger_compartment_armor["bottom"] = [0, 0, 0]
    z.ai.passenger_compartment_armor["left"] = [0, 0, 0]
    z.ai.passenger_compartment_armor["right"] = [0, 0, 0]
    z.ai.passenger_compartment_armor["front"] = [0.0, 0, 0]
    z.ai.passenger_compartment_armor["rear"] = [0, 0, 0]
    z.ai.max_speed = 385.9
    z.ai.max_offroad_speed = 177.6
    # z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
    z.ai.rotation_speed = 40.0
    z.collision_radius = 100
    z.bounding_circles.append([[-61.0, 0.0], 25])
    z.bounding_circles.append([[-35.0, 0.0], 25])
    z.bounding_circles.append([[-12.0, 0.0], 25])
    z.bounding_circles.append([[18.0, 0.0], 30])
    z.bounding_circles.append([[54.0, 0.0], 30])

    z.weight = 3100
    z.drag_coefficient = 0.9
    z.frontal_area = 5
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    z.ai.fuel_tanks[0].volume = 114
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[0], "gas_80_octane")
    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "maybach_hl42_engine", False)
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
    if random.randint(0, 1) == 1:
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "tt33", False))
    z.ai.min_wheels_per_side_front = 1
    z.ai.min_wheels_per_side_rear = 1
    z.ai.max_wheels = 4
    z.ai.max_spare_wheels = 0
    z.ai.front_left_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "251_wheel", False)
    )
    z.ai.front_right_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "251_wheel", False)
    )
    z.ai.rear_left_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "251_wheel", False)
    )
    z.ai.rear_right_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "251_wheel", False)
    )
    return z
