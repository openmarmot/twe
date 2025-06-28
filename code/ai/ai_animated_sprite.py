'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : sprite that spins for awhile or moves or whatever
'''

#import built in modules

#import custom packages
import engine.math_2d

class AIAnimatedSprite(object):
    def __init__(self, owner):
        self.owner=owner
        
        # determines if the update code is active
        self.alive=True

        # how long it animates
        self.alive_time_max=5

        # actual time the object has been alive
        self.alive_time=0

        # how long it rotates
        self.rotate_time_max=3

        # rotation speed per second
        self.rotation_speed=400

        # how long it moves along its heading 
        self.move_time_max=2

        # if true the heading is updated when rotation is updated
        self.heading_from_rotation=False

        self.speed=50

        # remove from world when alive time runs out
        self.self_remove=False

        # set to true to only remove when not visible
        self.only_remove_when_not_visible=False

        # set when the object is ready to be deleted as soon as it is not visible
        self.self_delete_when_not_visible=False

    #---------------------------------------------------------------------------
    def update(self):
        if self.self_delete_when_not_visible:
            if self.owner.grid_square.visible==False:
                self.owner.wo_stop()
                return
            return
        
        if self.alive:
            time_passed=self.owner.world.time_passed_seconds

            self.alive_time+=time_passed

            if self.alive_time>self.alive_time_max:
                self.alive=False
                
                # self terminate
                if self.self_remove:
                    if self.only_remove_when_not_visible:
                        self.self_delete_when_not_visible=True
                    else:
                        self.owner.wo_stop()
                        return

            else:
                if self.alive_time<self.rotate_time_max:
                    #rotate
                    self.owner.rotation_angle+=self.rotation_speed*time_passed

                    # normalize angles 
                    if self.owner.rotation_angle>360:
                        self.owner.rotation_angle=0
                    elif self.owner.rotation_angle<0:
                        self.owner.rotation_angle=360

                    if self.heading_from_rotation:
                        self.owner.heading=engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle)
                    
                    # reset immage as rotation has changed
                    self.owner.reset_image=True

                if self.alive_time<self.move_time_max:
                    # move along heading
                    self.owner.world_coords=engine.math_2d.moveAlongVector(self.speed,self.owner.world_coords,self.owner.heading,time_passed)

    #---------------------------------------------------------------------------
