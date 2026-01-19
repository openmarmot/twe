'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : vehicle commander code
'''

#import built in modules
import random
import copy

#import custom packages
import engine.math_2d
import engine.world_builder
import engine.log
import engine.penetration_calculator
from engine.vehicle_order import VehicleOrder
from engine.tactical_order import TacticalOrder

#import engine.global_exchange_rates

class AIHumanVehicleCommander():
    def __init__(self, owner):
        self.owner=owner

    #---------------------------------------------------------------------------
    def think(self):
        '''commander role'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle

        # determine what the primary weapon is and primary gunner is
        primary_gunner=None
        for role in vehicle.ai.vehicle_crew:
            if role.is_gunner and role.role_occupied:
                if role.turret:
                    if role.turret.ai.primary_turret:
                        primary_gunner=role
                        break

        # for now we have no actions if we don't have a primary gunner
        if primary_gunner is None:
            return

        max_armor=0
        biggest_threat=None
        for v in self.owner.ai.vehicle_targets:
            if v.ai.vehicle_armor['front'][0]>max_armor:
                biggest_threat=v
        
        if biggest_threat:
            engage_primary,engage_primary_reason=self.owner.ai.calculate_engagement(primary_gunner.turret.ai.primary_weapon,biggest_threat)
            if engage_primary and primary_gunner.human.ai.memory['task_vehicle_crew']['target']!=biggest_threat :
                # tell the gunner to engage
                primary_gunner.human.ai.memory['task_vehicle_crew']['target']=biggest_threat
                self.owner.ai.speak(f'Gunner, prioritize the {biggest_threat.name} ')

            # check if we should re-orientate the vehicle to face the biggest threat