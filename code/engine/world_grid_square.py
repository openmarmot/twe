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
            grid_size: Size of the grid square in units. normally 1000
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

        # - terrain sub grid - 
        # this was 100 originally. idk what a good number is
        self.terrain_grid_resolution = 75
        # 0=default (grass), 1=road, etc. 
        self.terrain_types = bytearray(self.terrain_grid_resolution * self.terrain_grid_resolution)  

        # set by graphic engine - whether the square is visible to the player
        self.visible=True

        self.wo_objects=[]
        self.wo_objects_update=[] #objects with no_update=False
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

        # set by ai_gun.fire. world.world_seconds when a fun was last fired
        # starts negative so no one immediately prones
        self.last_gun_fired=-100
    #---------------------------------------------------------------------------
    def add_wo_object(self,wo_object):
        ''' add a wo_object to the grid square'''
        if wo_object not in self.wo_objects:
            self.wo_objects.append(wo_object)

            if wo_object.no_update is False:
                self.wo_objects_update.append(wo_object)

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
            text+=f'{wo_object.name} is already in the wo_objects list'
            engine.log.add_data('error',text,True)

    #---------------------------------------------------------------------------
    def compute_terrain_values(self):
        '''compute terrain values'''

        # this is a layered overwriting approach. 
        

        # terrain types 
        # 0 -(default) open ground
        # 1 - vegetation
        # 2 - tree
        # 3 - road

        vegetation=[]
        trees=[]
        roads=[]

        for wo in self.wo_objects:
            if wo.world_builder_identity=='terrain_green':
                vegetation.append(wo.world_coords)
            elif wo.world_builder_identity=='pinus_sylvestris':
                trees.append(wo.world_coords)
            elif wo.world_builder_identity=='road_300':
                roads.append(wo.world_coords)

        for coord in vegetation:
            self.set_terrain_in_radius(coord,100,1)

        for coord in trees:
            self.set_terrain_in_radius(coord,50,2)

        for coord in roads:
            self.set_terrain_in_radius(coord,150,3)

    #---------------------------------------------------------------------------
    def get_terrain_type(self, world_coords):
        """
        Get terrain type at local coordinates within this square (0..grid_size).
        
        Uses integer math to avoid float precision issues.
        Clamps to bounds.
        """

        # convert world_coords to local grid coords
        local_x = world_coords[0] - self.top_left[0]
        local_y = world_coords[1] - self.top_left[1]

        # If outside square bounds, return default terrain type
        if (local_x < 0 or local_x >= self.grid_size or
            local_y < 0 or local_y >= self.grid_size):
            return 0

        ix = min(self.terrain_grid_resolution - 1, int(local_x * self.terrain_grid_resolution / self.grid_size))
        iy = min(self.terrain_grid_resolution - 1, int(local_y * self.terrain_grid_resolution / self.grid_size))
        idx = iy * self.terrain_grid_resolution + ix
        return self.terrain_types[idx]

    #---------------------------------------------------------------------------
    def remove_wo_object(self,wo_object):
        if wo_object in self.wo_objects:
            self.wo_objects.remove(wo_object)

            if wo_object.no_update is False:
                self.wo_objects_update.remove(wo_object)

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

    #---------------------------------------------------------------------------
    def set_terrain_in_radius(self, world_coords, radius, new_type):
        """
        Set the terrain type for all terrain grid cells whose centers are within
        the given radius of the specified world coordinates.
        
        Args:
            world_coords: (x, y) world coordinates of the center point.
            radius: Radius in world units.
            new_type: The new terrain type value (integer, e.g., 0-255).
        """
        local_x = world_coords[0] - self.top_left[0]
        local_y = world_coords[1] - self.top_left[1]
        res = self.terrain_grid_resolution
        cell_size = self.grid_size / res
        
        for iy in range(res):
            for ix in range(res):
                center_x = (ix + 0.5) * cell_size
                center_y = (iy + 0.5) * cell_size
                dist = engine.math_2d.get_distance([local_x, local_y], [center_x, center_y])
                if dist <= radius:
                    idx = iy * res + ix
                    self.terrain_types[idx] = new_type


