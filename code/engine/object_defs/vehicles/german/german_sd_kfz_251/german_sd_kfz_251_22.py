"""
german_sd_kfz_251/22 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_sd_kfz_251/22")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_sd_kfz_251_base", False)
    z.name = "Sd.Kfz.251/22"
    z.ai.passenger_compartment_ammo_racks = True
    z.ai.requires_afv_training = True
    z.ai.is_transport = False
    turret = engine.world_builder.spawn_object(world, world_coords, "251_pak40_turret", True)
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z

    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = turret
    role.seat_visible = True
    role.seat_offset = [19, -6]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("commander", z)
    role.is_commander = True
    role.seat_visible = True
    role.seat_rotation = 90
    role.seat_offset = [30, 9]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("assistant_gunner", z)
    role.is_assistant_gunner = True
    role.seat_visible = True
    role.seat_rotation = 90
    role.seat_offset = [49, -3]
    z.ai.vehicle_crew.append(role)

    z.ai.ammo_rack_capacity = 24
    # pak ammo
    for b in range(20):
        z.ai.ammo_rack.append(
            engine.world_builder.spawn_object(world, world_coords, "75mm_pak40_magazine", False)
        )
    for b in range(4):
        temp = engine.world_builder.spawn_object(world, world_coords, "75mm_pak40_magazine", False)
        engine.world_builder.load_magazine(world, temp, "Sprgr_34_75_L48")
        z.ai.ammo_rack.append(temp)
    return z
