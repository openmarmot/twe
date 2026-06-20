"""
smg42_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("smg42_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(world, ["smg42_turret"], AITurret)
    z.name = "SMG42 Turret"
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_iron_sights", False)
    z.is_turret = True
    z.ai.vehicle_mount_side = "top"
    z.ai.turret_accuracy = 5
    z.ai.turret_armor["top"] = [0, 0, 0]
    z.ai.turret_armor["bottom"] = [0, 0, 0]
    z.ai.turret_armor["left"] = [0, 0, 0]
    z.ai.turret_armor["right"] = [0, 0, 0]
    z.ai.turret_armor["front"] = [0, 0, 0]
    z.ai.turret_armor["rear"] = [0, 0, 0]
    z.ai.position_offset = [0, 0]
    z.ai.rotation_range = [-360, 360]
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "mg42", False)
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.primary_weapon_reload_speed = 10
    z.no_save = True
    return z
