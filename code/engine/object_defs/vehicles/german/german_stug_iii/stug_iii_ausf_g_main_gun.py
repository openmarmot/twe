"""
stug_iii_ausf_g_main_gun object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("stug_iii_ausf_g_main_gun")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(world, ["stug_iii_gun", "stug_iii_gun"], AITurret)
    z.name = "StuG III Ausf. G Main Gun"
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_sfl_zf_1a", False)
    z.is_turret = True
    z.ai.vehicle_mount_side = "front"
    z.ai.turret_accuracy = 1
    z.ai.turret_armor["top"] = [30, 0, 0]
    z.ai.turret_armor["bottom"] = [30, 0, 0]
    z.ai.turret_armor["left"] = [50, 0, 0]
    z.ai.turret_armor["right"] = [50, 0, 0]
    z.ai.turret_armor["front"] = [50, 0, 0]
    z.ai.turret_armor["rear"] = [50, 0, 0]
    # gun port is front-right of the casemate. pivot is the mantlet face
    # so the recoil housing sits in the port and the barrel extends forward
    z.ai.position_offset = [-22, 2.4]
    z.image_rotation_offset = [0, 38]
    z.ai.rotation_range = [-10, 10]
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "75mm_kwk40_l48", False)
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    z.ai.primary_weapon.ai.smoke_offset = [-66, 0]
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.coaxial_weapon = engine.world_builder.spawn_object(world, world_coords, "mg34", False)
    z.ai.coaxial_weapon.ai.equipper = z
    z.ai.coaxial_weapon.ai.spawn_case = False
    z.ai.primary_turret = True
    z.ai.primary_weapon_reload_speed = 20
    z.ai.coaxial_weapon_reload_speed = 10
    z.no_save = True
    return z
