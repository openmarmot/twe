
'''
repo : https://github.com/openmarmot/twe

notes :
'''

#import built in modules

#import custom packages

#global variables

class AIConsumable():
    def __init__(self, owner):
        self.owner=owner

        # positive or negative. will be added to corresponding attribute
        self.health_effect=0
        self.hunger_effect=0
        self.thirst_effect=0
        self.fatigue_effect=0
        self.spoiled=False

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        pass

    #---------------------------------------------------------------------------
