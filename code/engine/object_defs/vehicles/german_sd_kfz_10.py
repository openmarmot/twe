"""
german_sd_kfz_10 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_sd_kfz_10")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_sd_kfz_10_base", False)
    z.name = "Sd.Kfz.10"

    passenger_positions = [
        [15.0, -13.0],
        [15.0, 0.0],
        [15.0, 12.0],
        [43.0, -13.0],
        [42.0, 0.0],
        [42.0, 14.0],
    ]
    for x in range(6):
        role = VehicleRole("passenger", z)
        role.is_passenger = True
        role.seat_visible = True
        role.seat_offset = passenger_positions.pop()
        z.ai.vehicle_crew.append(role)
    return z
