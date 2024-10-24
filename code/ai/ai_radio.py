
'''
module : ai_radio.py
language : Python 3.x
email : andrew@openmarmot.com
notes : radio
'''

#import built in modules

#import custom packages
from ai.ai_base import AIBase
import engine.world_radio
import engine.math_2d



class AIRadio(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        self.frequency_range = [0,10]  # [20.0, 60.0] MHz
        self.current_frequency = 0
        self.battery = None # option for a single battery
        self.transmisson_power_range=[0,10]
        self.transmission_power = 5  # current transmission power
        #self.antenna_type = antenna_type  # e.g., 'standard'
        self.volume_range=[0,10]
        self.volume = 5  # Default volume level
        self.power_on = False  # whenther power is on or off
        self.signal_strength = 0  # Signal strength of received signal
        self.encryption = False  # Encryption status
        self.operational_status = True  # True if functional, False if damaged

        self.radio_operator=None

        self.last_message=''

    #---------------------------------------------------------------------------
    def recieve_message(self,message):
        if self.power_on:
            # prevents echos. we don't want to receive our own message
            if message!=self.last_message:
                distance=engine.math_2d.get_distance(self.owner.world_coords,self.owner.world.player.world_coords)
                if distance<(50*self.volume):
                    print(message)

    #---------------------------------------------------------------------------
    def send_message(self,message):
        if self.power_on:
            self.last_message=message
            engine.world_radio.send_message(self.current_frequency,message)

    #---------------------------------------------------------------------------
    def turn_frequency_down(self):
        if self.current_frequency>self.frequency_range[0]:
            self.current_frequency-=1
            self.turn_power_on()

    #---------------------------------------------------------------------------
    def turn_frequency_up(self):
        if self.current_frequency<self.frequency_range[1]:
            self.current_frequency+=1
            self.turn_power_on()

    #---------------------------------------------------------------------------
    def turn_power_on(self):
        self.power_on=True
        engine.world_radio.add_radio(self.current_frequency,self.owner)

    #---------------------------------------------------------------------------
    def turn_power_off(self):
        self.power_on=False
        engine.world_radio.remove_radio(self.owner)

    #---------------------------------------------------------------------------
    def update_electrical_system(self):
        
        # draw electric power from ?? 

        # update battery
        self.battery.update()


    #---------------------------------------------------------------------------
    def update(self):
        
        if self.power_on:
            self.update_electrical_system()
    

    #---------------------------------------------------------------------------
