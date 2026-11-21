"""
bramo_323_engine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_engine import AIEngine
from engine.object_registry import register_object


@register_object("bramo_323_engine")
def create(world, world_coords):
    # Fa 223 Drache engine. Bramo 323 Q3 nine-cylinder radial, 1000 hp.
    # the airframe burned aviation gasoline. the game gasoline is gas_80_octane.
    # sprite reused from the Jumo 211.
    z = WorldObject(world, ["jumo_211"], AIEngine)
    z.name = "Bramo 323 Engine"
    z.ai.fuel_type = ["gas_80_octane"]
    z.ai.fuel_consumption_rate = 0.0033
    # (horsepower * 745.7) / 0.7375, same scale as the vehicle engines
    z.ai.max_engine_force = 1011118.644
    z.rotation_angle = float(random.randint(0, 359))
    z.weight = 550
    return z
