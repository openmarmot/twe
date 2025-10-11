'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : the ai_human code for operating a radio
'''

# import built in modules

# import custom modules


class AIHumanRadioOperator():
    def __init__(self, owner):
        self.owner=owner

    #---------------------------------------------------------------------------
    def get_radio(self):
        '''get the radio object that we are using'''
        if self.in_vehicle():
            vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
            return vehicle.ai.rado
        
        # we must be on foot
        if self.owner.ai.large_pickup:
            if self.owner.ai.large_pickup.is_radio:
                return self.owner.ai.large_pickup
        
        return None
    
    #---------------------------------------------------------------------------
    def send_message(self,message):
        '''send a radio message'''
        # message is a string in the format from ai_radio.py
        radio=self.get_radio()
        if radio:
            frequency=self.owner.ai.squad.faction_tactical.radio_frequency
            self.turn_on_and_tune_radio(radio,frequency)

            radio.ai.send_message(message)
    
    #---------------------------------------------------------------------------
    def turn_on_and_tune_radio(radio,frequency):
        '''turn on and tune radio to the given frequency'''

        if radio.ai.power_on==False  or radio.ai.current_frequency!=frequency:
            radio.ai.frequency=frequency
            radio.ai.turn_power_on()

    #---------------------------------------------------------------------------
    def update(self):

        radio=self.get_radio()

        if radio is None:
            return
        
        self.turn_on_and_tune_radio(radio)

        # process recieve queue 


