"""
panzer_iv_g_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("panzer_iv_g_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(world, ["panzer_iv_g_turret", "panzer_iv_g_turret"], AITurret)
    z.name = "Panzer IV Ausf. G Turret"
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_tzf_5f", False)
    z.is_turret = True
    z.ai.vehicle_mount_side = "top"
    z.ai.turret_accuracy = 1
    z.ai.turret_armor["top"] = [16, 0, 0]
    z.ai.turret_armor["bottom"] = [8, 0, 0]
    z.ai.turret_armor["left"] = [30, 23, 0]
    z.ai.turret_armor["right"] = [30, 23, 0]
    z.ai.turret_armor["front"] = [50, 11, 0]
    z.ai.turret_armor["rear"] = [30, 15, 0]
    z.ai.position_offset = [-15, 0]
    z.ai.rotation_range = [-360, 360]
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "75mm_kwk40_l43", False)
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    z.ai.primary_weapon.ai.smoke_offset = [-93.0, 1.0]
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.coaxial_weapon = engine.world_builder.spawn_object(world, world_coords, "mg34", False)
    z.ai.coaxial_weapon.ai.equipper = z
    z.ai.coaxial_weapon.ai.spawn_case = False
    z.ai.primary_turret = True
    z.ai.primary_weapon_reload_speed = 20
    z.ai.coaxial_weapon_reload_speed = 10
    z.no_save = True
    return z
