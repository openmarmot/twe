"""
maybach_hl42_engine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("maybach_hl42_engine")
def create(world, world_coords):
    z = WorldObject(world, ["maybach_hl42"], AIEngine)
    z.name = "Maybach HL42 Engine"
    z.ai.fuel_type = ["gas_80_octane"]
    z.ai.fuel_consumption_rate = 0.0033
    z.ai.max_engine_force = 93022.91
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 250
    return z
