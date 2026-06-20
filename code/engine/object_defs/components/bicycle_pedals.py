"""
bicycle_pedals object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("bicycle_pedals")
def create(world, world_coords):
    z = WorldObject(world, ["bicycle_pedals"], AIEngine)
    z.name = "bicycle pedals"
    z.ai.internal_combustion = False
    z.ai.fuel_type = "none"
    z.ai.fuel_consumption_rate = 0
    z.ai.max_engine_force = 13100
    z.ai.engine_on = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
