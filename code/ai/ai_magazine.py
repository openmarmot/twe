
'''
module : ai_magazine.py
language : Python 3.x
email : andrew@openmarmot.com
notes : A (gun) magazine is a object that holds projectiles
'''


#import built in modules

#import custom packages

#global variables

class AIMagazine(object):
    def __init__(self, owner):
        self.owner=owner
        # list of compatible gun names
        self.compatible_guns=[]

        # list of compatible projectiles
        # from projectile_data dict in penetration_calculator.py
        self.compatible_projectiles=[]

        # int max number of projectiles
        self.capacity=0

        # whether the magazine is integrated into the gun or not
        self.removable=True

        # list of projectiles (world_object)
        self.projectiles=[]

        # disentegrating magazines dissapear from the world when they are emptied 
        # done by the ai_human reloading code
        self.disintegrating=False
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------
