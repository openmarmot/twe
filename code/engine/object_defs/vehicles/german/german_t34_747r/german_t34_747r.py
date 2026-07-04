"""
german_t34_747r object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_t34_747r")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "soviet_t34_76_model_1943", False)
    z.name = "T34 747r"
    z.image_list = ["t34_747r_chassis"]
    z.ai.turrets[0].image_list = ["t34_747r_turret"]
    return z
