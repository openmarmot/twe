"""
german_military_bicycle object definition

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


@register_object("german_military_bicycle")
def create(world, world_coords):
    z = WorldObject(world, ["german_military_bicycle"], AIVehicle)
    z.name = "German Military Bicycle"
    z.is_vehicle = True
    z.ai.is_transport = True

    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)

    z.ai.max_speed = 177.6
    z.ai.max_offroad_speed = 142.08
    z.ai.rotation_speed = 50.0
    z.collision_radius = 30
    z.bounding_circles.append([[0, 0], 15])
    z.weight = 25
    z.drag_coefficient = 0.9
    z.frontal_area = 1
    z.rotation_angle = float(random.randint(0, 359))
    z.ai.min_wheels_per_side_front = 1
    z.ai.min_wheels_per_side_rear = 0
    z.ai.max_wheels = 2
    z.ai.max_spare_wheels = 0
    z.ai.front_left_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "bicycle_wheel", False)
    )
    return z
