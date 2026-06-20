"""
hit_marker object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_hit_marker import AIHitMarker
from engine.object_registry import register_object


@register_object("hit_marker")
def create(world, world_coords):
    z = WorldObject(world, ["hit_green", "hit_orange"], AIHitMarker)
    z.name = "Hit marker"
    z.minimum_visible_scale = 0.2
    z.is_hit_marker = True
    return z
