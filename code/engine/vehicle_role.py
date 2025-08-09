'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : describes a vehicle role
'''

class VehicleRole():

    def __init__(self,role_name,vehicle):

        self.role_name=role_name

        # - clarify what the role can do -
        # these align with specific code in ai_human
        self.is_driver=False
        self.is_gunner=False
        self.is_assistant_gunner=False
        self.is_radio_operator=False
        self.is_commander=False
        self.is_passenger=False
        self.is_indirect_fire_gunner=False

        # object references 
        self.vehicle=vehicle
        self.turret=None
        self.radio=None

        # who is in this roles
        self.role_occupied=False
        self.human=None

        # seat information
        self.seat_visible=False
        # rotation relative to the vehicle
        self.seat_rotation=0
        # offset relative to the vehicle
        self.seat_offset=[0,0]
