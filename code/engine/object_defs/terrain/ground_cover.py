"""
ground_cover object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_none import AINone
from engine.object_registry import register_object


@register_object("ground_cover")
def create(world, world_coords):
    # z=WorldObject(world,['ground_dirt_vlarge'],AINone)
    z = WorldObject(world, ["terrain_light_sand"], AINone)
    z.name = "ground cover"
    z.is_ground_texture = True
    z.rotation_angle = 0
    z.no_update = True
    return z
