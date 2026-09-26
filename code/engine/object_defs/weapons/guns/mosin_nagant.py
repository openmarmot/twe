"""
mosin_nagant object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("mosin_nagant")
def create(world, world_coords):
    z = WorldObject(world, ["mosin_nagant"], AIGun)
    z.name = "mosin_nagant"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 1
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "mosin_magazine", False)
    # longer, stiffer bolt than the Kar98k
    z.ai.rate_of_fire = 2.8
    z.ai.reload_speed = 6
    z.ai.range = 2418
    z.ai.type = "rifle"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
