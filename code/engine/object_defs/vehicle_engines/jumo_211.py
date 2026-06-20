"""
jumo_211 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("jumo_211")
def create(world, world_coords):
    z = WorldObject(world, ["jumo_211"], AIEngine)
    z.name = "Jumo 211 Engine"
    z.ai.fuel_type = ["gas_80_octane"]
    z.ai.fuel_consumption_rate = 0.0033
    z.ai.max_engine_force = 2549953.75  # based on 1000 hp
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 640
    return z
