'''
repo : https://github.com/openmarmot/twe

notes :
'''

#import built in modules
import threading

#import custom packages
from engine.world_grid_square import WorldGridSquare
import engine.log

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
    def compute_terrain_values(self):
        # precompute world_area locations
        engine.log.add_data('note','Computing grid square terrain values..',True)
        threads = []
        for g in self.index_map.values():
            t = threading.Thread(target=g.compute_terrain_values)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
    
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
    def get_grid_squares_near_world_coords(self, coord, distance):
        '''return an array of grid squares within range of the supplied coordinates'''
        squares = []
        min_x = coord[0] - distance
        max_x = coord[0] + distance
        min_y = coord[1] - distance
        max_y = coord[1] + distance
        
        min_j = int((min_x - self.min_coord) // self.grid_size)
        max_j = int((max_x - self.min_coord) // self.grid_size)
        min_i = int((min_y - self.min_coord) // self.grid_size)
        max_i = int((max_y - self.min_coord) // self.grid_size)
        
        for i in range(min_i, max_i + 1):
            for j in range(min_j, max_j + 1):
                square = self.add_square(i, j)
                if square not in squares:  # Optional, but avoids duplicates
                    squares.append(square)
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

            
    

