"""
praga_ac_engine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("praga_ac_engine")
def create(world, world_coords):
    # Hetzer and Panzer 38(t) engine. 7.75 L gasoline inline-6, 160 PS.
    # sprite reused from the HL 42; this object is rarely drawn.
    z = WorldObject(world, ["maybach_hl42"], AIEngine)
    z.name = "Praga AC Engine"
    z.ai.fuel_type = ["gas_80_octane"]
    z.ai.fuel_consumption_rate = 0.0033
    # (horsepower * 745.7) / 0.7375
    z.ai.max_engine_force = 161778.983
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 250
    return z
