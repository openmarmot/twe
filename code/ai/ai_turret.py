
'''
repo : https://github.com/openmarmot/twe

notes : the turret for a tank, or the mg mount on a vehicle
'''

#import built in modules
import copy
import random

#import custom packages
import engine.math_2d
import engine.log
import engine.penetration_calculator
import engine.world_builder

#global variables

class AITurret():
    '''turret for a tank, or the mg mount on a vehicle'''
    def __init__(self, owner):
        self.owner=owner

        #[side][armor thickness,armor slope,spaced_armor_thickness]
        # slope 0 degrees is vertical, 90 degrees is horizontal
        # armor grade steel thickness in mm. standard soft aluminum/steel is a 0-1
        self.turret_armor={}
        self.turret_armor['top']=[0,0,0]
        self.turret_armor['bottom']=[0,0,0]
        self.turret_armor['left']=[0,0,0]
        self.turret_armor['right']=[0,0,0]
        self.turret_armor['front']=[0,0,0]
        self.turret_armor['rear']=[0,0,0]

        # the side of the vehicle the turret is mounted on top/bottom/left/right/front/rear
        # most turrets should be mounted on the top
        self.vehicle_mount_side='top'

        # turret accuracy. 0 is perfect accuracy
        # basically a measure of how easy/hard it is to aim
        self.turret_accuracy=0

        # this means that it can no longer rotate
        self.turret_jammed=False

        # for remote operated machine guns - mostly german
        self.remote_operated=False

        # offset to position it correctly on a vehicle. vehicle specific
        self.position_offset=[0,0]

        # this is relative to the vehicle
        # really + or - a certain amount of degrees
        self.turret_rotation=0

        # gunner requested rotation change
        self.rotation_change=0

        # rotation range for the turret
        # full rotation is [-360,360]
        self.rotation_range=[-20,20]

        # speed of rotation
        self.rotation_speed=20

        self.vehicle=None
        self.last_vehicle_position=[0,0]
        self.last_vehicle_rotation=0

        # very important!
        # whether this is the main/most important turret or not.
        # used by ai_human to determine actions
        self.primary_turret=False

        # note - extra magazines/ammo should be stored in the vehicle inventory
        self.primary_weapon=None
        self.coaxial_weapon=None

        # these are here because reload speed is heavily affected by turret design
        self.primary_weapon_reload_speed=0
        self.coaxial_weapon_reload_speed=0

        # turrets with the small attribute are less likely to be hit
        self.small=False

        self.gun_sight=None

    #---------------------------------------------------------------------------
    def calculate_accuracy(self,weapon):
        '''calculate mechanical accuracy. '''

        # note most accuracy calculation should be done in ai_human_vehicle_gunner.calculate_turret_aim
        # this is smaller variations that get added when the bullet is fired

        temp_heading=engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle)
        far_coords=engine.math_2d.moveAlongVector(1000,self.owner.world_coords,temp_heading,1)

        adjust_max=0
        adjust_max+=weapon.ai.mechanical_accuracy
        adjust_max+=self.turret_accuracy

        if self.vehicle.ai.current_speed>0:
            adjust_max+=20
        if self.vehicle.ai.current_speed>100:
            adjust_max+=30

        # apply adjustment
        far_coords=[far_coords[0]+random.uniform(-adjust_max,adjust_max),far_coords[1]+random.uniform(-adjust_max,adjust_max)]

        # get the new angle
        return engine.math_2d.get_rotation(self.owner.world_coords,far_coords)


    #---------------------------------------------------------------------------
    def event_collision(self,event_data):
        '''handle collision events for the turret'''

        if event_data.is_projectile:
            projectile=event_data
            distance=engine.math_2d.get_distance(self.owner.world_coords,projectile.ai.starting_coords)

            side,relative_angle=engine.math_2d.calculate_hit_side(self.owner.rotation_angle,projectile.rotation_angle)
            penetration,pen_value,armor_value,spaced_effect=engine.penetration_calculator.calculate_penetration(projectile,distance,'steel',self.turret_armor[side],side,relative_angle)
            result=''
            if spaced_effect == 'destabilized':
                result = 'destabilized by spaced armor'

            if penetration:
                event_data.wo_stop()
                result=self.handle_penetration(projectile,side,distance,pen_value,armor_value)
            else:
                result = self.handle_non_penetration(projectile,pen_value,armor_value,spaced_effect)

            if self.vehicle is not None:
                self.vehicle.ai.add_hit_data(projectile,penetration,side,distance,f'Turret {self.owner.name}',result,pen_value,armor_value)

        elif event_data.is_grenade:
            print('bonk')
        else:
            engine.log.add_data('error','ai_vehicle event_collision - unhandled collision type'+event_data.name,True)

    #---------------------------------------------------------------------------
    def handle_event(self, event, event_data):
        ''' overrides base handle_event'''
        # EVENT - text describing event
        # event_data - most likely a world_object but could be anything

        # not sure what to do here yet. will have to think of some standard events
        if event=='add_inventory':
            engine.log.add_data('Error','ai_turret handle_event add_inventory not implemented',True)
            #self.event_add_inventory(event_data)
        elif event=='collision':
            self.event_collision(event_data)
        elif event=='remove_inventory':
            engine.log.add_data('Error','ai_turret handle_event remove_inventory not implemented',True)
            #self.event_remove_inventory(event_data)
        else:
            print('Error: '+self.owner.name+' cannot handle event '+event)

    #---------------------------------------------------------------------------
    def handle_spalling_damage(self,projectile):
        '''handle damage from armor spalling due to near-miss penetrations'''

        num_fragments = random.randint(1, 3)

        for i in range(num_fragments):
            if random.randint(0, 2) == 0:
                shrapnel = engine.world_builder.spawn_object(self.owner.world, self.owner.world_coords, 'projectile', False)
                shrapnel.ai.projectile_type = 'shrapnel'
                shrapnel.name = 'shrapnel'
                shrapnel.ai.starting_coords = self.owner.world_coords
                shrapnel.ai.shooter=projectile.ai.shooter
                shrapnel.ai.weapon=projectile.ai.weapon

                if self.remote_operated is False:
                    for role in self.vehicle.ai.vehicle_crew:
                        if role.role_occupied:
                            if role.turret==self.owner:
                                if random.randint(0,1)==1:
                                    role.human.ai.handle_event('collision',shrapnel)

    #---------------------------------------------------------------------------
    def handle_rotate_left(self):
        '''handle left rotation input'''
        if self.turret_jammed is False:
            self.rotation_change=1

    #---------------------------------------------------------------------------
    def handle_rotate_right(self):
        '''handle right rotation input'''
        if self.turret_jammed is False:
            self.rotation_change=-1

    #---------------------------------------------------------------------------
    def handle_fire(self):
        '''fire the primary weapon'''
        if self.primary_weapon.ai.check_if_can_fire():
            self.primary_weapon.rotation_angle=self.calculate_accuracy(self.primary_weapon)
            self.primary_weapon.ai.fire()
            self.vehicle.ai.recent_noise_or_move=True
            self.vehicle.ai.recent_noise_or_move_time=self.owner.world.world_seconds
            return True
        return False

    #---------------------------------------------------------------------------
    def handle_fire_coax(self):
        '''fire the coaxial weapon'''
        if self.coaxial_weapon.ai.check_if_can_fire():
            self.coaxial_weapon.rotation_angle=self.calculate_accuracy(self.coaxial_weapon)
            self.coaxial_weapon.ai.fire()
            self.vehicle.ai.recent_noise_or_move=True
            self.vehicle.ai.recent_noise_or_move_time=self.owner.world.world_seconds
            return True
        return False

    #---------------------------------------------------------------------------
    def handle_penetration(self,projectile,side,distance,pen_value,armor_value):
        '''handle projectile penetration of turret armor'''

        result=''
        damage_options=['turret track']

        if self.remote_operated is False:
            damage_options.append('gunner hit')

        if self.primary_weapon:
            damage_options.append('primary weapon')
        if self.coaxial_weapon:
            damage_options.append('coaxial weapon')

        if self.vehicle:
            if self.vehicle_mount_side!='top':
                damage_options.append('penetration into vehicle')

            if len(self.vehicle.ai.ammo_rack)>0 and self.remote_operated is False:
                damage_options.append('ammo_rack')


        result=random.choice(damage_options)

        if result=='turret track':
            self.turret_jammed=True
            if self.primary_turret and self.vehicle:
                self.vehicle.ai.vehicle_disabled=True
        elif result=='primary weapon':
            if self.primary_weapon:
                if random.randint(0,1)==1:
                    if self.primary_weapon.ai.action_jammed:
                        self.primary_weapon.ai.damaged=True
                    else:
                        self.primary_weapon.ai.action_jammed=True
                else:
                    self.primary_weapon.ai.damaged=True

                if self.primary_turret and self.primary_weapon.ai.damaged:
                    if self.vehicle and self.vehicle.ai.is_transport is False:
                        self.vehicle.ai.vehicle_disabled=True

        elif result=='coaxial weapon':
            if self.coaxial_weapon:
                if random.randint(0,1)==1:
                    if self.coaxial_weapon.ai.action_jammed:
                        self.coaxial_weapon.ai.damaged=True
                    else:
                        self.coaxial_weapon.ai.action_jammed=True
                else:
                    self.coaxial_weapon.ai.damaged=True
        elif result=='gunner hit':
            for role in self.vehicle.ai.vehicle_crew:
                if role.role_occupied and role.turret==self.owner:
                    role.human.ai.handle_event('collision',projectile)
        elif result=='penetration into vehicle':
            extra_damage_options=['random_crew_projectile','random_crew_fire','engine']
            extra_damage=random.choice(extra_damage_options)
            result+=f': {extra_damage}'
            self.vehicle.ai.handle_component_damage(extra_damage,projectile)
        elif result=='ammo_rack':
            self.vehicle.ai.handle_component_damage('ammo_rack',projectile)
        else:
            engine.log.add_data('error',f'ai_turret.handle_penetration unknown result: {result}',True)

        return result

    #---------------------------------------------------------------------------
    def handle_non_penetration(self,projectile,pen_value,armor_value,spaced_effect):
        '''handle projectile that does not penetrate turret armor'''

        result=''
        if pen_value >= armor_value * 0.9 and spaced_effect != 'destabilized':
            self.handle_spalling_damage(projectile)
            result = 'spalling'
        else:
            self.vehicle.ai.projectile_bounce(projectile)

        return result

    #---------------------------------------------------------------------------
    def neutral_controls(self):
        ''' return controls to neutral over time'''

        if self.rotation_change!=0:
            # controls should return to neutral over time
            time_passed=self.owner.world.time_passed_seconds

            #return wheel to neutral
            self.rotation_change=engine.math_2d.regress_to_zero(self.rotation_change,time_passed)

    #---------------------------------------------------------------------------
    def update(self):
        '''update the turret state'''

        self.update_physics()

        self.neutral_controls()

    #---------------------------------------------------------------------------
    def update_physics(self):
        '''update turret physics'''
        time_passed=self.owner.world.time_passed_seconds
        moved=False

        if self.rotation_change!=0:
            moved=True
            self.turret_rotation+=(self.rotation_change*self.rotation_speed*time_passed)


            # Check if turret allows full 360-degree rotation
            if self.rotation_range == [-360, 360]:
                # Normalize rotation to stay within [0, 360) for continuous rotation
                self.turret_rotation = engine.math_2d.get_normalized_angle(self.turret_rotation)
            else:
                # Enforce restricted rotation range without resetting rotation_change
                if self.turret_rotation < self.rotation_range[0]:
                    self.turret_rotation = self.rotation_range[0]
                elif self.turret_rotation > self.rotation_range[1]:
                    self.turret_rotation = self.rotation_range[1]

        if self.vehicle is not None:
            if self.last_vehicle_position!=self.vehicle.world_coords:
                moved=True
                self.last_vehicle_position=copy.copy(self.vehicle.world_coords)
            elif self.last_vehicle_rotation!=self.vehicle.rotation_angle:
                moved=True
                self.last_vehicle_rotation=copy.copy(self.vehicle.rotation_angle)

        if moved:
            self.owner.reset_image=True
            if self.vehicle is not None:
                self.owner.rotation_angle=engine.math_2d.get_normalized_angle(self.vehicle.rotation_angle+self.turret_rotation)
                self.owner.world_coords=engine.math_2d.calculate_relative_position(self.vehicle.world_coords,self.vehicle.rotation_angle,self.position_offset)
