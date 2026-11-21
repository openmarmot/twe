"""
mg151_ground_turret object definition

repo : https://github.com/openmarmot/twe

notes :
A single MG 151/20 on an improvised ground mount.
Luftwaffe airfield and object defense, later in the war.
The sprite is the sMG42 until a mount is drawn.
Armor stays at zero until that art shows a shield.
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("mg151_ground_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(world, ["smg42_gun"], AITurret)
    z.name = "MG 151/20 Ground Mount"
    z.ai.gun_sight = engine.world_builder.spawn_object(
        world, world_coords, "optic_iron_sights", False
    )
    z.is_turret = True
    z.ai.vehicle_mount_side = "top"
    z.ai.small = True
    # improvised pipe or log. less steady than the Drilling's sighted pedestal
    z.ai.turret_accuracy = 6
    z.ai.turret_armor["top"] = [0, 0, 0]
    z.ai.turret_armor["bottom"] = [0, 0, 0]
    z.ai.turret_armor["left"] = [0, 0, 0]
    z.ai.turret_armor["right"] = [0, 0, 0]
    z.ai.turret_armor["front"] = [0, 0, 0]
    z.ai.turret_armor["rear"] = [0, 0, 0]
    z.ai.position_offset = [0, 0]
    # a pedestal tracks all the way around. the Lafette cradle does not.
    z.ai.rotation_range = [-360, 360]
    z.ai.rotation_speed = 30  # hand traverse, no gearing
    gun = engine.world_builder.spawn_object(world, world_coords, "mg151_20", False)
    gun.ai.equipper = z
    gun.ai.smoke_on_fire = True
    gun.ai.smoke_type = "cannon"
    gun.ai.smoke_offset = [-40, 0]
    # 750 rpm would fill the map with brass. the Drilling does the same.
    gun.ai.spawn_case = False
    z.ai.primary_weapon = gun
    # one 200-round belt. the triple mount is 25s for three belts.
    z.ai.primary_weapon_reload_speed = 15
    z.ai.primary_turret = True
    z.no_save = True
    return z
