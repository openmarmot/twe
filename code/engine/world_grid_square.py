'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
'''

#import built in modules

#import custom packages
import engine.math_2d
import engine.log

#global variables

class WorldGridSquare:
    """Represents a grid square in the 2D game world."""
    def __init__(self,i,j,top_left,bottom_right,grid_size):
        """
        Initialize a grid square.
        
        Args:
            i: Row index in the grid.
            j: Column index in the grid.
            top_left: (x, y) coordinates of top-left corner.
            bottom_right: (x, y) coordinates of bottom-right corner.
            grid_size: Size of the grid square in units.
        """
        self.i = i
        self.j = j
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.grid_size = grid_size
        self.center = (
            (top_left[0] + bottom_right[0]) / 2,
            (top_left[1] + bottom_right[1]) / 2
        )

        self.wo_objects=[]
        self.wo_objects_human=[]
        self.wo_objects_building=[]
        self.wo_objects_vehicle=[]
        self.wo_objects_gun_magazine=[]
        self.wo_objects_gun=[]
        self.wo_objects_container=[]
        self.wo_objects_radio=[]
        self.wo_objects_furniture=[]

        # special selection for projectile collision. used by ai_projectile
        self.wo_objects_projectile_collision=[]
    #---------------------------------------------------------------------------
    def add_wo_object(self,wo_object):
        ''' add a wo_object to the grid square'''
        if wo_object not in self.wo_objects:
            self.wo_objects.append(wo_object)

            if wo_object.is_human:
                self.wo_objects_human.append(wo_object)
                self.wo_objects_projectile_collision.append(wo_object)
            elif wo_object.is_building:
                self.wo_objects_building.append(wo_object)
                self.wo_objects_projectile_collision.append(wo_object)
            elif wo_object.is_vehicle:
                self.wo_objects_vehicle.append(wo_object)
                self.wo_objects_projectile_collision.append(wo_object)
            elif wo_object.is_gun_magazine:
                self.wo_objects_gun_magazine.append(wo_object)
            elif wo_object.is_gun:
                self.wo_objects_gun.append(wo_object)
            elif wo_object.is_container:
                self.wo_objects_container.append(wo_object)
            elif wo_object.is_radio:
                self.wo_objects_radio.append(wo_object)
            elif wo_object.is_furniture:
                self.wo_objects_furniture.append(wo_object)
        else:
            text='world_grid_square.add_wo_object - '
            text+=f'{wo_object.name} is alreay in the wo_objects list'
            engine.log.add_data('error',text,True)



    #---------------------------------------------------------------------------
    def remove_wo_object(self,wo_object):
        if wo_object in self.wo_objects:
            self.wo_objects.remove(wo_object)

            if wo_object.is_human:
                self.wo_objects_human.remove(wo_object)
                self.wo_objects_projectile_collision.remove(wo_object)
            elif wo_object.is_building:
                self.wo_objects_building.remove(wo_object)
                self.wo_objects_projectile_collision.remove(wo_object)
            elif wo_object.is_vehicle:
                self.wo_objects_vehicle.remove(wo_object)
                self.wo_objects_projectile_collision.remove(wo_object)
            elif wo_object.is_gun_magazine:
                self.wo_objects_gun_magazine.remove(wo_object)
            elif wo_object.is_gun:
                self.wo_objects_gun.remove(wo_object)
            elif wo_object.is_container:
                self.wo_objects_container.remove(wo_object)
            elif wo_object.is_radio:
                self.wo_objects_radio.remove(wo_object)
            elif wo_object.is_furniture:
                self.wo_objects_furniture.remove(wo_object)
        else:
            text='world_grid_square.remove_wo_object - '
            text+=f'{wo_object.name} is not in the wo_objects list'
            engine.log.add_data('error',text,True)


