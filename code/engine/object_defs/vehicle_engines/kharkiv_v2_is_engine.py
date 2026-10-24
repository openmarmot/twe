"""
kharkiv_v2-is_engine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("kharkiv_v2-is_engine")
def create(world, world_coords):
    # V-2-IS (V-2-10), 520 PS. Same force scale as the V-2-34:
    # (horsepower * 745.7) / 0.7375
    z = WorldObject(world, ["deutz_diesel_65hp_engine"], AIEngine)
    z.name = "Kharkiv V-2-IS Engine"
    z.ai.fuel_type = ["diesel"]
    z.ai.fuel_consumption_rate = 0.0033
    z.ai.max_engine_force = 525781.695
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 250
    return z
