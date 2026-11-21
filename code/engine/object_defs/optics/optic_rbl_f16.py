"""
optic_rbl_f16 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_optic import AIOptic
from engine.object_registry import register_object


@register_object("optic_rbl_f16")
def create(world, world_coords):
    # Rundblickfernrohr 16. panoramic dial sight on the leIG 18.
    z = WorldObject(world, ["cucumber"], AIOptic)
    z.name = "Rbl.F.16"
    z.ai.magnification = 4
    z.ai.field_of_view = 10
    z.ai.optical_quality = 1.0
    z.ai.close_range_penalty = 0
    return z
