"""
german_sd_kfz_251/9 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_sd_kfz_251/9")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_sd_kfz_251_base", False)
    z.name = "Sd.Kfz.251/9 Stummel"
    z.ai.passenger_compartment_ammo_racks = True
    z.ai.requires_afv_training = True
    z.ai.is_transport = False
    turret = engine.world_builder.spawn_object(world, world_coords, "251_9_turret", True)
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z

    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = turret
    role.seat_visible = True
    role.seat_offset = [17, 0]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("commander", z)
    role.is_commander = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("assistant_gunner", z)
    role.is_assistant_gunner = True
    z.ai.vehicle_crew.append(role)

    z.ai.ammo_rack_capacity = 52
    # HE
    for b in range(40):
        z.ai.ammo_rack.append(
            engine.world_builder.spawn_object(world, world_coords, "75mm_kwk37_l24_magazine", False)
        )
    # HEAT
    for b in range(12):
        temp = engine.world_builder.spawn_object(world, world_coords, "75mm_kwk37_l24_magazine", False)
        engine.world_builder.load_magazine(world, temp, "HL_Gr_38A_L24")
        z.ai.ammo_rack.append(temp)
    return z
