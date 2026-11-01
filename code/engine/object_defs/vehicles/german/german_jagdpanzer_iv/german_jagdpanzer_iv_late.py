"""
german_jagdpanzer_iv_late object definition

repo : https://github.com/openmarmot/twe

May 1944 Jagdpanzer IV, from chassis 320301. Same Pak 39 L/48.
The casemate front is 80 mm and the casemate sides are 40 mm.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_jagdpanzer_iv_late")
def create(world, world_coords):
    # ref : Chamberlain and Doyle, Encyclopedia of German Tanks
    # upper hull front and superstructure front to 80 mm.
    # superstructure sides from 30 mm to 40 mm.
    # the lower nose stayed 50 mm. the gun, rack, and crew are unchanged.
    z = engine.world_builder.spawn_object(world, world_coords, "german_jagdpanzer_iv", False)
    z.name = "Jagdpanzer IV Late"
    # 80 mm at 50 degrees is about 124 mm line of sight.
    z.ai.passenger_compartment_armor["front"] = [80, 50, 0]
    z.ai.passenger_compartment_armor["left"] = [40, 30, 0]
    z.ai.passenger_compartment_armor["right"] = [40, 30, 0]
    # the extra plate is about a tonne. published weight is 24 to 25 tonnes.
    z.weight = 25000
    return z
