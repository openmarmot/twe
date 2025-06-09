'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : describes a tactical role
'''

class TacticalOrder():

    def __init__(self):

        # - order type : should be exactly one of these -
        self.order_move_towed_object=False


        # additional details

        self.destination_coords=[0,0]
        self.target_object=None # a world_object