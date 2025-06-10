'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : describes a tactical role
'''

class VehicleOrder():

    def __init__(self):

        # - order type : should be exactly one of these -
        self.order_drive_to_coords=False
        self.order_tow_object=False

        # additional details

        self.world_coords=[0,0]
        self.target_object=None # a world_object