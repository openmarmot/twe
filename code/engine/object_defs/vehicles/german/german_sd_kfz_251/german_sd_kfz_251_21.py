"""
german_sd_kfz_251/21 object definition

repo : https://github.com/openmarmot/twe

notes :
mittlerer Schützenpanzerwagen (Drilling MG 151), Gerät 921.
Production from August 1944. Early guns were MG 151/15. Later guns were
MG 151/20 after 15mm ammunition was dropped.
US report: 3,000 rounds in belts. In 6, 28 September 1944, authorized
325 AP and 2,675 incendiary for the 15mm. Belts here are 200 rounds, so
the AP stash is three belts rather than 325 loose rounds.
Crew 4. The compartment holds the mount and the ammunition.
"""

# import custom packages
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


def _add_belts(world, world_coords, vehicle, belt_id, projectile, count):
    for _ in range(count):
        belt = engine.world_builder.spawn_object(world, world_coords, belt_id, False)
        if projectile is not None:
            engine.world_builder.load_magazine(world, belt, projectile, True)
        vehicle.ai.ammo_rack.append(belt)


def _load_guns(world, vehicle, projectile):
    for barrel in vehicle.ai.turrets[0].ai.primary_weapon.ai.barrels:
        engine.world_builder.load_magazine(
            world, barrel.ai.magazine, projectile, True
        )


def _create(world, world_coords, name, turret_id, belt_id, he_round, special):
    z = engine.world_builder.spawn_object(
        world, world_coords, "german_sd_kfz_251_base", False
    )
    z.name = name
    # wardrawings combat weight for the Ausf. D Drilling
    z.weight = 8800
    z.ai.passenger_compartment_ammo_racks = True
    z.ai.requires_afv_training = True
    z.ai.is_transport = False
    turret = engine.world_builder.spawn_object(world, world_coords, turret_id, True)
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z

    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = turret
    role.seat_visible = True
    role.seat_offset = [34, 0]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("commander", z)
    role.is_commander = True
    role.seat_visible = True
    role.seat_rotation = 90
    role.seat_offset = [26, 12]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("assistant_gunner", z)
    role.is_assistant_gunner = True
    role.seat_visible = True
    role.seat_rotation = 270
    role.seat_offset = [26, -12]
    z.ai.vehicle_crew.append(role)

    # 3,000 rounds: 3 belts on the guns, 12 in the rack.
    # the guns start on the thin-walled round. AP is in the rack.
    _load_guns(world, z, he_round)
    _add_belts(world, world_coords, z, belt_id, None, 3)
    if special is not None:
        _add_belts(world, world_coords, z, belt_id, special, 1)
        _add_belts(world, world_coords, z, belt_id, he_round, 8)
    else:
        _add_belts(world, world_coords, z, belt_id, he_round, 9)
    z.ai.ammo_rack_capacity = 12
    return z


@register_object("german_sd_kfz_251/21")
def create(world, world_coords):
    # MG 151/20. The later production gun.
    # default belt is 20x82_Pzgr, so the three AP belts need no reload call.
    return _create(
        world,
        world_coords,
        "Sd.Kfz.251/21",
        "251_21_turret",
        "mg151_20_belt",
        "20x82_M-Geschoss",
        "20x82_Pzsprgr",
    )


@register_object("german_sd_kfz_251/21_15")
def create_15(world, world_coords):
    # MG 151/15. The early production gun.
    return _create(
        world,
        world_coords,
        "Sd.Kfz.251/21 (15mm)",
        "251_21_15_turret",
        "mg151_15_belt",
        "15x96_HE",
        None,
    )
