"""
nahverteidigungswaffe object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("nahverteidigungswaffe")
def create(world, world_coords):
    # this is the late war german smoke/he mortar device (close defense)
    z = WorldObject(world, ["mg34"], AIGun)
    z.name = "Nahverteidigungswaffe"
    z.no_update = True
    z.is_gun = True
    z.ai.mechanical_accuracy = 15
    z.ai.magazine = engine.world_builder.spawn_object(
        world, world_coords, "kampfpistole_magazine", False
    )
    z.ai.rate_of_fire = 1
    z.ai.reload_speed = 5
    z.ai.range = 250
    z.ai.type = "pistol"
    z.ai.use_antitank = False
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
