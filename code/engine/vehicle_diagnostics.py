'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
'''
import copy

class VehicleDiagnostics(object):

    def __init__(self):
        self.vehicle=None
        self.screen_center=None

        # array of VehicleDiagnosticObject
        self.image_objects=[]

        # tells graphic_engine to switch mode back to tactical
        self.exit=False

        # [['test,[0,0]],]
        self.text_queue=[]

        self.text_black='#000000'
        self.text_red='#FF2121'

        self.menu_string='[Esc to Exit]  [1 Main]  [2 Turrets]  [3 Crew]  [4 Engine]  [5 Wheels]'

    #---------------------------------------------------------------------------
    def handle_keydown(self,translated_key):

        if translated_key=='esc':
            self.exit=True
            return
        if translated_key=='1':
            self.load_main_screen()
        if translated_key=='2':
            self.load_turret_screen()
        if translated_key=='3':
            pass
        if translated_key=='4':
            pass
        if translated_key=='5':
            pass

    #---------------------------------------------------------------------------
    def load(self,vehicle,screen_center):
        self.vehicle=vehicle
        self.screen_center=screen_center
        self.load_main_screen()

    #---------------------------------------------------------------------------
    def load_main_screen(self):
        '''load main screen text and image '''

        self.image_objects=[]
        # add the main object 
        v=VehicleDiagnosticObject()
        v.image_list=self.vehicle.image_list
        v.screen_coords=self.screen_center
        self.image_objects.append(v)


        self.text_queue=[]
        spacing=15
        coord=[40,15]

        self.text_queue.append([self.menu_string,copy.copy(coord),self.text_black])
        coord[1]+=spacing
        coord[1]+=spacing

        self.text_queue.append([f'vehicle: {self.vehicle.name}',copy.copy(coord),self.text_black])
        coord[1]+=spacing
        if self.vehicle.ai.vehicle_disabled:
            self.text_queue.append(['disabled',copy.copy(coord),self.text_red])

        # diagnostics 
        coord=[40,100]
        self.text_queue.append(['-- diagnostics --',copy.copy(coord),self.text_black])
        coord[1]+=spacing
        for b in self.vehicle.ai.turrets:
            if b.ai.turret_jammed:
                self.text_queue.append([f'{b.name} jammed',copy.copy(coord),self.text_red])
                coord[1]+=spacing
            if b.ai.primary_weapon.ai.damaged:
                self.text_queue.append([f'{b.ai.primary_weapon.name} damaged',copy.copy(coord),self.text_red])
                coord[1]+=spacing

        wheel_damage=False
        wheel_destroyed=False
        for b in self.vehicle.ai.front_left_wheels:
            if b.ai.damaged:
                wheel_damage=True
            if b.ai.destroyed:
                wheel_destroyed=True
        for b in self.vehicle.ai.front_right_wheels:
            if b.ai.damaged:
                wheel_damage=True
            if b.ai.destroyed:
                wheel_destroyed=True
        for b in self.vehicle.ai.rear_left_wheels:
            if b.ai.damaged:
                wheel_damage=True
            if b.ai.destroyed:
                wheel_destroyed=True
        for b in self.vehicle.ai.rear_right_wheels:
            if b.ai.damaged:
                wheel_damage=True
            if b.ai.destroyed:
                wheel_destroyed=True
        if wheel_damage:
            self.text_queue.append(['wheel(s) damaged',copy.copy(coord),self.text_red])
            coord[1]+=spacing
        if wheel_destroyed:
            self.text_queue.append(['wheel(s) destroyed',copy.copy(coord),self.text_red])
            coord[1]+=spacing
        engine_damaged=False
        for b in self.vehicle.ai.engines:
            if b.ai.damaged:
                engine_damaged=True
        if engine_damaged:
            self.text_queue.append(['engine(s) damaged',copy.copy(coord),self.text_red])
            coord[1]+=spacing
        
        # - engine data -
        # this should move to its own page
        
        coord=[40,200]
        self.text_queue.append(['-- engine data --',copy.copy(coord),self.text_black])
        coord[1]+=spacing
        for b in self.vehicle.ai.engines:
            self.text_queue.append([f'Engine: {b.name}',copy.copy(coord),self.text_black])
            coord[1]+=spacing
            self.text_queue.append([f'-> engine on: {b.ai.engine_on}',copy.copy(coord),self.text_black])
            coord[1]+=spacing
            if b.ai.damaged:
                self.text_queue.append([f'-> damaged',copy.copy(coord),self.text_red])
                coord[1]+=spacing

        # - fuel tank data -
        # this should move to its own page
        
        coord=[40,350]
        self.text_queue.append(['-- fuel data --',copy.copy(coord),self.text_black])
        coord[1]+=spacing
        for b in self.vehicle.ai.fuel_tanks:
            self.text_queue.append([f'Fuel Tank: {b.name}',copy.copy(coord),self.text_black])
            coord[1]+=spacing
            if len(b.ai.inventory)>0:
                if 'gas' in b.ai.inventory[0].name:
                    self.text_queue.append([f'-> gas: {b.ai.inventory[0].volume} liters',copy.copy(coord),self.text_black])
                    coord[1]+=spacing
                if 'diesel' in b.ai.inventory[0].name:
                    self.text_queue.append([f'-> diesel: {b.ai.inventory[0].volume} liters',copy.copy(coord),self.text_black])
                    coord[1]+=spacing
            if b.ai.punctured:
                self.text_queue.append([f'-> punctured',copy.copy(coord),self.text_red])
                coord[1]+=spacing
            if b.ai.contaminated:
                self.text_queue.append([f'-> contaminated',copy.copy(coord),self.text_red])
                coord[1]+=spacing


        

        # - hit log data -
        coord=[40,700]
        self.text_queue.append(['-- recent hit data --',copy.copy(coord),self.text_black])
        coord[1]+=spacing
        for b in self.vehicle.ai.collision_log[-10:]:
            if b.penetrated:
                self.text_queue.append([f'penetrated: {b.penetrated} distance: {b.distance} projectile: {b.projectile_name} side: {b.hit_side} compartment: {b.hit_compartment}',copy.copy(coord),self.text_red])
                coord[1]+=spacing
            else:
                self.text_queue.append([f'penetrated: {b.penetrated} distance: {b.distance} projectile: {b.projectile_name} side: {b.hit_side} compartment: {b.hit_compartment}',copy.copy(coord),self.text_black])
                coord[1]+=spacing


    #---------------------------------------------------------------------------
    def load_turret_screen(self):
        '''load main screen text and image '''

        self.image_objects=[]
        turret_coords=[]
        if len(self.vehicle.ai.turrets)==0:
            pass
        elif len(self.vehicle.ai.turrets)==1:
            turret_coords=[self.screen_center]
        if len(self.vehicle.ai.turrets)==2:
            turret_coords=[]
            turret_coords.append([self.screen_center[0]+200,self.screen_center[1]])
            turret_coords.append([self.screen_center[0]-200,self.screen_center[1]])

        for turret in self.vehicle.ai.turrets:
            v=VehicleDiagnosticObject()
            v.image_list=turret.image_list
            v.screen_coords=turret_coords.pop()
            self.image_objects.append(v)


        self.text_queue=[]
        spacing=15
        coord=[40,15]

        self.text_queue.append([self.menu_string,copy.copy(coord),self.text_black])
        coord[1]+=spacing
        coord[1]+=spacing

        # - turret data - 
        # this should eventually move to its own page 
        coord=[40,150]
       
        for b in self.vehicle.ai.turrets:
            self.text_queue.append([f'Turret: {b.name}',copy.copy(coord),self.text_black])
            coord[1]+=spacing

            if b.ai.turret_jammed:
                self.text_queue.append([' -> Turret ring is jammed',copy.copy(coord),self.text_red])
                coord[1]+=spacing
            
            if b.ai.primary_weapon!=None:
                self.text_queue.append([f' -> {b.ai.primary_weapon.name}',copy.copy(coord),self.text_black])
                coord[1]+=spacing
                if b.ai.primary_weapon.ai.action_jammed:
                    self.text_queue.append([' --> action is jammed',copy.copy(coord),self.text_red])
                    coord[1]+=spacing
                if b.ai.primary_weapon.ai.damaged:
                    self.text_queue.append([' --> weapon is damaged',copy.copy(coord),self.text_red])
                    coord[1]+=spacing
                ammo_gun,ammo_inventory,magazine_count=self.vehicle.world.player.ai.check_ammo(b.ai.primary_weapon,self.vehicle)
                self.text_queue.append([f' --> ammo {ammo_gun}/{ammo_inventory}',copy.copy(coord),self.text_black])
                coord[1]+=spacing

            if b.ai.coaxial_weapon!=None:
                self.text_queue.append([f' -> {b.ai.coaxial_weapon.name}',copy.copy(coord),self.text_black])
                coord[1]+=spacing
                if b.ai.coaxial_weapon.ai.action_jammed:
                    self.text_queue.append([' --> action is jammed',copy.copy(coord),self.text_red])
                    coord[1]+=spacing
                if b.ai.coaxial_weapon.ai.damaged:
                    self.text_queue.append([' --> weapon is damaged',copy.copy(coord),self.text_red])
                    coord[1]+=spacing
                ammo_gun,ammo_inventory,magazine_count=self.vehicle.world.player.ai.check_ammo(b.ai.coaxial_weapon,self.vehicle)
                self.text_queue.append([f' --> ammo {ammo_gun}/{ammo_inventory}',copy.copy(coord),self.text_black])
                coord[1]+=spacing

            coord[1]+=spacing
            coord[1]+=spacing

    #---------------------------------------------------------------------------
    def update(self):
        '''update. called by graphics_2d_pygame'''

        pass


class VehicleDiagnosticObject(object):
    def __init__(self):
        self.screen_coords=[0,0]
        self.scale_modifier=0
        self.image=None
        self.image_index=0
        self.image_list=[]
        self.image_size=None
        self.rotation_angle=0
        self.reset_image=True