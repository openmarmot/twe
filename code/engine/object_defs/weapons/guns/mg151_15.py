"""
mg151_15 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("mg151_15")
def create(world, world_coords):
    # Mauser MG 151/15. 15x96, cyclic rate about 740 rpm. Sprite is the MG34.
    z = WorldObject(world, ["mg34"], AIGun)
    z.name = "MG 151/15"
    z.description = "A Mauser MG 151/15 15mm aircraft cannon"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 10
    z.ai.mechanical_accuracy_deg = 0.20
    z.ai.magazine = engine.world_builder.spawn_object(
        world, world_coords, "mg151_15_belt", False
    )
    z.ai.rate_of_fire = 0.081
    z.ai.reload_speed = 15
    z.ai.range = 4000
    z.ai.type = "automatic cannon"
    z.ai.use_antipersonnel = True
    z.ai.use_antitank = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
