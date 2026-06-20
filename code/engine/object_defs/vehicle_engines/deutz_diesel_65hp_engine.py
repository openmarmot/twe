"""
deutz_diesel_65hp_engine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("deutz_diesel_65hp_engine")
def create(world, world_coords):
    z = WorldObject(world, ["deutz_diesel_65hp_engine"], AIEngine)
    z.name = "Deutz 65 HP Diesel Engine"
    z.ai.fuel_type = ["diesel"]
    z.ai.fuel_consumption_rate = 0.0033
    z.ai.max_engine_force = 65722.7
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 250
    return z
