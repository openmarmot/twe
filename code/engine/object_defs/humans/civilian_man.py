"""
civilian_man object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_human import AIHuman
import engine.name_gen
from engine.object_registry import register_object


@register_object("civilian_man")
def create(world, world_coords):
    z = WorldObject(
        world, ["civilian_man", "civilian_prone", "civilian_dead"], AIHuman
    )
    z.name = engine.name_gen.get_name("civilian")
    z.ai.speed = 30
    z.ai.morale = 70
    z.collision_radius = 15
    z.is_human = True
    if random.randint(0, 1) == 1:
        z.ai.wallet["Polish Zloty"] = round(random.uniform(0.05, 1.5), 2)
    if random.randint(0, 1) == 1:
        z.ai.wallet["Soviet Ruble"] = round(random.uniform(0.05, 1.5), 2)
    if random.randint(0, 1) == 1:
        z.ai.wallet["German Reichsmark"] = round(random.uniform(0.05, 1.5), 2)
    return z
