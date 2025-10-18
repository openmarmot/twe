'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : FireMission is a set of instructions for indirect fire on a area
'''

class FireMission():
    def __init__(self,world_coords,expiration_time):
        # coordinates of the strike
        self.world_coords=world_coords

        self.rounds_requested=10
        self.rounds_fired=0

        # world.world_seconds time when strike request expires
        self.expiration_time=expiration_time