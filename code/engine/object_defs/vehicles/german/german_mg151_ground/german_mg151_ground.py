"""
german_mg151_ground object definition

repo : https://github.com/openmarmot/twe

notes :
One MG 151/20 on an improvised ground mount. Luftwaffe stocks of the
aircraft gun were put on pipes, logs, and other local pedestals for
airfield and object defense. The triple mount was the systematic
version. This one is a single gun.
The sprite is the sMG42. Crew push it, same as that mount.
The gun is about 42 kg. The improvised carriage brings it to 75 kg.
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_vehicle import AIVehicle
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


def _add_belts(world, world_coords, vehicle, projectile, count):
    for _ in range(count):
        belt = engine.world_builder.spawn_object(
            world, world_coords, "mg151_20_belt", False
        )
        if projectile is not None:
            engine.world_builder.load_magazine(world, belt, projectile, True)
        # inventory, not the ammo rack. a single gun reload takes the belt
        # from inventory. the sMG42 stores its belts the same way.
        vehicle.add_inventory(belt)


@register_object("german_mg151_ground")
def create(world, world_coords):
    z = WorldObject(world, ["smg42_base"], AIVehicle)
    z.name = "MG 151/20 Ground Mount"
    z.is_vehicle = True
    z.is_towable = False
    turret = engine.world_builder.spawn_object(
        world, world_coords, "mg151_ground_turret", True
    )
    turret.ai.position_offset = [0, 0]
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z

    role = VehicleRole("driver", z)
    role.is_driver = True
    role.seat_visible = True
    role.seat_offset = [28.8, 20.0]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = turret
    role.seat_visible = True
    role.seat_offset = [19.6, -0.4]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("commander", z)
    role.is_commander = True
    role.seat_visible = True
    role.seat_offset = [27.6, -28.0]
    z.ai.vehicle_crew.append(role)

    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "bicycle_pedals", False)
    )
    # crew push, 75 kg. a step slower than the 32 kg Lafette (90).
    z.ai.max_speed = 85
    z.ai.max_offroad_speed = 85
    z.ai.open_top = True
    # z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
    z.ai.rotation_speed = 40.0
    z.collision_radius = 50
    z.bounding_circles.append([[0.0, 0.0], 25])
    z.weight = 75
    z.drag_coefficient = 0.9
    z.frontal_area = 5
    z.rotation_angle = float(random.randint(0, 359))
    z.ai.ammo_rack_capacity = 12
    # the gun starts on the mine shell. AP stays in the pile.
    # 5 mine belts (one on the gun), 2 AP, 1 APHE. 1,600 rounds.
    engine.world_builder.load_magazine(
        world,
        turret.ai.primary_weapon.ai.magazine,
        "20x82_M-Geschoss",
        True,
    )
    _add_belts(world, world_coords, z, "20x82_M-Geschoss", 4)
    _add_belts(world, world_coords, z, None, 2)
    _add_belts(world, world_coords, z, "20x82_Pzsprgr", 1)
    z.ai.max_wheels = 0
    z.ai.max_spare_wheels = 0
    return z
