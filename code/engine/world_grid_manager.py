'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
'''

#import built in modules

#import custom packages
from engine.world_grid_square import WorldGridSquare

#global variables

class WorldGridManager:
    def __init__(self, grid_size=1000):
        self.index_map = {}  # (i, j) -> GridSquare
        self.grid_size = grid_size
        self.min_coord = 0 # this doesn't really matter, just a way to index the array
    
    #---------------------------------------------------------------------------
    def add_square(self, i, j):
        if (i, j) not in self.index_map:
            top_left_x = self.min_coord + j * self.grid_size
            top_left_y = self.min_coord + i * self.grid_size
            square = WorldGridSquare(i, j, (top_left_x, top_left_y), 
                (top_left_x + self.grid_size, top_left_y + self.grid_size), 
                self.grid_size)
            self.index_map[(i, j)] = square
        return self.index_map[(i, j)]
    
    #---------------------------------------------------------------------------
    def get_or_create(self, coord):
        j = int((coord[0] - self.min_coord) // self.grid_size)
        i = int((coord[1] - self.min_coord) // self.grid_size)
        return self.add_square(i, j)
    
    #---------------------------------------------------------------------------
    def remove_object_from_world_grid(self,wo_object):
        if wo_object.grid_square is None:
            pass
        else:
            wo_object.grid_square.remove_wo_object(wo_object)
            wo_object.grid_square=None

    #---------------------------------------------------------------------------
    def update_wo_object_square(self,wo_object):
        '''update the square the wo object is in'''

        # this is called by world_object.update_grid_square
        # it is also called when a object is added to the world

        new_square=self.get_or_create(wo_object.world_coords)
        
        if wo_object.grid_square is None:
            wo_object.grid_square=new_square
            wo_object.grid_square.add_wo_object(wo_object)
            return
        
        if wo_object.grid_square is not new_square:
            wo_object.grid_square.remove_wo_object(wo_object)
            wo_object.grid_square=new_square
            wo_object.grid_square.add_wo_object(wo_object)

        # otherwise it is already in the right square
            
    

