'''
repo : https://github.com/openmarmot/twe

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

        # object references 
        self.vehicle=vehicle
        self.turret=None
        self.radio=None

        # who is in this roles
        self.role_occupied=False
        self.human=None

        # seat information
        self.seat_visible=False
        # if true, seat_offset and seat_rotation are relative to the turret (role.turret) instead of vehicle
        self.seat_rotates_with_turret=False
        # rotation relative to the vehicle (or turret if seat_rotates_with_turret)
        self.seat_rotation=0
        # offset relative to the vehicle (or turret if seat_rotates_with_turret)
        self.seat_offset=[0,0]
