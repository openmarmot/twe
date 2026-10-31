"""
zis_5_engine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("zis_5_engine")
def create(world, world_coords):
    # ZiS-5 truck engine. Gasoline inline-6, 73 hp at 2300 rpm.
    # sprite reused from the Volkswagen engine.
    z = WorldObject(world, ["volkswagen_type_82_engine"], AIEngine)
    z.name = "ZiS-5 Engine"
    z.ai.fuel_type = ["gas_80_octane"]
    z.ai.fuel_consumption_rate = 0.0033
    # (horsepower * 745.7) / 0.7375
    z.ai.max_engine_force = 73811.661
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 250
    return z
