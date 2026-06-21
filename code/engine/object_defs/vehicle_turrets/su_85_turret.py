"""
su_85_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("su_85_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(world, ["su_85_turret"], AITurret)
    z.name = "SU-85 Turret"
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_tsh_16", False)
    z.is_turret = True
    z.ai.vehicle_mount_side = "front"
    z.ai.turret_accuracy = 2
    z.ai.turret_armor["top"] = [20, 0, 0]
    z.ai.turret_armor["bottom"] = [8, 0, 0]
    z.ai.turret_armor["left"] = [45, 21, 0]
    z.ai.turret_armor["right"] = [45, 21, 0]
    z.ai.turret_armor["front"] = [45, 10, 0]
    z.ai.turret_armor["rear"] = [45, 9, 0]
    z.ai.position_offset = [-47, 8]
    z.ai.rotation_range = [-10, 10]
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "85mm_d_5s", False)
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    z.ai.primary_weapon.ai.smoke_offset = [-147, 0]
    z.ai.primary_turret = True
    z.ai.primary_weapon_reload_speed = 21
    z.no_save = True
    return z
