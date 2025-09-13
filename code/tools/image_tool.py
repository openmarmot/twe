
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
A special tool for working with images
'''


#import built in modules
from itertools import islice
import os 
import math

# import pip packages
import pygame
from pygame.locals import *
import pygame.freetype




class ImageTool(object):
    ''' 2D Graphics Engine using PyGame '''

    def __init__(self,screen_size):
        # called by World.__init__

        
        self.image_objects=[]
        self.selected_object=None
        self.selection_index=0

        self.images=dict()

        self.screen_size=screen_size
        pygame.init()

        # this seems to significantly improve visual quality when on 
        self.double_buffering=True
        if self.double_buffering:
            self.screen = pygame.display.set_mode(self.screen_size, pygame.DOUBLEBUF, 32)
        else:
            self.screen=pygame.display.set_mode(self.screen_size,0,32)
        
        self.background = pygame.surface.Surface(self.screen_size).convert()
        self.background.fill((255, 255, 255))


        
        # time stuff
        self.clock=pygame.time.Clock()
        self.time_passed=None
        self.time_passed_seconds=None

        # text stuff
        # Different text sizes for in menus
        self.small_font = pygame.freetype.SysFont(pygame.font.get_default_font(), 12)
        self.medium_font = pygame.freetype.SysFont(pygame.font.get_default_font(), 18)
        self.large_font = pygame.freetype.SysFont(pygame.font.get_default_font(), 30)

        self.menu_color=('#ffffff')
        self.color_black=('#000000')

        self.text_queue=[]

        # draw collision circles
        self.draw_collision=False

        # will cause everything to exit
        self.quit=False

        # max_fps max frames for every second.
        self.max_fps=60

        # scale min/max limit 
        #self.scale_limit=[0.2,1.1]
        self.scale_limit=[0.1,1.5]

        # scale. normal is 1. this is set by the player with []
        self.scale=self.scale_limit[1]

        # adjustment to viewing area. > == more visible
        # 100 seems to be about the minimum where there is no popping in and out of objects
        self.view_adjust_minimum=100
        self.view_adjust=self.view_adjust_minimum
        self.view_adjustment=400

        # load all images
        self.load_all_images('../images')


    #------------------------------------------------------------------------------
    def handleInput(self):

        # usefull for single button presses where you don't 
        # need to know if the button is still pressed
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                #pygame.quit()
                self.quit=True
            if event.type==pygame.KEYDOWN:
                #print(event.key)
                translated_key='none'
                if event.key==119: #w
                    if self.selected_object!=None:
                        self.selected_object.world_coords[1]-=1
                if event.key==100: #d
                    if self.selected_object!=None:
                        self.selected_object.world_coords[0]+=1
                if event.key==97: #a
                    if self.selected_object!=None:
                        self.selected_object.world_coords[0]-=1
                if event.key==115: #s
                    if self.selected_object!=None:
                        self.selected_object.world_coords[1]+=1
                if event.key==114: #w
                    if self.selected_object!=None:
                        self.selected_object.rotation_angle+=90
                        self.selected_object.rotation_angle=self.selected_object.rotation_angle % 360

                if event.key==113: #q
                    self.selection_index-=1
                    if self.selection_index<0:
                        self.selection_index=len(self.image_objects)-1
                    self.selected_object=self.image_objects[self.selection_index]

                if event.key==101: #e
                    self.selection_index+=1
                    if self.selection_index>len(self.image_objects)-1:
                        self.selection_index=0
                    self.selected_object=self.image_objects[self.selection_index]
                    
                
                if event.key==49: #1
                    self.print_offsets()

                if event.key==91: # [
                    self.zoom_out()
                elif event.key==93: # ]
                    self.zoom_in()



            if event.type==pygame.MOUSEBUTTONDOWN:
                # left click
                if event.button==1:
                    self.select_closest_object_with_mouse(self.get_mouse_screen_coords())
                # middle button click
                if event.button==2:
                    pass
                # right click
                if event.button==3:
                    pass
            if event.type==pygame.MOUSEMOTION:
                #print(str(event.pos))
                pass
        
 
    #------------------------------------------------------------------------------
    def load_all_images(self,folder_path):
        '''load all the images into pygame'''
        files_and_dirs = os.listdir(folder_path)
        # Filter out directories, keeping only files
        files = [f for f in files_and_dirs if os.path.isfile(os.path.join(folder_path, f))]

        for b in files:
            name=b.split('.')[0]
            image_path=folder_path+'/'+b
            self.images[name]=pygame.image.load(image_path).convert_alpha()
        
        print('Image loading complete')

    #------------------------------------------------------------------------------
    def print_offsets(self):
        if self.selected_object!=None:
            print('----------------------------------')
            print('offsets')
            print('----------------------------------')

            for b in self.image_objects:
                if b!=self.selected_object:
                    offset=[b.world_coords[0]-self.selected_object.world_coords[0],b.world_coords[1]-self.selected_object.world_coords[1]]
                    adjusted_offset=self.get_vector_rotation(offset,self.selected_object.rotation_angle)
                    print(b.image_list[b.image_index],' rotation:',b.rotation_angle,'offset:',adjusted_offset)

            print('----------------------------------')

    #------------------------------------------------------------------------------
    def render(self):
        self.update_render_info()

        self.screen.blit(self.background, (0, 0))
        for b in self.image_objects:
            self.reset_pygame_image(b)
            self.screen.blit(b.image, (b.screen_coords[0]-b.image_center[0], b.screen_coords[1]-b.image_center[1]))

            if(self.draw_collision):
                pygame.draw.circle(self.screen,(236,64,122),b.screen_coords,b.collision_radius)


        # text stuff

        self.h=0
        for b in self.text_queue:
            self.h+=15
            self.small_font.render_to(self.screen, (40, self.h), b, self.color_black)

        if self.double_buffering:
            pygame.display.flip()
        else:
            pygame.display.update()



    #---------------------------------------------------------------------------
    def select_closest_object_with_mouse(self,mouse_coords):

        object_distance=50
        closest_object=None

        for b in self.image_objects:
            distance=self.get_distance(mouse_coords,b.screen_coords)
            if distance<object_distance:
                object_distance=distance
                closest_object=b
        
        if closest_object != None:
            self.selected_object=closest_object



    #------------------------------------------------------------------------------
    def update(self):
        '''
            any misc updating that needs to be done
        '''
        self.handleInput()

        self.text_queue=[]
        self.text_queue.append('TWE Image Tool')
        self.text_queue.append('Q/E to select objects')
        if self.selected_object!=None:
            self.text_queue.append('Object: '+self.selected_object.image_list[self.selected_object.image_index])
            self.text_queue.append('Rotation angle: '+str(round(self.selected_object.rotation_angle,2)))
            self.text_queue.append('W/S/A/D to move')
            self.text_queue.append('R to rotate')
            self.text_queue.append('1: print offsets relative to this object (rotation should be 0)')

        # update time
        self.time_passed=self.clock.tick(self.max_fps)
        self.time_passed_seconds=self.time_passed / 1000.0

            
    #------------------------------------------------------------------------------
    def update_render_info(self):
        '''
            -checks if world objects are within the viewable
             screen area, and if so, translates their world coordinates
             to screen coordinates
        '''

        viewrange_x=((0+
            self.screen_size[0]+self.view_adjust), (0-
            self.screen_size[0]-self.view_adjust))
        viewrange_y=((0+
            self.screen_size[1]+self.view_adjust), (0-
            self.screen_size[1])-self.view_adjust)
        
        translation=self.get_translation()

        for b in self.image_objects:
            b.screen_coords[0]=(b.world_coords[0]*self.scale+translation[0])
            b.screen_coords[1]=(b.world_coords[1]*self.scale+translation[1])

    #------------------------------------------------------------------------------
    def get_distance(self,coords1, coords2,round_number=False):
        x=coords1[0]-coords2[0]
        y=coords1[1]-coords2[1]
        distance=math.sqrt(x*x+y*y)
        if round_number:
            return round(distance,1)
        else:
            return distance


    #------------------------------------------------------------------------------
    def get_mouse_screen_coords(self):
        x,y=pygame.mouse.get_pos()
        return [x,y]

    #------------------------------------------------------------------------------
    def get_mouse_world_coords(self):
        ''' return world coords of mouse'''
        # pretty sure this math doesnt make any sense
        x,y=pygame.mouse.get_pos()
        player_x=0
        player_y=0
        return [player_x-x,player_y-y]

    #-----------------------------------------------------------------------------
    def get_player_screen_coords(self):
        ''' return player screen coordinates'''
        return [self.screen_size[0]/2,self.screen_size[1]/2]
    
    #------------------------------------------------------------------------------
    def get_translation(self):
        ''' returns the translation for world to screen coords '''
        center_x=self.screen_size[0]/2
        center_y=self.screen_size[1]/2
        player_x=0*self.scale
        player_y=0*self.scale
        

        translate=[center_x-player_x,center_y-player_y]
        return translate
    
    #------------------------------------------------------------------------------
    def get_vector_rotation(self,vector,angle_degrees):
        # note this is adjusted to match how in game coordinates work
        # in the original code x and y were flipped
        # Convert angle to radians
        angle_rad = math.radians(angle_degrees)
        
        # Rotation matrix applied to vector
        y = vector[0] * math.cos(angle_rad) - vector[1] * math.sin(angle_rad)
        x = vector[0] * math.sin(angle_rad) + vector[1] * math.cos(angle_rad)
        
        return [x, y] 
    
    #------------------------------------------------------------------------------
    def reset_pygame_image(self, wo):
        '''reset the image for a world object'''
        obj_scale=self.scale+wo.scale_modifier
        wo.image_size=self.images[wo.image_list[wo.image_index]].get_size()
        wo.image_size=[int(wo.image_size[0]*obj_scale),int(wo.image_size[1]*obj_scale)]
        wo.image_center=[round(wo.image_size[0]*0.5,1),round(wo.image_size[1]*0.5,1)]
 
        try:
            image=self.images[wo.image_list[wo.image_index]]
            orig_rect = image.get_rect()
            rot_image = pygame.transform.rotate(image, wo.rotation_angle)
            rot_rect = orig_rect.copy()
            rot_rect.center = rot_image.get_rect().center
            rot_image = rot_image.subsurface(rot_rect).copy()
            resize_image=pygame.transform.scale(rot_image,wo.image_size)
            wo.image=resize_image
        except:
            print('error','graphics_2d_pygame.reset_pygame_image: image transform error with image '+wo.image_list[wo.image_index])
        

    #------------------------------------------------------------------------------
    def zoom_out(self):
        '''zoom out'''
        if self.scale>self.scale_limit[0]:
            self.scale=round(self.scale-0.1,1)
            self.view_adjust+=self.view_adjustment
            #print('zoom out',self.scale)
    #------------------------------------------------------------------------------
    def zoom_in(self):
        ''' zoom in'''
        if self.scale<self.scale_limit[1]:
            self.scale=round(self.scale+0.1,1)
            self.view_adjust-=self.view_adjustment
            # otherwise stuff starts getting clipped when its <0
            if self.view_adjust<self.view_adjust_minimum:
                self.view_adjust=self.view_adjust_minimum
            #print('zoom in',self.scale)

#------------------------------------------------------------------------------
            
class ImageObject(object):

    def __init__(self,image_list,rotation_angle):
        self.image_list=image_list
        self.image_index=0
        self.image=None
        self.image_size=None
        self.image_center=None
        self.world_coords=[0,0]
        self.screen_coords=[0,0]
        self.rotation_angle=rotation_angle
        self.scale_modifier=0


#------------------------------------------------------------------------------
# startup code
#------------------------------------------------------------------------------
screen_size = (1200,900)
image_tool=ImageTool(screen_size)

#image_tool.image_objects.append(ImageObject(['t20'],0))
#image_tool.image_objects.append(ImageObject(['german_soldier'],90))
#image_tool.image_objects.append(ImageObject(['german_soldier'],90))
#image_tool.image_objects.append(ImageObject(['german_soldier'],90))
#image_tool.image_objects.append(ImageObject(['german_soldier'],270))
#image_tool.image_objects.append(ImageObject(['german_soldier'],270))
#image_tool.image_objects.append(ImageObject(['german_soldier'],270))

#image_tool.image_objects.append(ImageObject(['panzer_iv_g_chassis'],0))
#image_tool.image_objects.append(ImageObject(['panzer_iv_hull_mg'],0))
#image_tool.image_objects.append(ImageObject(['panzer_iv_g_turret'],0))

#image_tool.image_objects.append(ImageObject(['pak40_carriage_deployed'],0))
#image_tool.image_objects.append(ImageObject(['pak40_turret'],0))
#image_tool.image_objects.append(ImageObject(['german_soldier'],0))
#image_tool.image_objects.append(ImageObject(['german_soldier'],0))


#image_tool.image_objects.append(ImageObject(['sd_kfz_251'],0))
#image_tool.image_objects.append(ImageObject(['251_2_turret'],0))

#image_tool.image_objects.append(ImageObject(['warehouse-outside'],0))
#image_tool.image_objects.append(ImageObject(['crate'],0))

image_tool.image_objects.append(ImageObject(['sd_kfz_10_chassis'],0))
image_tool.image_objects.append(ImageObject(['german_soldier'],0))
image_tool.image_objects.append(ImageObject(['german_soldier'],0))
image_tool.image_objects.append(ImageObject(['german_soldier'],0))
image_tool.image_objects.append(ImageObject(['german_soldier'],0))
image_tool.image_objects.append(ImageObject(['german_soldier'],0))
image_tool.image_objects.append(ImageObject(['german_soldier'],0))


while image_tool.quit==False:

    image_tool.update()
    image_tool.render()


