
'''
module : ai_player.py
language : Python 3.x
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
            'task_squad_leader':self.update_task_squad_leader,
            'task_loot_container':self.update_task_loot_container
        }

        self.memory={}
        self.memory['current_task']='task_think'

        # money !
        # amount can be a float to account for coinage
        # 'currency name',amount
        self.wallet={}



        # -- health stuff --
        self.health=100
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

        # -- distance tuning --
        # max distance that is walkable before deciding a vehicle is better 
        self.max_walk_distance=2000
        self.max_distance_to_interact_with_object=8

        # -- equipment --
        self.inventory=[]
        self.primary_weapon=None
        self.throwable=None
        self.antitank=None
        # self.melee=None
        # objects that are large_human_pickup. only one at a time
        self.large_pickup=None
        self.carrying_offset=[10,10]  #vector offset for when you are carrying a object

        # -- skills --
        self.is_pilot=False
        self.is_expert_marksman=False
        self.is_afv_trained=False # afv=armored fighting vehicle

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
        self.last_building_check_time=0
        self.building_check_rate=1

        # the ai group that this human is a part of 
        self.squad=None
        self.squad_max_distance=300

        # # target lists. these are refreshed periodically 
        self.near_targets=[]
        self.mid_targets=[]
        self.far_targets=[]
        self.last_target_eval_time=0
        self.target_eval_rate=random.uniform(0.1,0.9)

        # # used to prevent repeats
        self.last_speak=''

    #---------------------------------------------------------------------------
    def action_vehicle_gunner_engage_target(self):
        # this is the action the vehicle gunner takes when it is NOT thinking
        # and has a target that is not None
        target=self.memory['task_vehicle_crew']['target']
        turret=self.memory['task_vehicle_crew']['turret']

        if target.ai.health>0:
            # check actual turret rotation angle against angle to target
            needed_rotation=engine.math_2d.get_rotation(turret.world_coords,target.world_coords)
            
            # probably need to do some rounding here
            if round(needed_rotation,1)!=round(turret.rotation_angle,1):
                if needed_rotation>turret.rotation_angle:
                    turret.ai.handle_rotate_left()
                else:
                    turret.ai.handle_rotate_right()
            else:
                if target.is_human:
                    if turret.ai.coaxial_weapon!=None:
                        turret.ai.handle_fire_coax()
                    else:
                        # maybe fire HE 
                        # for now just fire with the main gun 
                        turret.ai.handle_fire()
                else:
                    turret.ai.handle_fire()
        else:
            self.memory['task_vehicle_crew']['target']=None

    #---------------------------------------------------------------------------
    def building_check(self):

        # randomize time before we hit this method again
        self.building_check_rate=random.uniform(0.1,1.5)
        # clear building list and in_building bool
        self.building_list=[]
        self.in_building=False
        # check to see if we are colliding with any of the buildings
        for b in self.owner.world.wo_objects_building:
            if engine.math_2d.checkCollisionCircleOneResult(self.owner,[b],[]) !=None:
                self.building_list.append(b)
                self.in_building=True

    #---------------------------------------------------------------------------
    def calculate_human_accuracy(self,target_coords,distance,weapon):
        '''returns target_coords adjusted for human weapon accuracy'''

        adjust_max=0


        # mechanical accuracy of the gun
        adjust_max+=weapon.ai.mechanical_accuracy

        # health based
        if self.health<100:
            adjust_max+=1
        if self.health<50:
            adjust_max+=1
        if self.health<30:
            adjust_max+=1

        # fatigue
        if self.fatigue>3:
            adjust_max+=0.5
        if self.fatigue>5:
            adjust_max+=0.5

        # distance based
        if distance>500:
            adjust_max+=1
        if distance>1000:
            adjust_max+=1
        if distance>1500:
            adjust_max+=1
        if distance>2000:
            adjust_max+=1

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
    def calculate_projectile_damage(self,projectile):
        '''calculate and apply damage from projectile hit'''

        bleeding_hit=False
        hit=random.randint(1,5)
        if hit==1:
            #head
            self.health-=random.randint(85,100)
            bleeding_hit=True
                
        elif hit==2:
            #upper body
            self.health-=random.randint(50,80)
            bleeding_hit=True
        elif hit==3:
            #lower body
            self.health-=random.randint(30,60)
            bleeding_hit=True
        elif hit==4:
            # feet
            self.health-=random.randint(30,40)
            bleeding_hit=True
        elif hit==5:
            # hands
            self.health-=random.randint(30,40)
            bleeding_hit=True

        # extra damage from large caliber projectiles
        if engine.penetration_calculator.projectile_data[projectile.ai.projectile_type]['diameter']>12:
            self.health-=30
            bleeding_hit=True
        
        if bleeding_hit:
            self.bleeding=True
            engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'blood_splatter',True)
            if self.owner.is_player:
                self.owner.world.text_queue.insert(0,'You are hit and begin to bleed')

        self.speak('react to being shot')

    #---------------------------------------------------------------------------
    def check_ammo(self,gun):
        '''check ammo and magazines for a gun. return ammo_gun,ammo_inventory,magazine_count'''
        # gun - a world object with ai_gun
        # check_inventory - bool. if true also check inventory
        # return [ammo in gun, ammo in inventory]
        ammo_gun=0
        if gun.ai.magazine!=None:
            ammo_gun=len(gun.ai.magazine.ai.projectiles)

        ammo_inventory=0
        magazine_count=0
        for b in self.inventory:
            if b.is_gun_magazine:
                if gun.name in b.ai.compatible_guns:
                    ammo_inventory+=len(b.ai.projectiles)
                    magazine_count+=1


        return ammo_gun,ammo_inventory,magazine_count

    #---------------------------------------------------------------------------
    def check_ammo_bool(self,gun):
        '''returns True/False as to whether gun has ammo'''
        ammo_gun,ammo_inventory,magazine_count=self.check_ammo(gun)
        if ammo_gun>0:
            return True
        elif ammo_inventory>0:
            return True
        else:
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
    def drop_object(self,OBJECT_TO_DROP):
        ''' drop object into the world '''
        # any distance calculation would be made before this function is called
        if OBJECT_TO_DROP.is_large_human_pickup:
            self.large_pickup=None
        else:
            self.event_remove_inventory(OBJECT_TO_DROP)
            # make sure the obj world_coords reflect the obj that had it in inventory
            OBJECT_TO_DROP.world_coords=copy.copy(self.owner.world_coords)
            
            # grenades get 'dropped' when they are thrown and are special
            if OBJECT_TO_DROP.is_grenade==False:
                engine.math_2d.randomize_position_and_rotation(OBJECT_TO_DROP)
            self.owner.world.add_queue.append(OBJECT_TO_DROP)  
        
    #---------------------------------------------------------------------------
    def eat(self,CONSUMABLE):
        # eat the consumable object. or part of it anyway
        self.health+=CONSUMABLE.ai.health_effect
        self.hunger+=CONSUMABLE.ai.hunger_effect
        self.thirst+=CONSUMABLE.ai.thirst_effect
        self.fatigue+=CONSUMABLE.ai.fatigue_effect

        # this should remove the object from the game because it is not added to world
        self.event_remove_inventory(CONSUMABLE)

    #---------------------------------------------------------------------------
    def evaluate_targets(self):
        '''find and categorize targets. react to close ones'''

        self.near_targets=[]
        self.mid_targets=[]
        self.far_targets=[]

        closest_distance=600
        closest_object=None

        # note we are using this list directly, this is ok because we aren't removing from it
        for b in self.squad.faction_tactical.hostile_humans:
            # quick check because this list isn't refreshed that often..
            if b.ai.health>0:
                d=engine.math_2d.get_distance(self.owner.world_coords,b.world_coords)

                target=b
                if 'task_vehicle_crew' in b.ai.memory:
                    target=b.ai.memory['task_vehicle_crew']['vehicle']
                    # could do something further here to check armor pen

                if d<800:
                    if target not in self.near_targets:
                        self.near_targets.append(target)
                elif d<1500:
                    if target not in self.mid_targets:
                        self.mid_targets.append(target)
                elif d<2450:
                    if target not in self.far_targets:
                        self.far_targets.append(target)

                if d<closest_distance:
                    closest_distance=d
                    closest_object=target

        if closest_object!=None:
            if self.memory['current_task']=='task_vehicle_crew':

                if self.memory['task_vehicle_crew']['role']=='gunner':
                    if self.memory['task_vehicle_crew']['target']==None:
                        self.memory['task_vehicle_crew']['target']=closest_object
                    else:
                        # should probably compare the current target to closest 
                        # and see if it makes sense to switch targets
                        self.memory['task_vehicle_crew']['target']=closest_object

            else:

                # don't want to over ride exiting a vehicle 
                if self.memory['current_task']!='task_exit_vehicle':
                    if self.primary_weapon!=None:
                        if self.check_ammo_bool(self.primary_weapon):
                            self.switch_task_engage_enemy(closest_object)
                    else:
                        engine.log.add_data('warn','close enemy and no primary weapon. not handled. faction:'+self.squad.faction,True)

    #---------------------------------------------------------------------------
    def event_collision(self,event_data):
        if event_data.is_projectile:
            distance=engine.math_2d.get_distance(self.owner.world_coords,event_data.ai.starting_coords,True)
            collision_description='hit by '+event_data.ai.projectile_type + ' projectile at a distance of '+ str(distance)
            starting_health=self.health

            self.calculate_projectile_damage(event_data)

            # data collection
            if event_data.ai.shooter !=None:
                collision_description+=(' from '+event_data.ai.shooter.name)
                if event_data.ai.shooter.ai.primary_weapon!=None:
                    collision_description+=("'s "+event_data.ai.weapon_name)
                self.collision_log.append(collision_description)   

                # kill tracking
                if event_data.ai.shooter.is_human:
                    if self.health<30:
                        # protects from recording hits on something that was already dead
                        if starting_health>0:
                            if self.health<1:
                                event_data.ai.shooter.ai.confirmed_kills+=1
                            else:
                                event_data.ai.shooter.ai.probable_kills+=1
                        else:
                            # collision on a dead human
                            pass
                
            else:
                engine.log.add_data('error', 'projectile '+event_data.name+' shooter is none',True)

            # react 
            if 'vehicle' in self.memory['current_task']:
                # - we are in a vehicle - 
                pass
            else:
                # - we are on foot -

                if self.owner.is_player==False:
                    destination=[0,0]
                    if self.squad.faction_tactical.faction=='civilian':
                        # civilian runs further
                        destination=[self.owner.world_coords[0]+float(random.randint(-560,560)),self.owner.world_coords[1]+float(random.randint(-560,560))]
                    else:
                        # soldier just repositions to get away from the fire
                        destination=[self.owner.world_coords[0]+float(random.randint(-30,30)),self.owner.world_coords[1]+float(random.randint(-30,30))]
                    if self.prone==False:
                        self.prone_state_change()
                    self.switch_task_move_to_location(destination)


        elif event_data.is_grenade:
            # not sure what to do here. the grenade explodes too fast to really do anything

            # attempt to throw the grenade back
            if random.randint(1,5)==1:
                event_data.ai.redirect(event_data.ai.equipper.world_coords)
            else:
                if 'vehicle' in self.memory['current_task']:
                    engine.log.add_data('warn','hit by a grenade while in a vehicle',True)
                else:
                    # - we are on foot - 
                    if self.prone==True:
                        self.prone_state_change()
                    destination=[self.owner.world_coords[0]+float(random.randint(-60,60)),self.owner.world_coords[1]+float(random.randint(-60,60))]
                    self.switch_task_move_to_location(destination)

        elif event_data.is_throwable:
            #throwable but not a grenade 
            self.speak('Oww!')

        else:
            engine.log.add_data('debug','unidentified collision: '+event_data.name,True)

    #---------------------------------------------------------------------------
    def event_add_inventory(self,event_data):
        ''' add object to inventory. does not remove obj from world'''
        if event_data not in self.inventory:
            if event_data.is_large_human_pickup:
                # note - this will happen when a large_human_pickup is in another container
                # for example if a fuel can is in a kubelwagen
                # this does NOT happen when an object is picked up from the world as it is intercepted
                # before it gets this far

                #add to world. (the object was in a inventory array)
                self.owner.world.add_queue.append(event_data)

                self.large_pickup=event_data

            else:

                self.inventory.append(event_data)

                if event_data.is_gun :
                    if self.primary_weapon!=None:
                        # drop the current obj and pick up the new one
                        self.drop_object(self.primary_weapon)
                    if self.owner.is_player :
                        self.owner.world.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                    self.primary_weapon=event_data
                    event_data.ai.equipper=self.owner
                elif event_data.is_throwable :
                    if self.throwable==None:
                        if self.owner.is_player :
                            self.owner.world.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                        self.throwable=event_data
                        event_data.ai.equipper=self.owner
                elif event_data.is_handheld_antitank :
                    if self.antitank!=None:
                        # drop the current obj and pick up the new one
                        self.drop_object(self.antitank)
                    if self.owner.is_player :
                        self.owner.world.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                    self.antitank=event_data
                    event_data.ai.equipper=self.owner

                elif event_data.is_wearable:
                    if event_data.ai.wearable_region=='head':
                        if self.wearable_head==None:
                            self.wearable_head=event_data
        else:
            engine.log.add_data('error','ai_human.event_add_inventory - obj already in inventory: '+event_data.name,True)

    #---------------------------------------------------------------------------
    def event_explosion(self,event_data):
        ''' explosion event '''
        # event_data is the explosion power as a float 

        # this will likely just kill the human

        self.health-=event_data
        engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'blood_splatter',True)

        # short move to simulate being stunned
        if self.owner.is_player==False:
            # move slightly
                coords=[self.owner.world_coords[0]+random.randint(-15,15),self.owner.world_coords[1]+random.randint(-15,15)]
                self.switch_task_move_to_location(coords)



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
            self.switch_task_enter_vehicle(event_data[1],self.squad.destination)
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
    def fire(self,weapon,target):
        ''' fires a weapon '''

        if weapon.ai.check_if_can_fire():

            aim_coords=target.world_coords
            # guess how long it will take for the bullet to arrive
            #time_passed=random.uniform(0.8,1.5)
            distance=engine.math_2d.get_distance(self.owner.world_coords,target.world_coords)
            time_passed=distance/1000
            if target.is_vehicle:
                if target.ai.current_speed>0:
                    aim_coords=engine.math_2d.moveAlongVector(target.ai.current_speed,target.world_coords,target.heading,time_passed)

            if target.is_human:
                if target.ai.memory['current_task']=='task_vehicle_crew':
                    vehicle=target.ai.memory['task_vehicle_crew']['vehicle']
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

                # note - this may be detrimental. needs a rething - 11/14/24
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
            weapon.rotation_angle=engine.math_2d.get_rotation(self.owner.screen_coords,adjusted_coords)
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
        
        return calc_speed
    
    #---------------------------------------------------------------------------
    def get_target(self,range):
        '''returns a target or None if there are None'''
        target=None
        if len(self.near_targets)>0:
            target=self.near_targets.pop()
        elif len(self.mid_targets)>0:
            target=self.mid_targets.pop()
        elif len(self.far_targets)>0:
            target=self.far_targets.pop()

        if target!=None:
            if target.ai.health<1:
                target=None
            else:
                distance=engine.math_2d.get_distance(self.owner.world_coords,target.world_coords)
                if distance>range:
                    # alternatively we could drive closer.
                    target=None
                
        return target
    
    #---------------------------------------------------------------------------
    def give_squad_transportation_orders(self,destination):
        '''assign transportation for the squad'''

        near_squad=self.owner.world.get_objects_within_range(self.owner.world_coords,self.squad.members,800)

        # determine if the whole squad is afv trained
        squad_afv_training=True
        for b in near_squad:
            if b.ai.is_afv_trained==False:
                squad_afv_training=False
                break

        # remove yourself to prevent recursion
        near_squad.remove(self.owner)

        near_vehicle=self.owner.world.get_objects_within_range(self.owner.world_coords,self.owner.world.wo_objects_vehicle,500)

        for b in near_vehicle:

            # skip AFVs if the whole squad isn't trained
            if b.ai.requires_afv_training and squad_afv_training==False:
                pass
            else:

                if len(near_squad)==0:
                    break
                # calculate occupants
                occupants=0

                # count the occupants already in the vehicle
                for c in b.ai.vehicle_crew.values():
                    if c[0]==True:
                        occupants+=1

                for c in self.owner.world.wo_objects_human:
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
                                near_squad[0].ai.switch_task_enter_vehicle(b,destination)
                                occupants+=1
                                near_squad.pop(0)
                    else:
                        break
    
    #---------------------------------------------------------------------------
    def handle_event(self, EVENT, EVENT_DATA):
        ''' overrides base handle_event'''
        # this is supposed to be the main interface that the outside world uses to interact with the ai
        # EVENT - text describing event
        # EVENT_DATA - most likely a world_object but could be anything

        # not sure what to do here yet. will have to think of some standard events
        if EVENT=='add_inventory':
            self.event_add_inventory(EVENT_DATA)
        elif EVENT=='collision':
            self.event_collision(EVENT_DATA)
        elif EVENT=='remove_inventory':
            self.event_remove_inventory(EVENT_DATA)
        elif EVENT=='speak':
            self.event_speak(EVENT_DATA)
        elif EVENT=='explosion':
            self.event_explosion(EVENT_DATA)

        else:
            engine.log.add_data('error','ai_human.handle_event cannot handle event'+EVENT,True)

    #---------------------------------------------------------------------------
    def launch_antitank(self,target_coords,mouse_screen_coords=None):
        ''' launch antitank ''' 

        # standup. kneel would be better if it becomes an option later
        if self.prone:
            self.prone_state_change()

        if self.antitank!=None:
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

            # drop the tube now that it is empty
            self.drop_object(self.antitank)

    #---------------------------------------------------------------------------
    def pickup_object(self,world_object):
        '''pick up a world object'''
        # called by world_menu and task_pickup_objects
        if world_object.is_large_human_pickup:

            # need to make sure nobody else is already carrying it
            in_use=False
            for b in self.owner.world.wo_objects_human:
                if b.ai.large_pickup==b:
                    in_use=True

            if in_use:
                engine.log.add_data('warn','Error large pick up is already picked up: '+b.name,True)
            else:
                self.large_pickup=world_object
        else:
            if world_object.is_gun:
                if self.owner.is_player==False:
                    near_magazines=self.owner.world.get_compatible_magazines_within_range(self.owner.world_coords,self.primary_weapon,200)
                    if len(near_magazines)>0:
                        self.switch_task_pickup_objects(near_magazines)

            self.speak('Picking up a '+world_object.name)

            self.event_add_inventory(world_object)
            # remove from world
            self.owner.world.remove_queue.append(world_object)

    #---------------------------------------------------------------------------
    def player_vehicle_role_change(self,role):
        'player changes vehicle roles'
        # this is called by world_menu
        if self.memory['current_task']=='task_vehicle_crew':
            vehicle=self.memory['task_vehicle_crew']['vehicle']

            # remove yourself from any existing roles 
            # first remove yourself from any existing crew spots
            for key,value in vehicle.ai.vehicle_crew.items():
                if value[1]==self.owner:
                    value[1]=None
                    value[0]=False

                    if key=='driver':
                        # this may not do anything. i think it regresses to zero
                        # turn on the brakes to prevent roll away
                        vehicle.ai.brake_power=1

                    elif key=='radio_operator':
                        if vehicle.ai.radio!=None:
                            if vehicle.ai.radio.ai.radio_operator==self.owner:
                                vehicle.ai.radio.ai.radio_operator=None
                    elif 'passenger' in key:
                        pass

            # --- add to the desired role --
            if role in vehicle.ai.vehicle_crew:
                # set the role in memory
                self.memory['task_vehicle_crew']['role']=role
                self.owner.render=vehicle.ai.vehicle_crew[role][4]

                # occupied?
                if vehicle.ai.vehicle_crew[role][0]==True:
                    # have the current crew member exit and re-enter
                    crew=vehicle.ai.vehicle_crew[role][1]
                    crew.ai.switch_task_exit_vehicle(vehicle)
                    crew.ai.update_task_exit_vehicle()

                vehicle.ai.vehicle_crew[role][0]=True
                vehicle.ai.vehicle_crew[role][1]=self.owner

                if 'gunner' in role:
                    self.memory['task_vehicle_crew']['turret']=vehicle.ai.vehicle_crew[role][5]

                

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
    def reload_weapon(self,weapon,obj_with_inventory):
        '''reload weapon'''
        self.speak('reloading!')
        if weapon.is_gun:
            # first get the current magazine
            old_magazine=None
            if weapon.ai.magazine!=None:
                if weapon.ai.magazine.ai.removable:
                    old_magazine=weapon.ai.magazine

            # find a new magazine, sorting by size
            new_magazine=None
            biggest=0
            for b in obj_with_inventory.ai.inventory:
                if b.is_gun_magazine:
                    if weapon.world_builder_identity in b.ai.compatible_guns:
                        if len(b.ai.projectiles)>biggest:
                            new_magazine=b
                            biggest=len(b.ai.projectiles)

            # remove old magazine ONLY if we have a new magazine
            if old_magazine!=None and new_magazine!=None:
                obj_with_inventory.ai.event_add_inventory(old_magazine)
                weapon.ai.magazine=None
            # add a new magazine (either the old magazine was removed, or was never there)
            if new_magazine!=None:
                obj_with_inventory.ai.event_remove_inventory(new_magazine)
                weapon.ai.magazine=new_magazine
            else:
                self.speak("I'm out of ammo!")

        # at this point we should do a ai_mode change with a timer to simulate the 
        # reload time
        

        
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
    def switch_task_enter_vehicle(self,vehicle,destination):
        '''switch task'''
        task_name='task_enter_vehicle'
        task_details = {
            'vehicle': vehicle,
            'destination': copy.copy(destination)
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name

        if self.squad.squad_leader==self.owner:
            # for now the afv stuff just confuses stuff. we don't want them joining up as passengers
            if self.is_afv_trained==False:
                self.give_squad_transportation_orders(destination)

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
    def switch_task_exit_vehicle(self,vehicle):
        '''switch task'''
        task_name='task_exit_vehicle'
        task_details = {
            'vehicle': vehicle,
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
    def switch_task_move_to_location(self,destination):
        '''switch task'''
        # destination : this is a world_coords
        task_name='task_move_to_location'
        task_details = {
            'destination': copy.copy(destination),
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
            self.memory[task_name][objects]+=objects
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
    def switch_task_squad_leader(self):
        '''switch task'''
        task_name='task_squad_leader'

        if task_name in self.memory:
            # something here eventually?
            pass
        else:
            task_details = {
                'last_think_time': 0,
                'think_interval': 0.5
            }

            self.memory[task_name]=task_details

        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def switch_task_think(self):
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
    def switch_task_vehicle_crew(self,vehicle,destination):
        '''switch task to vehicle crew and determine role'''
        # this should always overwrite if it exists
        # A player can go through this if they enter a vehicle
        # this can also be used by a ai in a vehicle already that wants to change role
        # role should be NONE in most cases. 

        # first remove yourself from any existing crew spots
        for key,value in vehicle.ai.vehicle_crew.items():
            if value[1]==self.owner:
                value[1]=None
                value[0]=False

                if key=='driver':
                    # this may not do anything. i think it regresses to zero
                    # turn on the brakes to prevent roll away
                    vehicle.ai.brake_power=1

                elif key=='radio_operator':
                    if vehicle.ai.radio!=None:
                        if vehicle.ai.radio.ai.radio_operator==self.owner:
                            vehicle.ai.radio.ai.radio_operator=None
                elif 'passenger' in key:
                    pass

        role=None
        turret=None
        # pick a role
        if vehicle.ai.vehicle_crew['driver'][0]==False:
            role='driver'
            vehicle.ai.vehicle_crew['driver'][0]=True
            vehicle.ai.vehicle_crew['driver'][1]=self.owner
            self.owner.render=vehicle.ai.vehicle_crew['driver'][4]
            self.speak("Taking over driving")

        if role==None:
            for key,value in vehicle.ai.vehicle_crew.items():
                if role!=None:
                    break
                if 'gunner' in key:
                    if value[0]==False:
                        vehicle.ai.vehicle_crew[key][0]=True
                        vehicle.ai.vehicle_crew[key][1]=self.owner
                        self.owner.render=vehicle.ai.vehicle_crew[key][4]
                        turret=vehicle.ai.vehicle_crew[key][5]
                        role='gunner'

        # note that some vehicles may not have this crew slot
        if role==None and 'radio_operator' in vehicle.ai.vehicle_crew:
            if vehicle.ai.vehicle_crew['radio_operator'][0]==False:
                vehicle.ai.vehicle_crew['radio_operator'][0]=True
                vehicle.ai.vehicle_crew['radio_operator'][1]=self.owner
                self.owner.render=vehicle.ai.vehicle_crew['radio_operator'][4]

                if vehicle.ai.radio!=None:
                    if vehicle.ai.radio.ai.radio_operator==None:
                            role='radio_operator'
                else:
                    # no radio - so just fill this crew spot as a passenger
                    role='passenger'
                
        if role==None:
            
            # check if any passenger slots are open
            for key,value in vehicle.ai.vehicle_crew.items():
                if 'passenger' in key:
                    if value[0]==False:
                        role='passenger'
                        vehicle.ai.vehicle_crew[key][0]=True
                        vehicle.ai.vehicle_crew[key][1]=self.owner
                        self.owner.render=vehicle.ai.vehicle_crew[key][4]
                        break

        if role==None:
            engine.log.add_data('error','ai_human.switch_task_vehicle_crew No role found!! Vehicle is full='+str(vehicle.ai.check_if_vehicle_is_full()),True)
            print('name: '+self.owner.name)
            print('vehicle crew')
            for key,value in vehicle.ai.vehicle_crew.items():
                if value[0]==True:
                    print(key,value[1].name)
                else:
                    print(key,'empty')


        # update the position to reflect the new seat
        vehicle.ai.update_child_position_rotation()

        task_name='task_vehicle_crew'
        task_details = {
            'vehicle': vehicle,
            'role': role,
            'turret': turret,
            'radio_recieve_queue': [], # this is populated by ai_radio
            'destination': copy.copy(destination),
            'target': None, # target for tthe gunner role
            'last_think_time': 0,
            'think_interval': 0.5
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name
        

    #---------------------------------------------------------------------------
    def think_vehicle_role_driver(self):
        vehicle=self.memory['task_vehicle_crew']['vehicle']
        destination=self.memory['task_vehicle_crew']['destination']

        # check if anyone is trying to get in 
        new_passengers=0
        for b in self.owner.world.wo_objects_human:
            if 'task_enter_vehicle' in b.ai.memory:
                if vehicle==b.ai.memory['task_enter_vehicle']['vehicle']:
                    new_passengers+=1
        
        distance=engine.math_2d.get_distance(self.owner.world_coords,destination)
        
        if distance<150 and vehicle.ai.current_speed<1:
            # check if we have a different destination from the squad 
            # this may have updated since we started driving
            if engine.math_2d.get_distance(destination,self.squad.destination)<350:
                # we are at our old destination AND we are near the current squad destination
                
                # lets jump out
                # only jump out if you aren't dedicated afv crew
                if self.is_afv_trained==False:
                    self.switch_task_exit_vehicle(vehicle)
            else:
                # we have a new destination
                self.memory['task_vehicle_crew']['destination']=engine.math_2d.randomize_coordinates(self.squad.destination,50)
        elif new_passengers>0:
            # wait for new passengers
            vehicle.ai.brake_power=1
            vehicle.ai.throtte=0

        else:

            # turn engines on
            # could do smarter checks here once engines have more stats
            need_start=False
            for b in vehicle.ai.engines:
                if b.ai.engine_on==False:
                    need_start=True
            if need_start:
                vehicle.ai.handle_start_engines()

            # get the rotation to the destination 
            r = engine.math_2d.get_rotation(vehicle.world_coords,destination)

            v = vehicle.rotation_angle

            if r>v:
                vehicle.ai.handle_steer_left()

            if r<v:
                vehicle.ai.handle_steer_right()

            
            # if its close just set it equal
            if r>v-3 and r<v+3:
                # neutral out steering 
                vehicle.ai.handle_steer_neutral()
                vehicle.rotation_angle=r
                vehicle.ai.update_heading()

            if (r>355 and v<5) or (r<5 and v>355):
                # i think the rotation angle wrapping 360->0 and 0->360 is goofing stuff
                vehicle.ai.handle_steer_neutral()
                vehicle.rotation_angle=r
                vehicle.ai.update_heading()
                engine.log.add_data('warn','fixing 360 vehicle steering issue',False)

            if distance<140:
                # apply brakes. bot will only exit when speed is zero
                # note this number should be < the minimum distance to jump out
                # or you can end up with drivers stuck in the vehicle if they slow down fast
                vehicle.ai.throttle=0
                vehicle.ai.brake_power=1
            elif distance<300:
                vehicle.ai.throttle=0.5
                vehicle.ai.brake_power=0
            else:
                vehicle.ai.throttle=1
                vehicle.ai.brake_power=0

    #---------------------------------------------------------------------------
    def think_vehicle_role_gunner(self):
        vehicle=self.memory['task_vehicle_crew']['vehicle']
        turret=self.memory['task_vehicle_crew']['turret']

        # check main gun ammo
        ammo_gun,ammo_inventory,magazine_count=self.check_ammo(turret.ai.primary_weapon)
        if ammo_gun==0 and ammo_inventory>0:
            # this should be re-done to check for ammo in vehicle, and do something if there is none
            self.reload_weapon(turret.ai.primary_weapon,vehicle)

        # check coax ammo
        if turret.ai.coaxial_weapon!=None:
            ammo_gun,ammo_inventory,magazine_count=self.check_ammo(turret.ai.primary_weapon)
            if ammo_gun==0 and ammo_inventory>0:
                # this should be re-done to check for ammo in vehicle, and do something if there is none
                self.reload_weapon(turret.ai.coaxial_weapon,vehicle)



        if self.memory['task_vehicle_crew']['target']==None:
            self.memory['task_vehicle_crew']['target']=self.get_target(turret.ai.primary_weapon.ai.range)
        else:
            if self.memory['task_vehicle_crew']['target'].ai.health<1:
                self.memory['task_vehicle_crew']['target']=self.get_target(turret.ai.primary_weapon.ai.range)

        # we either already had a target, or we might have just got a new one
        if self.memory['task_vehicle_crew']['target']!=None:
 
            # check rotation
            rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,self.memory['task_vehicle_crew']['target'].world_coords)
            if self.check_vehicle_turret_rotation_real_angle(rotation_angle,turret)==False:
                # lots of things we could do here.
                # we could have the driver rotate
                # for now just get rid of the target
                self.memory['task_vehicle_crew']['target']==None
            else:
                # check distance
                distance=engine.math_2d.get_distance(self.owner.world_coords,self.memory['task_vehicle_crew']['target'].world_coords)
                if distance>turret.ai.primary_weapon.ai.range:
                    # alternatively we could drive closer.
                    self.memory['task_vehicle_crew']['target']==None


        # if we get this far then we just fire at it
                
    #---------------------------------------------------------------------------
    def think_vehicle_role_passenger(self):
        vehicle=self.memory['task_vehicle_crew']['vehicle']

        # for whatever reason sometimes a vehicle will have a driver jump out
        # this will cause a passenger to take over. will also fill in any empty gunner spots
        if vehicle.ai.vehicle_crew['driver'][0]==False:
            self.switch_task_vehicle_crew(vehicle,self.squad.destination)
        
        if len(self.near_targets)>0:
            # check if we should be worried about small arms fire
            # near targets will absolutely chew up a unarmored vehicle

            # kind of a hack. left and right are likely symetric so its a good
            # general guess
            if vehicle.ai.passenger_compartment_armor['left'][0]<5:
                self.switch_task_exit_vehicle(vehicle)

    #---------------------------------------------------------------------------
    def think_vehicle_role_radio_operator(self):
        # note radio.ai.radio_operator set by switch_task_vehicle_crew
        # not a ton that we really need to do here atm


        vehicle=self.memory['task_vehicle_crew']['vehicle']
        radio=vehicle.ai.radio
        if radio==None:
            # radio dissapeared. get a different vehicle task
            self.switch_task_vehicle_crew(vehicle,self.memory['task_vehicle_crew']['destination'])
            
        else:
            if radio.ai.power_on==False:
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
                if len(self.memory['task_vehicle_crew']['radio_recieve_queue'])>0:
                    message=self.memory['task_vehicle_crew']['radio_recieve_queue'].pop()
                    
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
    def throw(self,TARGET_COORDS,mouse_screen_coords=None):
        ''' throw like you know the thing. cmon man '''   
        # stand up
        if self.prone:
            self.prone_state_change() 
        if self.throwable!=None:

            # this does all the needed internal ai stuff for the throwable 
            self.throwable.ai.throw()

            # set rotation and heading
            if self.owner.is_player :
                # do computations based off of where the mouse is. TARGET_COORDS is ignored
                self.throwable.rotation_angle=engine.math_2d.get_rotation(self.owner.screen_coords,mouse_screen_coords)
                self.throwable.heading=engine.math_2d.get_heading_vector(self.owner.screen_coords,mouse_screen_coords)
            else :
                self.throwable.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,TARGET_COORDS)
                self.throwable.heading=engine.math_2d.get_heading_vector(self.owner.world_coords,TARGET_COORDS)

            self.drop_object(self.throwable)


    #---------------------------------------------------------------------------
    def transfer_liquid(self,FROM_OBJECT,TO_OBJECT):
        '''transfer liquid/ammo/??? from one object to another'''
        

        if FROM_OBJECT.is_liquid and TO_OBJECT.is_container:
            source_amount=FROM_OBJECT.volume
            
            # add up total destination volume
            destination_amount=0
            for b in TO_OBJECT.ai.inventory:
                destination_amount+=b.volume

            # remember in containers this is considered a max volume    
            destination_maximum=TO_OBJECT.volume
            source_result,destination_result=engine.math_2d.get_transfer_results(source_amount,destination_amount,destination_maximum)
            FROM_OBJECT.volume=source_result
            
            # spawn a new liquid object with the amount to transfer
            z=engine.world_builder.spawn_object(self.owner.world,[0,0],FROM_OBJECT.name,False)
            z.volume=destination_result

            # add the new liquid to the container
            TO_OBJECT.add_inventory(z)
        else:
            engine.log.add_data('error','ai_human.transfer_liquid - src/dest not recognized',True)

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        # update health 
        self.update_health()

        if self.health>0:
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
            if (self.owner.world.world_seconds-self.last_target_eval_time>self.target_eval_rate) and self.owner.is_player==False:
                self.last_target_eval_time=self.owner.world.world_seconds
                self.target_eval_rate=random.uniform(0.8,6.5)
                self.evaluate_targets()

            # might be faster to have a bool we could check
            if self.large_pickup!=None:
                self.large_pickup.world_coords=engine.math_2d.get_vector_addition(self.owner.world_coords,self.carrying_offset)
                
            # building awareness stuff. ai and human need this
            if self.owner.world.world_seconds-self.last_building_check_time>self.building_check_rate:
                self.last_building_check_time=self.owner.world.world_seconds
                self.building_check()

    #---------------------------------------------------------------------------
    def update_equipment_slots(self):
        '''update any empty equipment slots'''

        # primmary weapon
        # could also take ammo into account here 
        if self.primary_weapon==None:
            for b in self.inventory:
                if b.is_gun:
                    self.primary_weapon=b
                    b.ai.equipper=self.owner
                    break

        # secondary weapon

        # throwable
        if self.throwable==None:
            for b in self.inventory:
                if b.is_throwable:
                    self.throwable=b
                    b.ai.equipper=self.owner
                    break

        # anti-tank
        if self.antitank==None:
            for b in self.inventory:
                if b.is_handheld_antitank:
                    self.antitank=b
                    b.ai.equipper=self.owner
                    break

    #---------------------------------------------------------------------------
    def update_health(self):
        '''update health and handle death'''

        if self.health>0:
            if self.bleeding:
                if self.owner.world.world_seconds-self.last_bleed_time>self.bleed_interval:
                    self.last_bleed_time=self.owner.world.world_seconds+random.uniform(0,2)
                    engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'small_blood',True)
                    self.health-=1+random.uniform(0,3)

                    if random.randint(0,3)==0:
                        for b in self.inventory:
                            if b.is_medical:
                                self.use_medical_object(b)
                                break
                # possibly have a random stop bleed even if you don't have medical

            # -- body attribute stuff --
            if self.fatigue>0:
                self.fatigue-=self.fatigue_remove_rate*self.owner.world.time_passed_seconds
            self.hunger+=self.hunger_rate*self.owner.world.time_passed_seconds
            self.thirst+=self.thirst_rate*self.owner.world.time_passed_seconds
    
        else:
            # -- handle death --
            # construct death message
            dm=''
            dm+=('\n  -------------------')
            dm+=('\n '+self.owner.name+' died.')
            dm+=('\n  - faction: '+self.squad.faction)
            dm+=('\n  - confirmed kills: '+str(self.confirmed_kills))
            dm+=('\n  - probable kills: '+str(self.probable_kills))
            dm+=('\n  - collision log --')
            for b in self.collision_log:
                dm+=('\n     - '+b)
            dm+=('\n  ------------------')
            
            
            # drop primary weapon 
            if self.primary_weapon!=None:
                ammo,ammo_inventory,magazines=self.check_ammo(self.primary_weapon)
                dm+=('\n  - weapon: '+self.primary_weapon.name)
                dm+=('\n  -- ammo in gun: '+str(ammo))
                dm+=('\n  -- ammo in inventory: '+str(ammo_inventory))
                dm+=('\n  -- magazine count: '+str(magazines))

                self.drop_object(self.primary_weapon)
            
            dm+=('\n  -------------------')

            # drop large pickup
            if self.large_pickup!=None:
                self.drop_object(self.large_pickup)

            if self.memory['current_task']=='task_vehicle_crew':
                # re-use this function to exit the vehicle cleanly
                self.switch_task_exit_vehicle(self.memory['task_vehicle_crew']['vehicle'])
                self.update_task_exit_vehicle()
            elif self.memory['current_task']=='task_exit_vehicle':
                self.update_task_exit_vehicle()

            # remove from squad 
            if self.squad != None:
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
            print(dm)

    #---------------------------------------------------------------------------
    def update_task_engage_enemy(self):

        # - getting this far assumes that you have a primary weapon

        enemy=self.memory['task_engage_enemy']['enemy']
        if enemy.ai.health<1:
            self.memory.pop('task_engage_enemy',None)
            self.switch_task_think()
        else:
            last_think_time=self.memory['task_engage_enemy']['last_think_time']
            think_interval=self.memory['task_engage_enemy']['think_interval']
    
            if self.owner.world.world_seconds-last_think_time>think_interval:
                # -- think --

                # reset time
                self.memory['task_engage_enemy']['last_think_time']=self.owner.world.world_seconds
                self.memory['task_engage_enemy']['think_interval']=random.uniform(0.1,1.5)

                # distance?
                distance=engine.math_2d.get_distance(self.owner.world_coords,enemy.world_coords)

                if distance<self.primary_weapon.ai.range:
                    # maybe only when not in buildings??
                    if not self.prone:
                        self.prone_state_change()

                    # out of ammo ?
                    ammo_gun,ammo_inventory,magazine_count=self.check_ammo(self.primary_weapon)
                    if ammo_gun==0:
                        if ammo_inventory>0:
                            self.reload_weapon(self.primary_weapon,self.owner)
                        else:
                            # need ammo or new gun. hand it over to think to deal with this
                            self.memory.pop('task_engage_enemy',None)
                            self.switch_task_think()
                            

                    # also check if we should chuck a grenade at it
                    if distance<310 and distance>150 and self.throwable!=None:
                        if enemy.is_human:
                            self.throw(enemy.world_coords)
                            self.speak('Throwing Grenade !!!!')
                        elif enemy.is_vehicle:
                            # grenades will miss if the vehicle is moving fast
                            if enemy.ai.current_speed<5:
                                # check pen
                                if enemy.ai.passenger_compartment_armor['left'][0]<4:
                                    self.throw(enemy.world_coords)
                                    self.speak('Throwing Grenade !!!!')


                    # also check if we should launch antitank
                    if enemy.is_vehicle:
                        if self.antitank!=None and distance<1800:
                            self.launch_antitank(enemy.world_coords)
                        else:
                            # if we get this far the gun has a magazine and ammo

                            # can we penetrate it in a best case scenario?
                            penetration=False
                            if ammo_gun>0:
                                if engine.penetration_calculator.calculate_penetration(self.primary_weapon.ai.magazine.ai.projectiles[0],distance,'steel',enemy.ai.vehicle_armor['left']):
                                    penetration=True
                                if engine.penetration_calculator.calculate_penetration(self.primary_weapon.ai.magazine.ai.projectiles[0],distance,'steel',enemy.ai.passenger_compartment_armor['left']):
                                    penetration=True

                            if penetration==False:
                                self.memory.pop('task_engage_enemy',None)
                                self.switch_task_think()
                                
                else:

                    new_enemy=self.get_target(self.primary_weapon.ai.range)
                    if new_enemy==None:

                            # no closer targets. is the target really far out of range?
                        if distance>(self.primary_weapon.ai.range+self.primary_weapon.ai.range*0.5):
                            self.memory.pop('task_engage_enemy',None)
                            self.switch_task_think()
                        else:
                            # note this should be rewritten to move just a bit towards the enemy, not the whole way
                            self.switch_task_move_to_location(enemy.world_coords)
                    else:
                        self.switch_task_engage_enemy(new_enemy)
                    

            else:
                # -- fire --
                self.fire(self.primary_weapon,enemy)
                self.fatigue+=self.fatigue_add_rate*self.owner.world.time_passed_seconds

    #---------------------------------------------------------------------------
    def update_task_enter_vehicle(self):
        # Note - this task can also handle the player trying to enter a vehicle 

        vehicle=self.memory['task_enter_vehicle']['vehicle']
        destination=self.memory['task_enter_vehicle']['destination']

        if self.owner.world.check_object_exists(vehicle)==False:
            self.speak('Where did that '+vehicle.name+' go?')
            self.memory.pop('task_enter_vehicle',None)
            self.switch_task_think()
        else:
            # -- vehicle still exists --

            distance=engine.math_2d.get_distance(self.owner.world_coords,vehicle.world_coords)
            distance_to_destination=engine.math_2d.get_distance(self.owner.world_coords,destination)

            if distance_to_destination<distance and self.owner.is_player==False:
                # -- vehicle is further than where we wanted to go --

                # i think this should never happen??
                # basically we are closer to our final destination than we are to the vehicle

                # first cancel the task
                self.memory.pop('task_enter_vehicle',None)
                self.switch_task_think()
                
                # double check its walkable
                if distance_to_destination<self.max_walk_distance:
                    self.switch_task_move_to_location(destination)
                else:
                    # this is probably a loop at this point, lets just cancel the original task
                    self.memory.pop('task_move_to_location',None)
                    self.switch_task_think()
            else:
                # -- vehicle task still makes sense --
                # -- OR we are the player--

                if distance<self.max_distance_to_interact_with_object or self.owner.is_player:

                    # no matter what at this point this task is complete
                    self.memory.pop('task_enter_vehicle',None)
                    # reset current task if we don't end up doing anything else
                    self.switch_task_think()

                    # remove this as well so we don't end up wanting to go back to where the vehicle was

                    precheck=True
                    if vehicle.ai.check_if_vehicle_is_full()==True:
                        precheck=False
                        self.speak('No more room in this vehicle!')
                    
                    if precheck:
                        for value in vehicle.ai.vehicle_crew.values():
                            if value[0]==True:
                                if value[1].ai.squad.faction!=self.squad.faction:
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
                        self.switch_task_vehicle_crew(vehicle,destination)

                else:
                    # -- too far away to enter, what do we do --
                    if distance<self.max_walk_distance:
                        self.switch_task_move_to_location(vehicle.world_coords)
                    else:
                        # vehicle is way too far away, just cancel task
                        self.memory.pop('task_enter_vehicle',None)
                        self.switch_task_think()
                        engine.log.add_data('warn','enter vehicle task canceled as vehicle is too far',True)

    #---------------------------------------------------------------------------
    def update_task_exit_vehicle(self):
        vehicle=self.memory['task_exit_vehicle']['vehicle']


        for key,value in vehicle.ai.vehicle_crew.items():
            if value[1]==self.owner:
                value[1]=None
                value[0]=False

                if key=='driver':
                    # this may not do anything. i think it regresses to zero
                    # turn on the brakes to prevent roll away
                    vehicle.ai.brake_power=1

                    # tell everyone else to GTFO
                    for b in vehicle.ai.vehicle_crew.values():
                        if b[0]==True:
                            b[1].ai.switch_task_exit_vehicle(vehicle)
                elif key=='radio_operator':
                    if vehicle.ai.radio!=None:
                        if vehicle.ai.radio.ai.radio_operator==self.owner:
                            vehicle.ai.radio.ai.radio_operator=None
                elif 'passenger' in key:
                    pass
                elif 'gunner' in key:
                    pass

                else:
                    engine.log.add_data('error','ai_human.update_task_exit_vehicle no role found!',True)


        # make sure we are visible again
        self.owner.render=True

        # delete vehicle role memory 
        self.memory.pop('task_vehicle_crew',None)

        # delete this task as it is now complete
        self.memory.pop('task_exit_vehicle',None)

        # maybe grab your large pick up if you put it in the trunk
        if self.health>0:
            self.speak('Jumping out')

            if self.owner.is_player==False:
            # move slightly
                coords=[self.owner.world_coords[0]+random.randint(-15,15),self.owner.world_coords[1]+random.randint(-15,15)]
                self.switch_task_move_to_location(coords)
            else:
                pass

    #---------------------------------------------------------------------------
    def update_task_loot_container(self):
        '''loot a container or object with ai.inventory'''
        container=self.memory['task_loot_container']['container']

        if self.owner.world.check_object_exists(container)==False:
            self.memory.pop('task_loot_container',None)
            self.switch_task_think()
        else:
            distance=engine.math_2d.get_distance(self.owner.world_coords,container.world_coords)
            if distance<self.max_distance_to_interact_with_object:
                # done with this task
                self.memory.pop('task_loot_container',None)
                self.switch_task_think()

                # -- loot container --
                need_medical=True
                need_consumable=True
                need_grenade=True
                need_antitank=False
                need_gun=self.primary_weapon==None

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
                    if gun==None:
                        if self.primary_weapon!=None:
                            gun=self.primary_weapon

                    # if we have a gun now, grab compatible magazines
                    # only grab 2 magazines though
                    grabbed=0
                    if gun!=None:
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
                self.switch_task_move_to_location(container.world_coords)

    #---------------------------------------------------------------------------
    def update_task_move_to_location(self):
        '''update task'''
        
        last_think_time=self.memory['task_move_to_location']['last_think_time']
        think_interval=self.memory['task_move_to_location']['think_interval']
        destination=self.memory['task_move_to_location']['destination']

        
        if self.owner.world.world_seconds-last_think_time>think_interval:
            # reset time
            self.memory['task_move_to_location']['last_think_time']=self.owner.world.world_seconds

            # -- think about walking --
            distance=engine.math_2d.get_distance(self.owner.world_coords,destination)

            if distance>200 and self.prone:
                self.prone_state_change()

            # should we get a vehicle instead of hoofing it to wherever we are going?
            if distance>self.max_walk_distance:
                
                b=self.owner.world.get_closest_vehicle(self.owner,(self.max_walk_distance*0.6))
                if b!=None:
                    # get_closest_vehicle only returns vehicles that aren't full
                    # won't return planes if not a pilot
                    # won't return AFVs if not AFV trained
                    self.switch_task_enter_vehicle(b,destination)


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
                self.owner.world_coords,destination,self.owner.world.time_passed_seconds)
            # add some fatigue
            self.fatigue+=self.fatigue_add_rate*self.owner.world.time_passed_seconds

    #---------------------------------------------------------------------------
    def update_task_pickup_objects(self):
        objects=self.memory['task_pickup_objects']['objects']
        remove_queue=[]
        nearest_distance=2000
        nearest_object=None
        for b in objects:
            if self.owner.world.check_object_exists(b)==False:
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
        if nearest_object!=None:
            self.switch_task_move_to_location(nearest_object.world_coords)

    #---------------------------------------------------------------------------
    def update_task_player_control(self):
        '''update player control task'''
        # controls got moved to world. nothing left over here for now
        pass

    #---------------------------------------------------------------------------
    def update_task_squad_leader(self):

        last_think_time=self.memory['task_squad_leader']['last_think_time']
        think_interval=self.memory['task_squad_leader']['think_interval']

        
        if self.owner.world.world_seconds-last_think_time>think_interval:
            # reset time
            self.memory['task_squad_leader']['last_think_time']=self.owner.world.world_seconds

            # -- do the longer thing ---
            action=False
            
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.squad.destination)
            if distance>150:
                self.switch_task_move_to_location(self.squad.destination)
                action=True

            # check on squad members?
                
            # coordinate with nearby squad lead?
                
            # check in with HQ ?
                
            # read and reply to radio messages
            
        else:
            # -- do the shorter thing --
            # this would be better as a task_do_random_thing
            # go for a walk
            decision=random.randint(1,100)
            if decision==1:
                coords=[self.owner.world_coords[0]+random.randint(-25,25),self.owner.world_coords[1]+random.randint(-25,25)]
                self.switch_task_move_to_location(coords)

    #---------------------------------------------------------------------------
    def update_task_think(self):
        '''task think - thinking about what to do next'''
        # the ugly function where we have to determine what we are doing

        # !! probably need to check the last time we were here so we aren't 
        # hitting this too often as it is likely computationally intense

        action=False
        
        # -- priorities --

        if self.owner.is_player:
            self.switch_task_player_control()
            action=True

        if action==False:


            # primary weapon
            if self.primary_weapon==None:
                # need to get a gun
                distance=4000
                if len(self.near_targets)>0:
                    distance=200
                elif len(self.mid_targets)>0:
                    distance=400
                elif len(self.far_targets)>0:
                    distance=900

                # this also means that humans without any targets will not get a gun
                if distance<4000:
                    gun=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_guns,distance)

                    if gun!=None:
                        self.switch_task_pickup_objects([gun])
                        action=True
            else:
                # -- we have a gun. is it usable? --
                if self.check_ammo_bool==False:
                    # need to get ammo. check for nearby magazines
                    near_magazines=self.owner.world.get_compatible_magazines_within_range(self.owner.world_coords,self.primary_weapon,500)
                    if len(near_magazines)>0:
                        self.switch_task_pickup_objects(near_magazines)
                        action=True
                    else:
                        # check containers
                        containers=self.owner.world.get_objects_within_range(self.owner.world_coords,self.owner.world.wo_objects_container,500)
                        if len(containers)>0:
                            self.switch_task_loot_container(random.choice(containers))
                        else:
                            # set primary weapon to none - possibly causing the bot to pickup a new weapon
                            self.primary_weapon=None
        
        # -- check if we have older tasks to resume --
        # this is important for compound tasks 
        if action==False:
            if 'task_enter_vehicle' in self.memory:
                self.memory['current_task']='task_enter_vehicle'
                action=True
            elif 'task_pickup_objects' in self.memory:
                self.memory['current_task']='task_pickup_objects'
                action=True
            elif 'task_loot_container' in self.memory:
                self.memory['current_task']='task_loot_container'
                action=True

        # -- squad stuff --
        # this should be AFTER anything else important
        if action==False:
            if self.squad.squad_leader==None:
                self.squad.squad_leader=self.owner

            if self.squad.squad_leader==self.owner:
                self.switch_task_squad_leader()
                action=True
            else:
                # being in a squad wwhen we aren't lead basically just means staying close to the squad lead
                distance=engine.math_2d.get_distance(self.owner.world_coords,self.squad.squad_leader.world_coords)
                # are we close enough to squad?
                if distance>self.squad_max_distance:
                    self.switch_task_move_to_location(self.squad.squad_leader.world_coords)
                    action=True

        # -- ok now we've really run out of things to do. do things that don't matter
        # ! NOTE Squad Lead will never get this far
        if action==False:
            decision=random.randint(0,10)
            if decision==1:
                # go for a walk
                coords=[self.owner.world_coords[0]+random.randint(-45,45),self.owner.world_coords[1]+random.randint(-45,45)]
                self.switch_task_move_to_location(coords)
            elif decision==2:
                # check containers
                containers=self.owner.world.get_objects_within_range(self.owner.world_coords,self.owner.world.wo_objects_container,1000)
                if len(containers)>0:
                    self.switch_task_loot_container(random.choice(containers))
            elif decision==3:
                # eat 
                for b in self.inventory:
                    if b.is_consumable:
                        self.eat(b)
                        break

    #---------------------------------------------------------------------------
    def update_task_vehicle_crew(self):

        vehicle=self.memory['task_vehicle_crew']['vehicle']
        if vehicle.ai.health<1:
            self.switch_task_exit_vehicle(vehicle)
        else:
            vehicle=self.memory['task_vehicle_crew']['vehicle']
            role=self.memory['task_vehicle_crew']['role']
            turret=self.memory['task_vehicle_crew']['turret']

            if self.owner.is_player:
                # not sure what we need to to do here. controls are now handled by world
                pass
            else:
                last_think_time=self.memory['task_vehicle_crew']['last_think_time']
                think_interval=self.memory['task_vehicle_crew']['think_interval']

                # think
                if self.owner.world.world_seconds-last_think_time>think_interval:
                    # reset time
                    self.memory['task_vehicle_crew']['last_think_time']=self.owner.world.world_seconds
                    

                    if role=='driver':
                        # driver needs a fast refresh for smooth vehicle controls
                        self.memory['task_vehicle_crew']['think_interval']=random.uniform(0.1,0.1)
                        self.think_vehicle_role_driver()
                    elif role=='gunner':
                        self.memory['task_vehicle_crew']['think_interval']=random.uniform(0.1,0.3)
                        self.think_vehicle_role_gunner()
                    elif role=='passenger':
                        self.memory['task_vehicle_crew']['think_interval']=random.uniform(0.1,0.5)
                        self.think_vehicle_role_passenger()
                    elif role=='radio_operator':
                        self.memory['task_vehicle_crew']['think_interval']=random.uniform(0.1,0.5)
                        self.think_vehicle_role_radio_operator()
                    else:
                        engine.log.add_data('error','unknown vehicle role: '+role,True)

                else:
                    # some roles will want to do something every update cycle

                    if role=='gunner':
                        if self.memory['task_vehicle_crew']['target']!=None:
                            self.action_vehicle_gunner_engage_target()


    #-----------------------------------------------------------------------
    def use_medical_object(self,medical):
        # MEDICAL - a medical object

        # should eventually handle bandages, morphine, etc etc
        # probably need attributes similar to consumables

        # should select the correct medical item to fix whatever the issue is

        self.speak('Using medical '+medical.name)

        self.bleeding=False

        self.health+=medical.ai.health_effect
        self.hunger+=medical.ai.hunger_effect
        self.thirst_rate+=medical.ai.thirst_effect
        self.fatigue+=medical.ai.fatigue_effect

        # calling this by itself should remove all references to the object
        self.event_remove_inventory(medical)

            


