
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
event - something that could happen to the ai, possibly caused by external forces
for humans the current owner.image_list is [normal,prone,dead]
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

#global variables

class AIHuman(object):
    def __init__(self, owner):
        self.owner=owner

        self.task_map={
            'task_player_control':self.update_task_player_control,
            'task_enter_vehicle':self.update_task_enter_vehicle,
            'task_exit_vehicle':self.update_task_exit_vehicle,
            'task_move_to_location':self.update_task_move_to_location,
            'task_vehicle_crew':self.update_task_vehicle_crew,
            'task_engage_enemy':self.update_task_engage_enemy,
            'task_pickup_objects':self.update_task_pickup_objects,
            'task_think':self.update_task_think,
            'task_think_idle':self.update_task_think_idle,
            'task_squad_leader':self.update_task_squad_leader,
            'task_loot_container':self.update_task_loot_container,
            'task_sit_down':self.update_task_sit_down,
            'task_medic':self.update_task_medic,
            'task_mechanic':self.update_task_mechanic,
            'task_reload':self.update_task_reload,
            'task_wait':self.update_task_wait
        }

        # memory a dictionary with a ton of stuff in it. 
        self.memory={}
        self.memory['current_task']='task_think'

        # money !
        # amount can be a float to account for coinage
        # 'currency name',amount
        self.wallet={}

        # -- health stuff --
        self.blood_pressure=100
        self.blood_pressure_max=100 # as mm/hg
        self.blood_pressure_min=30 # goes into shock below this

        self.bleeding=False
        self.last_bleed_time=0
        self.bleed_interval=0.5

        # -- body attributes --
        self.fatigue=0
        self.fatigue_add_rate=1
        self.fatigue_remove_rate=0.75
        self.hunger=0
        self.hunger_rate=0.1
        self.thirst=0
        self.thirst_rate=0.1
        self.prone=False
        self.speed = 0
        self.morale=100 # lower is worse

        # -- distance tuning --
        # max distance that is walkable before deciding a vehicle is better
        self.max_walk_distance=2000
        self.max_distance_to_interact_with_object=8
        # when a vehicle is < this distance to a target it is considered arrived
        self.vehicle_arrival_distance=150

        # -- equipment --
        self.inventory=[]
        self.primary_weapon=None
        self.throwable=None
        self.antitank=None
        # self.melee=None
        # objects that are large_human_pickup. only one at a time
        self.large_pickup=None

        # -- skills --
        self.is_pilot=False
        self.is_expert_marksman=False
        self.is_afv_trained=False # afv=armored fighting vehicle
        self.is_medic=False
        self.is_mechanic=False

        # -- stats --
        self.confirmed_kills=0
        self.probable_kills=0
        self.collision_log=[]

        # -- firing pattern stuff
        # burst control keeps ai from shooting continuous streams
        self.current_burst=0 # int number of bullets shot in current burst
        self.max_burst=10

        self.wearable_head=None
        self.wearable_upper_body=None
        self.wearable_lower_body=None
        self.wearable_feet=None
        self.wearable_hand=None

        self.in_building=False
        self.building_list=[] # list of buildings the ai is overlapping spatially
        self.closest_building=None
        self.last_building_check_time=0
        self.building_check_rate=1

        self.recent_noise_or_move=False
        # reset in update
        self.last_noise_or_move_time=0 # in world.world_seconds
        self.recent_noise_or_move_reset_seconds=30

        # the ai group that this human is a part of
        self.squad=None
        self.squad_max_distance=300

        # # target lists. these are refreshed periodically
        self.near_human_targets=[]
        self.mid_human_targets=[]
        self.far_human_targets=[]
        self.near_vehicle_targets=[]
        self.mid_vehicle_targets=[]
        self.far_vehicle_targets=[]
        self.last_target_eval_time=0
        self.target_eval_rate=random.uniform(0.1,0.9)

        # # used to prevent repeats
        self.last_speak=''

    #---------------------------------------------------------------------------
    def action_vehicle_driver(self):
        ''' the action the driver is taking when not thinking'''
        # some default values
        vehicle = self.memory['task_vehicle_crew']['vehicle_role'].vehicle
        vehicle.ai.throttle = 0
        vehicle.ai.brake_power = 1

        if self.memory['task_vehicle_crew']['current_action'] == 'driving':
            calculated_distance = self.memory['task_vehicle_crew']['calculated_distance_to_target']
            calculated_vehicle_angle = self.memory['task_vehicle_crew']['calculated_vehicle_angle']
            
            # initial throttle settings
            if calculated_distance < 150:
                # apply brakes. bot will only exit when speed is zero
                # note this number should be < the minimum distance to jump out
                # or you can end up with drivers stuck in the vehicle if they slow down fast
                vehicle.ai.throttle = 0
                vehicle.ai.brake_power = 1
            elif calculated_distance < 300:
                vehicle.ai.throttle = 0.5
                vehicle.ai.brake_power = 0
            else:
                vehicle.ai.throttle = 1
                vehicle.ai.brake_power = 0

            # Normalize both angles to [0, 360)
            current_angle = engine.math_2d.get_normalized_angle(vehicle.rotation_angle)
            desired_angle = engine.math_2d.get_normalized_angle(calculated_vehicle_angle)
            
            # Compute shortest signed difference (-180 to +180)
            diff = (desired_angle - current_angle + 180) % 360 - 180
            
            # If close enough, snap to exact angle and neutral steering
            if abs(diff) <= 4:  # Adjusted threshold to match original logic
                vehicle.ai.handle_steer_neutral()
                vehicle.rotation_angle = desired_angle
                vehicle.ai.update_heading()
            else:
                # Steer in the direction of the shortest diff
                if diff > 0:
                    vehicle.ai.handle_steer_left()  # Assuming this increases angle
                    # helps turn faster
                    if vehicle.ai.throttle > 0.5:
                        vehicle.ai.throttle = 0.5
                else:
                    vehicle.ai.handle_steer_right()  # Assuming this decreases angle
                    # helps turn faster
                    if vehicle.ai.throttle > 0.5:
                        vehicle.ai.throttle = 0.5
            
            return
        
        if self.memory['task_vehicle_crew']['current_action'] == 'rotating':
            # rotating in place with minimal movement
            # throttle + brake seems to be working here fairly well

            calculated_vehicle_angle = self.memory['task_vehicle_crew']['calculated_vehicle_angle']

            if vehicle.ai.current_speed > 10:
                vehicle.ai.throttle = 0
                vehicle.ai.brake_power = 1
            else:
                vehicle.ai.throttle = 0.2
                vehicle.ai.brake_power = 1

            # Normalize both angles to [0, 360)
            current_angle = engine.math_2d.get_normalized_angle(vehicle.rotation_angle)
            desired_angle = engine.math_2d.get_normalized_angle(calculated_vehicle_angle)
            
            # Compute shortest signed difference (-180 to +180)
            diff = (desired_angle - current_angle + 180) % 360 - 180
            
            # If close enough, snap to exact angle and stop
            if abs(diff) <= 6:  # Adjusted threshold to match original logic
                vehicle.ai.handle_steer_neutral()
                vehicle.rotation_angle = desired_angle
                vehicle.ai.update_heading()
                vehicle.ai.throttle = 0
                vehicle.ai.brake_power = 1
                # this action is now done
                self.memory['task_vehicle_crew']['current_action'] = 'idle'
            else:
                # Rotate in the direction of the shortest diff
                if diff > 0:
                    vehicle.ai.handle_steer_left()
                else:
                    vehicle.ai.handle_steer_right()

    #---------------------------------------------------------------------------
    def action_vehicle_gunner_engage_target(self):
        # this is the action the vehicle gunner takes when it is NOT thinking
        # and has a target that is not None
        target=self.memory['task_vehicle_crew']['target']
        # the computed lead on the target
        turret=self.memory['task_vehicle_crew']['vehicle_role'].turret

        # rotate turret towards target. true if rotation matches
        if self.rotate_turret(turret,self.memory['task_vehicle_crew']['calculated_turret_angle']):
            if target.is_human:
                if target.ai.blood_pressure<1:
                    self.memory['task_vehicle_crew']['target']=None
                    self.memory['task_vehicle_crew']['current_action']='Scanning for targets'
                    return


            # handle bursts and fire weapon
            if self.memory['task_vehicle_crew']['engage_primary_weapon']:
                if turret.ai.handle_fire():
                    self.current_burst+=1

            if self.memory['task_vehicle_crew']['engage_coaxial_weapon']:
                if turret.ai.handle_fire_coax():
                    self.current_burst+=1

            if self.current_burst>self.max_burst:
                # randomize burst length a little
                self.current_burst=random.randint(-2,int(self.max_burst*0.5))
                self.memory['task_vehicle_crew']['target']=None
                self.memory['task_vehicle_crew']['current_action']='Scanning for targets'


    #---------------------------------------------------------------------------
    def building_check(self):

        # randomize time before we hit this method again
        self.building_check_rate=random.uniform(1.5,2.5)
        # clear building list and in_building bool
        self.building_list=[]
        self.in_building=False
        self.closest_building=None

        closest_distance=1000
        for b in self.owner.grid_square.wo_objects_building:
            distance=engine.math_2d.get_distance(self.owner.world_coords,b.world_coords)
            if distance<closest_distance:
                closest_distance=distance
                self.closest_building=b

            # check if we are in/overlapping any buildings
            if distance<(self.owner.collision_radius+b.collision_radius):
                self.building_list.append(b)
                self.in_building=True

    #---------------------------------------------------------------------------
    def calculate_engagement(self,weapon,target):
        '''calculate bool as to whether a target can be successfully engaged with a weapon'''
        # only consider the round currently loaded in the gun 
        if weapon.ai.damaged or weapon.ai.action_jammed:
            return False
        if weapon.ai.magazine is None:
            return False
        if len(weapon.ai.magazine.ai.projectiles)==0:
            return False
        
        distance=engine.math_2d.get_distance(self.owner.world_coords,target.world_coords)
        if distance>weapon.ai.range:
            return False
        
        if target.is_vehicle:
            penetration=engine.penetration_calculator.calculate_penetration(weapon.ai.magazine.ai.projectiles[0],distance,'steel',target.ai.passenger_compartment_armor['left'])
            return penetration
        
        # default
        return True
                
    #---------------------------------------------------------------------------
    def calculate_human_accuracy(self,target_coords,distance,weapon):
        '''returns target_coords adjusted for human weapon accuracy'''

        adjust_max=0


        # mechanical accuracy of the gun
        adjust_max+=weapon.ai.mechanical_accuracy

        # health based
        if self.blood_pressure<100:
            adjust_max+=1
        if self.blood_pressure<50:
            adjust_max+=10


        # fatigue
        if self.fatigue>3:
            adjust_max+=3
        if self.fatigue>5:
            adjust_max+=6

        # distance based
        if distance>500:
            adjust_max+=3
        if distance>1000:
            adjust_max+=5
        if distance>1500:
            adjust_max+=5
        if distance>2000:
            adjust_max+=15
        # prone bonus 
        if self.prone:
            adjust_max-=1

        # skills 
        if self.is_expert_marksman:
            adjust_max-=2

        # recent experience
        if self.confirmed_kills>0:
            adjust_max-=1

        # reset lower bounds
        if adjust_max<0:
            adjust_max=0


        # final results
        if adjust_max>0:
            return [target_coords[0]+random.uniform(-adjust_max,adjust_max),target_coords[1]+random.uniform(-adjust_max,adjust_max)]
        else:
            return target_coords

    #---------------------------------------------------------------------------
    def calculate_projectile_damage(self,projectile,distance):
        '''calculate and apply damage from projectile hit'''

        bleeding_hit=False
        hit=random.randint(1,5)
        if hit==1:
            #head
            if self.wearable_head is None:
                self.blood_pressure-=random.randint(30,100)
                bleeding_hit=True
            else:
                penetration=engine.penetration_calculator.calculate_penetration(projectile,distance,'steel',self.wearable_head.ai.armor)
                if penetration:
                    self.blood_pressure-=random.randint(30,75)
                    bleeding_hit=True
                else:
                    # armor stopped the hit
                    engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'spark',True)
                    self.owner.world.helmet_bounces+=1
                    self.morale-=5
                    self.speak('A projectile just bounced off my helmet!!')
        elif hit==2:
            #upper body
            if self.wearable_upper_body is None:
                self.blood_pressure-=random.randint(50,80)
                bleeding_hit=True
            else:
                penetration=engine.penetration_calculator.calculate_penetration(projectile,distance,'steel',self.wearable_upper_body.ai.armor)
                if penetration:
                    self.blood_pressure-=random.randint(30,75)
                    bleeding_hit=True
                else:
                    # armor stopped the hit
                    engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'spark',True)
                    self.owner.world.body_armor_bounces+=1
                    self.morale-=5
                    self.speak('A projectile just bounced off my body armor!!')

        elif hit==3:
            #lower body
            self.blood_pressure-=random.randint(30,60)
            bleeding_hit=True
        elif hit==4:
            # feet
            self.blood_pressure-=random.randint(30,40)
            bleeding_hit=True
        elif hit==5:
            # hands
            self.blood_pressure-=random.randint(30,40)
            bleeding_hit=True

        # extra damage from large caliber projectiles
        if engine.penetration_calculator.projectile_data[projectile.ai.projectile_type]['diameter']>12:
            self.blood_pressure-=30
            bleeding_hit=True
        
        if engine.penetration_calculator.projectile_data[projectile.ai.projectile_type]['diameter']>20:
            # do additional damage for large projectiless
            self.blood_pressure-=30
            bleeding_hit=True
        
        if bleeding_hit:
            # morale damage
            self.morale-=random.randint(10,20)
            self.bleeding=True
            engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'blood_splatter',True)
            if self.owner.is_player:
                self.owner.world.text_queue.insert(0,'You are hit and begin to bleed')

        self.speak('react to being shot')

    #---------------------------------------------------------------------------
    def calculate_turret_aim(self,turret,target,weapon):
        '''calculates the correct turret angle to hit a target'''

        # target : world_object
        # turret : world_object with ai_turret

        aim_coords=target.world_coords
        # guess how long it will take for the bullet to arrive
        distance=engine.math_2d.get_distance(turret.world_coords,target.world_coords)
        time_passed=distance/weapon.ai.muzzle_velocity
        if target.is_vehicle:
            if target.ai.current_speed>0:
                aim_coords=engine.math_2d.moveAlongVector(target.ai.current_speed,target.world_coords,target.heading,time_passed)

        if target.is_human:
            if target.ai.memory['current_task']=='task_vehicle_crew':
                vehicle=target.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
                if vehicle.ai.current_speed>0:
                    aim_coords=engine.math_2d.moveAlongVector(vehicle.ai.current_speed,vehicle.world_coords,vehicle.heading,time_passed)
            else:
                if target.ai.memory['current_task']=='task_move_to_location':
                    destination=target.ai.memory['task_move_to_location']['destination']
                    aim_coords=engine.math_2d.moveTowardsTarget(target.ai.get_calculated_speed(),aim_coords,destination,time_passed)

        self.memory['task_vehicle_crew']['calculated_turret_angle']=engine.math_2d.get_rotation(turret.world_coords,aim_coords)

    #---------------------------------------------------------------------------
    def check_ammo(self,gun,object_with_inventory):
        '''check ammo and magazines for a gun. return ammo_gun,ammo_inventory,magazine_count'''
        # gun - a world object with ai_gun
        # check_inventory - bool. if true also check inventory
        # return [ammo in gun, ammo in inventory]
        ammo_gun=0
        if gun.ai.magazine is not None:
            ammo_gun=len(gun.ai.magazine.ai.projectiles)

        ammo_inventory=0
        magazine_count=0
        for b in object_with_inventory.ai.inventory:
            if b.is_gun_magazine:
                if gun.world_builder_identity in b.ai.compatible_guns:
                    ammo_inventory+=len(b.ai.projectiles)
                    magazine_count+=1
        if object_with_inventory.is_vehicle:
            for b in object_with_inventory.ai.ammo_rack:
                if b.is_gun_magazine:
                    if gun.world_builder_identity in b.ai.compatible_guns:
                        ammo_inventory+=len(b.ai.projectiles)
                        magazine_count+=1

        return ammo_gun,ammo_inventory,magazine_count

    #---------------------------------------------------------------------------
    def check_ammo_bool(self,gun,object_with_inventory):
        '''returns True/False as to whether gun has ammo'''
        ammo_gun,ammo_inventory,magazine_count=self.check_ammo(gun,object_with_inventory)
        if ammo_gun>0:
            return True
        if ammo_inventory>0:
            return True
        #default
        return False  
        
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
    def check_visibility(self,target,distance):
        '''check whether we can see a target at a distance'''
        if distance<800:
            # humans always see everything at this range
            return True
        if distance<1500:                        
            if target.is_human:
                # if in building, only seen if noise/move
                if target.ai.in_building:
                    if target.ai.recent_noise_or_move:
                        return True
                    return False
                # if not in building, everything is seen at this range
                return True
            # vehicles are ALWAYS seen by humans at this range
            return True
        if distance<2500:
            if target.is_human:
                if target.ai.recent_noise_or_move and target.ai.in_building is False:
                    return True
                else:
                    return False
            #vehicle
            if target.ai.recent_noise_or_move:
                return True
            return False
        
        # default
        return False

    #---------------------------------------------------------------------------
    def check_visibility_from_vehicle(self,target,distance):
        '''check whether we can see a target at a distance from inside a vehicle'''
        if distance<400:
            return True
        if distance<800:
            if target.is_human:
                # if in building, only seen if noise/move
                if target.ai.in_building:
                    if target.ai.recent_noise_or_move:
                        return True
                    return False
                return True
            # vehicles are ALWAYS seen at this range
            return True
        if distance<1500:                        
            if target.is_human:
                # if in building, only seen if noise/move
                if target.ai.in_building:
                    if target.ai.recent_noise_or_move:
                        return True
                    return False
                if target.ai.prone is False:
                    return True
                return False
            # vehicles are seen at this range
            return True
        if distance<4000:
            if target.is_human:
                if target.ai.recent_noise_or_move and target.ai.in_building is False and target.ai.prone is False:
                    return True
                return False
            if target.ai.recent_noise_or_move:
                return True
            return False

        #default
        return False
        
    #---------------------------------------------------------------------------
    def drop_object(self,OBJECT_TO_DROP):
        ''' drop object into the world '''
        if OBJECT_TO_DROP.is_large_human_pickup:
            self.large_pickup=None
        else:
            self.event_remove_inventory(OBJECT_TO_DROP)
            # make sure the obj world_coords reflect the obj that had it in inventory
            OBJECT_TO_DROP.world_coords=copy.copy(self.owner.world_coords)
            
            # grenades get 'dropped' when they are thrown and are special
            if OBJECT_TO_DROP.is_grenade is False:
                engine.math_2d.randomize_position_and_rotation(OBJECT_TO_DROP)
            self.owner.world.add_queue.append(OBJECT_TO_DROP)  
        
    #---------------------------------------------------------------------------
    def eat(self,CONSUMABLE):
        # eat the consumable object. or part of it anyway
        self.blood_pressure+=CONSUMABLE.ai.health_effect
        self.hunger+=CONSUMABLE.ai.hunger_effect
        self.thirst+=CONSUMABLE.ai.thirst_effect
        self.fatigue+=CONSUMABLE.ai.fatigue_effect

        # this should remove the object from the game because it is not added to world
        self.event_remove_inventory(CONSUMABLE)

    #---------------------------------------------------------------------------
    def evaluate_targets(self):
        '''find and categorize targets. react to close ones'''

        self.near_human_targets=[]
        self.mid_human_targets=[]
        self.far_human_targets=[]
        self.near_vehicle_targets=[]
        self.mid_vehicle_targets=[]
        self.far_vehicle_targets=[]

        closest_distance=1000
        closest_object=None

        # note we are using this list directly, this is ok because we aren't removing from it
        for b in self.squad.faction_tactical.hostile_humans:
            spotted=False
            # quick check because this list isn't refreshed that often..
            if b.ai.blood_pressure>0:
                d=engine.math_2d.get_distance(self.owner.world_coords,b.world_coords)
                # 3000 is the max engagement range for anything
                if d<4000:

                    target=b
                    if 'task_vehicle_crew' in b.ai.memory:
                        target=b.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
                        # could do something further here to check armor pen

                    # vehicle crew target analysis
                    if self.memory['current_task']=='task_vehicle_crew':
                        spotted=self.check_visibility_from_vehicle(target,d)

                    # - human (not in vehicle) target analysis - 
                    else:
                        spotted=self.check_visibility(target,d)


                    if spotted:
                        if target.is_human:
                            if d<800:
                                self.near_human_targets.append(target)
                            elif d<1500:
                                self.mid_human_targets.append(target)
                            elif d<2500:
                                self.far_human_targets.append(target)
                        else:
                            #eventually these will be vehicle specific lists
                            if d<1000:
                                self.near_vehicle_targets.append(target)
                            elif d<2000:
                                self.mid_vehicle_targets.append(target)
                            elif d<4000:
                                self.far_vehicle_targets.append(target)


                    if d<closest_distance:
                        closest_distance=d
                        closest_object=target

        # note that we should double check that we can actually see the closest target
        if closest_object is not None:
            if self.memory['current_task']=='task_vehicle_crew':
                # i think its better to NOT do anything here.
                # vehicle gunners have a lot of logic to pick new targets now
                pass 

            else:

                # don't want to over ride exiting a vehicle 
                if self.memory['current_task']!='task_exit_vehicle':
                    if self.primary_weapon is not None:
                        if self.check_ammo_bool(self.primary_weapon,self.owner):
                            self.switch_task_engage_enemy(closest_object)
                    else:
                        engine.log.add_data('warn','close enemy and no primary weapon. not handled. faction:'+self.squad.faction,True)

    #---------------------------------------------------------------------------
    def event_collision(self,event_data):
        if event_data.is_projectile:
            
            distance=engine.math_2d.get_distance(self.owner.world_coords,event_data.ai.starting_coords)
            collision_description='hit by '+event_data.ai.projectile_type + ' projectile at a distance of '+ str(distance)
            starting_health=self.blood_pressure

            self.calculate_projectile_damage(event_data,distance)

            # data collection
            if event_data.ai.shooter is not None:
                collision_description+=(' from '+event_data.ai.shooter.name)
                if event_data.ai.shooter.ai.primary_weapon is not None:
                    collision_description+=("'s "+event_data.ai.weapon.name)
                self.collision_log.append(collision_description)   

                # kill tracking
                if event_data.ai.shooter.is_human:
                    if self.blood_pressure<30:
                        # protects from recording hits on something that was already dead
                        if starting_health>0:
                            if self.blood_pressure<1:
                                event_data.ai.shooter.ai.confirmed_kills+=1
                            else:
                                event_data.ai.shooter.ai.probable_kills+=1
                        else:
                            # collision on a dead human
                            pass
                
            else:
                engine.log.add_data('error', 'projectile '+event_data.name+' shooter is none',True)

            # react 
            if self.memory['current_task'] in ['task_vehicle_crew','task_exit_vehicle']:
                # - we are in a vehicle - 
                pass
            else:
                # - we are on foot -

                if self.owner.is_player is False:
                    destination=[0,0]
                    if self.squad.faction_tactical.faction=='civilian':
                        # civilian runs further
                        destination=[self.owner.world_coords[0]+float(random.randint(-560,560)),self.owner.world_coords[1]+float(random.randint(-560,560))]
                    else:
                        # soldier just repositions to get away from the fire
                        destination=[self.owner.world_coords[0]+float(random.randint(-30,30)),self.owner.world_coords[1]+float(random.randint(-30,30))]
                    if self.prone is False:
                        self.prone_state_change()
                    self.switch_task_move_to_location(destination,None)


        elif event_data.is_grenade:
            # not sure what to do here. the grenade explodes too fast to really do anything

            # attempt to throw the grenade back
            if random.randint(1,5)==1:
                event_data.ai.redirect(event_data.ai.equipper.world_coords)
            else:
                if self.memory['current_task']=='task_vehicle_crew':
                    engine.log.add_data('warn','hit by a grenade while in a vehicle',True)
                else:
                    # - we are on foot - 
                    if self.prone is True:
                        self.prone_state_change()
                    destination=[self.owner.world_coords[0]+float(random.randint(-60,60)),self.owner.world_coords[1]+float(random.randint(-60,60))]
                    self.switch_task_move_to_location(destination,None)

        elif event_data.is_throwable:
            #throwable but not a grenade 
            self.speak('Oww!')

        else:
            engine.log.add_data('debug','unidentified collision: '+event_data.name,True)

    #---------------------------------------------------------------------------
    def event_add_inventory(self,event_data):
        ''' add object to inventory. does not remove obj from world'''
        self.recent_noise_or_move=True
        self.last_noise_or_move_time=self.owner.world.world_seconds
        if event_data not in self.inventory:
            if event_data.is_large_human_pickup:
                # note - this will happen when a large_human_pickup is in another container
                # for example if a fuel can is in a kubelwagen
                # this does NOT happen when an object is picked up from the world as it is intercepted
                # before it gets this far

                #add to world.
                if event_data.in_world is False:
                    self.owner.world.add_queue.append(event_data)

                self.large_pickup=event_data

            else:

                self.inventory.append(event_data)

                if event_data.is_gun :
                    if self.primary_weapon is not None:
                        # drop the current obj and pick up the new one
                        self.drop_object(self.primary_weapon)
                    if self.owner.is_player :
                        self.owner.world.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                    self.primary_weapon=event_data
                    event_data.ai.equipper=self.owner
                elif event_data.is_throwable :
                    if self.throwable is None:
                        if self.owner.is_player :
                            self.owner.world.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                        self.throwable=event_data
                        event_data.ai.equipper=self.owner
                elif event_data.is_handheld_antitank :
                    if self.antitank is not None:
                        # drop the current obj and pick up the new one
                        self.drop_object(self.antitank)
                    if self.owner.is_player :
                        self.owner.world.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                    self.antitank=event_data
                    event_data.ai.equipper=self.owner

                elif event_data.is_wearable:
                    if event_data.ai.wearable_region=='head':
                        if self.wearable_head is None:
                            self.wearable_head=event_data
                    elif event_data.ai.wearable_region=='upper_body':
                        if self.wearable_upper_body is None:
                            self.wearable_upper_body=event_data
        else:
            engine.log.add_data('error','ai_human.event_add_inventory - obj already in inventory: '+event_data.name,True)

    #---------------------------------------------------------------------------
    def event_explosion(self,event_data):
        ''' explosion event '''
        # event_data is the explosion power as a float 

        # this will likely just kill the human

        self.morale-=random.randint(20,40)

        self.blood_pressure-=event_data
        engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'blood_splatter',True)

        self.collision_log.append('hurt by explosion')

        # short move to simulate being stunned
        if self.owner.is_player is False:
            if self.memory['current_task']!='task_vehicle_crew':
                # move slightly
                coords=[self.owner.world_coords[0]+random.randint(-15,15),self.owner.world_coords[1]+random.randint(-15,15)]
                self.switch_task_move_to_location(coords,None)

    #---------------------------------------------------------------------------
    def event_remove_inventory(self,event_data):
        ''' remove object from inventory. does NOT add to world '''

        if event_data in self.inventory:

            self.inventory.remove(event_data)
            # NOTE - if this object is meant to be added to the world it should be done by whatever calls this

            if self.primary_weapon==event_data:
                self.primary_weapon=None
                event_data.ai.equipper=None
                self.update_equipment_slots()
            elif self.throwable==event_data:
                self.throwable=None
                # equipper is used to figure out who threw the grenade
                # need a better way to handle this in the future
                #EVENT_DATA.ai.equipper=None
                self.update_equipment_slots()
            elif self.antitank==event_data:
                self.antitank=None
                event_data.ai.equipper=None
                self.update_equipment_slots()
            elif self.large_pickup==event_data:
                # large_pickup should not go through this method
                pass
            elif self.wearable_head==event_data:
                self.wearable_head=None

            # need to add a method call here that will search inventory and add new weapon/grendade/whatever if available

        else:
            engine.log.add_data('error','ai_human.event_remove_inventory object is not in inventory: '+event_data.name,True)

    #---------------------------------------------------------------------------
    def event_speak(self,event_data):
        '''speak event'''
        # note - this replaces the 'react' system

        # event_data ['command',relevant_data]
        if event_data[0]=='task_enter_vehicle':
            # should probably sanity check this first
            self.switch_task_enter_vehicle(event_data[1],None)
        elif event_data[0]=='ask to join squad':
            if event_data[1]==self.squad:
                self.speak("I'm already in that squad")
            else:
                if event_data[1].faction==self.squad.faction:
                    # yes - lets join this squad 

                    event_data[1].add_to_squad(self.owner)
                    self.speak('joined squad')
                else:
                    self.speak('no')
        elif event_data[0]=='ask to upgrade gear':
            self.speak("wut?")
            engine.log.add_data('warn','ask upgrade gear not implemented',True)
        else:
            self.speak("I don't understand")
            engine.log.add_data('error','speak inscruction: '+event_data[0]+' not handled',True)

    #---------------------------------------------------------------------------
    def event_vehicle_hit(self,hit):
        ''' react to a vehicle we are in being hit'''
        # hit is hit_data.py 

        if self.memory['current_task']=='task_vehicle_crew':
            if hit.penetrated:
                self.morale-=10
                if self.morale_check()==False:
                    self.speak('The vehicle is hit! Bail out!!')
                    self.switch_task_exit_vehicle()
            else:
                # hit bounced, could still effect morale
                if self.morale<100:
                    self.morale-=random.randint(0,5)

                    if self.morale<60:
                        if self.morale_check()==False:
                            self.speak('We are taking fire! I cannot take it anymore! Abandon the vehicle!!')
                            self.switch_task_exit_vehicle()
    




    #---------------------------------------------------------------------------
    def fire(self,weapon,target):
        ''' fires a weapon '''

        if weapon.ai.check_if_can_fire():
            self.recent_noise_or_move=True
            self.last_noise_or_move_time=self.owner.world.world_seconds

            aim_coords=target.world_coords
            # guess how long it will take for the bullet to arrive
            distance=engine.math_2d.get_distance(self.owner.world_coords,target.world_coords)
            time_passed=distance/weapon.ai.muzzle_velocity
            if target.is_vehicle:
                if target.ai.current_speed>0:
                    aim_coords=engine.math_2d.moveAlongVector(target.ai.current_speed,target.world_coords,target.heading,time_passed)

            if target.is_human:
                if target.ai.memory['current_task']=='task_vehicle_crew':
                    vehicle=target.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
                    if vehicle.ai.current_speed>0:
                        aim_coords=engine.math_2d.moveAlongVector(vehicle.ai.current_speed,vehicle.world_coords,vehicle.heading,time_passed)
                else:
                    if target.ai.memory['current_task']=='task_move_to_location':
                        destination=target.ai.memory['task_move_to_location']['destination']
                        aim_coords=engine.math_2d.moveTowardsTarget(target.ai.get_calculated_speed(),aim_coords,destination,time_passed)


            # adjust for human accuracy factors
            aim_coords=self.calculate_human_accuracy(aim_coords,distance,weapon)
            weapon.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,aim_coords)
            weapon.ai.fire()

            self.current_burst+=1

            if self.current_burst>self.max_burst:
                # stop firing, give the ai a chance to rethink and re-engage
                self.current_burst=0

                # note - this may be detrimental. needs a rethink - 11/14/24
                self.memory['current_task']='None'
    
    #---------------------------------------------------------------------------
    def fire_player(self,weapon,mouse_coords):
        # mouse_coords - mouse screen coords
        if weapon.ai.check_if_can_fire():
            # do computations based off of where the mouse is. 

            # adjusted coords
            # this function was meant for world coords.
            # because it is mouse coords distance won't apply, which may even it out a bit
            adjusted_coords=self.calculate_human_accuracy(mouse_coords,0,weapon)
            rotation_angle=engine.math_2d.get_rotation(self.owner.screen_coords,adjusted_coords)
            weapon.rotation_angle=rotation_angle
            self.owner.rotation_angle=rotation_angle
            self.owner.reset_image=True
            weapon.ai.fire()

    #---------------------------------------------------------------------------
    def get_calculated_speed(self):
        calc_speed=self.speed
        if self.fatigue<3:
            calc_speed*=1.5
        if self.fatigue>5:
            calc_speed*=0.95
        if self.fatigue>10:
            calc_speed*=0.9
        if self.fatigue>20:
            calc_speed*=0.9
        if self.fatigue>30:
            calc_speed*=0.9
        if self.prone:
            calc_speed*=0.5
        if self.blood_pressure<100:
            calc_speed*=0.9
        if self.blood_pressure<50:
            calc_speed*=0.5
        
        return calc_speed
    
    #---------------------------------------------------------------------------
    def get_compatible_magazines_within_range(self,gun,max_distance):
        compatible_magazines=[]
        for b in self.owner.grid_square.wo_objects_gun_magazine:
            if gun.name in b.ai.compatible_guns:
                if engine.math_2d.get_distance(self.owner.world_coords,b.world_coords)<max_distance:
                    compatible_magazines.append(b)
        return compatible_magazines
    
    #---------------------------------------------------------------------------
    def get_nearby_damaged_vehicles(self,max_range):
        '''return a list of nearby disabled vehicles'''
        # this could be modified to return damaged vehicles that are not fully disabled

        damaged_vehicles=[]
        # could instead search a range from grid_manager
        for vehicle in self.owner.grid_square.wo_objects_vehicle:
            if vehicle.ai.vehicle_disabled:
                if engine.math_2d.get_distance(self.owner.world_coords,vehicle.world_coords)<max_range:
                    damaged_vehicles.append(vehicle)
        return damaged_vehicles

    #---------------------------------------------------------------------------
    def get_nearby_wounded_humans(self,human_list,max_range):
        '''return a list of nearby wounded humans'''
        wounded_humans=[]
        for human in human_list:
            if human.ai.blood_pressure<80:
                if engine.math_2d.get_distance(self.owner.world_coords,human.world_coords)<max_range:
                    wounded_humans.append(human)
        return wounded_humans

    #---------------------------------------------------------------------------
    def get_target_human(self,max_range):
        '''returns a target or None if there are None'''
        target=None
        if len(self.near_human_targets)>0:
            target=self.near_human_targets.pop()
        elif len(self.mid_human_targets)>0:
            target=self.mid_human_targets.pop()
        elif len(self.far_human_targets)>0:
            target=self.far_human_targets.pop()

        if target is not None:

            distance=engine.math_2d.get_distance(self.owner.world_coords,target.world_coords)
            if distance>max_range:
                # alternatively we could drive closer.
                target=None
                
        return target
    
    #---------------------------------------------------------------------------
    def get_target_vehicle(self,max_range):
        '''returns a target or None if there are None'''
        target=None
        if len(self.near_vehicle_targets)>0:
            target=self.near_vehicle_targets.pop()
        elif len(self.mid_vehicle_targets)>0:
            target=self.mid_vehicle_targets.pop()
        elif len(self.far_vehicle_targets)>0:
            target=self.far_vehicle_targets.pop()

        if target is not None:

            distance=engine.math_2d.get_distance(self.owner.world_coords,target.world_coords)
            if distance>max_range:
                # alternatively we could drive closer.
                target=None
                
        return target
    
    #---------------------------------------------------------------------------
    def give_squad_transportation_orders(self,vehicle_order):
        '''assign transportation for the squad'''

        near_squad=self.owner.world.get_objects_within_range(self.owner.world_coords,self.squad.members,800)

        # determine if the whole squad is afv trained
        squad_afv_training=True
        for b in near_squad:
            if b.ai.is_afv_trained is False:
                squad_afv_training=False
                break

        # remove yourself to prevent recursion
        near_squad.remove(self.owner)
        vehicle_distance=600
        possible_vehicles=self.owner.world.grid_manager.get_objects_from_grid_squares_near_world_coords(self.owner.world_coords,vehicle_distance,False,True)
        near_vehicle=self.owner.world.get_objects_within_range(self.owner.world_coords,possible_vehicles,vehicle_distance)

        for b in near_vehicle:
            # skip disabled vehicles
            if b.ai.vehicle_disabled:
                continue

            # skip AFVs if the whole squad isn't trained
            if b.ai.requires_afv_training and squad_afv_training is False:
                continue

            if len(near_squad)==0:
                break
            # calculate occupants
            occupants=0

            # count the occupants already in the vehicle
            for c in b.ai.vehicle_crew:
                if c.role_occupied:
                    occupants+=1

            for c in self.owner.world.grid_manager.get_objects_from_all_grid_squares(True,False):
                if 'task_enter_vehicle' in c.ai.memory:
                    if c.ai.memory['task_enter_vehicle']['vehicle']==b:
                        occupants+=1

            while occupants<len(b.ai.vehicle_crew):
                if len(near_squad)>0:

                    # want to exclude the player as otherwise the ai will take over, but want to also let the player know somehow
                    if near_squad[0].is_player:
                        self.speak('Get in the vehicle')
                        near_squad.pop(0)
                    else:

                        if near_squad[0].ai.memory['current_task']=='task_vehicle_crew':
                            #already in a vehicle, so no further action needed
                            near_squad.pop(0)
                        else:
                            near_squad[0].ai.switch_task_enter_vehicle(b,vehicle_order)
                            occupants+=1
                            near_squad.pop(0)
                else:
                    break
    
    #---------------------------------------------------------------------------
    def handle_event(self, event, event_data):
        ''' overrides base handle_event'''
        # this is supposed to be the main interface that the outside world uses to interact with the ai
        # EVENT - text describing event
        # EVENT_DATA - most likely a world_object but could be anything

        # not sure what to do here yet. will have to think of some standard events
        if event=='add_inventory':
            self.event_add_inventory(event_data)
        elif event=='collision':
            self.event_collision(event_data)
        elif event=='remove_inventory':
            self.event_remove_inventory(event_data)
        elif event=='speak':
            self.event_speak(event_data)
        elif event=='explosion':
            self.event_explosion(event_data)
        elif event=='vehicle_hit':
            self.event_vehicle_hit(event_data)

        else:
            engine.log.add_data('error','ai_human.handle_event cannot handle event'+event,True)

    #---------------------------------------------------------------------------
    def handle_hit_with_flame(self):
        '''handle being hit with something that is on fire'''
        self.blood_pressure-=random.randint(20,100)

        self.collision_log.append('burned by fire')

    #---------------------------------------------------------------------------
    def handle_player_reload(self):
        '''handle player hitting r to reload'''
        # called by world.handle_key_press

        # check if we are in a vehicle
        if self.memory['current_task']=='task_vehicle_crew':
            turret=self.memory['task_vehicle_crew']['vehicle_role'].turret
            vehicle=self.memory['task_vehicle_crew']['vehicle_role'].vehicle
            # make sure the player is actually in a turret
            if turret!=None:
                # basically if both are out of ammo the player will have to reload twice to get both done

                # check main gun ammo
                ammo_gun,ammo_inventory,magazine_count=self.check_ammo(turret.ai.primary_weapon,vehicle)
                if ammo_gun==0:
                    if ammo_inventory>0:
                        # start the reload process
                        self.memory['task_vehicle_crew']['reload_start_time']=self.owner.world.world_seconds
                        self.memory['task_vehicle_crew']['current_action']='reloading primary weapon'
                        self.speak('reloading main gun')
                        return

                # check coax ammo
                if turret.ai.coaxial_weapon is not None:
                    ammo_gun,ammo_inventory,magazine_count=self.check_ammo(turret.ai.coaxial_weapon,vehicle)
                    if ammo_gun==0:
                        if ammo_inventory>0:
                            # start the reload process
                            self.memory['task_vehicle_crew']['reload_start_time']=self.owner.world.world_seconds
                            self.memory['task_vehicle_crew']['current_action']='reloading coax gun'
                            self.speak('reloading coax')
                            return
            else:
                # in the future it will probably be possible to shoot a regular gun from a vehicle
                # and then this can be reloaded here 
                pass
        else:
            # player is not in a vehicle so lets reload their regular weapons 

            # check AT weapon first
            if self.antitank is not None:
                ammo_gun,ammo_inventory,magazine_count=self.check_ammo(self.antitank,self.owner)
                if ammo_gun==0 and ammo_inventory>0:
                    self.switch_task_reload(self.antitank)
                    self.speak(f'reloading {self.antitank.name}')
                    return

            # check primary weapon if we didn't reload the AT weapon
            # player gun reload is special - the player doesn't check ammo in gun so they can reload 
            # partially full magazines
            if self.primary_weapon is not None:
                ammo_gun,ammo_inventory,magazine_count=self.check_ammo(self.primary_weapon,self.owner)
                if ammo_inventory>0:
                    self.switch_task_reload(self.primary_weapon)
                    self.speak(f'reloading {self.primary_weapon.name}')


    #---------------------------------------------------------------------------
    def launch_antitank(self,target_coords,mouse_screen_coords=None):
        ''' launch antitank ''' 

        # standup. kneel would be better if it becomes an option later
        if self.prone:
            self.prone_state_change()

        if self.antitank is not None:
            if self.owner.is_player :
                # do computations based off of where the mouse is. TARGET_COORDS is ignored
                adjusted_coords=self.calculate_human_accuracy(mouse_screen_coords,0,self.antitank)
                self.antitank.rotation_angle=engine.math_2d.get_rotation(self.owner.screen_coords,adjusted_coords)

            else :
                distance=engine.math_2d.get_distance(self.owner.world_coords,target_coords)
                adjusted_coords=self.calculate_human_accuracy(target_coords,distance,self.antitank)
                self.antitank.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,adjusted_coords)
            self.antitank.ai.fire()
            self.owner.world.panzerfaust_launches+=1

            # attempt reload. drop if fail
            if self.owner.is_player is False:
                ammo_gun,ammo_inventory,magazine_count=self.check_ammo(self.antitank,self.owner)
                if ammo_gun==0 and ammo_inventory==0:
                    # drop the tube now that it is empty
                    self.drop_object(self.antitank)
                elif ammo_gun==0 and ammo_inventory>0:
                    self.switch_task_reload(self.antitank)

    #---------------------------------------------------------------------------
    def morale_check(self):
        '''checks morale, returns results'''
        check=random.randint(0,100)
        if self.morale<check:
            return False
        return True

    #---------------------------------------------------------------------------
    def pickup_object(self,world_object):
        '''pick up a world object'''
        # called by world_menu and task_pickup_objects
        if world_object.is_large_human_pickup:

            # need to make sure nobody else is already carrying it
            in_use=False
            for b in self.owner.world.grid_manager.get_objects_from_all_grid_squares(True,False):
                if b.ai.large_pickup==b:
                    in_use=True

            if in_use:
                engine.log.add_data('warn','Error large pick up is already picked up',True)
            else:
                self.large_pickup=world_object
        else:
            if world_object.is_gun:
                if self.owner.is_player is False:
                    near_magazines=self.get_compatible_magazines_within_range(self.primary_weapon,500)
                    if len(near_magazines)>0:
                        self.switch_task_pickup_objects(near_magazines)

            self.speak('Picking up a '+world_object.name)

            self.event_add_inventory(world_object)
            # remove from world
            self.owner.world.remove_queue.append(world_object)

    #---------------------------------------------------------------------------
    def player_vehicle_role_change(self,requested_role):
        'player changes vehicle roles'
        # this is called by world_menu
        if self.memory['current_task']=='task_vehicle_crew':
            vehicle=self.memory['task_vehicle_crew']['vehicle_role'].vehicle

            # remove yourself from any existing roles 
            # first remove yourself from any existing crew spots
            for role in vehicle.ai.vehicle_crew:
                if role.role_occupied:
                    if role.human==self.owner:
                        role.human=None
                        role.role_occupied=False

                        if role.is_driver:
                            # this may not do anything. i think it regresses to zero
                            # turn on the brakes to prevent roll away
                            vehicle.ai.brake_power=1



            # --- add to the desired role --
            if requested_role in vehicle.ai.vehicle_crew:
                # set the role in memory
                self.memory['task_vehicle_crew']['vehicle_role']=requested_role
                self.owner.render=requested_role.seat_visible

                # occupied?
                if requested_role.role_occupied:
                    # have the current crew member exit and re-enter
                    requested_role.human.ai.switch_task_exit_vehicle()
                    requested_role.human.ai.update_task_exit_vehicle()

                requested_role.role_occupied=True
                requested_role.human=self.owner                

            else:
                engine.log.add_data('warn','ai_human.player_vehicle_role_change - role not available in vehicle',True)



        else:
            engine.log.add_data('warn','ai_human.player_vehicle_role - current task is not task_vehicle_crew,'+str(self.memory['current_task']),True)

    #---------------------------------------------------------------------------
    def prone_state_change(self):
        '''if prone, stand up. If standing, go prone'''

        # reverse state
        self.prone=not self.prone

        if self.prone:
            self.owner.image_index=1
        else: 
            self.owner.image_index=0

        # good to do this as it changed
        self.owner.reset_image=True

        # add some fatigue, not sure how much
        self.fatigue+=15
    #-----------------------------------------------------------------------
    def reload_weapon(self,weapon,obj_with_inventory,new_magazine):
        '''reload weapon. return bool as to whether it was successful'''

        # new_magazine - magazine obj that you want to reload with. if None the function finds a compatible one

        self.speak('reloading!')
        if weapon.is_gun or weapon.is_handheld_antitank:
            # first get the current magazine
            old_magazine=None
            if weapon.ai.magazine is not None:
                if weapon.ai.magazine.ai.removable:
                    old_magazine=weapon.ai.magazine

            # find a new magazine, sorting by size
            if new_magazine is None:
                biggest=0
                for b in obj_with_inventory.ai.inventory:
                    if b.is_gun_magazine:
                        if weapon.world_builder_identity in b.ai.compatible_guns:
                            if len(b.ai.projectiles)>biggest:
                                new_magazine=b
                                biggest=len(b.ai.projectiles)

            if new_magazine is None and obj_with_inventory.is_vehicle:
                for b in obj_with_inventory.ai.ammo_rack:
                    if b.is_gun_magazine:
                        if weapon.world_builder_identity in b.ai.compatible_guns:
                            if len(b.ai.projectiles)>biggest:
                                new_magazine=b
                                biggest=len(b.ai.projectiles)

            # add a new magazine (either the old magazine was removed, or was never there)
            if new_magazine is not None:
                if old_magazine is not None:
                    # empty disintegrating magazines get de-referenced and dissapear 
                    if old_magazine.ai.disintegrating==False or len(old_magazine.ai.projectiles)>0:
                        obj_with_inventory.ai.event_add_inventory(old_magazine)

                # remove the new magazine from inventory
                if new_magazine in obj_with_inventory.ai.inventory:
                    obj_with_inventory.ai.event_remove_inventory(new_magazine)
                elif obj_with_inventory.is_vehicle:
                    if new_magazine in obj_with_inventory.ai.ammo_rack:
                        obj_with_inventory.ai.event_remove_inventory(new_magazine)
                    else:
                        engine.log.add_data('error','ai_human.reload_weapon - new magazine not in inventory or ammo rack',True)
                
                weapon.ai.magazine=new_magazine
                return True
            else:
                self.speak("No new magazines available")
                return False
        else:
            engine.log.add_data('error',f'ai_human.reload_weapon {weapon.name}- not supported',True)
            return False
        
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
    def speak(self,what):
        ''' say something if the ai is close to the player '''

        # simple way of preventing repeats
        if what !=self.last_speak:
            self.last_speak=what
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.owner.world.player.world_coords)
            if distance<400:
                s='['+self.owner.name+'] '

                if what=='status':
                    s+=' what?'
                elif what=='bandage':
                    s+=' applying bandage'
                elif what=='joined squad':
                    s+=' joined squad'
                elif what=='react to being shot':
                    s+=" Aagh! I'm hit !!"
                elif what=='scream':
                    s+='Aaaaaaaaaaaah!!!'
                else:
                    s+=what

                self.owner.world.text_queue.insert(0,s)

    #---------------------------------------------------------------------------
    def squad_leader_review_orders(self):
        '''review tactical orders return true if a action was taken'''

        # the distance that is considered close enough to have arrived at a target distance
        # this should be greater than the distance a vehicle driver stops at.
        close_distance=300

        # note this can be called from inside a vehicle or from on foot

        # this is a list of TacticalOrder objects
        # for now i think its always only one
        orders=self.memory['task_squad_leader']['orders']

        if len(orders)==0:
            self.squad_leader_tactical_decision()
            return False
        
         # i think we will just focus on the first one
        order=orders[0]

        if order.order_defend_area:
            distance=engine.math_2d.get_distance(self.owner.world_coords,order.world_coords)
            if distance>close_distance:
                # in a vehicle
                if self.memory['current_task']=='task_vehicle_crew':
                    vehicle_order=VehicleOrder()
                    vehicle_order.order_drive_to_coords=True
                    if self.memory['task_vehicle_crew']['vehicle_role'].vehicle.ai.is_transport:
                        vehicle_order.exit_vehicle_when_finished=True
                    
                    # the driver will grab this when out of orders
                    self.memory['task_vehicle_crew']['vehicle_order']=vehicle_order
                    return True
                # we must be on foot
                self.switch_task_move_to_location(order.world_coords,None)
                return True
            else:
                # close enough. should we cancel this order at some point?
                if order.world_area.is_contested is False:
                    orders.remove(order)
                return False
        if order.order_move_to_location:
            distance=engine.math_2d.get_distance(self.owner.world_coords,order.world_coords)
            if distance>close_distance:
                # in a vehicle
                if self.memory['current_task']=='task_vehicle_crew':
                    vehicle_order=VehicleOrder()
                    vehicle_order.order_drive_to_coords=True
                    if self.memory['task_vehicle_crew']['vehicle_role'].vehicle.ai.is_transport:
                        vehicle_order.exit_vehicle_when_finished=True
                    
                    # the driver will grab this when out of orders
                    self.memory['task_vehicle_crew']['vehicle_order']=vehicle_order
                    return True
                # we must be on foot
                self.switch_task_move_to_location(order.world_coords,None)
                return True
            else:
                # close enough. order is complete
                orders.remove(order)
                return False

        # default 
        return False
            
    #---------------------------------------------------------------------------
    def squad_leader_tactical_decision(self):
        '''the squad leader makes a tactical decision and generates a new order'''

        #close_world_area=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.world_areas,3000)

        # - are we currently in combat?
        humans=self.near_human_targets+self.mid_human_targets+self.far_human_targets
        vehicles=self.near_vehicle_targets+self.mid_vehicle_targets+self.far_vehicle_targets
        if len(humans+vehicles)>0:

            if len(vehicles)>len(self.squad.vehicles):
                # lets get out of here 
                friendly_area=None
                for area in self.owner.world.world_areas:
                    if area.faction==self.squad.faction:
                       friendly_area=area
                       break
                if friendly_area is not None:
                    tactical_order=TacticalOrder()
                    tactical_order.order_move_to_location=True
                    tactical_order.world_coords=engine.math_2d.randomize_coordinates(friendly_area.world_coords,300)
                    self.memory['task_squad_leader']['orders'].append(tactical_order)
                    return

            # default - stay and fight. do we need a order here ?
            return
        
        # - defend a contested area -
        contested_area=None
        for area in self.owner.world.world_areas:
            if area.is_contested:
                contested_area=area
                break
        if contested_area is not None:
            tactical_order=TacticalOrder()
            tactical_order.order_defend_area=True
            tactical_order.world_coords=engine.math_2d.randomize_coordinates(contested_area.world_coords,300)
            tactical_order.world_area=contested_area
            self.memory['task_squad_leader']['orders'].append(tactical_order)
            return
        
        # - move to a random area - 
        random_area=random.choice(self.owner.world.world_areas)
        tactical_order=TacticalOrder()
        tactical_order.order_move_to_location=True
        tactical_order.world_coords=engine.math_2d.randomize_coordinates(random_area.world_coords,300)
        self.memory['task_squad_leader']['orders'].append(tactical_order)
        return


          
    #---------------------------------------------------------------------------
    def switch_task_enter_vehicle(self,vehicle,vehicle_order):
        '''switch task'''
        # vehicle_order a VehicleOrder object. can be None if there are no orders
        distance=engine.math_2d.get_distance(self.owner.world_coords,vehicle.world_coords)
        task_name='task_enter_vehicle'
        task_details = {
            'vehicle': vehicle,
            'vehicle_order': vehicle_order,
            'original_distance_to_vehicle':distance
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name

        if self.squad.squad_leader==self.owner:
            # for now the afv stuff just confuses stuff. we don't want them joining up as passengers
            if self.is_afv_trained is False:
                self.give_squad_transportation_orders(vehicle_order)

    #---------------------------------------------------------------------------
    def switch_task_engage_enemy(self,enemy):
        '''switch task'''
        # destination : this is a world_coords
        task_name='task_engage_enemy'
        task_details = {
            'enemy': enemy,
            'last_think_time': 0,
            'think_interval': 0.5
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name

        self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,enemy.world_coords)
        # tell graphics engine to redo the image 
        self.owner.reset_image=True

    #---------------------------------------------------------------------------
    def switch_task_exit_vehicle(self):
        '''switch task'''
        task_name='task_exit_vehicle'
        task_details = {
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def switch_task_loot_container(self,container):
        '''switch task'''
        task_name='task_loot_container'
        task_details = {
            'container': container,
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def switch_task_medic(self,wounded_humans):
        '''switch to task_think'''
        task_name='task_medic'

        if task_name in self.memory:
            # eventually will probably having something to update here
            pass
        else:
            # otherwise create a new one
            
            task_details = {
                'wounded_humans': wounded_humans,
                'current_patient': None
            }

            self.memory[task_name]=task_details

        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def switch_task_mechanic(self,damaged_vehicles):
        '''switch to task_think'''
        task_name='task_mechanic'

        if task_name in self.memory:
            # eventually will probably having something to update here
            pass
        else:
            # otherwise create a new one
            
            task_details = {
                'damaged_vehicles': damaged_vehicles,
                'current_vehicle': None
            }

            self.memory[task_name]=task_details

        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def switch_task_move_to_location(self,destination,moving_object):
        '''switch task'''
        # moving_object : optional game_object. set when we are moving to something that may move position
        # destination : this is a world_coords
        task_name='task_move_to_location'
        task_details = {
            'destination': copy.copy(destination),
            'moving_object': moving_object,
            'last_think_time': 0,
            'think_interval': 0.5
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name

        self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,destination)
        # tell graphics engine to redo the image 
        self.owner.reset_image=True

    #---------------------------------------------------------------------------
    def switch_task_pickup_objects(self,objects):
        '''switch task'''
        
        task_name='task_pickup_objects'
        # if this task already exists we just want to update it
        if task_name in self.memory:
            # just add the extra objects on
            self.memory[task_name]['objects']+=objects
        else:
            # otherwise create a new one
            
            task_details = {
                'objects': objects
            }

            self.memory[task_name]=task_details

        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def switch_task_player_control(self):
        '''switch task'''
        task_name='task_player_control'
        task_details = {
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def switch_task_reload(self,weapon):
        '''switch to task_reload'''
        task_name='task_reload'

        if task_name in self.memory:
            # eventually will probably having something to update here
            pass
        else:
            # otherwise create a new one
            
            task_details = {
                'reload_start_time':self.owner.world.world_seconds,
                'weapon':weapon
            }

            self.memory[task_name]=task_details

        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def switch_task_sit_down(self):
        '''switch task'''
        task_name='task_sit_down'
        task_details = {
            'status':'searching',
            'furniture_object': None,
            'sit_start_time':0,
            'sit_duration':300
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def switch_task_squad_leader(self,order):
        '''switch task'''
        # order - a TacticalOrder object. can be none
        task_name='task_squad_leader'

        if task_name in self.memory:
            # something here eventually?
            if order is not None:
                self.memory['task_squad_leader']['orders']=[order]
        else:
            task_details = {
                'last_think_time': 0,
                'think_interval': 0.5,
                'orders':[],

            }
            if order is not None:
                task_details['orders']=[order]

            self.memory[task_name]=task_details

        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def switch_task_think(self):
        '''switch to task_think'''
        task_name='task_think'

        if task_name in self.memory:
            # eventually will probably having something to update here
            pass
        else:
            # otherwise create a new one
            
            task_details = {
                'something': 'something'
            }

            self.memory[task_name]=task_details

        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def switch_task_think_idle(self):
        '''switch to task_think_idle'''
        task_name='task_think_idle'

        if task_name in self.memory:
            # eventually will probably having something to update here
            pass
        else:
            # otherwise create a new one
            
            task_details = {
                'something': 'something'
            }

            self.memory[task_name]=task_details

        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def switch_task_vehicle_crew(self,vehicle,vehicle_order):
        '''switch task to vehicle crew and determine role'''
        # this should always overwrite if it exists
        # A player can go through this if they enter a vehicle
        # this can also be used by a ai in a vehicle already that wants to change role
        # role should be NONE in most cases. 

        # first remove yourself from any existing crew spots
        for role in vehicle.ai.vehicle_crew:
            if role.human == self.owner:
                role.human=None
                role.role_occupied=False

                if role.role_name=='driver':
                    # this may not do anything. i think it regresses to zero
                    # turn on the brakes to prevent roll away
                    vehicle.ai.brake_power=1

        vehicle_role=None
        for role in vehicle.ai.vehicle_crew:
            if role.role_occupied is False:
                vehicle_role=role
                role.role_occupied=True
                role.human=self.owner
                self.owner.render=role.seat_visible
                break


        if role is None:
            engine.log.add_data('error','ai_human.switch_task_vehicle_crew No role found!! Vehicle is full='+str(vehicle.ai.check_if_vehicle_is_full()),True)



        # update the position to reflect the new seat
        vehicle.ai.update_child_position_rotation()

        task_name='task_vehicle_crew'
        task_details = {
            'vehicle_role': vehicle_role,
            'current_action': 'none', # used to describe/inform the rest of the crew what this crew member is doing
            'target': None, # target for the gunner role
            'calculated_turret_angle': None, #used by the gunner role
            'engage_primary_weapon': False, # used by gunner
            'engage_coaxial_weapon': False, #used by gunner
            'calculated_vehicle_angle': None, # used by driver role
            'calculated_distance_to_target':None, # used by driver role
            'last_think_time': 0,
            'think_interval': 0.5,
            'reload_start_time':0,
            'vehicle_order':vehicle_order
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def switch_task_wait(self,wait_time_seconds):
        '''switch task wait'''
        task_name='task_wait'
        task_details = {
            'end_time': self.owner.world.world_seconds+wait_time_seconds,
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name        

    #---------------------------------------------------------------------------
    def think_vehicle_role_driver(self):
        vehicle=self.memory['task_vehicle_crew']['vehicle_role'].vehicle

        # precheck to make sure we aren't in combat 
        for role in vehicle.ai.vehicle_crew:
            if role.role_occupied and role.is_gunner:
                if role.turret.ai.primary_weapon:
                    current_action=role.human.ai.memory['task_vehicle_crew']['current_action']
                    if 'reloading' in current_action:
                        self.memory['task_vehicle_crew']['current_action']='waiting on crew to finish reloading'
                        vehicle.ai.brake_power=1
                        vehicle.ai.throttle=0
                        # wait to think for a bit so we don't end up doing something else immediately
                        self.memory['task_vehicle_crew']['think_interval']=random.uniform(5,15)
                        return
                    if 'Engaging' in current_action:
                        self.memory['task_vehicle_crew']['current_action']='waiting on crew to finish engagement'
                        vehicle.ai.brake_power=1
                        vehicle.ai.throttle=0
                        # wait to think for a bit so we don't end up doing something else immediately
                        self.memory['task_vehicle_crew']['think_interval']=random.uniform(5,15)
                        return
                    if current_action=='Waiting for driver to rotate the vehicle':
                        target=role.human.ai.memory['task_vehicle_crew']['target']
                        if target is not None:
                            rotation_required=engine.math_2d.get_rotation(vehicle.world_coords,target.world_coords)
                            v=vehicle.rotation_angle
                            if rotation_required>v-1 and rotation_required<v+1:
                                # we are close enough
                                self.memory['task_vehicle_crew']['current_action']='waiting'
                                vehicle.ai.brake_power=1
                                vehicle.ai.throttle=0
                                # wait to think for a bit so we don't end up doing something else immediately
                                self.memory['task_vehicle_crew']['think_interval']=random.uniform(5,15)
                                return
                            #default
                            self.memory['task_vehicle_crew']['calculated_vehicle_angle']=rotation_required
                            self.memory['task_vehicle_crew']['current_action']='rotating'
                            return
        
        # next lets check if anyone is trying to get in 
        if vehicle.ai.check_if_vehicle_is_full() is False:
            new_passengers=False
            for b in self.squad.faction_tactical.allied_humans:
                if 'task_enter_vehicle' in b.ai.memory:
                    if vehicle is b.ai.memory['task_enter_vehicle']['vehicle']:
                        new_passengers=True
                        break

            if new_passengers:
                # wait for new passengers
                # no need to check this again for a bit
                self.memory['task_vehicle_crew']['think_interval']=random.uniform(0.8,1)
                vehicle.ai.brake_power=1
                vehicle.ai.throttle=0
                self.memory['task_vehicle_crew']['current_action']='waiting for passengers'
                return
        
        # lets check our orders
        if self.memory['task_vehicle_crew']['vehicle_order'] is not None:
            self.think_vehicle_role_driver_vehicle_order()
            return
        else:
            # does anyone else have any orders?
            for role in vehicle.ai.vehicle_crew:
                if role.role_occupied:
                    if role.human.ai.memory['task_vehicle_crew']['vehicle_order'] is not None:
                        # grab their order
                        self.memory['task_vehicle_crew']['vehicle_order']=role.human.ai.memory['task_vehicle_crew']['vehicle_order']
                        role.human.ai.memory['task_vehicle_crew']['vehicle_order']=None
                        return

        # should be not very likely to get this far.
        
        # how far are we from the squad leader?
        if self.squad.squad_leader is not None:
            distance_to_squad_lead=engine.math_2d.get_distance(self.owner.world_coords,self.squad.squad_leader.world_coords)
            if distance_to_squad_lead > 300:
                vehicle_order=VehicleOrder()
                vehicle_order.order_drive_to_coords=True
                vehicle_order.world_coords=copy.copy(self.squad.squad_leader.world_coords)
                if vehicle.ai.is_transport:
                    vehicle_order.exit_vehicle_when_finished=True
                self.memory['task_vehicle_crew']['vehicle_order']=vehicle_order
                return
        
        # default behavior after everything else 
        # no orders 
        # close to squad lead
        self.memory['task_vehicle_crew']['current_action']='Waiting at destination'
        vehicle.ai.brake_power=1
        vehicle.ai.throttle=0

        # should probably make a decision about jumping out at this point
        if vehicle.ai.is_transport:
            # check if any squad leads are in the crew. if so they will figure out what to do
            crew_squad_lead=False
            for role in vehicle.ai.vehicle_crew:
                if role.role_occupied:
                    if role.human.ai.squad.squad_leader==role.human:
                        crew_squad_lead=True
                        break
            if crew_squad_lead is False:
                # no squad lead so no new vehicle orders unless if the squad lead moves
                # might as well get out for a bit

                # this might cause issues if the crew has conditions that cause them 
                # to re-enter the vehicle 
                

                for role in vehicle.ai.vehicle_crew:
                    if role.role_occupied:
                        role.human.ai.switch_task_exit_vehicle()

    #---------------------------------------------------------------------------
    def think_vehicle_role_driver_drive_to_destination(self,destination,distance):
        '''perform actions necessary to start driving somewhere'''
        vehicle=self.memory['task_vehicle_crew']['vehicle_role'].vehicle
        rotation=engine.math_2d.get_rotation(vehicle.world_coords,destination)
        self.memory['task_vehicle_crew']['current_action']='driving'
        self.memory['task_vehicle_crew']['calculated_distance_to_target']=distance
        self.memory['task_vehicle_crew']['calculated_vehicle_angle']=rotation
        # turn engines on
        # could do smarter checks here once engines have more stats
        need_start=False
        for b in vehicle.ai.engines:
            if b.ai.engine_on is False:
                need_start=True
                break
        if need_start:
            vehicle.ai.handle_start_engines()
    #---------------------------------------------------------------------------
    def think_vehicle_role_driver_vehicle_order(self):
        '''think about the drivers current vehicle order'''
        order=self.memory['task_vehicle_crew']['vehicle_order']
        vehicle=self.memory['task_vehicle_crew']['vehicle_role'].vehicle
        if order.order_drive_to_coords:
            distance=engine.math_2d.get_distance(vehicle.world_coords,order.world_coords)
            if distance<self.vehicle_arrival_distance and vehicle.ai.current_speed<10:
                # we have arrived and can delete the order.
                self.memory['task_vehicle_crew']['current_action']='waiting'
                vehicle.ai.brake_power=1
                vehicle.ai.throttle=0

                if order.exit_vehicle_when_finished:
                    for role in vehicle.ai.vehicle_crew:
                        if role.role_occupied:
                            role.human.ai.switch_task_exit_vehicle()
                            # this will also clear out any vehicle_orders they had

                return
            #default
            self.think_vehicle_role_driver_drive_to_destination(order.world_coords,distance)
            return
        if order.order_tow_object:
            # future 
            return


    #---------------------------------------------------------------------------
    def think_vehicle_role_gunner(self):
        vehicle=self.memory['task_vehicle_crew']['vehicle_role'].vehicle
        turret=self.memory['task_vehicle_crew']['vehicle_role'].turret

        # handle the reloading action
        if self.memory['task_vehicle_crew']['current_action']=='reloading primary weapon':
            if (self.owner.world.world_seconds-self.memory['task_vehicle_crew']['reload_start_time'] 
            > turret.ai.primary_weapon_reload_speed):
                self.memory['task_vehicle_crew']['current_action']='none'
                self.think_vehicle_role_gunner_reload(turret.ai.primary_weapon)
            else:
                return
        if self.memory['task_vehicle_crew']['current_action']=='reloading coax gun':
            if (self.owner.world.world_seconds-self.memory['task_vehicle_crew']['reload_start_time'] 
            > turret.ai.coaxial_weapon_reload_speed):
                self.memory['task_vehicle_crew']['current_action']='none'
                self.think_vehicle_role_gunner_reload(turret.ai.coaxial_weapon)
                
            else:
                return    

        out_of_ammo_primary=False
        out_of_ammo_coax=False
        turret_jammed=turret.ai.turret_jammed
        weapons_damaged=False
        weapons_jammed=False

        # check main gun ammo
        ammo_gun,ammo_inventory,magazine_count=self.check_ammo(turret.ai.primary_weapon,vehicle)
        if ammo_gun==0:
            if ammo_inventory>0:
                # start the reload process
                self.memory['task_vehicle_crew']['reload_start_time']=self.owner.world.world_seconds
                self.memory['task_vehicle_crew']['current_action']='reloading primary weapon'
                self.memory['task_vehicle_crew']['target']=None
                return
            else:
                out_of_ammo_primary=True

        # check coax ammo
        if turret.ai.coaxial_weapon is not None:
            ammo_gun,ammo_inventory,magazine_count=self.check_ammo(turret.ai.coaxial_weapon,vehicle)
            if ammo_gun==0:
                if ammo_inventory>0:
                    # start the reload process
                    self.memory['task_vehicle_crew']['reload_start_time']=self.owner.world.world_seconds
                    self.memory['task_vehicle_crew']['current_action']='reloading coax gun'
                    self.memory['task_vehicle_crew']['target']=None
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
                weapons_damaged=True
            if turret.ai.coaxial_weapon.ai.action_jammed:
                weapons_jammed=True

        if out_of_ammo_coax and out_of_ammo_primary:
            self.memory['task_vehicle_crew']['current_action']='Out of Ammo'
            self.memory['task_vehicle_crew']['target']=None
            return
        
        if turret_jammed:
            # we should probably bail out
            self.memory['task_vehicle_crew']['current_action']='Turret Jammed'
            self.memory['task_vehicle_crew']['target']=None
            return

        if weapons_damaged:
            self.memory['task_vehicle_crew']['current_action']='Weapons Damaged'
            self.memory['task_vehicle_crew']['target']=None
            return
        
        if weapons_jammed:
            # this we can fix ourselves
            #if we are already in this state then consider it fixed 
            if self.memory['task_vehicle_crew']['current_action']=='Weapons Jammed':
                engine.log.add_data('info','ai_human.think_vehicle_role_gunner - fixing jammed gun',True)
                if turret.ai.primary_weapon:
                    if turret.ai.primary_weapon.ai.action_jammed:
                        self.speak('fixing jammed gun')
                        turret.ai.primary_weapon.ai.action_jammed=False
                if turret.ai.coaxial_weapon:
                    if turret.ai.coaxial_weapon.ai.action_jammed:
                        self.speak('fixing jammed gun')
                        turret.ai.coaxial_weapon.ai.action_jammed=False
                # wait for a bit to simulate fixing
                self.memory['task_vehicle_crew']['think_interval']=random.uniform(25,45)
            else:
                self.memory['task_vehicle_crew']['current_action']='Weapons Jammed'
                self.memory['task_vehicle_crew']['target']=None

            return

        if self.memory['task_vehicle_crew']['target'] is None:
            target=None
            if turret.ai.primary_weapon.ai.use_antitank:
                #prioritize vehicles
                target=self.get_target_vehicle(turret.ai.primary_weapon.ai.range)
                if target is None:
                    target=self.get_target_human(turret.ai.primary_weapon.ai.range)
            else:
                # prioritize humans 
                target=self.get_target_human(turret.ai.primary_weapon.ai.range)
                if target is None:
                    target=self.get_target_vehicle(turret.ai.primary_weapon.ai.range)
            if target is not None:
                self.memory['task_vehicle_crew']['target']=target

        # we have a target, lets think about it in more detail
        if self.memory['task_vehicle_crew']['target'] is not None:
            self.think_vehicle_role_gunner_examine_target(out_of_ammo_primary,out_of_ammo_coax)
                
    #---------------------------------------------------------------------------
    def think_vehicle_role_gunner_examine_target(self,out_of_ammo_primary,out_of_ammo_coax):
        '''thinking about the current target after other things have been thought about'''
        vehicle=self.memory['task_vehicle_crew']['vehicle_role'].vehicle
        turret=self.memory['task_vehicle_crew']['vehicle_role'].turret
        target=self.memory['task_vehicle_crew']['target']

        # check whether target is still a threat
        if target.is_human:
            if target.ai.blood_pressure<1:
                self.memory['task_vehicle_crew']['target']=None
                self.memory['task_vehicle_crew']['current_action']='Scanning for targets'
                return
        elif target.is_vehicle:
            if target.ai.check_if_vehicle_is_occupied() is False or target.ai.vehicle_disabled:
                self.memory['task_vehicle_crew']['target']=None
                self.memory['task_vehicle_crew']['current_action']='Scanning for targets'
                return

        # check rotation
        rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,target.world_coords)
        rotation_check=self.check_vehicle_turret_rotation_real_angle(rotation_angle,turret)
        
        # check engagement for each weapon
        engage_primary=False
        engage_coaxial=False
        if out_of_ammo_primary is False:
            engage_primary=self.calculate_engagement(turret.ai.primary_weapon,target)

            # this is necessary to force a reload if we are
            # trying to engage a vehicle with HE and have AT in the inventory
            # otherwise the gunner will just drop all vehicle targets because he can't pen
            if engage_primary is False and target.is_vehicle:
                # do we have HE loaded and do we have AT available?
                if turret.ai.primary_weapon.ai.magazine:
                    if turret.ai.primary_weapon.ai.magazine.ai.use_antitank is False:
                        for m in vehicle.ai.ammo_rack:
                            if len(m.ai.projectiles)>0:
                                if m.ai.use_antitank:
                                    # start the reload process
                                    self.memory['task_vehicle_crew']['reload_start_time']=self.owner.world.world_seconds
                                    self.memory['task_vehicle_crew']['current_action']='reloading primary weapon'
                                    self.memory['task_vehicle_crew']['target']=None
                                    return

            # possibly should also check if we are engaging a soft skinned vehicle with AT
                

        if out_of_ammo_coax is False:
            engage_coaxial=self.calculate_engagement(turret.ai.coaxial_weapon,target)
        

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
                self.memory['task_vehicle_crew']['engage_primary_weapon']=engage_primary
                self.memory['task_vehicle_crew']['engage_coaxial_weapon']=engage_coaxial

                if engage_primary:
                    self.calculate_turret_aim(turret,target,turret.ai.primary_weapon)
                    self.memory['task_vehicle_crew']['current_action']='Engaging Targets'
                    return
                if engage_coaxial:
                    self.calculate_turret_aim(turret,target,turret.ai.coaxial_weapon)
                    self.memory['task_vehicle_crew']['current_action']='Engaging Targets'
                    return

        

        # - results: rotation issue
        if rotation_check is False:
            # lets only ask to rotate if we are the main turret
            if turret.ai.primary_turret:
                if engage_primary or engage_coaxial:
                    # check if there is a driver
                    if vehicle.ai.vehicle_crew[0].is_driver and vehicle.ai.vehicle_crew[0].role_occupied:
                    # ask the driver to rotate towards the target
                        if target.is_vehicle or random.randint(0,1)==1:

                            # wait for a couple seconds before rechecking
                            self.memory['task_vehicle_crew']['think_interval']=random.uniform(1.5,5)
                            self.memory['task_vehicle_crew']['current_action']='Waiting for driver to rotate the vehicle'
                            return


        # default
        self.memory['task_vehicle_crew']['target']=None
        self.memory['task_vehicle_crew']['current_action']='Scanning for targets'
            
    #---------------------------------------------------------------------------
    def think_vehicle_role_gunner_reload(self,weapon):
        '''think about how we want to reload'''
        vehicle=self.memory['task_vehicle_crew']['vehicle_role'].vehicle
        turret=self.memory['task_vehicle_crew']['vehicle_role'].turret
        target=self.memory['task_vehicle_crew']['target']
        self.memory['task_vehicle_crew']['current_action']='none'

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
                            engine.log.add_data('error',f'ai_human.think_vehicle_role_gunner_reload magazine {m.name} unknown use')

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
                            engine.log.add_data('error',f'ai_human.think_vehicle_role_gunner_reload magazine {m.name} unknown use')

        new_magazine=None
        prefer_at=False
        prefer_ap=False

        if len(for_both)>0:
            new_magazine=for_both[0]
        else:
            if target is None:
                # could check if vehicles are near
                if len(self.near_vehicle_targets)>0 or len(self.mid_vehicle_targets)>0 or len(self.far_vehicle_targets)>0:
                    prefer_at=True
                elif len(self.near_human_targets)>0:
                    prefer_ap=True

            else:
                if target.is_vehicle:
                    prefer_at=True
                else:
                    prefer_ap=True

        if prefer_at and len(for_at)>0:
            new_magazine=for_at[0]
        
        if prefer_ap and len(for_ap)>0:
            new_magazine=for_ap[0]

        #print(f'{vehicle.name} {weapon.name} AT:{len(for_at)}, AP: {len(for_ap)}, BOTH: {len(for_both)}')

        reload_success=self.reload_weapon(weapon,vehicle,new_magazine)
        if reload_success is False:
            engine.log.add_data('Error','think_vehicle_role_gunner reload failed',True)
                
    #---------------------------------------------------------------------------
    def think_vehicle_role_passenger(self):
        '''think.. as a passenger'''
        vehicle=self.memory['task_vehicle_crew']['vehicle_role'].vehicle

        # check if there are any empty roles
        for role in vehicle.ai.vehicle_crew:
            if role.role_occupied is False and role.is_passenger is False:
                self.switch_task_vehicle_crew(vehicle,None)
                return

        if len(self.near_human_targets)>0:
            # check if we should be worried about small arms fire
            # near targets will absolutely chew up a unarmored vehicle

            # kind of a hack. left and right are likely symetric so its a good
            # general guess
            # but only jump out if the vehicle is going slow. otherwise it might get away 
            if vehicle.ai.current_speed<20 and vehicle.ai.passenger_compartment_armor['left'][0]<5:
                self.switch_task_exit_vehicle()

    #---------------------------------------------------------------------------
    def think_vehicle_role_radio_operator(self):
        # note radio.ai.radio_operator set by switch_task_vehicle_crew
        # not a ton that we really need to do here atm

        vehicle_role=self.memory['task_vehicle_crew']['vehicle_role']
        vehicle=vehicle_role.vehicle
        radio=vehicle.ai.radio

        if radio is None:

            # should we try to do something else?
            return
            
        else:
            # gunner also uses this, do not want to over write 
            if vehicle_role.is_gunner is False:
                self.memory['task_vehicle_crew']['current_action']='Beep boop. operating the radio'
            if radio.ai.power_on is False:
                radio.ai.current_frequency=self.squad.faction_tactical.radio_frequency
                radio.ai.turn_power_on()

                # should double check here that this worked.
                # but what are the failure conditions?
                # - bad battery 
                # - no battery?
            else:
                # check the frequency
                if radio.ai.current_frequency!=self.squad.faction_tactical.radio_frequency:
                    radio.ai.current_frequency=self.squad.faction_tactical.radio_frequency
                    # this is needed to reset frequency with world_radio
                    radio.ai.turn_power_on()

                # -- receive radio messages --
                if len(radio.ai.receive_queue)>0:
                    message=radio.ai.receive_queue.pop()
                    
                    # avoid duplicates from other radio operators
                    if message not in self.squad.radio_receive_queue:
                        # ideally do some processing here 
                        self.squad.radio_receive_queue.append(message)

                # -- send radio messages --
                if len(self.squad.radio_send_queue)>0:
                    message=self.squad.radio_send_queue.pop()
                    vehicle.ai.radio.ai.send_message(message)
                    # maybe speak something here?
        

    #---------------------------------------------------------------------------
    def throw(self,target_coords,mouse_screen_coords=None):
        ''' throw like you know the thing. cmon man '''   
        # stand up
        if self.prone:
            self.prone_state_change() 
        if self.throwable is not None:

            # this does all the needed internal ai stuff for the throwable 
            self.throwable.ai.throw()

            # set rotation and heading
            if self.owner.is_player :
                # do computations based off of where the mouse is. TARGET_COORDS is ignored
                self.throwable.rotation_angle=engine.math_2d.get_rotation(self.owner.screen_coords,mouse_screen_coords)
                self.throwable.heading=engine.math_2d.get_heading_vector(self.owner.screen_coords,mouse_screen_coords)
            else :
                self.throwable.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,target_coords)
                self.throwable.heading=engine.math_2d.get_heading_vector(self.owner.world_coords,target_coords)

            self.drop_object(self.throwable)


    #---------------------------------------------------------------------------
    def transfer_liquid(self,from_object,to_object):
        '''transfer liquid/ammo/??? from one object to another'''
        

        if from_object.is_liquid and to_object.is_container:
            source_amount=from_object.volume
            
            # add up total destination volume
            destination_amount=0
            for b in to_object.ai.inventory:
                destination_amount+=b.volume

            # remember in containers this is considered a max volume    
            destination_maximum=to_object.volume
            source_result,destination_result=engine.math_2d.get_transfer_results(source_amount,destination_amount,destination_maximum)
            from_object.volume=source_result
            
            # spawn a new liquid object with the amount to transfer
            z=engine.world_builder.spawn_object(self.owner.world,[0,0],from_object.name,False)
            z.volume=destination_result

            # add the new liquid to the container
            to_object.add_inventory(z)
        else:
            engine.log.add_data('error','ai_human.transfer_liquid - src/dest not recognized',True)

    #---------------------------------------------------------------------------
    def update(self):
        ''' update '''
        # update health 
        self.update_health()

        if self.blood_pressure>self.blood_pressure_min:
            # update the current task
            if self.memory['current_task'] in self.memory:
                if self.memory['current_task'] in self.task_map:
                    # call the associated update function for the current task
                    self.task_map[self.memory['current_task']]()
                else:
                    engine.log.add_data('error','current task '+self.memory['current_task']+' not in task map',True)

            else:
                self.switch_task_think()

            # identify and categorize targets. should not be run for the player as it can result in new current_task
            if (self.owner.world.world_seconds-self.last_target_eval_time>self.target_eval_rate) and self.owner.is_player is False:
                self.last_target_eval_time=self.owner.world.world_seconds
                self.target_eval_rate=random.uniform(0.8,6.5)
                self.evaluate_targets()

            
                
            # building awareness stuff. ai and human need this
            if self.owner.world.world_seconds-self.last_building_check_time>self.building_check_rate:
                self.last_building_check_time=self.owner.world.world_seconds
                self.building_check()

            if self.recent_noise_or_move:
                if self.owner.world.world_seconds-self.last_noise_or_move_time>self.recent_noise_or_move_reset_seconds:
                    self.recent_noise_or_move=False
                
                # reset large pickup positiion if we moved
                # this is a lazy way to check if we moved. could probably add a bool..
                if self.large_pickup is not None:
                    self.update_large_pickup_position()


    #---------------------------------------------------------------------------
    def update_equipment_slots(self):
        '''update any empty equipment slots'''

        # primmary weapon
        # could also take ammo into account here 
        if self.primary_weapon is None:
            for b in self.inventory:
                if b.is_gun:
                    self.primary_weapon=b
                    b.ai.equipper=self.owner
                    break

        # secondary weapon

        # throwable
        if self.throwable is None:
            for b in self.inventory:
                if b.is_throwable:
                    self.throwable=b
                    b.ai.equipper=self.owner
                    break

        # anti-tank
        if self.antitank is None:
            for b in self.inventory:
                if b.is_handheld_antitank:
                    self.antitank=b
                    b.ai.equipper=self.owner
                    break

    #---------------------------------------------------------------------------
    def update_health(self):
        '''update health and handle death'''

        if self.blood_pressure>0:
            if self.bleeding:
                if self.owner.world.world_seconds-self.last_bleed_time>self.bleed_interval:
                    self.last_bleed_time=self.owner.world.world_seconds+random.uniform(0,2)
                    engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'small_blood',True)
                    self.blood_pressure-=10+random.uniform(0,3)
                    
                    # only self heal if not passed out
                    if self.blood_pressure>self.blood_pressure_min:
                        if random.randint(0,3)==0:
                            for b in self.inventory:
                                if b.is_medical:
                                    self.use_medical_object(b)
                                    break
                # possibly have a random stop bleed even if you don't have medical
            else:
                # regain morale if not bleeding
                self.morale+=0.5*self.owner.world.time_passed_seconds


            # -- body attribute stuff --
            if self.fatigue>0:
                self.fatigue-=self.fatigue_remove_rate*self.owner.world.time_passed_seconds
            self.hunger+=self.hunger_rate*self.owner.world.time_passed_seconds
            self.thirst+=self.thirst_rate*self.owner.world.time_passed_seconds

            # passed out
            if self.blood_pressure<self.blood_pressure_min:
                if self.prone is False:
                    self.prone_state_change()
                if self.memory['current_task']=='task_vehicle_crew':
                    # re-use this function to exit the vehicle cleanly
                    self.switch_task_exit_vehicle()
                    self.update_task_exit_vehicle()
                elif self.memory['current_task']=='task_exit_vehicle':
                    self.update_task_exit_vehicle()
    
        else:
            # -- handle death --

            # -- create death log --
            death_log={
                'name':self.owner.name,
                'faction':self.squad.faction,
                'last collision':'none',
                'primary weapon':'none',
                'confirmed kills':str(self.confirmed_kills),
                'probably kills':str(self.probable_kills)
            }
            if self.primary_weapon is not None:
                death_log['primary weapon']=self.primary_weapon.name

            if len(self.collision_log)>0:
                death_log['last collision']=self.collision_log[-1]

            engine.log.human_death_log.append(death_log)
            # --

            # drop primary weapon 
            if self.primary_weapon is not None:
                self.drop_object(self.primary_weapon)
            

            # drop large pickup
            if self.large_pickup is not None:
                self.drop_object(self.large_pickup)

            if self.memory['current_task']=='task_vehicle_crew':
                # re-use this function to exit the vehicle cleanly
                self.switch_task_exit_vehicle()
                self.update_task_exit_vehicle()
            elif self.memory['current_task']=='task_exit_vehicle':
                self.update_task_exit_vehicle()

            # remove from squad 
            if self.squad is not None:
                if self.owner in self.squad.members:
                    self.squad.members.remove(self.owner)

                    if self.owner==self.squad.squad_leader:
                        self.squad.squad_leader=None
                else: 
                    # note this just in case but the bug causing this was fixed.
                    print('!! Error : '+self.owner.name+' not in squad somehow')

            # spawn body
            engine.world_builder.spawn_container_body('body: '+self.owner.name,self.owner,2)

            # remove from world
            self.owner.world.remove_queue.append(self.owner)

            if self.owner.is_player:
                # turn on the player death menu
                self.owner.world.world_menu.active_menu='death'
                self.owner.world.world_menu.menu_state='none'
                # fake input to get the text added
                self.owner.world.world_menu.handle_input('none')
        
            #print death message
            #print(dm)

    #---------------------------------------------------------------------------
    def update_large_pickup_position(self):
        '''update large pickup position'''
        # eventually will support custom angles and offsets
        self.large_pickup.rotation_angle=engine.math_2d.get_normalized_angle(self.owner.rotation_angle+0)
        self.large_pickup.world_coords=engine.math_2d.calculate_relative_position(
            self.owner.world_coords,self.owner.rotation_angle,self.large_pickup.large_pickup_offset)
        self.large_pickup.reset_image=True

    #---------------------------------------------------------------------------
    def update_task_engage_enemy(self):

        # - getting this far assumes that you have a primary weapon

        enemy=self.memory['task_engage_enemy']['enemy']
        if enemy.is_human:
            if enemy.ai.blood_pressure<1:
                self.memory.pop('task_engage_enemy',None)
                self.switch_task_think()
                return
        elif enemy.is_vehicle:
            if enemy.ai.vehicle_disabled:
                self.memory.pop('task_engage_enemy',None)
                self.switch_task_think()
                return
        
        last_think_time=self.memory['task_engage_enemy']['last_think_time']
        think_interval=self.memory['task_engage_enemy']['think_interval']

        if self.owner.world.world_seconds-last_think_time>think_interval:
            # -- think --

            # reset time
            self.memory['task_engage_enemy']['last_think_time']=self.owner.world.world_seconds
            self.memory['task_engage_enemy']['think_interval']=random.uniform(0.1,1.5)

            if enemy.is_human:
                self.update_task_engage_enemy_human()
            elif enemy.is_vehicle:
                self.update_task_engage_enemy_vehicle()
            else:
                engine.log.add_data('error',f'ai_human.update_task_engage_enemy unkown object {enemy.name}',True)

        else:
            # -- fire --
            self.fire(self.primary_weapon,enemy)
            self.fatigue+=self.fatigue_add_rate*self.owner.world.time_passed_seconds

    #---------------------------------------------------------------------------
    def update_task_engage_enemy_human(self):
        enemy=self.memory['task_engage_enemy']['enemy']
        distance=engine.math_2d.get_distance(self.owner.world_coords,enemy.world_coords)
        if distance<self.primary_weapon.ai.range:
            # maybe only when not in buildings??
            if not self.prone:
                self.prone_state_change()

            # out of ammo ?
            ammo_gun,ammo_inventory,magazine_count=self.check_ammo(self.primary_weapon,self.owner)
            if ammo_gun==0:
                if ammo_inventory>0:
                    self.switch_task_reload(self.primary_weapon)
                    return
                else:
                    # need ammo or new gun. hand it over to think to deal with this
                    self.memory.pop('task_engage_enemy',None)
                    self.switch_task_think()
                    return
                    
            # also check if we should chuck a grenade at it
            if self.throwable is not None:
                if distance<self.throwable.ai.range and distance>150:
                    if enemy.is_human:
                        self.throw(enemy.world_coords)
                        self.speak('Throwing Grenade !!!!')

        else:

            new_enemy=self.get_target_human(self.primary_weapon.ai.range)
            if new_enemy is None:
                new_enemy=self.get_target_vehicle(self.primary_weapon.ai.range)
            if new_enemy is None:

                    # no closer targets. is the target really far out of range?
                if distance>(self.primary_weapon.ai.range+self.primary_weapon.ai.range*0.5):
                    self.memory.pop('task_engage_enemy',None)
                    self.switch_task_think()
                else:
                    # move about 150 units closer to the enemy and re-engage 
                    self.switch_task_move_to_location(engine.math_2d.moveTowardsTarget(150,self.owner.world_coords,enemy.world_coords,1),None)
            else:
                self.switch_task_engage_enemy(new_enemy)
    
    #---------------------------------------------------------------------------
    def update_task_engage_enemy_vehicle(self):
        enemy=self.memory['task_engage_enemy']['enemy']
        distance=engine.math_2d.get_distance(self.owner.world_coords,enemy.world_coords)
        penetration=False

        if self.antitank is not None:
            if distance<self.antitank.ai.range:
                self.launch_antitank(enemy.world_coords)
        else:

            # also check if we should chuck a grenade at it
            if self.throwable is not None:
                if distance<self.throwable.ai.range and distance>150:

                    # grenades will miss if the vehicle is moving fast
                    if enemy.ai.current_speed<130:
                        # check pen
                        if enemy.ai.passenger_compartment_armor['top'][0]<5 or self.throwable.ai.use_antitank:
                            self.speak(f'Throwing {self.throwable.name} !!!!')
                            self.throw(enemy.world_coords)
                            
            ammo_gun,ammo_inventory,magazine_count=self.check_ammo(self.primary_weapon,self.owner)
            # can we penetrate it in a best case scenario?
            if ammo_gun>0:
                if engine.penetration_calculator.calculate_penetration(self.primary_weapon.ai.magazine.ai.projectiles[0],distance,'steel',enemy.ai.vehicle_armor['left']):
                    penetration=True
                if engine.penetration_calculator.calculate_penetration(self.primary_weapon.ai.magazine.ai.projectiles[0],distance,'steel',enemy.ai.passenger_compartment_armor['left']):
                    penetration=True

        if penetration is False:
            self.memory.pop('task_engage_enemy',None)
            self.switch_task_think()

    #---------------------------------------------------------------------------
    def update_task_enter_vehicle(self):
        '''update task_enter_vehicle'''
        # Note - this task can also handle the player trying to enter a vehicle 

        vehicle=self.memory['task_enter_vehicle']['vehicle']
        

        if self.owner.world.check_object_exists(vehicle) is False:
            self.speak('Where did that '+vehicle.name+' go?')
            self.memory.pop('task_enter_vehicle',None)
            self.switch_task_think()
            return

        if vehicle.ai.vehicle_disabled:
            self.speak(f'This {vehicle.name} is destroyed!')
            self.memory.pop('task_enter_vehicle',None)
            self.switch_task_think()
            return

        distance=engine.math_2d.get_distance(self.owner.world_coords,vehicle.world_coords)

        # check if the vehicle is getting further away
        if distance>self.memory['task_enter_vehicle']['original_distance_to_vehicle']+100:
            self.speak('My ride is driving away!')
            self.memory.pop('task_enter_vehicle',None)
            self.switch_task_think()


        # check if we are close enough to enter
        if distance<self.max_distance_to_interact_with_object or self.owner.is_player:
            precheck=True
            if vehicle.ai.check_if_vehicle_is_full() is True:
                precheck=False
                self.speak('No more room in this vehicle!')
            
            if precheck:
                # check that everyone is the same faction
                for role in vehicle.ai.vehicle_crew:
                    if role.role_occupied:
                        if role.human.ai.squad.faction!=self.squad.faction:
                            precheck=False
                            self.speak('This vehicle is crewed by the enemy!')
                            break

            if precheck:
                # put your large items in the trunk
                if self.large_pickup:
                    vehicle.add_inventory(self.large_pickup)
                    self.owner.world.remove_queue.append(self.large_pickup)
                    self.large_pickup=None

                # this will decide crew position as well
                vehicle_order=self.memory['task_enter_vehicle']['vehicle_order']
                self.memory.pop('task_enter_vehicle',None)
                # make sure we aren't prone
                if self.prone:
                    self.prone_state_change()
                self.switch_task_vehicle_crew(vehicle,vehicle_order)
            else:
                # something went wrong, cancel the task
                self.memory.pop('task_enter_vehicle',None)
                self.switch_task_think()

        else:
            # -- too far away to enter, what do we do --
            if distance<self.max_walk_distance:
                self.switch_task_move_to_location(vehicle.world_coords,vehicle)
            else:
                # vehicle is way too far away, just cancel task
                self.speak(f"The {vehicle.name} is too far away. Let's rethink this.")
                self.memory.pop('task_enter_vehicle',None)
                self.switch_task_think()

    #---------------------------------------------------------------------------
    def update_task_exit_vehicle(self):

        vehicle_role=self.memory['task_vehicle_crew']['vehicle_role']
        vehicle_role.human=None
        vehicle_role.role_occupied=False
        if vehicle_role.role_name=='driver':

            # this may not do anything. i think it regresses to zero
            # turn on the brakes to prevent roll away
            vehicle_role.vehicle.ai.brake_power=1

        # make sure we are visible again
        self.owner.render=True
        self.owner.reset_image=True # needed for dead guys i think because they don't move

        # delete vehicle role memory 
        self.memory.pop('task_vehicle_crew',None)

        # delete this task as it is now complete
        self.memory.pop('task_exit_vehicle',None)
        self.memory['current_task']=''

        # maybe grab your large pick up if you put it in the trunk
        if self.blood_pressure>0:
            self.speak('Jumping out')

            if self.owner.is_player is False:
                # move slightly
                # this seems to be needed to prevent the ai from immediately jumping back in 
                coords=[self.owner.world_coords[0]+random.randint(-15,15),self.owner.world_coords[1]+random.randint(-15,15)]
                self.switch_task_move_to_location(coords,None)
            else:
                pass
        else:
            # this is also needed to prevent dead passengers from being under a disabled vehicle
            self.owner.world_coords=[self.owner.world_coords[0]+random.randint(5,15),self.owner.world_coords[1]+random.randint(5,15)]


    #---------------------------------------------------------------------------
    def update_task_loot_container(self):
        '''loot a container or object with ai.inventory'''
        container=self.memory['task_loot_container']['container']

        if self.owner.world.check_object_exists(container) is False:
            self.memory.pop('task_loot_container',None)
            self.switch_task_think()
        else:
            distance=engine.math_2d.get_distance(self.owner.world_coords,container.world_coords)
            if distance<self.max_distance_to_interact_with_object:
                # done with this task
                self.memory.pop('task_loot_container',None)
                self.switch_task_wait(random.randint(14,30))

                # -- loot container --
                need_medical=True
                need_consumable=True
                need_grenade=True
                need_antitank=False
                need_gun=self.primary_weapon is None

                # check our inventory
                for b in self.inventory:
                    if b.is_medical:
                        need_medical=False
                    elif b.is_consumable:
                        need_consumable=False
                    elif b.is_grenade:
                        need_grenade=False
                    elif b.is_handheld_antitank:
                        need_antitank=False

                # grab stuff based on what we want
                take=[]
                gun_magazines=[]
                for b in container.ai.inventory:
                    if b.is_medical and need_medical:
                        take.append(b)
                        need_medical=False
                    elif b.is_consumable and need_consumable:
                        take.append(b)
                        need_consumable=False
                    elif b.is_grenade and need_grenade:
                        take.append(b)
                        need_grenade=False
                    elif b.is_handheld_antitank and need_antitank:
                        take.append(b)
                        need_antitank=False
                    elif b.is_gun and need_gun:
                        take.append(b)
                        need_gun=False
                    elif b.is_gun_magazine:
                        gun_magazines.append(b)

                if len(take)==0:
                    # nothing we wanted. lets grab something random
                    chance=random.randint(1,5)
                    if chance==1 and len(container.ai.inventory)>0:
                        take.append(container.ai.inventory[0])
                
                # handle gun magazine decisions
                if len(gun_magazines)>0:
                    gun=None

                    # check if we are grabbing a gun
                    for b in take:
                        if b.is_gun:
                            gun=b

                    # if not, set it to the gun we have, if we have one
                    if gun is None:
                        if self.primary_weapon is not None:
                            gun=self.primary_weapon

                    # if we have a gun now, grab compatible magazines
                    # only grab 2 magazines though
                    grabbed=0
                    if gun is not None:
                        for b in gun_magazines:
                            if gun.name in b.ai.compatible_guns:
                                if grabbed<2:
                                    take.append(b)
                                    grabbed+=1

                # take items!
                for c in take:
                    container.remove_inventory(c)
                    self.event_add_inventory(c)
                    self.speak('Grabbed a '+c.name)

            elif distance>self.max_walk_distance:
                # maybe should add a option to ignore this but for the most part you want to forget distant objects
                # done with this task
                self.memory.pop('task_loot_container',None)
                self.switch_task_think()
            else:
                # the distance is intermediate. we still want to pick the item up
                self.switch_task_move_to_location(container.world_coords,None)

    #---------------------------------------------------------------------------
    def update_task_mechanic(self):
        '''update task mechanic'''
        # simple task. takes care of all the wounded and then pops itself.

        if self.memory['task_mechanic']['current_vehicle'] is None:
            if len(self.memory['task_mechanic']['damaged_vehicles'])==0:
                self.memory.pop('task_mechanic',None)
                self.switch_task_wait(random.randint(15,30))
                return
            self.memory['task_mechanic']['current_vehicle']=self.memory['task_mechanic']['damaged_vehicles'].pop()
        current_vehicle=self.memory['task_mechanic']['current_vehicle']
        distance=engine.math_2d.get_distance(self.owner.world_coords,current_vehicle.world_coords)
        if distance>1000:
            self.memory['task_mechanic']['current_vehicle']=None
            return
        if distance>self.max_distance_to_interact_with_object:
            self.switch_task_move_to_location(current_vehicle.world_coords,current_vehicle)
            return         

        # if we get this far we are close enough to work on the vehicle
        #engine
        for b in current_vehicle.ai.engines:
            if b.ai.damaged:
                b.ai.damaged=False
        #turret 
        for b in current_vehicle.ai.turrets:
            if b.ai.turret_jammed:
                b.ai.turret_jammed=False
        current_vehicle.ai.vehicle_disabled=False

        # clear out this vehicle so a new one is picked next cycle
        self.memory['task_mechanic']['current_vehicle']=None

        # update this stat counter so i can track if this ever actually happens.. lol
        self.owner.world.mechanic_fixes+=1
        

    #---------------------------------------------------------------------------
    def update_task_medic(self):
        '''update task medic'''
        # simple task. takes care of all the wounded and then pops itself.
        if self.memory['task_medic']['current_patient'] is None:
            if len(self.memory['task_medic']['wounded_humans'])==0:
                self.memory.pop('task_medic',None)
                self.switch_task_wait(random.randint(10,15))
                return
            self.memory['task_medic']['current_patient']=self.memory['task_medic']['wounded_humans'].pop()
        patient=self.memory['task_medic']['current_patient']
        distance=engine.math_2d.get_distance(self.owner.world_coords,patient.world_coords)
        if distance>1000:
            self.memory['task_medic']['current_patient']=None
            return
        if distance>self.max_distance_to_interact_with_object:
            self.switch_task_move_to_location(patient.world_coords,patient)
            return         

        # if we get this far we are close enough to treat the patient
        patient.ai.bleeding=False
        patient.ai.blood_pressure+=15
        self.memory['task_medic']['current_patient']=None
        self.speak('You will live soldier. All patched up.')

        # update this stat counter so i can track if this ever actually happens.. lol
        self.owner.world.medic_heals+=1

    #---------------------------------------------------------------------------
    def update_task_move_to_location(self):
        '''update task'''
        
        last_think_time=self.memory['task_move_to_location']['last_think_time']
        think_interval=self.memory['task_move_to_location']['think_interval']

        self.recent_noise_or_move=True
        self.last_noise_or_move_time=self.owner.world.world_seconds
        
        if self.owner.world.world_seconds-last_think_time>think_interval:
            # reset time
            self.memory['task_move_to_location']['last_think_time']=self.owner.world.world_seconds

            # if there is a moving object, reset the destination to match in case it moved
            if self.memory['task_move_to_location']['moving_object'] is not None:

                # if its a vehicle check if its full
                if self.memory['task_move_to_location']['moving_object'].is_vehicle:
                    if self.memory['task_move_to_location']['moving_object'].ai.check_if_vehicle_is_full() is True:
                        self.speak('Vehicle looks full')
                        self.memory.pop('task_move_to_location',None)
                        self.memory.pop('task_enter_vehicle',None)
                        self.switch_task_think()
                        return

                self.memory['task_move_to_location']['destination']=copy.copy(self.memory['task_move_to_location']['moving_object'].world_coords)
                # reset bot facing angle 
                self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,self.memory['task_move_to_location']['destination'])
                self.owner.reset_image=True

            # -- think about walking --
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.memory['task_move_to_location']['destination'])

            if distance>200 and self.prone:
                self.prone_state_change()

            # should we get a vehicle instead of hoofing it to wherever we are going?
            if distance>self.max_walk_distance:
                b=self.owner.world.get_closest_vehicle(self.owner,(self.max_walk_distance*0.6))
                if b is not None:
                    # get_closest_vehicle only returns vehicles that aren't full
                    # won't return planes if not a pilot
                    # won't return AFVs if not AFV trained
                    vehicle_order=VehicleOrder()
                    vehicle_order.order_drive_to_coords=True
                    vehicle_order.world_coords=self.memory['task_move_to_location']['destination']
                    vehicle_order.exit_vehicle_when_finished=True
                    self.switch_task_enter_vehicle(b,vehicle_order)

                else:
                    # no vehicles ? guess we are walking
                    pass
            elif distance<self.max_distance_to_interact_with_object:
                # we've arrived ! 
                self.memory.pop('task_move_to_location',None)
                self.switch_task_think()
        
        else:

            # -- walk --
            # move
            self.owner.world_coords=engine.math_2d.moveTowardsTarget(self.get_calculated_speed(),
                self.owner.world_coords,self.memory['task_move_to_location']['destination'],
                self.owner.world.time_passed_seconds)
            # add some fatigue
            self.fatigue+=self.fatigue_add_rate*self.owner.world.time_passed_seconds

    #---------------------------------------------------------------------------
    def update_task_pickup_objects(self):
        objects=self.memory['task_pickup_objects']['objects']
        remove_queue=[]
        nearest_distance=2000
        nearest_object=None
        for b in objects:
            if self.owner.world.check_object_exists(b) is False:
                remove_queue.append(b)
            else:
                distance=engine.math_2d.get_distance(self.owner.world_coords,b.world_coords)
                if distance<self.max_distance_to_interact_with_object:
                    # -- pickup object --
                    # remove as we will be picking it up
                    remove_queue.append(b)
                    self.pickup_object(b)

                elif distance>self.max_walk_distance:
                    # maybe should add a option to ignore this but for the most part you want to forget distant objects
                    remove_queue.append(b)
                else:
                    # the distance is intermediate. we still want to pick the item up
                    # track which object is closest
                    if distance<nearest_distance:
                        nearest_object=b
                        nearest_distance=distance
        # process remove queue
        for b in remove_queue:
            objects.remove(b)

        # go towards the closest one
        if nearest_object is not None:
            self.switch_task_move_to_location(nearest_object.world_coords,None)
        else:
            if len(objects)==0:
                self.memory.pop('task_pickup_objects',None)
                self.switch_task_wait(random.randint(5,15))

    #---------------------------------------------------------------------------
    def update_task_player_control(self):
        '''update player control task'''
        # controls got moved to world. nothing left over here for now
        pass

    #---------------------------------------------------------------------------
    def update_task_reload(self):
        ''' update task reload'''
        # this is used to reload a hand held gun or at weapon 
        if (self.owner.world.world_seconds-self.memory['task_reload']['reload_start_time'] > 
            self.memory['task_reload']['weapon'].ai.reload_speed):
            self.reload_weapon(self.memory['task_reload']['weapon'],self.owner,None)
            self.memory.pop('task_reload',None)
            self.switch_task_think()
            
    #---------------------------------------------------------------------------
    def update_task_squad_leader(self):

        # this is a task that is checked temporarily if there is nothing better to do.
        # as such it should always switch_task_think() after doing what it planned on doing, 
        # unless if it switched to something else

        last_think_time=self.memory['task_squad_leader']['last_think_time']
        think_interval=self.memory['task_squad_leader']['think_interval']

        
        if self.owner.world.world_seconds-last_think_time>think_interval:
            # reset time
            self.memory['task_squad_leader']['last_think_time']=self.owner.world.world_seconds

            # -- do the longer thing ---
            if self.squad_leader_review_orders() is False:
                # this means the tactical orders didn't result in any new actions

                self.switch_task_think()
                
        else:
            # -- do the shorter thing --
            # this would be better as a task_do_random_thing
            # go for a walk
            decision=random.randint(1,100)
            if decision==1:
                coords=[self.owner.world_coords[0]+random.randint(-25,25),self.owner.world_coords[1]+random.randint(-25,25)]
                self.switch_task_move_to_location(coords,None)

            self.switch_task_think()

    #---------------------------------------------------------------------------
    def update_task_sit_down(self):
        '''update task_sit_down'''
        

        if self.memory['task_sit_down']['status']=='searching':
            distance=1000
            # don't want the soldiers wandering off too far 
            if self.squad.faction in ['german','soviet','american']:
                distance=500
            temp=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.grid_square.wo_objects_furniture,distance)

            if temp is None:
                # give up for now
                self.memory.pop('task_sit_down',None)
                return
            else:
                self.memory['task_sit_down']['status']='moving_to_object'
                self.memory['task_sit_down']['furniture_object']=temp

        if self.memory['task_sit_down']['status']=='moving_to_object':
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.memory['task_sit_down']['furniture_object'].world_coords)
            if distance<self.max_distance_to_interact_with_object:
                # sit down
                self.memory['task_sit_down']['status']='sitting'
                self.memory['task_sit_down']['sit_start_time']=self.owner.world.world_seconds
            else:
                self.switch_task_move_to_location(self.memory['task_sit_down']['furniture_object'].world_coords,None)

        if self.memory['task_sit_down']['status']=='sitting':
            # should get up after a time limit passes 
            if self.owner.world.world_seconds-self.memory['task_sit_down']['sit_start_time']>self.memory['task_sit_down']['sit_duration']:
                self.memory.pop('task_sit_down',None)
    #---------------------------------------------------------------------------
    def update_task_think(self):
        '''task think - thinking about what to do next'''
        # the ugly function where we have to determine what we are doing

        # !! probably need to check the last time we were here so we aren't 
        # hitting this too often as it is likely computationally intense

        # note - this function uses heavy use of 'return' to control flow

        
        # -- priorities --

        # player will switch_task for a couple things like reloading 
        if self.owner.is_player:
            self.switch_task_player_control()
            return
        
        # check for AT targets as a high priority
        if self.antitank is not None:
            if self.check_ammo_bool(self.antitank,self.owner):
                vehicle_target=self.get_target_vehicle(self.antitank.ai.range)
                if vehicle_target is not None:
                    self.switch_task_engage_enemy(vehicle_target)
                    return


        # primary weapon
        if self.primary_weapon is None:
            # need to get a gun
            distance=4000
            if len(self.near_human_targets)>0:
                distance=400
            elif len(self.mid_human_targets)>0:
                distance=600
            elif len(self.far_human_targets)>0:
                distance=900

            # this also means that humans without any targets will not get a gun
            if distance<4000:
                gun=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.grid_square.wo_objects_gun,distance)

                if gun is not None:
                    self.switch_task_pickup_objects([gun])
                    return
        else:
            # -- we have a gun. is it usable? --
            if self.check_ammo_bool(self.primary_weapon,self.owner):
                
                # focus on humans, AT weapon specific check was done earlier (above)
                human_target=self.get_target_human(self.primary_weapon.ai.range)
                if human_target is not None:
                    self.switch_task_engage_enemy(human_target)
                    return

            else:
                # need to get ammo. check for nearby magazines
                near_magazines=self.get_compatible_magazines_within_range(self.primary_weapon,500)
                if len(near_magazines)>0:
                    self.switch_task_pickup_objects(near_magazines)
                    return
                
                # check containers for spare ammo
                containers=self.owner.world.get_objects_within_range(self.owner.world_coords,self.owner.grid_square.wo_objects_container,500)
                if len(containers)>0:
                    self.switch_task_loot_container(random.choice(containers))
                    return
                
                # ran out of options to find ammo. set this to cause the bot to pickup a new weapon
                self.primary_weapon=None
            
        
        # -- check if we have older tasks to resume --
        # this is important for compound tasks
        if 'task_medic' in self.memory:
            self.memory['current_task']='task_medic'
            return 
        if 'task_enter_vehicle' in self.memory:
            self.memory['current_task']='task_enter_vehicle'
            return
        if 'task_pickup_objects' in self.memory:
            self.memory['current_task']='task_pickup_objects'
            return
        if 'task_loot_container' in self.memory:
            self.memory['current_task']='task_loot_container'
            return
        if 'task_sit_down' in self.memory:
            self.memory['current_task']='task_sit_down'
            return
        if 'task_mechanic' in self.memory:
            self.memory['current_task']='task_mechanic'
            return
        
        # -- unique job role stuff -- 
        if self.is_medic:
            wounded_humans=self.get_nearby_wounded_humans(self.squad.faction_tactical.allied_humans,1000)
            if len(wounded_humans)>0:
                self.switch_task_medic(wounded_humans)
                return
        if self.is_mechanic:
            damaged_vehicles=self.get_nearby_damaged_vehicles(1000)
            if len(damaged_vehicles)>0:
                self.switch_task_mechanic(damaged_vehicles)
                return

        # -- squad stuff (lower importance)--
        # could maybe have some logic to this if i ever add ranks 
        if self.squad.squad_leader is None:
            self.squad.squad_leader=self.owner

        if self.squad.squad_leader==self.owner:
            self.switch_task_squad_leader(None)
            return
    
        # being in a squad wwhen we aren't lead basically just means staying close to the squad lead
        distance=engine.math_2d.get_distance(self.owner.world_coords,self.squad.squad_leader.world_coords)
        # are we close enough to squad?
        if distance>self.squad_max_distance:
            self.switch_task_move_to_location(self.squad.squad_leader.world_coords,None)
            return

        # -- ok now we've really run out of things to do. do things that don't matter
        # ! NOTE Squad Lead will never get this far
        self.switch_task_think_idle()

    #---------------------------------------------------------------------------
    def update_task_think_idle(self):
        '''update task_think_idle '''
        # update task_think was getting too long
        # this task is used to figure out something to do when the bot is idle (has nothing urgent to do)

        decision=random.randint(0,10)
        if decision==1:
            # go for a walk
            coords=[self.owner.world_coords[0]+random.randint(-45,45),self.owner.world_coords[1]+random.randint(-45,45)]
            self.switch_task_move_to_location(coords,None)
        elif decision==2:
            # check containers
            containers=self.owner.world.get_objects_within_range(self.owner.world_coords,self.owner.grid_square.wo_objects_container,1000)
            if len(containers)>0:
                self.switch_task_loot_container(random.choice(containers))
        elif decision==3:
            # eat 
            if self.hunger>20 or self.thirst>20:
                for b in self.inventory:
                    if b.is_consumable:
                        self.eat(b)
                        break
        elif decision==4:
            self.switch_task_sit_down()
        elif decision==5:
            if self.closest_building is not None:
                self.switch_task_move_to_location(self.closest_building.world_coords,None)

    #---------------------------------------------------------------------------
    def update_task_vehicle_crew(self):
        '''update task_vehicle_crew'''

        # this is for all crew
        vehicle=self.memory['task_vehicle_crew']['vehicle_role'].vehicle
        if vehicle.ai.vehicle_disabled:
            self.switch_task_exit_vehicle()
            return

        role=self.memory['task_vehicle_crew']['vehicle_role']

        if self.owner.is_player:
            self.update_task_vehicle_crew_player()
        else:
            last_think_time=self.memory['task_vehicle_crew']['last_think_time']
            think_interval=self.memory['task_vehicle_crew']['think_interval']

            # think
            if self.owner.world.world_seconds-last_think_time>think_interval:
                # reset time
                self.memory['task_vehicle_crew']['last_think_time']=self.owner.world.world_seconds
                
                # note that roles can have multiple functions now
                if role.is_driver:
                    # driver needs a fast refresh for smooth vehicle controls
                    self.memory['task_vehicle_crew']['think_interval']=random.uniform(0.1,0.2)
                    self.think_vehicle_role_driver()
                if role.is_gunner:
                    self.memory['task_vehicle_crew']['think_interval']=random.uniform(0.1,0.3)
                    self.think_vehicle_role_gunner()
                if role.is_passenger:
                    self.memory['task_vehicle_crew']['think_interval']=random.uniform(0.5,0.9)
                    self.think_vehicle_role_passenger()
                if role.is_radio_operator:
                    self.memory['task_vehicle_crew']['think_interval']=random.uniform(0.3,0.7)
                    self.think_vehicle_role_radio_operator()

                if self.owner==self.squad.squad_leader:
                    # if we don't have a vehicle order, check to see if we can create 
                    # one from tactical orders
                    if self.memory['task_vehicle_crew']['vehicle_order'] is None:
                        self.squad_leader_review_orders()


            else:
                # some roles will want to do something every update cycle

                if role.is_gunner:
                    if self.memory['task_vehicle_crew']['target'] is not None:
                        if self.memory['task_vehicle_crew']['calculated_turret_angle'] is not None:
                            self.action_vehicle_gunner_engage_target()
                if role.is_driver:
                    self.action_vehicle_driver()
    #---------------------------------------------------------------------------
    def update_task_vehicle_crew_player(self):
        vehicle=self.memory['task_vehicle_crew']['vehicle_role'].vehicle
        role=self.memory['task_vehicle_crew']['vehicle_role']
        if role.is_gunner:
            # handle vehicle turret gun reloads for the player
            turret=role.turret
            if self.memory['task_vehicle_crew']['current_action']=='reloading primary weapon':
                if (self.owner.world.world_seconds-self.memory['task_vehicle_crew']['reload_start_time'] 
                > turret.ai.primary_weapon_reload_speed):
                    self.reload_weapon(turret.ai.primary_weapon,vehicle,None)
                    self.memory['task_vehicle_crew']['current_action']='none'
                else:
                    return
            if self.memory['task_vehicle_crew']['current_action']=='reloading coax gun':
                if (self.owner.world.world_seconds-self.memory['task_vehicle_crew']['reload_start_time'] 
                > turret.ai.coaxial_weapon_reload_speed):
                    self.reload_weapon(turret.ai.coaxial_weapon,vehicle,None)
                    self.memory['task_vehicle_crew']['current_action']='none'
                else:
                    return
            
            # this action is set by world. triggered by hitting 'w'
            if self.memory['task_vehicle_crew']['current_action']=='rotate turret':
                if self.rotate_turret(turret,self.memory['task_vehicle_crew']['calculated_turret_angle']):
                    # rotation achieved. we can remove this action
                    self.memory['task_vehicle_crew']['current_action']=''
                
    #---------------------------------------------------------------------------
    def update_task_wait(self):
        '''update task wait'''
        if self.owner.world.world_seconds>self.memory['task_wait']['end_time']:
            self.switch_task_think()
    #-----------------------------------------------------------------------
    def use_medical_object(self,medical):
        # MEDICAL - a medical object

        # should eventually handle bandages, morphine, etc etc
        # probably need attributes similar to consumables

        # should select the correct medical item to fix whatever the issue is

        self.speak('Using medical '+medical.name)

        self.bleeding=False

        self.blood_pressure+=medical.ai.health_effect
        self.hunger+=medical.ai.hunger_effect
        self.thirst_rate+=medical.ai.thirst_effect
        self.fatigue+=medical.ai.fatigue_effect

        # calling this by itself should remove all references to the object
        self.event_remove_inventory(medical)

            


