'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : describes a tactical role
'''

class TacticalOrder():

    def __init__(self):

        # - order type : should be exactly one of these -
        # not in use yet
        self.order_move_towed_object=False

        # ai will move to area and stay until world_area.is_contested==False
        self.order_defend_area=False
        self.order_move_to_location=False

        # additional details
        self.world_area=None
        self.world_coords=None # [0,0]
        self.target_object=None # a world_object