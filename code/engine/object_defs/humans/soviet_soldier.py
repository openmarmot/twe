"""
soviet_soldier object definition (base)

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_human import AIHuman
import engine.name_gen
from engine.object_registry import register_object


@register_object("soviet_soldier")
def create(world, world_coords):
    z = WorldObject(
        world, ["soviet_soldier", "soviet_soldier_prone", "soviet_dead"], AIHuman
    )
    z.name = engine.name_gen.get_name("soviet")
    z.ai.speed = 30
    z.collision_radius = 15
    z.is_human = True
    z.ai.is_small_arms_trained = True
    return z
