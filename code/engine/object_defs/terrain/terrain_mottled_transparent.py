"""
terrain_mottled_transparent object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_none import AINone
from engine.object_registry import register_object


@register_object("terrain_mottled_transparent")
def create(world, world_coords):
    z = WorldObject(world, ["terrain_mottled_transparent"], AINone)
    z.name = "mottled terrain"
    z.is_ground_texture = True
    z.rotation_angle = 0
    z.default_scale = 1
    z.no_update = True
    return z
