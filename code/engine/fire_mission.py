'''
repo : https://github.com/openmarmot/twe

notes : FireMission is a set of instructions for indirect fire on a area
'''

# import built in modules
import copy


class FireMission():
    def __init__(self,world_coords,expiration_time,target_obj):
        # coordinates of the strike (snapshot - do not share caller's list)
        self.world_coords=copy.copy(world_coords)

        # reference to target object for mission tracking
        self.target_obj=target_obj

        self.rounds_requested=10
        self.rounds_fired=0

        # world.world_seconds time when strike request expires
        self.expiration_time=expiration_time