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
        '''added a new square in the coordinates or returns the existing square'''
        if (i, j) not in self.index_map:
            top_left_x = self.min_coord + j * self.grid_size
            top_left_y = self.min_coord + i * self.grid_size
            square = WorldGridSquare(i, j, (top_left_x, top_left_y), 
                (top_left_x + self.grid_size, top_left_y + self.grid_size), 
                self.grid_size)
            self.index_map[(i, j)] = square
        return self.index_map[(i, j)]
    
    #---------------------------------------------------------------------------
    def get_all_objects(self):
        '''return a list of all world objects in the grids'''
        return_objects=[]
        for g in self.index_map.values():
            return_objects+=g.wo_objects
        return return_objects
    
    #---------------------------------------------------------------------------
    def get_all_wo_update(self):
        '''get all objects that have no_update=False'''
        return_objects=[]
        for g in self.index_map.values():
            return_objects+=g.wo_objects_update
        return return_objects

    #---------------------------------------------------------------------------
    def get_grid_square_for_world_coords(self, coord):
        '''get the grid square for the supplied world coordinates'''
        j = int((coord[0] - self.min_coord) // self.grid_size)
        i = int((coord[1] - self.min_coord) // self.grid_size)
        return self.add_square(i, j)
    
    #---------------------------------------------------------------------------
    def get_grid_squares_near_world_coords(self,coord,range):
        '''return a array of grid squares within range of the supplied coordinates'''
        squares=[]
        squares.append(self.get_grid_square_for_world_coords(coord))
        temp=self.get_grid_square_for_world_coords([coord[0]+range,coord[1]])
        if temp not in squares:
            squares.append(temp)
        temp=self.get_grid_square_for_world_coords([coord[0]-range,coord[1]])
        if temp not in squares:
            squares.append(temp)
        temp=self.get_grid_square_for_world_coords([coord[0],coord[1]+range])
        if temp not in squares:
            squares.append(temp)
        temp=self.get_grid_square_for_world_coords([coord[0]+range,coord[1]-range])
        if temp not in squares:
            squares.append(temp)

        return squares
    
    #---------------------------------------------------------------------------
    def get_objects_from_all_grid_squares(self,get_humans,get_vehicles):
        '''get a list of specified objects from all grid squares'''
        return_objects=[]
        for g in self.index_map.values():
            if get_humans:
                return_objects+=g.wo_objects_human
            if get_vehicles:
                return_objects+=g.wo_objects_vehicle
        return return_objects
    
    #---------------------------------------------------------------------------
    def get_objects_from_grid_squares_near_world_coords(self,coord,range,get_humans,get_vehicles):
        '''get a list of the specified objects from nearby grid_squares'''
        grid_square=self.get_grid_squares_near_world_coords(coord,range)
        return_objects=[]
        for g in grid_square:
            if get_humans:
                return_objects+=g.wo_objects_human
            if get_vehicles:
                return_objects+=g.wo_objects_vehicle
        return return_objects

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

        new_square=self.get_grid_square_for_world_coords(wo_object.world_coords)
        
        if wo_object.grid_square is None:
            wo_object.grid_square=new_square
            wo_object.grid_square.add_wo_object(wo_object)
            return
        
        if wo_object.grid_square is not new_square:
            wo_object.grid_square.remove_wo_object(wo_object)
            wo_object.grid_square=new_square
            wo_object.grid_square.add_wo_object(wo_object)

        # otherwise it is already in the right square
            
    #---------------------------------------------------------------------------
    def update_world_objects(self):
        '''update the world objects in the grid'''
        #objects=self.get_all_objects()
        objects=self.get_all_wo_update()
        for wo in objects:
            wo.update()

            
    

