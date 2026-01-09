
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : the ai_human code for decisions when in vehicles
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
from ai.ai_human_vehicle_gunner import AIHumanVehicleGunner
from ai.ai_human_vehicle_driver import AIHumanVehicleDriver
#import engine.global_exchange_rates

class AIHumanVehicle():
    def __init__(self, owner):
        self.owner=owner

        self.role_driver=AIHumanVehicleDriver(self.owner)
        self.role_gunner=AIHumanVehicleGunner(self.owner)

        


    #---------------------------------------------------------------------------
    def think_vehicle_hit(self):
        '''vehicle occupant reacts to the vehicle being hit'''
        # for this to be called the vehicle_hits list is not empty
        
        # set it to whatever the first one is
        important_hit=self.owner.ai.memory['task_vehicle_crew']['vehicle_hits'][0]

        # check if anything is more important
        for hit in self.owner.ai.memory['task_vehicle_crew']['vehicle_hits']:
            if hit.penetrated:
                important_hit=hit
                break

            if hit.projectile_shooter:
                if hit.projectile_shooter.is_turret:
                    important_hit=hit
        
        # we can now clear the list
        self.owner.ai.memory['task_vehicle_crew']['vehicle_hits']=[]

        role=self.owner.ai.memory['task_vehicle_crew']['vehicle_role']

        if important_hit.penetrated:
            self.owner.ai.morale-=10
            if self.owner.ai.morale_check() is False:
                self.owner.ai.speak('The vehicle is hit! Bail out!!')
                self.owner.ai.switch_task_exit_vehicle()
                return
            
            if role.is_gunner:
                if hit.projectile_shooter:
                    if hit.projectile_shooter.is_turret:
                        self.owner.ai.memory['task_vehicle_crew']['target']=hit.projectile_shooter.ai.vehicle
                    else:
                        self.owner.ai.memory['task_vehicle_crew']['target']=hit.projectile_shooter
                    return
            if role.is_passenger:
                # i feel that passengers should probably bail if there is a penetration 
                # really no reason for them to do anything else
                self.owner.ai.speak('The vehicle is hit! Bail out!!')
                self.owner.ai.switch_task_exit_vehicle()
                return
        else:
            # not a penetration, so less of a reaction 

            if role.is_gunner:
                if hit.projectile_shooter:
                    if hit.projectile_shooter.is_turret:
                        self.owner.ai.memory['task_vehicle_crew']['target']=hit.projectile_shooter.ai.vehicle
                        return
                    # only engage humans if we aren't doing anything else
                    if self.owner.ai.memory['task_vehicle_crew']['target'] is None:
                        self.owner.ai.memory['task_vehicle_crew']['target']=hit.projectile_shooter
                        return
                    
            # maybe add some morale damage?

    #---------------------------------------------------------------------------
    def think_vehicle_role_commander(self):
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

    #---------------------------------------------------------------------------
    def think_vehicle_role_passenger(self):
        '''think.. as a passenger'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle

        if self.owner.ai.human_targets or self.owner.ai.vehicle_targets:
            if vehicle.ai.current_speed<20:
                self.owner.ai.switch_task_exit_vehicle()

    #---------------------------------------------------------------------------
    def think_vehicle_role_radio_operator(self):
        # note radio.ai.radio_operator set by switch_task_vehicle_crew
        # not a ton that we really need to do here atm

        # !! radio specific stuff should be handled under a ai_human role so that humans with 
        # radios who are not in vehicles can also call it

        vehicle_role=self.owner.ai.memory['task_vehicle_crew']['vehicle_role']
        vehicle=vehicle_role.vehicle
        radio=vehicle.ai.radio

        if radio is None:
            # should we try to do something else?
            return
            
        # gunner also uses this, do not want to over write 
        if vehicle_role.is_gunner is False:
            self.owner.ai.memory['task_vehicle_crew']['current_action']='Beep boop. operating the radio'
        
        self.owner.ai.radio_operator_ai.update()


    #---------------------------------------------------------------------------
    def update_task_vehicle_crew(self):
        '''update task_vehicle_crew'''

        # this is for all crew
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        if vehicle.ai.vehicle_disabled:
            self.owner.ai.switch_task_exit_vehicle()
            return

        role=self.owner.ai.memory['task_vehicle_crew']['vehicle_role']

        if self.owner.is_player:
            self.update_task_vehicle_crew_player()
            return
        
        last_think_time=self.owner.ai.memory['task_vehicle_crew']['last_think_time']
        think_interval=self.owner.ai.memory['task_vehicle_crew']['think_interval']

        # --- think ----
        if self.owner.world.world_seconds-last_think_time>think_interval:
            # reset time
            self.owner.ai.memory['task_vehicle_crew']['last_think_time']=self.owner.world.world_seconds

            # universal check for empty priority spots
            if role.is_driver is False and role.is_gunner is False:
                # check if there are any empty roles
                for available_role in vehicle.ai.vehicle_crew:
                    if available_role.role_occupied is False:
                        if available_role.is_driver or available_role.is_gunner:
                            self.owner.ai.switch_task_vehicle_crew(vehicle,None)
                            return
                        
            # universal respond to vehicle being hit
            # this probably needs to be kept seperate from the role thinks as there is role overlap
            if len(self.owner.ai.memory['task_vehicle_crew']['vehicle_hits'])>0:
                self.think_vehicle_hit()
            
            # double check that we haven't decided to do something else like exit the vehicle
            if self.owner.ai.memory['current_task']!='task_vehicle_crew':
                return

            # note that roles can have multiple functions now
            if role.is_driver:
                # driver needs a fast refresh for smooth vehicle controls
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(0.1,0.2)
                self.role_driver.think()
            if role.is_gunner:
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(0.1,0.3)
                self.role_gunner.think()
            if role.is_passenger:
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(1.3,3.5)
                self.think_vehicle_role_passenger()
            if role.is_radio_operator:
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(0.3,0.7)
                self.think_vehicle_role_radio_operator()
            if role.is_commander:
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(1.1,2.5)
                self.think_vehicle_role_commander()

            # the squad lead has some stuff to do independent of their vehicle role
            if self.owner==self.owner.ai.squad.squad_leader:
                # if we don't have a vehicle order, check to see if we can create 
                # one from tactical orders
                if self.owner.ai.memory['task_vehicle_crew']['vehicle_order'] is None:
                    self.owner.ai.squad_leader_review_orders()


        else:
            # some roles will want to do something every update cycle

            if role.is_gunner:
                self.role_gunner.action()
                
            if role.is_driver:
                self.role_driver.action()

    #---------------------------------------------------------------------------
    def update_task_vehicle_crew_player(self):
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        role=self.owner.ai.memory['task_vehicle_crew']['vehicle_role']
        if role.is_gunner:
            # handle vehicle turret gun reloads for the player
            turret=role.turret
            if self.owner.ai.memory['task_vehicle_crew']['current_action']=='reloading primary weapon':
                if (self.owner.world.world_seconds-self.owner.ai.memory['task_vehicle_crew']['reload_start_time'] 
                > turret.ai.primary_weapon_reload_speed):
                    self.owner.ai.reload_weapon(turret.ai.primary_weapon,vehicle,None)
                    self.owner.ai.memory['task_vehicle_crew']['current_action']='none'
                else:
                    return
            if self.owner.ai.memory['task_vehicle_crew']['current_action']=='reloading coax gun':
                if (self.owner.world.world_seconds-self.owner.ai.memory['task_vehicle_crew']['reload_start_time'] 
                > turret.ai.coaxial_weapon_reload_speed):
                    self.owner.ai.reload_weapon(turret.ai.coaxial_weapon,vehicle,None)
                    self.owner.ai.memory['task_vehicle_crew']['current_action']='none'
                else:
                    return
            
            # this action is set by world. triggered by hitting 'w'
            if self.owner.ai.memory['task_vehicle_crew']['current_action']=='rotate turret':
                if self.rotate_turret(turret,self.owner.ai.memory['task_vehicle_crew']['calculated_turret_angle']):
                    # rotation achieved. we can remove this action
                    self.owner.ai.memory['task_vehicle_crew']['current_action']=''
