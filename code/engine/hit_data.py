'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : this records all the data for a hit on a vehicle or other object
- should contain data ONLY, not object references
'''

#import built in modules

#import custom packages
import engine.math_2d

#global variables

class HitData():
    '''Hit Data'''
    def __init__(self,hit_object,projectile,penetrated,hit_side,distance,hit_compartment,result,penetration_value,armor_value):
        # calculate offsets. this is used later to display a visual representation of the hit
        self.position_offset,self.rotation_offset=engine.math_2d.calculate_offset_coords_and_rotation(hit_object.world_coords,hit_object.rotation_angle,projectile.world_coords,projectile.rotation_angle)

        # - projectile data - 
        self.projectile_name=projectile.ai.projectile_type
        self.projectile_shooter=projectile.ai.shooter
        self.projectile_weapon=projectile.ai.weapon


        # distance the projectile traveled to make the hit
        self.distance=round(distance,1)

        # - hit data -
        self.hit_object_name=hit_object.name
        # bool. did it penetrate
        self.penetrated=penetrated
        # string, the side that was hit
        self.hit_side=hit_side
        # string, the vehicle compartment hit
        self.hit_compartment=hit_compartment

        # what happened because of the hit (damage effects)
        self.result=result

        self.penetration_value=penetration_value
        self.armor_value=round(armor_value,2)
        

        