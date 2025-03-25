
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : anything that is.. a wheel 
'''

#import built in modules

#import custom packages

class AIWheel(object):
    def __init__(self, owner):
        self.owner=owner

        self.compatible_vehicles=[] # list of compatibile world_builder_identity (vehicles)

        self.damaged=False # can be repaired
        self.destroyed=False # cannot be repaired

        #[armor thickness,armor slope,spaced_armor_thickness]
        self.armor=[1,0,0]
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        pass

    #---------------------------------------------------------------------------
