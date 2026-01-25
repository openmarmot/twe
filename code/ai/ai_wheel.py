
'''
repo : https://github.com/openmarmot/twe

notes : anything that is.. a wheel 
'''

#import built in modules

#import custom packages

class AIWheel():
    def __init__(self, owner):
        self.owner=owner

        # note as of 8/5/2025 this isn't used for anything yet
        self.compatible_vehicles=[] # list of compatibile world_builder_identity (vehicles)

        self.damaged=False # can be repaired
        self.destroyed=False # cannot be repaired

        # some wheels like tank wheels don't have a inflated tire
        self.has_tire=True
        self.tire_damaged=False
        self.tire_destroyed=False

        #[armor thickness,armor slope,spaced_armor_thickness]
        self.armor=[1,0,0]
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        pass

    #---------------------------------------------------------------------------
