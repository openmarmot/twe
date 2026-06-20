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
    z = WorldObject(world, ["ju88", "ju88_destroyed"], AIVehicle)
    z.name = "JU-88"
    z.is_vehicle = True
    z.ai.is_transport = True

    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)
    role = VehicleRole("passenger", z)
    z.ai.vehicle_crew.append(role)

    z.ai.max_speed = 500
    z.ai.max_offroad_speed = 400
    z.ai.rotation_speed = 30.0
    z.collision_radius = 150
    z.bounding_circles.append([[-50, 0], 40])
    z.bounding_circles.append([[50, 0], 40])
    z.weight = 14000
    z.drag_coefficient = 0.5
    z.frontal_area = 10
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    z.ai.fuel_tanks[0].volume = 2000
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[0], "gas_80_octane")
    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "jumo_211", False)
    )
    z.ai.batteries.append(
        engine.world_builder.spawn_object(world, world_coords, "battery_vehicle_24v", False)
    )
    z.rotation_angle = float(random.randint(0, 359))
    z.ai.min_wheels_per_side_front = 1
    z.ai.min_wheels_per_side_rear = 1
    z.ai.max_wheels = 3
    z.ai.max_spare_wheels = 0
    return z
