'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : vehicle gunner code
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

class AIHumanVehicleGunner():
    def __init__(self, owner):
        self.owner=owner

        # -- firing pattern stuff
        # burst control keeps ai from shooting continuous streams
        self.current_burst=0 # int number of bullets shot in current burst
        self.max_burst=5

    #---------------------------------------------------------------------------
    def action(self):
        '''action - called by ai_human_vehicle.update_task_vehicle_crew()'''
        role=self.owner.ai.memory['task_vehicle_crew']['vehicle_role']

        # figure out what action we are taking 
        if self.owner.ai.memory['task_vehicle_crew']['target'] is None and self.owner.ai.memory['task_vehicle_crew']['engage_indirect_fire']:
                    self.action_engage_indirect_fire()

        if self.owner.ai.memory['task_vehicle_crew']['target'] is not None:
            if self.owner.ai.memory['task_vehicle_crew']['calculated_turret_angle'] is not None:
                self.action_engage_target()


    #---------------------------------------------------------------------------
    def action_engage_indirect_fire(self):
        turret=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].turret
        fire_mission=self.owner.ai.memory['task_vehicle_crew']['fire_missions'][0]

        # rotate turret towards target. true if rotation matches
        if self.rotate_turret(turret,self.owner.ai.memory['task_vehicle_crew']['calculated_turret_angle']):

            if turret.ai.handle_fire():
                fire_mission.rounds_fired+=1
                #engine.log.add_data('note',f'{turret.name} fired a indirect fire round',True)


        # thats pretty much it. think can stop the engagement when we've fired enough as indirect fire weapons are fairly slow firing

    #---------------------------------------------------------------------------
    def action_engage_target(self):
        # this is the action the vehicle gunner takes when it is NOT thinking
        # and has a target that is not None
        target=self.owner.ai.memory['task_vehicle_crew']['target']
        # the computed lead on the target
        turret=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].turret

        # rotate turret towards target. true if rotation matches
        if self.rotate_turret(turret,self.owner.ai.memory['task_vehicle_crew']['calculated_turret_angle']):
            if target.is_human:
                if target.ai.blood_pressure<1:
                    self.owner.ai.memory['task_vehicle_crew']['target']=None
                    self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'
                    return
            if target.is_vehicle:
                if target.ai.check_if_vehicle_is_occupied() is False or target.ai.vehicle_disabled:
                    self.owner.ai.memory['task_vehicle_crew']['target']=None
                    self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'
                    return

            # handle bursts and fire weapon
            if self.owner.ai.memory['task_vehicle_crew']['engage_primary_weapon']:
                if turret.ai.handle_fire():
                    self.current_burst+=1

            if self.owner.ai.memory['task_vehicle_crew']['engage_coaxial_weapon']:
                if turret.ai.handle_fire_coax():
                    self.current_burst+=1

            if self.current_burst>self.max_burst:
                # randomize burst length a little. this should create a random burst length from 3 to the max burst
                self.current_burst=random.randint(0,self.max_burst-3)

                # prevents the next burst from being sent at the same target while bullets are in flight
                # less of an issue with vehicle targets
                self.owner.ai.memory['task_vehicle_crew']['target']=None
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'

    #---------------------------------------------------------------------------
    def calculate_turret_aim(self,turret,target,weapon):
        '''calculates the correct turret angle to hit a target'''

        # this is where we should be applying the majority of the aim adjustments

        # target : world_object
        # turret : world_object with ai_turret

        aim_coords=target.world_coords
        # guess how long it will take for the bullet to arrive
        distance=engine.math_2d.get_distance(turret.world_coords,target.world_coords)

        # - determine adjustment - 
        adjust_max=0
        adjust_max+=weapon.ai.mechanical_accuracy

        if self.owner.ai.blood_pressure<100:
            adjust_max+=1
        if self.owner.ai.blood_pressure<50:
            adjust_max+=20

        if distance>1000:
            adjust_max+=1
        if distance>2000:
            adjust_max+=2
        if distance>3000:
            adjust_max+=5
        if distance>3500:
            adjust_max+=5

        if adjust_max<0:
            adjust_max=0

        # final results
        aim_coords=[aim_coords[0]+random.uniform(-adjust_max,adjust_max),aim_coords[1]+random.uniform(-adjust_max,adjust_max)]

         # we want the projectile to collide so aim point will be a bit past it
        weapon.ai.calculated_range=distance+random.randint(0,500)
        time_passed=distance/weapon.ai.muzzle_velocity
        if target.is_vehicle:

            if target.ai.current_speed>0:
                aim_coords=engine.math_2d.moveAlongVector(target.ai.current_speed,aim_coords,target.heading,time_passed)

        if target.is_human:
            if target.ai.in_vehicle():
                vehicle=target.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
                if vehicle.ai.current_speed>0:
                    aim_coords=engine.math_2d.moveAlongVector(vehicle.ai.current_speed,aim_coords,vehicle.heading,time_passed)
            else:
                if target.ai.memory['current_task']=='task_move_to_location':
                    destination=target.ai.memory['task_move_to_location']['destination']
                    aim_coords=engine.math_2d.moveTowardsTarget(target.ai.get_calculated_speed(),aim_coords,destination,time_passed)

        

        self.owner.ai.memory['task_vehicle_crew']['calculated_turret_angle']=engine.math_2d.get_rotation(turret.world_coords,aim_coords)

    #---------------------------------------------------------------------------
    def calculate_turret_aim_indirect(self,turret,target_position,weapon):
        '''calculates the correct turret angle to hit a target'''

        # this is where we should be applying the majority of the aim adjustments

        # target : world_object
        # turret : world_object with ai_turret

        aim_coords=target_position
        # guess how long it will take for the bullet to arrive
        distance=engine.math_2d.get_distance(turret.world_coords,target_position)

        # - determine adjustment - 
        adjust_max=0
        adjust_max+=weapon.ai.mechanical_accuracy

        if self.owner.ai.blood_pressure<100:
            adjust_max+=10
        if self.owner.ai.blood_pressure<50:
            adjust_max+=50

        if distance>1000:
            adjust_max+=10
        if distance>2000:
            adjust_max+=20
        if distance>3000:
            adjust_max+=30
        if distance>3500:
            adjust_max+=40

        if adjust_max<0:
            adjust_max=0

        # final results
        aim_coords=[aim_coords[0]+random.uniform(-adjust_max,adjust_max),aim_coords[1]+random.uniform(-adjust_max,adjust_max)]

         # we want the projectile to collide so aim point will be a bit past it
        weapon.ai.calculated_range=distance+random.randint(-adjust_max,adjust_max)

        self.owner.ai.memory['task_vehicle_crew']['calculated_turret_angle']=engine.math_2d.get_rotation(turret.world_coords,aim_coords)

    #---------------------------------------------------------------------------
    def check_vehicle_turret_rotation_real_angle(self,rotation_angle,turret):
        '''checks whether a vehicle turret can rotate to match a world angle'''
        # this checks whether a turret can rotate to match a angle given the turrets restraints
        # this is here because it is a human dead reckoning thing, not a function of the turret itself
        # returns true if the turret can rotate to this angle
        # reeturns false if it cannot
        angle_ok=False
        if rotation_angle>turret.ai.vehicle.rotation_angle+turret.ai.rotation_range[0]:
            if rotation_angle<turret.ai.vehicle.rotation_angle+turret.ai.rotation_range[1]:
                angle_ok=True

        # this also needs to check the turrets starting rotation.
        # for example, some turrets may face forward, some may face backward 

        return angle_ok
    
    #---------------------------------------------------------------------------
    def rotate_turret(self, turret, desired_angle):
        '''rotates a turret. returns True/False as to whether the turret is at the desired angle'''
        
        # Normalize both angles to [0, 360)
        current_angle = engine.math_2d.get_normalized_angle(turret.rotation_angle)
        desired_angle = engine.math_2d.get_normalized_angle(desired_angle)
        
        # Compute shortest signed difference (-180 to +180)
        diff = (desired_angle - current_angle + 180) % 360 - 180
        
        # If close enough, snap to exact angle and stop
        if abs(diff) <= 2:  # Adjust threshold if needed for precision
            turret.rotation_angle = desired_angle
            turret.ai.rotation_change = 0
            return True
        
        # Rotate in the direction of the shortest diff
        # Assumption: positive rotation_change increases angle (e.g., clockwise); adjust signs if your coord system is counterclockwise
        if diff > 0:
            turret.ai.handle_rotate_left()  # Increases angle
        else:
            turret.ai.handle_rotate_right()  # Decreases angle
        
        return False
    
    #---------------------------------------------------------------------------
    def think(self):
        '''think - called by ai_human_vehicle.update_task_vehicle_crew
        '''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        turret=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].turret

        if turret is None:
            print(f'turret none in {vehicle.name}, role {self.owner.ai.memory["task_vehicle_crew"]["vehicle_role"].role_name}')
            for b in vehicle.ai.vehicle_crew:
                print(f' role: {b.role_name} is_driver: {b.is_driver} is_gunner: {b.is_gunner} is_commander {b.is_commander}')

        # reset engagement commands 
        self.owner.ai.memory['task_vehicle_crew']['engage_primary_weapon'] = False
        self.owner.ai.memory['task_vehicle_crew']['engage_coaxial_weapon'] = False
        self.owner.ai.memory['task_vehicle_crew']['engage_indirect_fire'] = False

        # handle the reloading action
        if self.owner.ai.memory['task_vehicle_crew']['current_action']=='reloading primary weapon':
            if (self.owner.world.world_seconds-self.owner.ai.memory['task_vehicle_crew']['reload_start_time'] 
            > turret.ai.primary_weapon_reload_speed):
                self.owner.ai.memory['task_vehicle_crew']['current_action']='none'
                self.think_reload(turret.ai.primary_weapon)
            else:
                return
        if self.owner.ai.memory['task_vehicle_crew']['current_action']=='reloading coax gun':
            if (self.owner.world.world_seconds-self.owner.ai.memory['task_vehicle_crew']['reload_start_time'] 
            > turret.ai.coaxial_weapon_reload_speed):
                self.owner.ai.memory['task_vehicle_crew']['current_action']='none'
                self.think_reload(turret.ai.coaxial_weapon)
                
            else:
                return    

        out_of_ammo_primary=False
        out_of_ammo_coax=False
        turret_jammed=turret.ai.turret_jammed
        weapons_damaged=False
        weapons_jammed=False

        # check main gun ammo
        ammo_gun,ammo_inventory,magazine_count=self.owner.ai.check_ammo(turret.ai.primary_weapon,vehicle)
        if ammo_gun==0:
            if ammo_inventory>0:
                # start the reload process
                self.owner.ai.memory['task_vehicle_crew']['reload_start_time']=self.owner.world.world_seconds
                self.owner.ai.memory['task_vehicle_crew']['current_action']='reloading primary weapon'
                self.owner.ai.memory['task_vehicle_crew']['target']=None
                return
            else:
                out_of_ammo_primary=True

        # check coax ammo
        if turret.ai.coaxial_weapon is not None:
            ammo_gun,ammo_inventory,magazine_count=self.owner.ai.check_ammo(turret.ai.coaxial_weapon,vehicle)
            if ammo_gun==0:
                if ammo_inventory>0:
                    # start the reload process
                    self.owner.ai.memory['task_vehicle_crew']['reload_start_time']=self.owner.world.world_seconds
                    self.owner.ai.memory['task_vehicle_crew']['current_action']='reloading coax gun'
                    self.owner.ai.memory['task_vehicle_crew']['target']=None
                    return
                else:
                    out_of_ammo_coax=True
        else:
            out_of_ammo_coax=True

        # check weapons 
        if turret.ai.primary_weapon:
            if turret.ai.primary_weapon.ai.damaged:
                weapons_damaged=True
            if turret.ai.primary_weapon.ai.action_jammed:
                weapons_jammed=True
        if turret.ai.coaxial_weapon:
            if turret.ai.coaxial_weapon.ai.damaged:
                # don't want this because it soft locks the gunner
                #weapons_damaged=True
                # do this instead which will prevent engaging with the coax, but will still allow primary weapon engagement
                out_of_ammo_coax=True
            if turret.ai.coaxial_weapon.ai.action_jammed:
                weapons_jammed=True

        if out_of_ammo_coax and out_of_ammo_primary:
            self.owner.ai.memory['task_vehicle_crew']['current_action']='Out of Ammo'
            self.owner.ai.memory['task_vehicle_crew']['target']=None
            return
        
        if turret_jammed:
            # # if this was the primary turret the vehicle will be marked disabled.
            self.owner.ai.memory['task_vehicle_crew']['current_action']='Turret Jammed'
            self.owner.ai.memory['task_vehicle_crew']['target']=None
            return

        # need to figure out what we do if anything for a damaged coax 
        if weapons_damaged:
            # if this was the primary weapon in a primary turret the vehicle will be marked disabled (if not a transport)
            self.owner.ai.memory['task_vehicle_crew']['current_action']='Weapons Damaged'
            self.owner.ai.memory['task_vehicle_crew']['target']=None
            return
        
        if weapons_jammed:
            # this we can fix ourselves
            #if we are already in this state then consider it fixed 
            if self.owner.ai.memory['task_vehicle_crew']['current_action']=='Clearing weapon jam':
                if turret.ai.primary_weapon:
                    if turret.ai.primary_weapon.ai.action_jammed:
                        self.owner.ai.speak('fixing jammed gun')
                        turret.ai.primary_weapon.ai.action_jammed=False
                if turret.ai.coaxial_weapon:
                    if turret.ai.coaxial_weapon.ai.action_jammed:
                        self.owner.ai.speak('fixing jammed gun')
                        turret.ai.coaxial_weapon.ai.action_jammed=False
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'
                # this should then flow through to getting a new target
            else:
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Clearing weapon jam'
                self.owner.ai.memory['task_vehicle_crew']['target']=None
                # wait for a bit to simulate fixing.
                # on the next loop it will be fixed
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(25,45)
                return

        if self.owner.ai.memory['task_vehicle_crew']['target'] is None:
            target=None
            if turret.ai.primary_weapon.ai.direct_fire:
                if turret.ai.primary_weapon.ai.use_antitank:
                    #prioritize vehicles
                    target=self.owner.ai.get_target(False,True)
                else:
                    # prioritize soft targets 
                    target=self.owner.ai.get_target(True,False)
                if target is not None:
                    self.owner.ai.memory['task_vehicle_crew']['target']=target
            elif turret.ai.coaxial_weapon:
                if turret.ai.coaxial_weapon.ai.direct_fire:
                    # prioritize soft targets 
                    target=self.owner.ai.get_target(True,False)

        # we have a target, lets think about it in more detail
        if self.owner.ai.memory['task_vehicle_crew']['target'] is not None:
            self.think_examine_target(out_of_ammo_primary,out_of_ammo_coax)
        else:
            if self.owner.ai.memory['task_vehicle_crew']['fire_missions'] and out_of_ammo_primary == False:
                self.think_fire_mission()
            else:
                # we reach this when we have gone through the whole ai gunner decision tree and have found 
                # nothing to do. perhaps we pop out to a gunner idle function here?
                self.think_idle()

    #---------------------------------------------------------------------------
    def think_examine_target(self,out_of_ammo_primary,out_of_ammo_coax):
        '''thinking about the current target after other things have been thought about'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        turret=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].turret
        target=self.owner.ai.memory['task_vehicle_crew']['target']

        # check whether target is still a threat
        if target.is_human:
            if target.ai.blood_pressure<1:
                self.owner.ai.memory['task_vehicle_crew']['target']=None
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'
                return
        elif target.is_vehicle:
            if target.ai.check_if_vehicle_is_occupied() is False or target.ai.vehicle_disabled:
                self.owner.ai.memory['task_vehicle_crew']['target']=None
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'
                return

        # check rotation
        rotation_angle=engine.math_2d.get_rotation(turret.world_coords,target.world_coords)
        rotation_check=self.check_vehicle_turret_rotation_real_angle(rotation_angle,turret)
        
        # check engagement for each weapon
        engage_primary=False
        engage_primary_reason=''
        engage_coaxial=False
        engage_coaxial_reason=''
        if out_of_ammo_primary is False:
            engage_primary,engage_primary_reason=self.owner.ai.calculate_engagement(turret.ai.primary_weapon,target)

            # this is necessary to force a reload if we are
            # trying to engage a vehicle with HE and have compatible AT in the inventory
            # otherwise the gunner will just drop all vehicle targets because he can't pen
            if engage_primary is False and target.is_vehicle:
                if engage_primary_reason=='':
                    # do we have HE loaded and do we have AT available?
                    if turret.ai.primary_weapon.ai.magazine:
                        if turret.ai.primary_weapon.ai.magazine.ai.use_antitank is False:
                            for m in vehicle.ai.ammo_rack:
                                if turret.ai.primary_weapon.world_builder_identity in m.ai.compatible_guns:
                                    if len(m.ai.projectiles)>0:
                                        if m.ai.use_antitank:
                                            if random.randint(0,1)==0:
                                                # fire to clear the shell out 
                                                return
                                            else:
                                                #reload to clear the shell out
                                            # start the reload process
                                                self.owner.ai.memory['task_vehicle_crew']['reload_start_time']=self.owner.world.world_seconds
                                                self.owner.ai.memory['task_vehicle_crew']['current_action']='reloading primary weapon'
                                                return
                elif engage_primary_reason=='need to get closer to penetrate':
                    if turret.ai.primary_turret:
                        # wait for a couple seconds before rechecking
                        self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(0.5,1)
                        self.owner.ai.memory['task_vehicle_crew']['current_action']=f'Waiting for driver to close distance with {target.name}'
                        return
            
            # if we can't pen occasionally send a round out anyways. 
            if engage_primary is False and engage_primary_reason=='':
                if random.randint(0,4)==0:
                    engage_primary=True

            # possibly should also check if we are engaging a soft skinned vehicle with AT
                
        # out_of_ammo_coax will be true if there is no coax, or the coax is damaged
        if out_of_ammo_coax is False:
            engage_coaxial,engage_coaxial_reason=self.owner.ai.calculate_engagement(turret.ai.coaxial_weapon,target)

        if rotation_check:

                if engage_primary:
                    
                    if engage_coaxial:
                        if target.is_human:
                            # don't waste the main gun shot
                            engage_primary=False
                    else:
                        if target.is_human:
                            # only use AP mag 
                            if turret.ai.primary_weapon.ai.magazine:
                                if turret.ai.primary_weapon.ai.magazine.ai.use_antipersonnel==False:
                                    engage_primary=False

                # save the engagement commands for the gunner actions
                self.owner.ai.memory['task_vehicle_crew']['engage_primary_weapon']=engage_primary
                self.owner.ai.memory['task_vehicle_crew']['engage_coaxial_weapon']=engage_coaxial
                turret.ai.primary_weapon.ai.indirect_fire_mode=False

                if engage_primary:
                    self.calculate_turret_aim(turret,target,turret.ai.primary_weapon)
                    target_name=target.name
                    if target.is_human:
                        target_name='soldiers'
                    self.owner.ai.memory['task_vehicle_crew']['current_action']=f'Engaging {target_name}'
                    return
                if engage_coaxial:
                    self.calculate_turret_aim(turret,target,turret.ai.coaxial_weapon)
                    target_name=target.name
                    if target.is_human:
                        target_name='soldiers'
                    self.owner.ai.memory['task_vehicle_crew']['current_action']=f'Engaging {target_name}'
                    return
        

        # - results: rotation issue
        if rotation_check is False:
            # lets only ask to rotate if we are the main turret
            if turret.ai.primary_turret:
                if engage_primary or engage_coaxial:
                    # check if there is a driver
                    # note this should be fixed in the future. we shouldn't assume driver is in position 0 
                    if vehicle.ai.vehicle_crew[0].is_driver and vehicle.ai.vehicle_crew[0].role_occupied:
                    # ask the driver to rotate towards the target
                        if target.is_vehicle or random.randint(0,1)==1:

                            # wait for a couple seconds before rechecking
                            self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(1.5,2)
                            self.owner.ai.memory['task_vehicle_crew']['current_action']='Waiting for driver to rotate the vehicle'
                            return

        # default
        self.owner.ai.memory['task_vehicle_crew']['target']=None
        self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'

    #---------------------------------------------------------------------------
    def think_fire_mission(self):
        '''indirect fire mission'''
        turret=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].turret
        fire_mission=self.owner.ai.memory['task_vehicle_crew']['fire_missions'][0]

        # getting this far means we have ammo for the primary weapon and a fire mission

        # check if the fire mission is complete
        if fire_mission.rounds_fired>fire_mission.rounds_requested:
            # remove the fire mission. maybe we should do a radio broadcast ?
            self.owner.ai.memory['task_vehicle_crew']['fire_missions'].pop(0)
            return

        # range ?
        distance=engine.math_2d.get_distance(self.owner.world_coords,fire_mission.world_coords)
        if distance > turret.ai.primary_weapon.ai.indirect_range:
            # wait for a couple seconds before rechecking
            self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(1.5,2)
            self.owner.ai.memory['task_vehicle_crew']['current_action']='Waiting for driver to get in position for fire mission'
            return
            
        # turret rotation ?
        # check rotation
        rotation_angle=engine.math_2d.get_rotation(turret.world_coords,fire_mission.world_coords)
        rotation_check=self.check_vehicle_turret_rotation_real_angle(rotation_angle,turret)

        if rotation_check == False:

            # wait for a couple seconds before rechecking
            self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(1.5,2)
            self.owner.ai.memory['task_vehicle_crew']['current_action']='Waiting for driver to rotate the vehicle for fire mission'
            return

        # if we got this far then we are set to fire i guess
        self.calculate_turret_aim_indirect(turret,fire_mission.world_coords,turret.ai.primary_weapon)
        self.owner.ai.memory['task_vehicle_crew']['engage_indirect_fire'] = True
        turret.ai.primary_weapon.ai.indirect_fire_mode=True
        # gotta think of a better word, but 'Engaging' triggers the driver to wait
        self.owner.ai.memory['task_vehicle_crew']['current_action']='Engaging Fire Mission'

    #---------------------------------------------------------------------------
    def think_idle(self):
        '''think about what to do when we have no other tasks'''
        pass
            
    #---------------------------------------------------------------------------
    def think_reload(self,weapon):
        '''think about how we want to reload'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        turret=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].turret
        target=self.owner.ai.memory['task_vehicle_crew']['target']
        self.owner.ai.memory['task_vehicle_crew']['current_action']='none'

        for_at=[]
        for_ap=[]
        for_both=[]

        # ammo rack
        for m in vehicle.ai.ammo_rack:
            if m.is_gun_magazine:
                if weapon.world_builder_identity in m.ai.compatible_guns:
                    if len(m.ai.projectiles)>0:
                        if m.ai.use_antitank and m.ai.use_antipersonnel:
                            for_both.append(m)
                        elif m.ai.use_antitank:
                            for_at.append(m)
                        elif m.ai.use_antipersonnel:
                            for_ap.append(m)
                        else:
                            engine.log.add_data('error',f'ai_human.think_reload magazine {m.name} unknown use',True)

        for m in vehicle.ai.inventory:
            if m.is_gun_magazine:
                if weapon.world_builder_identity in m.ai.compatible_guns:
                    if len(m.ai.projectiles)>0:
                        if m.ai.use_antitank and m.ai.use_antipersonnel:
                            for_both.append(m)
                        elif m.ai.use_antitank:
                            for_at.append(m)
                        elif m.ai.use_antipersonnel:
                            for_ap.append(m)
                        else:
                            engine.log.add_data('error',f'ai_human.think_reload magazine {m.name} unknown use',True)

        new_magazine=None
        prefer_at=False
        prefer_ap=False


        if target is None:
            if self.owner.ai.vehicle_targets:
                prefer_at=True
            elif self.owner.ai.human_targets:
                prefer_ap=True

        else:
            if target.is_vehicle:
                if target.ai.vehicle_armor['front'][0]>4:
                    prefer_at=True
                else:
                    prefer_ap=True
            else:
                prefer_ap=True

        if prefer_at:
            if len(for_at)>0:
                new_magazine=for_at[0]
            elif len(for_both)>0:
                new_magazine=for_both[0]
        
        elif prefer_ap:
            if len(for_ap)>0:
                new_magazine=for_ap[0]
            elif len(for_both)>0:
                new_magazine=for_both[0]

        # if we don't specify a magazine the reload process picks one
        reload_success=self.owner.ai.reload_weapon(weapon,vehicle,new_magazine)
        if reload_success is False:
            engine.log.add_data('Error','ai_human_vehicle_gunner reload failed',True)
        