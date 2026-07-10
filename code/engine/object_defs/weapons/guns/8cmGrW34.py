"""
8cmGrW34 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("8cmGrW34")
def create(world, world_coords):
    # ref : https://en.wikipedia.org/wiki/8_cm_Granatwerfer_34
    z = WorldObject(world, ["mg34"], AIGun)
    z.name = "8cm Granatwerfer 34"
    z.no_update = True
    z.is_gun = True
    z.ai.mechanical_accuracy = 10
    z.ai.mechanical_accuracy_deg = 0.20
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "GrW34_magazine", False)
    z.ai.rate_of_fire = 1
    z.ai.range = 4000
    z.ai.indirect_range = 4500
    # historical min ~60m; use a game-scale floor so AI doesn't try to fire under it
    z.ai.minimum_range = 400
    z.ai.type = "cannon"
    z.ai.use_antitank = False
    z.ai.use_antipersonnel = True
    z.ai.direct_fire = False
    z.ai.indirect_fire = True
    z.ai.indirect_fire_mode = True
    z.rotation_angle = 0
    return z
