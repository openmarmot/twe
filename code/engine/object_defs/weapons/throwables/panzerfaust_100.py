"""
panzerfaust_100 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("panzerfaust_100")
def create(world, world_coords):
    z = WorldObject(world, ["panzerfaust", "panzerfaust_empty"], AIGun)
    z.name = "panzerfaust 100"
    z.description = "A Panzerfaust 100 anti-tank launcher"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.ai.mechanical_accuracy = 15
    z.ai.speed = 300
    z.is_handheld_antitank = True
    z.ai.magazine = engine.world_builder.spawn_object(
        world, world_coords, "panzerfaust_100_magazine", False
    )
    z.ai.rate_of_fire = 0.12
    z.ai.reload_speed = 0
    z.ai.range = 1813
    z.ai.type = "antitank launcher"
    z.ai.use_antitank = True
    z.ai.smoke_on_fire = True
    z.ai.smoke_type = "rocket"
    z.rotation_angle = float(random.randint(0, 359))
    return z
