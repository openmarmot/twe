"""
german_field_commander object definition

repo : https://github.com/openmarmot/twe

notes : the only soldier who runs command-group orders. the flag
stays on this man. a replacement squad leader does not inherit it.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_field_commander")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_soldier", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "mp40")
    z.ai.is_field_commander = True
    z.ai.morale = 110
    return z
