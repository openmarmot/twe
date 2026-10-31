"""
maybach_hl230_p45_engine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("maybach_hl230_p45_engine")
def create(world, world_coords):
    # Tiger I production engine. 23 L gasoline V-12, 700 PS at 3000 rpm.
    # early hulls had the 650 PS HL 210. this is the mid/late Ausf. E engine.
    # sprite reused from the HL 42; this object is rarely drawn.
    z = WorldObject(world, ["maybach_hl42"], AIEngine)
    z.name = "Maybach HL 230 P45 Engine"
    z.ai.fuel_type = ["gas_80_octane"]
    z.ai.fuel_consumption_rate = 0.0033
    # (horsepower * 745.7) / 0.7375, same scale as the HL 120
    z.ai.max_engine_force = 707783.051
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 1200
    return z
