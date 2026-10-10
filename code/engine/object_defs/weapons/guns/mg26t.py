"""
mg26t object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("mg26t")
def create(world, world_coords):
    # ZB vz. 26, German MG 26(t). Magazine-fed, about 500 rpm. Sprite is the MG34.
    z = WorldObject(world, ["mg34"], AIGun)
    z.name = "mg26t"
    z.description = "A Czech ZB vz. 26 light machine gun, German MG 26(t)"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.bipod = True
    z.ai.mechanical_accuracy = 2
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "mg26t_magazine", False)
    z.ai.rate_of_fire = 0.12
    z.ai.reload_speed = 6
    z.ai.range = 2418
    z.ai.type = "machine gun"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
