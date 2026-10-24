"""
122mm_d_25t_magazine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_magazine import AIMagazine
import engine.world_builder
from engine.object_registry import register_object


@register_object("122mm_d_25t_magazine")
def create(world, world_coords):
    z = WorldObject(world, ["stg44_magazine"], AIMagazine)
    z.name = "122mm_d_25t_magazine"
    z.minimum_visible_scale = 0.4
    z.is_gun_magazine = True
    z.ai.compatible_guns = ["122mm_d_25t"]
    # BR-471 was the wartime AP round. BR-471B is compatible but was not
    # issued in quantity until after the war.
    z.ai.compatible_projectiles = ["BR-471", "BR-471B", "OF-471"]
    z.ai.capacity = 1
    z.ai.disintegrating = True
    z.rotation_angle = float(random.randint(0, 359))
    engine.world_builder.load_magazine(world, z)
    return z
