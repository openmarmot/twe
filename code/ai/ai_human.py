
'''
module : ai_player.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
event - something that could happen to the ai, possibly caused by external forces
handle_SOMETHING - something that the AI decides to do that requires some code to make happen
take_action_ - something simple that sets ai_state and ai_goal to start an action, but not a lot of logic
think_ - something that requires a lot of logic code
react_ - player or bot calls this when they want to give orders to another bot
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
            'task_player_vehicle_control':update_task_player_vehicle_control,
            'task_enter_vehicle':update_task_enter_vehicle,
            'task_exit_vehicle':update_task_exit_vehicle,
            'task_move_to_location':update_task_move_to_location,
            'task_vehicle_crew':update_task_vehicle_crew
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

        # -- OLD ---
        
        # self.throwable=None
        # self.antitank=None
        # self.melee=None

        # self.wearable_head=None
        # self.wearable_upper_body=None
        # self.wearable_lower_body=None
        # self.wearable_feet=None
        # self.wearable_hand=None

        # self.in_building=False
        # self.building_list=[] # list of buildings the ai is overlapping spatially
        # self.time_since_building_check=0
        # self.building_check_rate=1

        # # the ai group that this human is a part of 
        # self.squad=None
        # self.squad_min_distance=30
        # self.squad_max_distance=300


        # # burst control keeps ai from shooting continuous streams
        # self.current_burst=0 # int number of bullets shot in current burst
        # self.max_burst=10
 
        # # target lists. these are refreshed periodically 
        # self.near_targets=[]
        # self.mid_targets=[]
        # self.far_targets=[]
        # self.time_since_target_evaluation=0
        # self.target_eval_rate=random.uniform(0.1,0.9)

        
        # # used to prevent repeats
        # self.last_speak=''

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
    def evaluate_targets(self):
        '''find and categorize targets'''
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

        for b in target_list:
            d=engine.math_2d.get_distance(self.owner.world_coords,b.world_coords)

            if d<500:
                self.near_targets.append(b)
            elif d<850:
                self.mid_targets.append(b)
            elif d<1300:
                self.far_targets.append(b)

    #---------------------------------------------------------------------------
    def event_collision(self,event_data):
        self.last_collision_description=''
        if event_data.is_projectile:
            distance=engine.math_2d.get_distance(self.owner.world_coords,event_data.ai.starting_coords,True)
            self.last_collision_description='hit by '+event_data.name + ' at a distance of '+ str(distance)
            starting_health=self.health

            self.calculate_projectile_damage(event_data)

            # add the shooter of the bullet to the personal enemies list
            # shrapnel from grenades and panzerfausts dont track ownership
            if event_data.ai.shooter !=None:
                self.last_collision_description+=(' from '+event_data.ai.shooter.name)

                if event_data.ai.shooter.is_human:

                    if event_data.ai.shooter.ai.squad != None:
                        if event_data.ai.shooter.ai.squad.faction != self.squad.faction or event_data.ai.shooter.is_player:
                            # this creates a lot of friendly fire - but its interesting 
                            self.personal_enemies.append(event_data.ai.shooter)

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

            if self.owner.is_civilian:
                # civilian runs further
                self.ai_goal='react to collision'
                self.destination=[self.owner.world_coords[0]+float(random.randint(-560,560)),self.owner.world_coords[1]+float(random.randint(-560,560))]
                self.ai_state='start_moving'
            else:
                # soldier just repositions
                self.ai_goal='react to collision'
                self.destination=[self.owner.world_coords[0]+float(random.randint(-30,30)),self.owner.world_coords[1]+float(random.randint(-30,30))]
                self.ai_state='start_moving'

        elif event_data.is_grenade:
            # not sure what to do here. the grenade explodes too fast to really do anything

            # attempt to throw the grenade back
            if random.randint(1,5)==1:
                event_data.ai.redirect(event_data.ai.equipper.world_coords)
            else:
                self.ai_goal='react to collision'
                self.destination=[self.owner.world_coords[0]+float(random.randint(-60,60)),self.owner.world_coords[1]+float(random.randint(-60,60))]
                self.ai_state='start_moving'
        elif event_data.is_throwable:
            #throwable but not a grenade 
            self.speak('Oww!')
            # temp do something else later
            self.take_action_panic()

        else:
            print('unidentified collision')

            # this is very important because it breaks us out of whatever ai cycle we were in
            # we are put in a very short movement cycle and then the AI can 'think' about what to do next
            self.ai_goal='react to collision'
            self.destination=[self.owner.world_coords[0]+float(random.randint(-60,60)),self.owner.world_coords[1]+float(random.randint(-60,60))]
            self.ai_state='start_moving'

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
                    self.ai_want_gun=False
                elif event_data.is_throwable :
                    if self.throwable==None:
                        if self.owner.is_player :
                            self.owner.world.graphic_engine.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                        self.throwable=event_data
                        event_data.ai.equipper=self.owner
                    if event_data.is_grenade:
                        self.ai_want_grenade=False
                elif event_data.is_handheld_antitank :
                    if self.antitank!=None:
                        # drop the current obj and pick up the new one
                        self.handle_drop_object(self.antitank)
                    if self.owner.is_player :
                        self.owner.world.graphic_engine.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                    self.antitank=event_data
                    event_data.ai.equipper=self.owner
                    self.ai_want_antitank=False
                elif event_data.is_consumable:
                    self.ai_want_food=False
                elif event_data.is_medical:
                    self.ai_want_medical=False
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
            self.reset_ai()

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
    def handle_building_check(self):

        # reset transition to zero
        self.time_since_building_check=0

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
    def handle_check_ammo(self,gun):
        '''check ammo and magazines for a gun'''
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


        return [ammo_gun,ammo_inventory,magazine_count]        

    #---------------------------------------------------------------------------
    def handle_check_near_magazines(self,weapon,range=50):
        ''' check nearby surroundings for specific magazines'''

        # can something more useful be done here ? 

        # for now we will return a list of nearby magazines, in the future maybe 
        # actually do something like create tasks 

        near_mags=self.owner.world.get_objects_within_range(self.owner.world_coords,self.owner.world.wo_objects_gun_magazines,range)
        correct_mags=[]
        for b in near_mags:
            if weapon.name in b.ai.compatible_guns:
                correct_mags.append(b)

        return near_mags


    #---------------------------------------------------------------------------
    def handle_drink(self,LIQUID):
        print('drinking no longer implemented')

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

        if self.in_vehicle:
            if self.vehicle.is_airplane:
                if key=='p':
                    self.handle_exit_vehicle()
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

  
    #-----------------------------------------------------------------------
    def handle_normal_ai_update(self):
        ''' handle code for civilians and soldiers '''
        # this is what the bot does when it isn't thinking 
        # basically mindlessly carries on whatever task it is doing 
        # if there is something that should be decided it goes in handle_normal_ai_think

        time_passed=self.owner.world.graphic_engine.time_passed_seconds

        # identify and categorize targets
        self.time_since_target_evaluation+=time_passed
        if self.time_since_target_evaluation>self.target_eval_rate :
            self.target_eval_rate=random.uniform(0.8,6.5)
            self.evaluate_targets()


    #---------------------------------------------------------------------------
    def handle_pickup_object(self,OBJECT_TO_PICKUP):
        ''' pickup object from the world '''
        # any distance calculation would be made before this function is called

        # reset ai 
        self.reset_ai()

        # double check the object is still there 
        if self.owner.world.check_object_exists(OBJECT_TO_PICKUP)==False:
            print('Debug object to pickup '+OBJECT_TO_PICKUP.name+' is no longer in the world')
        else:

            if OBJECT_TO_PICKUP.is_large_human_pickup:

                # need to make sure nobody else is already carrying it
                in_use=False
                for b in self.owner.world.wo_objects_human:
                    if b.ai.large_pickup==OBJECT_TO_PICKUP:
                        in_use=True

                if in_use:
                    print('Error large pick up is already picked up: ',OBJECT_TO_PICKUP.name)
                else:
                    self.large_pickup=OBJECT_TO_PICKUP
            else:
                if OBJECT_TO_PICKUP.is_gun:

                    # for now just pick up near by magazines (probably aren't any)
                    near_mags=self.handle_check_near_magazines(OBJECT_TO_PICKUP,50)
                    for b in near_mags:
                        self.handle_pickup_object(b)

                    # also loot any nearby containers
                    container=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_container,100)
                    if container!=None:
                        self.take_action_loot_container(container)

                self.speak('Picking up a '+OBJECT_TO_PICKUP.name)

                self.event_add_inventory(OBJECT_TO_PICKUP)
                # remove from world
                self.owner.world.remove_queue.append(OBJECT_TO_PICKUP)



 

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
                self.ai_want_ammo=True

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
                    #self.ai_want_ammo=True

        # at this point we should do a ai_mode change with a timer to simulate the 
        # reload time
        
        self.speak('reloading!')

    #-----------------------------------------------------------------------
    def handle_replenish_ammo(self):
        '''replenish ammo from a target object that we walked to'''
        if self.target_object==None:
            print('Error: replenish ammo from None target_object')
        else:
            if self.target_object.is_human:
                pass
            elif self.target_object.is_ammo_container:
                pass
            elif self.target_object.is_gun_magazine:
                pass
            elif self.target_object.is_container:
                pass

            # for now just cheat 
            for b in self.inventory:
                if b.is_gun_magazine:
                    engine.world_builder.load_magazine(self.owner.world,b)

            # load the magazine in the gun as well
            if self.primary_weapon!=None:
                if self.primary_weapon.ai.magazine!=None:
                    engine.world_builder.load_magazine(self.owner.world,self.primary_weapon.ai.magazine)

            self.ai_want_ammo=False

            print('debug: '+self.owner.name+' replenishing ammo')

    #--------------------------------------------------------------------------
    def handle_squad_actions(self):
        '''handle various squad decisions. returns true/false if an action was taken'''
        action=False
        if self.squad.squad_leader!=None:
            
            # are we the squad leader?
            if self.owner==self.squad.squad_leader:

                # check distance to destination 
                distance=engine.math_2d.get_distance(self.owner.world_coords,self.squad.destination)

                if distance>100:
                    self.ai_goal='move towards squad destination'
                    self.destination=self.squad.destination
                    self.ai_state='start_moving'
                    action=True
                    
            else:
                    
                # first we should check if we outrank the squad leader 
                        
                # check to see if we should get closer 
                distance_group=engine.math_2d.get_distance(self.owner.world_coords,self.squad.squad_leader.world_coords)
                if distance_group >self.squad_max_distance:
                    if self.prone:
                        self.handle_prone_state_change()
                    self.ai_goal='close_with_group'
                    self.destination=copy.copy(self.squad.squad_leader.world_coords)
                    self.time_since_ai_transition=0
                    self.ai_state='start_moving'

                    action=True
        else:
            # elect yourself as squad leader. Naturally!
            self.squad.squad_leader=self.owner
        return action
    
    #---------------------------------------------------------------------------
    def handle_squad_transportation_orders(self):
        '''assign transportation for the squad'''

        near_squad=self.owner.world.get_objects_within_range(self.owner.world_coords,self.squad.members,800)

        # remove yourself to prevent recursion
        near_squad.remove(self.owner)

        near_vehicle=self.owner.world.get_objects_within_range(self.owner.world_coords,self.owner.world.wo_objects_vehicle,1000)

        for b in near_vehicle:
            if len(near_squad)==0:
                break
            # calculate occupants
            occupants=len(b.ai.passengers)
            for c in self.owner.world.wo_objects_human:
                if c.ai.ai_goal=='enter_vehicle' and c.ai.target_object==b:
                    occupants+=1

            while occupants<b.ai.max_occupants:
                if len(near_squad)>0:
                    if near_squad[0].ai.in_vehicle:
                        #already in a vehicle, so no further action needed
                        near_squad.pop(0)
                    else:
                    # set this so they know where to go
                        if self.ai_vehicle_destination!=None:
                            near_squad[0].ai.ai_vehicle_destination=self.ai_vehicle_destination
                        near_squad[0].ai.react_asked_to_enter_vehicle(b)
                        occupants+=1
                        near_squad.pop(0)
                else:
                    break
        

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
        ''' throw like you know the thing. cmon man ''' 

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
                    s+=' '+self.ai_state+' '+self.ai_goal
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
        self.current_task=task_name

    #---------------------------------------------------------------------------
    def switch_task_exit_vehicle(self,vehicle):
        '''switch task'''
        task_name='task_exit_vehicle'
        task_details = {
            'vehicle': vehicle,
        }

        self.memory[task_name]=task_details
        self.current_task=task_name

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
        self.current_task=task_name

        self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,self.destination)
        # tell graphics engine to redo the image 
        self.owner.reset_image=True

    #---------------------------------------------------------------------------
    def switch_task_vehicle_crew(self,vehicle,destination,role=None,turret=None):
        '''switch task to vehicle crew and determine role'''
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
        self.current_task=task_name


    #-----------------------------------------------------------------------
    def think_eat(self):
        '''evaluate food options return bool as to whether something is eaten'''
        status=False

        if self.hunger>75 or self.thirst>50:
            # 1 check if we have anything in inventory
            item=None
            for b in self.inventory:
                if b.is_consumable:
                    item=b
                    break
            if item!=None:
                self.speak('eating '+item.name)
                self.handle_eat(item)
                status=True
            else:
                self.ai_want_food=True

        return status


    #-----------------------------------------------------------------------
    def think_healing_options(self):
        '''evaluate health options return bool as to whether action is taken'''
        status=False
        # 1 check if we have anything in inventory
        items=[]
        for b in self.inventory:
            if b.is_medical:
                items.append(b)
                #break #why was this here? don't we want all of them?s
        if len(items)>0:
            # pass the whole list and let the function determine the best one to use
            self.handle_use_medical_object(items)
            status=True
        else:
            self.ai_want_medical=True

        # 3 (kind of)
        if self.bleeding:
            if random.randint(1,15)==1:
                self.speak('applying bandage')
                # bleeding stopped through make shift bandage
                self.bleeding=False
                self.health+=5
                self.fatigue+=10
                # i guess this counts as an action
                status=True
        return status


        
    #-----------------------------------------------------------------------
    def think_loot_container(self,CONTAINER):
        '''look at the contents of a container and take what we need'''
        # written for ai_container but will work for anything that has ai.inventory
        # getting to this function assumes that the bot is <5 from the container

        # reset AI 
        self.reset_ai()

        # make sure the object is still there
        if self.owner.world.check_object_exists(CONTAINER)==False:
            self.speak('Where did that '+CONTAINER.name+' go?')
        else:       
            medical_items=[]
            consumable_items=[]
            guns=[]
            grenades=[]
            anti_tank=[]
            gun_magazine=[]
            
            # should handle liquids consumable + fuel

            # should handle ammo containers

            # sort items
            for b in CONTAINER.ai.inventory:
                if b.is_medical:
                    medical_items.append(b)
                elif b.is_consumable:
                    consumable_items.append(b)
                elif b.is_gun:
                    guns.append(b)
                elif b.is_grenade:
                    grenades.append(b)
                elif b.is_handheld_antitank:
                    anti_tank.append(b)
                elif b.is_gun_magazine:
                    gun_magazine.append(b)

            # grab stuff based on what we want
            take=[]
            if self.ai_want_medical and len(medical_items)>0:
                take.append(medical_items[0])
                self.ai_want_medical=False
            if self.ai_want_food and len(consumable_items)>0:
                take.append(consumable_items[0])
                self.ai_want_food=False
            if self.ai_want_gun and len(guns)>0:
                take.append(guns[0])
                self.ai_want_gun=False
            if self.ai_want_grenade and len(grenades)>0:
                take.append(grenades[0])
                self.ai_want_grenade=False
            if self.ai_want_antitank and len(anti_tank)>0:
                take.append(anti_tank[0])
                self.ai_want_antitank=False

            if len(take)==0:
                # nothing we wanted. lets grab something random
                chance=random.randint(1,5)
                if chance==1 and len(CONTAINER.ai.inventory)>0:
                    take.append(CONTAINER.ai.inventory[0])
            
            # handle gun magazine decisions
            if len(gun_magazine)>0:
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
                    for b in gun_magazine:
                        if gun.name in b.ai.compatible_guns:
                            if grabbed<2:
                                take.append(b)
                                grabbed+=1

            # take items!
            for c in take:
                CONTAINER.remove_inventory(c)
                self.event_add_inventory(c)
                self.speak('Grabbed a '+c.name)

    #-----------------------------------------------------------------------
    def think_upgrade_gear(self):
        '''think about upgrading gear. return True/False if upgrading'''

        # !! this is kinda pointless as most of this stuff is also done under think_generic now
        # maybe make it more thinky than think_generic which is kind of a last ditch find something to do 
        # method 

        status=False
        # grab another grenade?
        if self.throwable == None:
            status=self.take_action_get_item(True,self.owner.world.wo_objects_grenade)
        # upgrade weapon?
        if status==False:
            # will attempt to upgrade gun, or get any nearby gun if ai doesn't have one
            status=self.take_action_get_gun(True,True)
        # grab anti-tank 
        if status==False and self.antitank==None:
            status=self.take_action_get_item(True,self.owner.world.wo_objects_handheld_antitank)

        # upgrade clothes / armor

        # top off ammo ?
        if status==False and self.primary_weapon!=None:
            ammo=self.handle_check_ammo(self.primary_weapon)
            # check if we have extra magazines in inventory
            # - if we don't then it is somewhat pointless to get more ammo
            if ammo[2]>0 :
                if ammo[1]<(ammo[0]):
                    # basically if we have less ammo in our inventory than in our gun
                    status=self.take_action_get_ammo(True)
            else:
                # no magazines, should we get a new gun?
                status=self.take_action_get_gun(True,False)


        return status

    #---------------------------------------------------------------------------
    def think_vehicle_role_driver(self):
        time_passed=self.owner.world.graphic_engine.time_passed_seconds
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
            self.determine_current_task()

        # update health 
        self.update_health()

        #----------- OLD ----------------------------------------
 


        #     # might be faster to have a bool we could check
        #     if self.large_pickup!=None:
        #         self.large_pickup.world_coords=engine.math_2d.get_vector_addition(self.owner.world_coords,self.carrying_offset)
            
        #     # building awareness stuff. ai and human need this 
        #     self.time_since_building_check+=self.owner.world.graphic_engine.time_passed_seconds
        #     if self.time_since_building_check>self.building_check_rate:
        #         self.handle_building_check()


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


                # out of ammo ?



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
                self.owner.world_coords,self.destination,self.owner.world.graphic_engine.time_passed_seconds)
            # add some fatigue
            self.fatigue+=self.fatigue_add_rate*self.owner.world.graphic_engine.time_passed_seconds


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

            


