"""
tatra_103_engine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("tatra_103_engine")
def create(world, world_coords):
    # Sd.Kfz. 234 engine. Air-cooled diesel V-12, about 210 hp (157 kW).
    # sprite reused from the Deutz diesel.
    z = WorldObject(world, ["deutz_diesel_65hp_engine"], AIEngine)
    z.name = "Tatra 103 Engine"
    z.ai.fuel_type = ["diesel"]
    z.ai.fuel_consumption_rate = 0.0033
    # (horsepower * 745.7) / 0.7375
    z.ai.max_engine_force = 212334.915
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 250
    return z
