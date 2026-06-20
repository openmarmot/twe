"""
german_sd_kfz_234/1 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_sd_kfz_234/1")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_sd_kfz_234_base", False)
    z.name = "Sd.Kfz.234/1"
    z.ai.passenger_compartment_ammo_racks = True
    z.ai.requires_afv_training = True
    z.ai.is_transport = False
    turret = engine.world_builder.spawn_object(world, world_coords, "234_1_turret", True)
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z

    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = turret

    z.ai.vehicle_crew.append(role)

    role = VehicleRole("commander", z)
    role.is_commander = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("assistant_gunner", z)
    role.is_assistant_gunner = True
    z.ai.vehicle_crew.append(role)
    # mg ammo
    for b in range(10):
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg34_belt", False))
    # armor piercing belt
    if random.randint(0, 1) == 1:
        belt = engine.world_builder.spawn_object(world, world_coords, "mg34_belt", False)
        engine.world_builder.load_magazine(world, belt, "7.92x57_SMK")
        z.add_inventory(belt)
    return z
