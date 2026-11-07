"""
251_21_turret object definition

repo : https://github.com/openmarmot/twe

notes :
The Drilling sat on a pedestal in the passenger compartment.
Traverse is a full circle, shoulder aimed, -5 to +49 degrees.
Elevation is not modeled. The sprite is the 251 pintle shield until
the Drilling shield is drawn.
US report: 3x telescope, 8 degree field. That sight is not its own object.
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


def _create(world, world_coords, weapon_id, name):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(
        world, ["sd_kfz_251_mg34_turret", "sd_kfz_251_mg34_turret"], AITurret
    )
    z.name = name
    z.is_turret = True
    # 3x, 8 degree field, from the US Aberdeen report on the captured mount
    sight = engine.world_builder.spawn_object(
        world, world_coords, "optic_iron_sights", False
    )
    sight.name = "3x telescopic sight"
    sight.ai.magnification = 3
    sight.ai.field_of_view = 8
    sight.ai.optical_quality = 1.0
    z.ai.gun_sight = sight
    z.ai.small = True
    z.ai.vehicle_mount_side = "top"
    z.ai.turret_accuracy = 4
    # shield thickness is not from a measured plate. the mount was a light shield.
    z.ai.turret_armor["top"] = [0, 0, 0]
    z.ai.turret_armor["bottom"] = [8, 0, 0]
    z.ai.turret_armor["left"] = [6, 20, 0]
    z.ai.turret_armor["right"] = [6, 20, 0]
    z.ai.turret_armor["front"] = [8, 20, 0]
    z.ai.turret_armor["rear"] = [0, 0, 0]
    # passenger compartment, aft of the driver's roof. positive x is rearward.
    z.ai.position_offset = [18, 0]
    z.ai.rotation_range = [-360, 360]
    z.ai.rotation_speed = 40  # shoulder traverse, no gearing
    z.ai.primary_weapon = engine.world_builder.spawn_object(
        world, world_coords, weapon_id, False
    )
    z.ai.primary_weapon.ai.equipper = z
    for barrel in z.ai.primary_weapon.ai.barrels:
        barrel.ai.equipper = z
    # one action changes all three belts
    z.ai.primary_weapon_reload_speed = 25
    z.ai.primary_turret = True
    z.no_save = True
    return z


@register_object("251_21_turret")
def create(world, world_coords):
    return _create(
        world, world_coords, "mg151_20_drilling", "Sd.Kfz.251/21 Turret"
    )


@register_object("251_21_15_turret")
def create_15(world, world_coords):
    return _create(
        world, world_coords, "mg151_15_drilling", "Sd.Kfz.251/21 Turret"
    )
