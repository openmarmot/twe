"""
maybach_hl120_trm_engine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("maybach_hl120_trm_engine")
def create(world, world_coords):
    # Panzer IV engine. 11.9 L gasoline V-12, 300 PS at 3000 rpm.
    # sprite reused from the HL 42; this object is rarely drawn.
    z = WorldObject(world, ["maybach_hl42"], AIEngine)
    z.name = "Maybach HL 120 TRM Engine"
    z.ai.fuel_type = ["gas_80_octane"]
    z.ai.fuel_consumption_rate = 0.0033
    # (horsepower * 745.7) / 0.7375, same scale as the other engines
    z.ai.max_engine_force = 303335.593
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 920
    return z
