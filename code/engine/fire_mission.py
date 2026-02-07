'''
repo : https://github.com/openmarmot/twe

notes : FireMission is a set of instructions for indirect fire on a area
'''

class FireMission():
    def __init__(self,world_coords,expiration_time,target_obj):
        # coordinates of the strike
        self.world_coords=world_coords

        # reference to target object for mission tracking
        self.target_obj=target_obj

        self.rounds_requested=10
        self.rounds_fired=0

        # world.world_seconds time when strike request expires
        self.expiration_time=expiration_time