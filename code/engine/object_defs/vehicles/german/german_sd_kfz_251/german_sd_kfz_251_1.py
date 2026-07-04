"""
german_sd_kfz_251/1 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_sd_kfz_251/1")
def create(world, world_coords):
    # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
    z = engine.world_builder.spawn_object(world, world_coords, "german_sd_kfz_251_base", False)
    z.name = "Sd.Kfz.251/1"
    turret = engine.world_builder.spawn_object(world, world_coords, "sd_kfz_251_mg34_turret", True)
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z
    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)
    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = turret
    role.seat_visible = True
    role.seat_offset = [-3, 0]
    z.ai.vehicle_crew.append(role)

    # commander for threat assessment / self-preservation (new commander AI behaviors)
    role = VehicleRole("commander", z)
    role.is_commander = True
    role.seat_visible = False
    z.ai.vehicle_crew.append(role)

    # assistant gunner / radio operator / etc
    role = VehicleRole("assistant_gunner", z)
    role.is_assistant_gunner = True
    role.seat_visible = True
    role.seat_rotation = 90
    role.seat_offset = [49, -3]
    z.ai.vehicle_crew.append(role)

    passenger_positions = [
        [4, 10],
        [12, 10],
        [21, 10],
        [35, 10],
        [51, 10],
        [4, -10],
        [12, -10],
        [21, -10],
        [35, -10],
        [51, -10],
    ]
    passenger_rotation = [90, 90, 90, 90, 90, 270, 270, 270, 270, 270]
    for x in range(9):
        role = VehicleRole("passenger", z)
        role.is_passenger = True
        role.seat_visible = True
        role.seat_rotation = passenger_rotation.pop()
        role.seat_offset = passenger_positions.pop()
        z.ai.vehicle_crew.append(role)

    # mg ammo (drums in old for this variant)
    for b in range(11):
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg34_drum_magazine", False))

    # armor piercing belt
    if random.randint(0, 1) == 1:
        belt = engine.world_builder.spawn_object(world, world_coords, "mg34_belt", False)
        engine.world_builder.load_magazine(world, belt, "7.92x57_SMK")
        z.add_inventory(belt)
    return z
