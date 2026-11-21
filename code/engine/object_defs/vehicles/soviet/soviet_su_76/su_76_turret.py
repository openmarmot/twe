"""
su_76_turret object definition

repo : https://github.com/openmarmot/twe

ZiS-3 mount in the SU-76M casemate. The barrel sprite points up.
Pivot is the trunnion, at the center of su_76_gun.png.
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("su_76_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(world, ["su_76_gun"], AITurret)
    z.name = "SU-76 Gun"
    # Soviet 76 mm family sight. the vehicle used a panoramic sight and a telescope.
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_tmfd_7", False)
    z.is_turret = True
    z.ai.vehicle_mount_side = "front"
    z.ai.turret_accuracy = 2
    # gun shield is about 15 mm. stored vertical so a center hit is not thickened.
    # top and bottom stay open. the casemate plates are on the hull.
    z.ai.turret_armor["top"] = [0, 0, 0]
    z.ai.turret_armor["bottom"] = [0, 0, 0]
    z.ai.turret_armor["left"] = [15, 0, 0]
    z.ai.turret_armor["right"] = [15, 0, 0]
    z.ai.turret_armor["front"] = [15, 0, 0]
    z.ai.turret_armor["rear"] = [15, 0, 0]
    # 8 px forward of the hull center, on the casemate front wall.
    # nudge in image_tool if the shield sits off the plate.
    z.ai.position_offset = [16.8, 0.8]
    z.image_rotation_offset = [0.0, 35.2]
    # handwheel. 15 degrees left and right.
    z.ai.rotation_range = [-15, 15]
    z.ai.rotation_speed = 8
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "76mm_m1940_f34", False)
    z.ai.primary_weapon.name = "76mm ZiS-3"
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    # drawn muzzle is about 40 px forward of the trunnion
    z.ai.primary_weapon.ai.smoke_offset = [-40, 0]
    z.ai.primary_weapon.ai.spawn_case = False
    # same piece as the towed ZiS-3. starts in direct fire.
    z.ai.primary_weapon.ai.indirect_range = 13000
    z.ai.primary_weapon.ai.indirect_fire = True
    z.ai.primary_weapon.ai.indirect_fire_mode = False
    z.ai.primary_turret = True
    z.ai.primary_weapon_reload_speed = 20
    z.no_save = True
    return z
