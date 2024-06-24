
'''
module : ai_radio.py
language : Python 3.x
email : andrew@openmarmot.com
notes : radio
'''

#import built in modules

#import custom packages
from ai.ai_base import AIBase



class AIRadio(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        self.frequency_range = [0,0]  # [20.0, 60.0] MHz
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
