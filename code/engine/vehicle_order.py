'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : VehicleOrder is a simplified task for a vehicle driver
it is set on vehicle entry, and wiped on vehicle exit
'''

class VehicleOrder():

    def __init__(self):

        # - order type : should be exactly one of these -
        self.order_drive_to_coords=False
        self.order_tow_object=False

        # additional details
        self.exit_vehicle_when_finished=False
        self.world_coords=[0,0]
        self.target_object=None # a world_object