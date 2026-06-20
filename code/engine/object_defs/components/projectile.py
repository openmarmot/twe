"""
projectile object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_projectile import AIProjectile
from engine.object_registry import register_object


@register_object("projectile")
def create(world, world_coords):
    z = WorldObject(world, ["projectile"], AIProjectile)
    z.name = "projectile"
    z.ai.speed = 1000.0
    z.is_projectile = True
    z.no_save = True
    return z
