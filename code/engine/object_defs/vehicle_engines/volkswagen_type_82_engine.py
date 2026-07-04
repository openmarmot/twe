"""
volkswagen_type_82_engine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("volkswagen_type_82_engine")
def create(world, world_coords):
    z = WorldObject(world, ["volkswagen_type_82_engine"], AIEngine)
    z.name = "Volkswagen Type 82 Engine"
    z.ai.fuel_type = ["gas_80_octane"]
    z.ai.fuel_consumption_rate = 0.0033
    z.ai.max_engine_force = 25277.9
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 250
    return z
