"""
soviet_82mm_mortar_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("soviet_82mm_mortar_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    # 82-BM-37 tube on the mortar base. tube sprite is still 251_2_turret
    # until this mount has its own art.
    z = WorldObject(world, ["251_2_turret"], AITurret)
    z.name = "82-BM-37 Turret"
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_iron_sights", False)
    z.is_turret = True
    # center means the tube is not a separate hit volume. the mortar
    # is the vehicle; crew hits go through the open passenger compartment.
    z.ai.vehicle_mount_side = "center"
    z.ai.turret_accuracy = 1
    z.ai.turret_armor["top"] = [0, 0, 0]
    z.ai.turret_armor["bottom"] = [0, 0, 0]
    z.ai.turret_armor["left"] = [0, 0, 0]
    z.ai.turret_armor["right"] = [0, 0, 0]
    z.ai.turret_armor["front"] = [0, 0, 0]
    z.ai.turret_armor["rear"] = [0, 0, 0]
    z.ai.position_offset = [0, 0]
    z.ai.rotation_range = [-30, 30]
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "82mm_bm37", False)
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    z.ai.primary_weapon.ai.smoke_offset = [-0, 0]
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon_reload_speed = 3
    z.ai.primary_turret = True
    z.no_save = True
    return z
