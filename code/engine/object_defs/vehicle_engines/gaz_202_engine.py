"""
gaz_202_engine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("gaz_202_engine")
def create(world, world_coords):
    # One bank of the T-70 powerplant. The tank carried two GAZ-202
    # gasoline sixes, 70 hp each, paired as the GAZ-203.
    # sprite reused from the Volkswagen engine.
    z = WorldObject(world, ["volkswagen_type_82_engine"], AIEngine)
    z.name = "GAZ-202 Engine"
    z.ai.fuel_type = ["gas_80_octane"]
    z.ai.fuel_consumption_rate = 0.0033
    # (horsepower * 745.7) / 0.7375
    z.ai.max_engine_force = 70778.305
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 250
    return z
