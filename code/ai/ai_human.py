
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
from ai.ai_base import AIBase
import engine.math_2d
import engine.world_builder
import engine.log

#global variables

class AIHuman(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        self.task_map={
            'task_player_control':update_task_player_control,
            'task_enter_vehicle':update_task_enter_vehicle,
            'task_exit_vehicle':update_task_exit_vehicle,
            'task_move_to_location':update_task_move_to_location,
            'task_vehicle_crew':update_task_vehicle_crew,
            'task_engage_enemy':update_task_engage_enemy,
            'task_pickup_objects':update_task_pickup_objects
        }

        self.memory={}

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
        # objects that are large_human_pickup. only one at a time
        self.large_pickup=None
        self.carrying_offset=[10,10]  #vector offset for when you are carrying a object

        # -- skills --
        self.is_pilot=False

        # -- stats --
        self.confirmed_kills=0
        self.probable_kills=0
        self.last_collision_description=''

        # -- firing pattern stuff
        # burst control keeps ai from shooting continuous streams
        self.current_burst=0 # int number of bullets shot in current burst
        self.max_burst=10

        # -- OLD ---
        
        # self.throwable=None
        # self.antitank=None
        # self.melee=None

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
    def aim_and_fire_weapon(self,weapon,target):
        ''' handles special aiming and firing code for various targets'''
        aim_coords=self.target_object.world_coords
        # guess how long it will take for the bullet to arrive
        time_passed=random.uniform(0.8,1.5)
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

        self.fire(aim_coords,weapon)

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
        
        if bleeding_hit:
            self.bleeding=True
            engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'blood_splatter',True)
            if self.owner.is_player:
                self.owner.world.graphic_engine.text_queue.insert(0,'You are hit and begin to bleed')

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
    def evaluate_targets(self):
        '''find and categorize targets. react to close ones'''
        target_list=[]
        if self.squad.faction=='german':
            target_list=self.owner.world.wo_objects_soviet+self.owner.world.wo_objects_american
        elif self.squad.faction=='american':
            target_list=self.owner.world.wo_objects_soviet+self.owner.world.wo_objects_german
        elif self.squad.faction=='soviet':
            target_list=self.owner.world.wo_objects_german+self.owner.world.wo_objects_american
        elif self.squad.faction=='civilian':
            pass
        else:
            print('error! unknown squad faction!')

        self.near_targets=[]
        self.mid_targets=[]
        self.far_targets=[]

        closest_distance=600
        closest_object=None
        for b in target_list:
            d=engine.math_2d.get_distance(self.owner.world_coords,b.world_coords)

            if d<500:
                self.near_targets.append(b)
            elif d<850:
                self.mid_targets.append(b)
            elif d<1300:
                self.far_targets.append(b)

            if d<closest_distance:
                closest_distance=d
                closest_object=b

        if closest_object!=None:
            if self.memory['current_task']=='task_vehicle_crew':
                # not sure what to do here yet
                engine.log.add_data('warn','close enemy while in vehicle. not handled',True)
        else:
            if self.primary_weapon!=None:
                if self.check_ammo_bool(self.primary_weapon):
                    self.switch_task_engage_enemy(closest_object)
            else:
                engine.log.add_data('warn','close enemy and no primary weapon. not handled',True)

    #---------------------------------------------------------------------------
    def event_collision(self,event_data):
        self.last_collision_description=''
        if event_data.is_projectile:
            distance=engine.math_2d.get_distance(self.owner.world_coords,event_data.ai.starting_coords,True)
            self.last_collision_description='hit by '+event_data.name + ' at a distance of '+ str(distance)
            starting_health=self.health

            self.calculate_projectile_damage(event_data)

            # shrapnel from grenades and panzerfausts dont track ownership
            if event_data.ai.shooter !=None:
                self.last_collision_description+=(' from '+event_data.ai.shooter.name)

                if event_data.ai.shooter.is_human:

                    if event_data.ai.shooter.ai.squad != None:
                        if event_data.ai.shooter.ai.squad.faction != self.squad.faction or event_data.ai.shooter.is_player:
                            # not sure if this is the best way to do this.
                            # this used to be where the shooter was added to personal_enemies
                            self.switch_task_engage_enemy(event_data.ai.shooter)

                    # kill tracking

                    if self.health<30:
                        # protects from recording hits on something that was already dead
                        if starting_health>0:
                            if self.health<1:
                                event_data.ai.shooter.ai.confirmed_kills+=1
                            else:
                                event_data.ai.shooter.ai.probable_kills+=1
                        else:
                            print('collision on a dead human ai detected')

                    if event_data.ai.shooter.ai.primary_weapon!=None:
                        self.last_collision_description+=("'s "+event_data.ai.weapon_name)
            else:
                print('Error - projectile '+event_data.name+' shooter is none')
                # other way to get here is if its not a projectile
                print('or its not a projectile')
            
            destination=[0,0]
            if self.owner.is_civilian:
                # civilian runs further
                destination=[self.owner.world_coords[0]+float(random.randint(-560,560)),self.owner.world_coords[1]+float(random.randint(-560,560))]
            else:
                # soldier just repositions to get away from the fire
                destination=[self.owner.world_coords[0]+float(random.randint(-30,30)),self.owner.world_coords[1]+float(random.randint(-30,30))]
            if self.memory['current_task']!='task_vehicle_crew':
                if self.prone==False:
                    self.handle_prone_state_change()
                self.switch_task_move_to_location(destination)
            else:
                engine.log.add_data('warn','hit by a projectile while in a vehicle',True)

        elif event_data.is_grenade:
            # not sure what to do here. the grenade explodes too fast to really do anything

            # attempt to throw the grenade back
            if random.randint(1,5)==1:
                event_data.ai.redirect(event_data.ai.equipper.world_coords)
            else:
                if self.memory['current_task']!='task_vehicle_crew':
                    if self.prone==True:
                        self.handle_prone_state_change()
                    destination=[self.owner.world_coords[0]+float(random.randint(-60,60)),self.owner.world_coords[1]+float(random.randint(-60,60))]
                    self.switch_task_move_to_location(destination)
                else:
                    engine.log.add_data('warn','hit by a projectile while in a vehicle',True)

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
                        self.handle_drop_object(self.primary_weapon)
                    if self.owner.is_player :
                        self.owner.world.graphic_engine.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                    self.primary_weapon=event_data
                    event_data.ai.equipper=self.owner
                elif event_data.is_throwable :
                    if self.throwable==None:
                        if self.owner.is_player :
                            self.owner.world.graphic_engine.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                        self.throwable=event_data
                        event_data.ai.equipper=self.owner
                elif event_data.is_handheld_antitank :
                    if self.antitank!=None:
                        # drop the current obj and pick up the new one
                        self.handle_drop_object(self.antitank)
                    if self.owner.is_player :
                        self.owner.world.graphic_engine.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                    self.antitank=event_data
                    event_data.ai.equipper=self.owner

                elif event_data.is_wearable:
                    if event_data.ai.wearable_region=='head':
                        if self.wearable_head==None:
                            self.wearable_head=event_data
        else:
            print('ERROR - object '+event_data.name+' is already in inventory')
            print('inventory list:')
            for b in self.inventory:
                print(' - ',b.name)


    #---------------------------------------------------------------------------
    def event_remove_inventory(self,event_data):
        ''' remove object from inventory. does NOT add to world '''

        if event_data in self.inventory:

            self.inventory.remove(event_data)
            # NOTE - if this object is meant to be added to the world it should be done by whatever calls this

            if self.primary_weapon==event_data:
                self.primary_weapon=None
                event_data.ai.equipper=None
            elif self.throwable==event_data:
                self.throwable=None
                # equipper is used to figure out who threw the grenade
                # need a better way to handle this in the future
                #EVENT_DATA.ai.equipper=None
            elif self.antitank==event_data:
                self.antitank=None
                event_data.ai.equipper=None
            elif self.large_pickup==event_data:
                print('ERROR - large pickup should not go through inventory functions')
            elif self.wearable_head==event_data:
                self.wearable_head=None

            # need to add a method call here that will search inventory and add new weapon/grendade/whatever if available

        else:
            print('removal error - object not in inventory',event_data.name)

    #---------------------------------------------------------------------------
    def fire(self,target_coords,weapon):
        ''' fires a weapon '''
        if self.owner.is_player :
            # do computations based off of where the mouse is. TARGET_COORDS is ignored
            weapon.rotation_angle=engine.math_2d.get_rotation(self.owner.world.graphic_engine.get_player_screen_coords(),self.owner.world.graphic_engine.get_mouse_screen_coords())

        else :
            weapon.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,target_coords)

        if weapon.ai.fire():
            self.current_burst+=1

        if self.current_burst>self.max_burst:
            # stop firing, give the ai a chance to rethink and re-engage
            self.current_burst=0
            self.memory['current_task']='None'

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
    def get_target(self):
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
                # could get intesting if there are a lot of dead targets but 
                # it should self clear with this recursion
                print('error: got dead target: '+target.name+' retrying')
                print('near ',len(self.near_targets))
                print('mid',len(self.mid_targets))
                print('far',len(self.far_targets))
                target=self.get_target()
                
        return target
    
    #---------------------------------------------------------------------------
    def give_squad_transportation_orders(self,destination):
        '''assign transportation for the squad'''

        near_squad=self.owner.world.get_objects_within_range(self.owner.world_coords,self.squad.members,800)

        # remove yourself to prevent recursion
        near_squad.remove(self.owner)

        near_vehicle=self.owner.world.get_objects_within_range(self.owner.world_coords,self.owner.world.wo_objects_vehicle,500)

        for b in near_vehicle:
            if len(near_squad)==0:
                break
            # calculate occupants
            occupants=len(b.ai.passengers)
            for c in self.owner.world.wo_objects_human:
                if 'task_enter_vehicle' in c.ai.memory:
                    if c.ai.memory['task_enter_vehicle']['vehicle']==b
                        occupants+=1

            while occupants<b.ai.max_occupants:
                if len(near_squad)>0:
                    if near_squad[0].ai.memory['current_task']=='task_vehicle_crew':
                        #already in a vehicle, so no further action needed
                        near_squad.pop(0)
                    else:
                        self.switch_task_enter_vehicle()
                        near_squad[0].ai.switch_task_enter_vehicle(b,destination)
                        occupants+=1
                        near_squad.pop(0)
                else:
                    break
    
    #---------------------------------------------------------------------------
    def handle_drop_object(self,OBJECT_TO_DROP):
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
    def handle_eat(self,CONSUMABLE):
        # eat the consumable object. or part of it anyway
        self.health+=CONSUMABLE.ai.health_effect
        self.hunger+=CONSUMABLE.ai.hunger_effect
        self.thirst+=CONSUMABLE.ai.thirst_effect
        self.fatigue+=CONSUMABLE.ai.fatigue_effect

        # this should remove the object from the game because it is not added to world
        self.event_remove_inventory(CONSUMABLE)

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

        else:
            print('Error: '+self.owner.name+' cannot handle event '+EVENT)

    #-----------------------------------------------------------------------
    def handle_keydown(self,key):
        ''' handle keydown passed from world.handle_keydown'''
        # this is a one off key press, not press and hold
        # world.handle_keydown will pass the key as the actual keyboard letter

        if self.memory['current_task']=='task_vehicle_crew':
            if self.memory['task_vehicle_crew']['vehicle'].is_airplane:
                if key=='p':
                    self.switch_task_exit_vehicle(self.memory['task_vehicle_crew']['vehicle'])
                    self.speak('bailing out!')
                    # note - physics needs to be udpdate to handle falling
        else:
            # controls for when you are walking about
            if key=='g':
                self.throw([])
            elif key=='p':
                self.handle_prone_state_change()
            elif key=='t':
                self.launch_antitank([])

        # controls for vehicles and walking 
        if key=='r':
            if self.memory['current_task']=='task_player_control':
                self.reload_weapon()
            elif self.memory['current_task']=='task_vehicle_crew':
                self.reload_turret()


    #---------------------------------------------------------------------------
    def handle_prone_state_change(self):
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
    def reload_weapon(self,weapon):
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
            for b in self.inventory:
                if b.is_gun_magazine:
                    if weapon.name in b.ai.compatible_guns:
                        if len(b.ai.projectiles)>biggest:
                            new_magazine=b
                            biggest=len(b.ai.projectiles)

            # remove old magazine ONLY if we have a new magazine
            if old_magazine!=None and new_magazine!=None:
                self.event_add_inventory(old_magazine)
                weapon.ai.magazine=None
            # add a new magazine (either the old magazine was removed, or was never there)
            if new_magazine!=None:
                self.event_remove_inventory(new_magazine)
                weapon.ai.magazine=new_magazine
            else:
                self.speak("I'm out of ammo!")

        # at this point we should do a ai_mode change with a timer to simulate the 
        # reload time
        
    #-----------------------------------------------------------------------
    def reload_turret(self):
        if self.vehicle_turret!=None:
            if self.vehicle_turret.ai.vehicle!=None and self.vehicle_turret.ai.primary_weapon!=None:
                weapon=self.vehicle_turret.ai.primary_weapon
                # first get the current magazine
                old_magazine=None
                if weapon.ai.magazine!=None:
                    if weapon.ai.magazine.ai.removable:
                        old_magazine=weapon.ai.magazine

                # find a new magazine, sorting by size
                new_magazine=None
                biggest=0
                for b in self.vehicle.ai.inventory:
                    if b.is_gun_magazine:
                        if weapon.name in b.ai.compatible_guns:
                            if len(b.ai.projectiles)>biggest:
                                new_magazine=b
                                biggest=len(b.ai.projectiles)

                # perform the swap 
                if old_magazine!=None:
                    self.vehicle.ai.event_add_inventory(old_magazine)
                    weapon.ai.magazine=None
                if new_magazine!=None:
                    self.vehicle.ai.event_remove_inventory(new_magazine)
                    weapon.ai.magazine=new_magazine
                else:
                    self.speak("This turret is out of ammo!")

        # at this point we should do a ai_mode change with a timer to simulate the 
        # reload time
        
        self.speak('reloading!')

    #---------------------------------------------------------------------------
    def handle_transfer(self,FROM_OBJECT,TO_OBJECT):
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
            print('error: handle_transfer error: src/dest not recognized!')


    #-----------------------------------------------------------------------
    def handle_use_medical_object(self,MEDICAL):
        # MEDICAL - list of is_medical World Object(s)

        # should eventually handle bandages, morphine, etc etc
        # probably need attributes similar to consumables

        # should select the correct medical item to fix whatever the issue is
        selected = MEDICAL[0]
        self.speak('Using medical '+selected.name)

        self.bleeding=False

        self.health+=selected.ai.health_effect
        self.hunger+=selected.ai.hunger_effect
        self.thirst_rate+=selected.ai.thirst_effect
        self.fatigue+=selected.ai.fatigue_effect

        # calling this by itself should remove all references to the object
        self.event_remove_inventory(selected)

    #---------------------------------------------------------------------------
    def launch_antitank(self,target_coords):
        ''' launch antitank ''' 

        # standup. kneel would be better if it becomes an option later
        if self.prone:
            self.handle_prone_state_change()

        if self.antitank!=None:
            if self.owner.is_player :
                # do computations based off of where the mouse is. TARGET_COORDS is ignored
                self.antitank.rotation_angle=engine.math_2d.get_rotation(self.owner.world.graphic_engine.get_player_screen_coords(),self.owner.world.graphic_engine.get_mouse_screen_coords())

            else :
                self.antitank.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,target_coords)
            self.antitank.ai.fire()

            # drop the tube now that it is empty
            self.handle_drop_object(self.antitank)

    #---------------------------------------------------------------------------
    def speak(self,WHAT):
        ''' say something if the ai is close to the player '''

        # simple way of preventing repeats
        if WHAT !=self.last_speak:
            self.last_speak=WHAT
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.owner.world.player.world_coords)
            if distance<400:
                s='['+self.owner.name+'] '

                if WHAT=='status':
                    s+=' what?'
                elif WHAT=='bandage':
                    s+=' applying bandage'
                elif WHAT=='joined squad':
                    s+=' joined squad'
                elif WHAT=='react to being shot':
                    s+=" Aagh! I'm hit !!"
                elif WHAT=='scream':
                    s+='Aaaaaaaaaaaah!!!'
                else:
                    s+=WHAT

                self.owner.world.graphic_engine.add_text(s)
          
    #---------------------------------------------------------------------------
    def switch_task_enter_vehicle(self,vehicle,destination):
        '''switch task'''
        task_name='task_enter_vehicle'
        task_details = {
            'vehicle': vehicle,
            'destination': destination
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name

        if self.squad.squad_lead==self.owner:
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
            'destination': destination,
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
    def switch_task_squad_lead(self):
        '''switch task'''
        task_name='task_squad_lead'

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
    def switch_task_vehicle_crew(self,vehicle,destination,role=None,turret=None):
        '''switch task to vehicle crew and determine role'''
        # this should always overwrite if it exists

        # pick a role
        if role==None:
            if vehicle.ai.driver==None:
                role='driver'
                self.speak("Taking over driving")

            if role==None:
                for b in self.vehicle.ai.turrets:
                    if b.ai.gunner==None:
                        self.speak("Taking over gunner position")
                        b.ai.gunner=self.owner
                        turret=b
                        role='gunner'
                        break
            if role==None:
                role='passenger'

        task_name='task_vehicle_crew'
        task_details = {
            'vehicle': vehicle,
            'role': role,
            'turret': turret,
            'destination': destination,
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
        
        distance=engine.math_2d.get_distance(self.owner.world_coords,self.ai_vehicle_destination)
        
        if distance<20 or new_passengers>0:
            self.vehicle.ai.brake_power=1
            self.vehicle.ai.throtte=0
        else:

            # we want a tighter and more uniform time interval because we are 
            # actually driving here
            #self.ai_think_rate=0.1

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

            # compare that with the current vehicle rotation.. somehow?
            v = vehicle.rotation_angle

            if r>v:
                vehicle.ai.handle_steer_left()
                #self.ai_think_rate=0.01
            if r<v:
                vehicle.ai.handle_steer_right()
                #self.ai_think_rate=0.01
            
            # if its close just set it equal
            if r>v-1 and r<v+1:
                # neutral out steering 
                vehicle.ai.handle_steer_neutral()
                #self.vehicle.rotation_angle=r
                vehicle.reset_image=True

            if (r>355 and v<5) or (r<5 and v>355):
                # i think the rotation angle wrapping 360->0 and 0->360 is goofing stuff
                vehicle.ai.handle_steer_neutral()
                vehicle.rotation_angle=r
                engine.log.add_data('warn','fixing 360 vehicle steering issue',True)

            if distance<150:
                # apply brakes. bot will only exit when speed is zero
                self.vehicle.ai.throttle=0
                self.vehicle.ai.brake_power=1
            elif distance<500:
                self.vehicle.ai.throttle=0.5
                self.vehicle.ai.brake_power=0
            else:
                self.vehicle.ai.throttle=1
                self.vehicle.ai.brake_power=0

    #---------------------------------------------------------------------------
    def think_vehicle_role_gunner(self):
        pass

    #---------------------------------------------------------------------------
    def think_vehicle_role_passenger(self):
        pass

    #---------------------------------------------------------------------------
    def throw(self,TARGET_COORDS):
        ''' throw like you know the thing. cmon man '''   
        # stand up
        if self.prone:
            self.handle_prone_state_change() 
        if self.throwable!=None:
            #self.throwable.ai.throw(TARGET_COORDS)

            self.throwable.ai.thrown=True

            # set rotation and heading
            if self.owner.is_player :
                # do computations based off of where the mouse is. TARGET_COORDS is ignored
                self.throwable.rotation_angle=engine.math_2d.get_rotation(self.owner.world.graphic_engine.get_player_screen_coords(),self.owner.world.graphic_engine.get_mouse_screen_coords())
                self.throwable.heading=engine.math_2d.get_heading_vector(self.owner.world.graphic_engine.get_player_screen_coords(),self.owner.world.graphic_engine.get_mouse_screen_coords())
            else :
                self.throwable.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,TARGET_COORDS)
                self.throwable.heading=engine.math_2d.get_heading_vector(self.owner.world_coords,TARGET_COORDS)

            self.handle_drop_object(self.throwable)

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # update the current task
        if self.memory['current_task'] in self.memory:
            if self.memory['current_task'] in self.task_map:
                # call the associated update function for the current task
                self.task_map[self.memory['current_task']]()
            else:
                engine.log.add_data('error','current task '+self.memory['current_task']+' not in task map',True)

        else:
            self.switch_task_think()

        # update health 
        self.update_health()

        # identify and categorize targets
        if self.owner.world.world_seconds-self.last_target_eval_time>self.target_eval_rate:
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
    def update_health(self):
        '''update health and handle death'''

        if self.health>0:
            if self.bleeding:
                if self.owner.world.world_seconds-self.last_bleed_time>self.bleed_interval:
                    self.last_bleed_time=self.owner.world.world_seconds+random.uniform(0,2)
                    engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'small_blood',True)
                    self.health-=1+random.uniform(0,3)

            # -- body attribute stuff --
            if self.fatigue>0:
                self.fatigue-=self.fatigue_remove_rate*self.owner.world.graphic_engine.time_passed_seconds
            self.hunger+=self.hunger_rate*self.owner.world.graphic_engine.time_passed_seconds
            self.thirst+=self.thirst_rate*self.owner.world.graphic_engine.time_passed_seconds
    
        else:
            # -- handle death --
            # construct death message
            dm=''
            dm+=(self.owner.name+' died.')
            dm+=('\n  - faction: '+self.squad.faction)
            dm+=('\n  - confirmed kills: '+str(self.confirmed_kills))
            dm+=('\n  - probable kills: '+str(self.probable_kills))
            dm+=('\n  - killed by : '+self.last_collision_description)
            
            # drop primary weapon 
            if self.primary_weapon!=None:
                ammo=self.handle_check_ammo(self.primary_weapon)
                dm+=('\n  - weapon: '+self.primary_weapon.name)
                dm+=('\n  -- ammo in gun: '+str(ammo[0]))
                dm+=('\n  -- ammo in inventory: '+str(ammo[1]))
                dm+=('\n  -- magazine count: '+str(ammo[2]))

                self.handle_drop_object(self.primary_weapon)

            if self.large_pickup!=None:
                self.handle_drop_object(self.large_pickup)

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
            engine.world_builder.spawn_container('body: ',self.owner,2)

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
    def update_player_vehicle_controls(self,vehicle,role,turret):
        '''update player vehicle controls'''
        if role=='driver':

            if vehicle.is_airplane:
                # ---- controls for airplanes ------------
                if(self.owner.world.graphic_engine.keyPressed('w')):
                    vehicle.ai.handle_elevator_up()
                if(self.owner.world.graphic_engine.keyPressed('s')):
                    vehicle.ai.handle_elevator_down()
                    if self.owner.altitude<1:
                        vehicle.ai.brake_power=1
                if(self.owner.world.graphic_engine.keyPressed('a')):
                    vehicle.ai.handle_aileron_left()
                    vehicle.ai.handle_rudder_left()
                    if self.owner.altitude<1:
                        vehicle.ai.handle_steer_left()
                if(self.owner.world.graphic_engine.keyPressed('d')):
                    vehicle.ai.handle_aileron_right()
                    vehicle.ai.handle_rudder_right()
                    if self.owner.altitude<1:
                        vehicle.ai.handle_steer_right()
                if(self.owner.world.graphic_engine.keyPressed('up')):
                    print('up')
                if(self.owner.world.graphic_engine.keyPressed('down')):
                    print('down')
                if(self.owner.world.graphic_engine.keyPressed('left')):
                    vehicle.ai.handle_throttle_down()
                if(self.owner.world.graphic_engine.keyPressed('right')):
                    vehicle.ai.handle_throttle_up()
            else:
                # ---- controls for ground vehicles ------------

                if(self.owner.world.graphic_engine.keyPressed('w')):
                    vehicle.ai.throttle=1
                    vehicle.ai.brake_power=0

                if(self.owner.world.graphic_engine.keyPressed('s')):
                    vehicle.ai.brake_power=1
                    vehicle.ai.throttle=0

                if(self.owner.world.graphic_engine.keyPressed('a')):
                    vehicle.ai.handle_steer_left()

                if(self.owner.world.graphic_engine.keyPressed('d')):
                    vehicle.ai.handle_steer_right()

        elif role=='gunner':
            if(self.owner.world.graphic_engine.keyPressed('a')):
                turret.ai.handle_rotate_left()

            if(self.owner.world.graphic_engine.keyPressed('d')):
                turret.ai.handle_rotate_right()

            if(self.owner.world.graphic_engine.keyPressed('f')):
                turret.ai.handle_fire()

    #---------------------------------------------------------------------------
    def update_task_engage_enemy(self):

        enemy=self.memory['task_engage_enemy']['enemy']
        if enemy.ai.health<1:
            self.memory.pop('task_engage_enemy',None)
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


                # out of ammo ?
                ammo_gun,ammo_inventory,magazine_count=self.check_ammo(self.primary_weapon)
                if ammo_gun==0:
                    if ammo_inventory>0:
                        self.reload_weapon(self.primary_weapon)
                    else:
                        # need ammo or new gun
                        near_magazines=self.owner.world.get_compatible_magazines_within_range(self.owner.world_coords,self.primary_weapon,200)
                        if len(near_magazines)>0:
                            self.switch_task_pickup_objects(near_magazines)

            else:
                # -- fire --
                self.aim_and_fire_weapon(self.primary_weapon,enemy)
                self.fatigue+=self.fatigue_add_rate*self.owner.world.graphic_engine.time_passed_seconds

    #---------------------------------------------------------------------------
    def update_task_enter_vehicle(self):
        vehicle=self.memory['task_enter_vehicle']['vehicle']
        destination=self.memory['task_enter_vehicle']['destination']

        if self.owner.world.check_object_exists(vehicle)==False:
            self.speak('Where did that '+vehicle.name+' go?')
            self.memory.pop('task_enter_vehicle',None)
        else:
            # -- vehicle still exists --

            distance=engine.math_2d.get_distance(self.owner.world_coords,vehicle.world_coords)
            distance_to_destination=engine.math_2d.get_distance(self.owner.world_coords,destination)

            if distance_to_destination<distance:
                # -- vehicle is further than where we wanted to go --

                # i think this should never happen??
                # basically we are closer to our final destination than we are to the vehicle

                # first cancel the task
                self.memory.pop('task_enter_vehicle',None)
                
                # double check its walkable
                if distance_to_destination<self.max_walk_distance:
                    self.switch_task_move_to_location(destination)
                else:
                    # this is probably a loop at this point, lets just cancel the original task
                    self.memory.pop('task_move_to_location',None)
            else:
                # -- vehicle task still makes sense --

                if distance<self.max_distance_to_interact_with_object:

                    # no matter what at this point this task is complete
                    self.memory.pop('task_enter_vehicle',None)

                    precheck=True
                    if vehicle.ai.max_occupants<=len(vehicle.ai.passengers):
                        precheck=False
                        self.speak('No more room in this vehicle!')
                    
                    if vehicle.ai.driver!=None:
                        if vehicle.ai.driver.ai.squad.faction!=self.squad.faction:
                            precheck=False
                            self.speak('The enemy took this vehicle!')
                    
                    if precheck:
                        # put your large items in the trunk
                        if self.large_pickup:
                            vehicle.add_inventory(self.large_pickup)
                            self.owner.world.remove_queue.append(self.large_pickup)
                            self.large_pickup=None

                        vehicle.ai.passengers.append(self.owner)
                        
                        if vehicle.ai.open_top==False:
                            # human is hidden by top of vehicle so don't render
                            self.owner.render=False

                        # tell the squad to mount up
                        #if self.owner==self.squad.squad_leader:
                        #   self.handle_squad_transportation_orders()

                        # this will decide crew position as well
                        self.switch_task_vehicle_crew(vehicle)
                else:
                    # -- too far away to enter, what do we do --
                    if distance<self.max_walk_distance:
                        self.switch_task_move_to_location(vehicle.world_coords)
                    else:
                        # vehicle is way too far away, just cancel task
                        self.memory.pop('task_enter_vehicle',None)
                        engine.log.add_data('warn','enter vehicle task canceled as vehicle is too far',True)

    #---------------------------------------------------------------------------
    def update_task_exit_vehicle(self):
        vehicle=self.memory['task_exit_vehicle']['vehicle']

        # remove from passenger list
        vehicle.ai.passengers.remove(self.owner)

        # remove yourself from any turrets
        for b in vehicle.ai.turrets:
            if b.ai.gunner==self.owner:
                b.ai.gunner=None

        # remove yourself from driver role
        if vehicle.ai.driver==self.owner:
            vehicle.ai.driver=None
            # turn on the brakes to prevent roll away
            self.vehicle.ai.brake_power=1

        # make sure we are visible again
        self.owner.render=True

        # delete vehicle role memory 
        self.memory.pop('task_player_vehicle_control',None)
        self.memory.pop('task_vehicle_crew',None)

        # delete this task as it is now complete
        self.memory.pop('task_exit_vehicle',None)

        # maybe grab your large pick up if you put it in the trunk
            
        self.speak('Jumping out')

        # move slightly
        coords=[self.owner.world_coords[0]+random.randint(-5,5),self.owner.world_coords[1]+random.randint(-5,5)]
        self.switch_task_move_to_location(coords)

    #---------------------------------------------------------------------------
    def update_task_loot_container(self):
        '''loot a container or object with ai.inventory'''
        container=self.memory['task_loot_container']['container']

        if self.owner.world.check_object_exists(container)==False:
            self.memory.pop('task_loot_container',None)
        else:
            distance=engine.math_2d.get_distance(self.owner.world_coords,container.world_coords)
            if distance<self.max_distance_to_interact_with_object:
                # done with this task
                self.memory.pop('task_loot_container',None)

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

            # should we get a vehicle instead of hoofing it to wherever we are going?
            if distance>self.max_walk_distance:
                
                b=self.owner.world.get_closest_vehicle(self.owner,(self.max_walk_distance*0.6))
                if b!=None:
                    # get_closest_vehicle only returns vehicles that aren't full
                    # won't return planes if not a pilot
                    self.switch_task_enter_vehicle(b,destination)


                else:
                    # no vehicles ? guess we are walking
                    pass
            elif distance<self.max_distance_to_interact_with_object:
                # we've arrived ! 
                self.memory.pop('task_move_to_location',None)
        
        else:
            # -- walk --
            # move
            self.owner.world_coords=engine.math_2d.moveTowardsTarget(self.get_calculated_speed(),
                self.owner.world_coords,destination,self.owner.world.graphic_engine.time_passed_seconds)
            # add some fatigue
            self.fatigue+=self.fatigue_add_rate*self.owner.world.graphic_engine.time_passed_seconds

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

                    if b.is_large_human_pickup:

                        # need to make sure nobody else is already carrying it
                        in_use=False
                        for b in self.owner.world.wo_objects_human:
                            if b.ai.large_pickup==b:
                                in_use=True

                        if in_use:
                            engine.log.add_data('warn','Error large pick up is already picked up: '+b.name,True)
                        else:
                            self.large_pickup=b
                    else:
                        if b.is_gun:

                            near_magazines=self.owner.world.get_compatible_magazines_within_range(self.owner.world_coords,self.primary_weapon,200)
                            if len(near_magazines)>0:
                                self.switch_task_pickup_objects(near_magazines)

                        self.speak('Picking up a '+b.name)

                        self.event_add_inventory(b)
                        # remove from world
                        self.owner.world.remove_queue.append(b)
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
        
        # graphic_engine.keyPressed works for keys that need to be held down
        # keys that should trigger an event only when they keydown (once) are handled 
        # by world.handle_keydown()

        # ---- controls for walking around ------------

        action=False
        speed=self.get_calculated_speed()
        if(self.owner.world.graphic_engine.keyPressed('w')):
            self.owner.world_coords[1]-=speed*self.owner.world.graphic_engine.time_passed_seconds
            self.owner.rotation_angle=0
            self.owner.reset_image=True
            action=True
        if(self.owner.world.graphic_engine.keyPressed('s')):
            self.owner.world_coords[1]+=speed*self.owner.world.graphic_engine.time_passed_seconds
            self.owner.rotation_angle=180
            self.owner.reset_image=True
            action=True
        if(self.owner.world.graphic_engine.keyPressed('a')):
            self.owner.world_coords[0]-=speed*self.owner.world.graphic_engine.time_passed_seconds
            self.owner.rotation_angle=90
            self.owner.reset_image=True
            action=True
        if(self.owner.world.graphic_engine.keyPressed('d')):
            self.owner.world_coords[0]+=speed*self.owner.world.graphic_engine.time_passed_seconds
            self.owner.rotation_angle=270
            self.owner.reset_image=True
            action=True
        if(self.owner.world.graphic_engine.keyPressed('f')):
            # fire the gun
            if self.primary_weapon!=None:
                self.fire(self.owner.world.graphic_engine.get_mouse_world_coords(),self.primary_weapon)
            action=True

        if action:
            self.fatigue+=self.fatigue_add_rate*self.owner.world.graphic_engine.time_passed_seconds
            self.time_since_player_interact=0

    #---------------------------------------------------------------------------
    def update_task_squad_lead(self):

        last_think_time=self.memory['task_squad_lead']['last_think_time']
        think_interval=self.memory['task_squad_lead']['think_interval']

        
        if self.owner.world.world_seconds-last_think_time>think_interval:
            # reset time
            self.memory['task_move_to_location']['last_think_time']=self.owner.world.world_seconds

            # -- do the longer thing ---
            action=False
            
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.squad.destination)
            if distance>150:
                self.switch_task_move_to_location(self.squad.destination)
                action=True

            # check on squad members?
                
            # coordinate with nearby squad lead?
                
            # check in with HQ ?
            
        else:
            # -- do the shorter thing --
            # go for a walk
            coords=[self.owner.world_coords[0]+random.randint(-5,5),self.owner.world_coords[1]+random.randint(-5,5)]
            self.switch_task_move_to_location(coords)

    #---------------------------------------------------------------------------
    def update_task_think(self):
        '''task think - thinking about what to do next'''
        # the ugly function where we have to determine what we are doing

        # !! probably need to check the last time we were here so we aren't 
        # hitting this too often as it is likely computationally intense

        action=False
        
        # -- priorities --

        # health - maybe this should be all done by update_health?

        # primary weapon
        if self.primary_weapon==None:
            # need to get a gun
            distance=4000
            if self.near_targets>0:
                distance=200
            elif self.mid_targets>0:
                distance=400
            elif self.far_targets>0:
                distance=900

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
                self.switch_task_squad_lead()
                action=True
            else:
                # being in a squad wwhen we aren't lead basically just means staying close to the squad lead
                distance=engine.math_2d.get_distance(self.owner.world_coords,self.squad.squad_lead.world_coords)
                # are we close enough to squad?
                if distance>self.squad_max_distance:
                    self.switch_task_move_to_location(self.squad.squad_lead.world_coords)
                    action=True

        # -- ok now we've really run out of things to do. do things that don't matter
        # ! NOTE Squad Lead will never get this far
        if action==False:
            decision=random.randint(0,10)
            if decision==1:
                # go for a walk
                coords=[self.owner.world_coords[0]+random.randint(-5,5),self.owner.world_coords[1]+random.randint(-5,5)]
                self.switch_task_move_to_location(coords)
            elif decision==2:
                # check containers
                containers=self.owner.world.get_objects_within_range(self.owner.world_coords,self.owner.world.wo_objects_container,1000)
                if len(containers)>0:
                    self.switch_task_loot_container(random.choice(containers))

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
                self.update_player_vehicle_controls(vehicle,role,turret)
            else:
                last_think_time=self.memory['task_vehicle_crew']['last_think_time']
                think_interval=self.memory['task_vehicle_crew']['think_interval']
        
                if self.owner.world.world_seconds-last_think_time>think_interval:
                    # reset time
                    self.memory['task_vehicle_crew']['last_think_time']=self.owner.world.world_seconds
                    self.memory['task_vehicle_crew']['think_interval']=random.uniform(0.1,1.5)

                    if role=='driver':
                        self.think_vehicle_role_driver()
                    elif role=='gunner':
                        self.think_vehicle_role_gunner()
                    elif role=='passenger':
                        self.think_vehicle_role_passenger()
                    else:
                        engine.log.add_data('error','unknown vehicle role: '+role,True)

            


