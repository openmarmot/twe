"""
horch_38_v8_engine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("horch_38_v8_engine")
def create(world, world_coords):
    # Sd.Kfz. 222 Ausf. B engine. 3.8 L gasoline V-8, 90 PS.
    # the early 3.5 L Horch was 75 PS.
    # sprite reused from the Volkswagen engine.
    z = WorldObject(world, ["volkswagen_type_82_engine"], AIEngine)
    z.name = "Horch 3.8 V8 Engine"
    z.ai.fuel_type = ["gas_80_octane"]
    z.ai.fuel_consumption_rate = 0.0033
    # (horsepower * 745.7) / 0.7375
    z.ai.max_engine_force = 91000.678
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 250
    return z
