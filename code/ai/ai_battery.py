
'''
module : ai_none.py
language : Python 3.x
email : andrew@openmarmot.com
notes : battery
'''

#import built in modules

#import custom packages
from ai.ai_base import AIBase



class AIBattery(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # capacity in ampere-hours (Ah)
        self.max_capacity=55

        # in ampere-hours (Ah)
        self.state_of_charge=55

        self.voltage=6

        self.type="lead-acid"

        # affects max_capacity float 0-1
        self.health=1

    #---------------------------------------------------------------------------
    def discharge(self,amount_ah):
        # note amount_ah should already be normalized for time_passed
        self.state_of_charge-=amount_ah

    #---------------------------------------------------------------------------
    def recharge(self,amount_ah):
        # note amount_ah should already be normalized for time_passed
        self.state_of_charge+=amount_ah


    #---------------------------------------------------------------------------
    def update(self):
        
        # normalize battery values
        # more efficient to do it once here as we may have multiple discharge/charge calls
        if self.state_of_charge<0:
            self.state_of_charge=0
        elif self.state_of_charge>self.max_capacity*self.health:
            self.state_of_charge=self.max_capacity*self.health
    

    #---------------------------------------------------------------------------
