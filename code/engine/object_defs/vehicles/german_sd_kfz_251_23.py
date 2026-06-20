"""
german_sd_kfz_251/23 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_sd_kfz_251/23")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_sd_kfz_251_base", False)
    z.name = "Sd.Kfz.251/23"
    z.ai.passenger_compartment_ammo_racks = True
    z.ai.requires_afv_training = True
    z.ai.is_transport = False
    turret = engine.world_builder.spawn_object(world, world_coords, "234_1_turret", True)
    # reset position offset to match this vehicle
    turret.ai.position_offset = [12, 0]
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z

    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = turret
    role.seat_visible = False
    role.seat_offset = [0, 0]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("commander", z)
    role.is_commander = True
    role.seat_visible = False
    role.seat_rotation = 90
    role.seat_offset = [4, 10]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("assistant_gunner", z)
    role.is_assistant_gunner = True
    role.seat_visible = False
    role.seat_rotation = 90
    role.seat_offset = [12, 10]
    z.ai.vehicle_crew.append(role)

    # mg ammo
    for b in range(10):
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg34_belt", False))

    # armor piercing belt
    if random.randint(0, 1) == 1:
        belt = engine.world_builder.spawn_object(world, world_coords, "mg34_belt", False)
        engine.world_builder.load_magazine(world, belt, "7.92x57_SMK")
        z.add_inventory(belt)

    z.ai.ammo_rack_capacity = 30
    # AP
    for b in range(15):
        z.ai.ammo_rack.append(
            engine.world_builder.spawn_object(world, world_coords, "2cm_kwk38_l55_magazine", False)
        )
    # HE
    for b in range(15):
        temp = engine.world_builder.spawn_object(world, world_coords, "2cm_kwk38_l55_magazine", False)
        engine.world_builder.load_magazine(world, temp, "20x138_HE")
        z.ai.ammo_rack.append(temp)
    return z
