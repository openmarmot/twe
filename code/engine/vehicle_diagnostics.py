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

    #---------------------------------------------------------------------------
    def handle_keydown(self,translated_key):
        print(translated_key)

        if translated_key=='esc':
            self.exit=True
            return


    #---------------------------------------------------------------------------
    def load(self,vehicle,screen_center):
        self.vehicle=vehicle
        self.screen_center=screen_center
        self.image_objects=[]
        # add the main object 
        v=VehicleDiagnosticObject()
        v.image_list=self.vehicle.image_list
        v.screen_coords=screen_center
        self.image_objects.append(v)

        self.update_text_main_screen()

    #---------------------------------------------------------------------------
    def update(self):
        '''update. called by graphics_2d_pygame'''

        pass
        

    #---------------------------------------------------------------------------
    def update_text_main_screen(self):
        '''update the main screen text'''
        self.text_queue=[]
        spacing=15
        coord=[40,15]

        self.text_queue.append([f'vehicle: {self.vehicle.name}',copy.copy(coord),self.text_black])
        coord[1]+=spacing
        if self.vehicle.ai.vehicle_disabled:
            self.text_queue.append(['disabled',copy.copy(coord),self.text_red])

        # diagnostics 
        coord=[40,80]
        self.text_queue.append(['--diagnostics--',copy.copy(coord),self.text_black])
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