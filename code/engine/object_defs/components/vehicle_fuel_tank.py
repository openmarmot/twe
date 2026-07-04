"""
vehicle_fuel_tank object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_container import AIContainer
from engine.object_registry import register_object


@register_object("vehicle_fuel_tank")
def create(world, world_coords):
    z = WorldObject(world, ["vehicle_fuel_tank"], AIContainer)
    z.is_container = True
    z.volume = 20
    z.name = "vehicle_fuel_tank"
    z.world_builder_identity = "vehicle_fuel_tank"
    z.rotation_angle = float(random.randint(0, 359))
    return z
