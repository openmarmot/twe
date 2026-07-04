"""
kharkiv_v2-34_engine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("kharkiv_v2-34_engine")
def create(world, world_coords):
    z = WorldObject(world, ["deutz_diesel_65hp_engine"], AIEngine)
    z.name = "Kharkiv V2-34 Engine"
    z.ai.fuel_type = ["diesel"]
    z.ai.fuel_consumption_rate = 0.0033
    z.ai.max_engine_force = 505559.322
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 250
    return z
