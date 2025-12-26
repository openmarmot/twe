
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : battery
'''

#import built in modules

#import custom packages

class AIBattery():
    def __init__(self, owner):
        self.owner=owner
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
        '''discharge battery'''
        # note amount_ah should already be normalized for time_passed
        self.state_of_charge = max(0, self.state_of_charge - amount_ah)

    #---------------------------------------------------------------------------
    def recharge(self,amount_ah):
        '''recharge battery'''
        # note amount_ah should already be normalized for time_passed
        self.state_of_charge=min(self.state_of_charge+amount_ah,self.max_capacity*self.health)

    #---------------------------------------------------------------------------
    def update(self):
        '''updates battery'''
        # all logic got moved to subfunctions
        pass
    
