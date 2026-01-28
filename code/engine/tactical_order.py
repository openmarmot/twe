'''
repo : https://github.com/openmarmot/twe

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

        # defend order state tracking
        # True once the area has been contested at least once
        # defend order only completes when was_contested=True AND is_contested=False
        self.was_contested=False

        # direction enemies are expected from (rotation angle in degrees)
        # used so defenders can face the right direction
        self.threat_direction=None