'''
repo : https://github.com/openmarmot/twe

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




class ImageTool():
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
        self.collision_radius=50

        # draw alignment lines (new)
        self.draw_alignment_lines=True

        # click sets image_rotation_offset instead of moving the object
        self.pivot_set_mode=False

        # colors for different images
        self.colors = [(255,0,0), (0,255,0), (0,0,255), (255,165,0), (128,0,128), (0,255,255), (255,0,255), (255,255,0)]

        # will cause everything to exit
        self.quit=False

        # max_fps max frames for every second.
        self.max_fps=60

        # Discrete zoom levels (synced with main game)
        self.zoom_levels = [
            0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.075,
            0.1, 0.125, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5,
            0.6, 0.75, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5
        ]
        self.scale_limit = [self.zoom_levels[0], self.zoom_levels[-1]]

        # scale. normal is 1. this is set by the player with []
        self.scale=1

        # adjustment to viewing area. > == more visible
        # 100 seems to be about the minimum where there is no popping in and out of objects
        self.view_adjust_minimum=100
        self.view_adjust=self.view_adjust_minimum
        self.view_adjustment=400

        # load all images. object_defs is the source of truth (typically
        # an images/ folder next to each object). code/images is a
        # fallback for sprites that have not been moved yet.
        tools_dir = os.path.dirname(os.path.abspath(__file__))
        code_dir = os.path.dirname(tools_dir)
        self.load_all_images(os.path.join(code_dir, 'engine', 'object_defs'))
        self.load_all_images(os.path.join(code_dir, 'images'), overwrite=False)


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

                if event.key==99: #c
                    self.pivot_set_mode=not self.pivot_set_mode

                if event.key==120: #x
                    self.reset_selected_pivot()

                if event.key==91: # [
                    self.zoom_out()
                elif event.key==93: # ]
                    self.zoom_in()



            if event.type==pygame.MOUSEBUTTONDOWN:
                # left click
                if event.button==1:
                    if self.selected_object:
                        if self.pivot_set_mode:
                            self.set_selected_pivot(self.get_mouse_world_coords())
                        else:
                            self.selected_object.world_coords=self.get_mouse_world_coords()
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
    def load_all_images(self,folder_path,overwrite=True):
        '''Recursively load PNG images from folder_path into pygame.

        Images are keyed by filename without extension so existing
        image_list entries keep working. Skip __pycache__.
        overwrite=False leaves the first loaded image in place.
        '''
        folder_path=os.path.abspath(folder_path)
        if not os.path.isdir(folder_path):
            print('error','Image folder does not exist: '+folder_path)
            return

        loaded=0
        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for filename in files:
                name, ext = os.path.splitext(filename)
                if ext.lower() != '.png':
                    continue
                if name in self.images and not overwrite:
                    continue
                image_path=os.path.join(root, filename)
                if name in self.images:
                    print('warn','Duplicate image name '+name+', replacing with '+image_path)
                image = pygame.image.load(image_path).convert_alpha()
                w, h = image.get_size()
                if w != h:
                    print(f"Alert: Image {name} is not square (width: {w}, height: {h})")
                self.images[name]=image
                loaded+=1

        print('Image loading complete: '+str(loaded)+' from '+folder_path)

    #------------------------------------------------------------------------------
    def print_offsets(self):
        if self.selected_object!=None:
            print('----------------------------------')
            print('offsets')
            print('----------------------------------')

            for b in self.image_objects:
                ox=round(b.image_rotation_offset[0],1)
                oy=round(b.image_rotation_offset[1],1)
                print(b.image_list[b.image_index],' image_rotation_offset:',[ox,oy])
                print(f"z.image_rotation_offset = [{ox}, {oy}]")

            for b in self.image_objects:
                if b!=self.selected_object:
                    offset=[b.world_coords[0]-self.selected_object.world_coords[0],b.world_coords[1]-self.selected_object.world_coords[1]]
                    adjusted_offset=self.get_vector_rotation(offset,self.selected_object.rotation_angle)
                    print(b.image_list[b.image_index],' rotation:',b.rotation_angle,'offset:',adjusted_offset)

            # print out the specific format for bounding circles
            for b in self.image_objects:
                if 'bound_circle' in b.image_list[b.image_index]:
                    offset=[b.world_coords[0]-self.selected_object.world_coords[0],b.world_coords[1]-self.selected_object.world_coords[1]]
                    adjusted_offset=self.get_vector_rotation(offset,self.selected_object.rotation_angle)
                    size=b.image_list[b.image_index].split('r')[-1]
                    print(f'z.bounding_circles.append([{adjusted_offset},{size}])')

            print('----------------------------------')

    #------------------------------------------------------------------------------
    def render(self):
        self.update_render_info()

        self.screen.blit(self.background, (0, 0))

        if self.draw_collision and self.image_objects :
            self.reset_pygame_image(self.image_objects[0])
            coords=[self.image_objects[0].screen_coords[0]-self.image_objects[0].image_center[0], self.image_objects[0].screen_coords[1]-self.image_objects[0].image_center[1]]
            pygame.draw.circle(self.screen,(236,64,122),self.image_objects[0].screen_coords,self.collision_radius)

        for i, b in enumerate(self.image_objects):
            self.reset_pygame_image(b)
            blit_offset=b.image_blit_offset
            if blit_offset is None:
                blit_offset=b.image_center
            blit_x=b.screen_coords[0]-blit_offset[0]
            blit_y=b.screen_coords[1]-blit_offset[1]
            self.screen.blit(b.image, (blit_x, blit_y))

            if self.draw_alignment_lines:
                color = self.colors[i % len(self.colors)]
                pivot_x, pivot_y = b.screen_coords
                # Vertical / horizontal lines through the rotation origin
                v_start = (pivot_x, blit_y)
                v_end = (pivot_x, blit_y + b.image_size[1])
                pygame.draw.line(self.screen, color, v_start, v_end, 1)
                h_start = (blit_x, pivot_y)
                h_end = (blit_x + b.image_size[0], pivot_y)
                pygame.draw.line(self.screen, color, h_start, h_end, 1)
                # Outline around the image
                pygame.draw.rect(self.screen, color, (blit_x, blit_y, b.image_size[0], b.image_size[1]), 1)
                # rotation origin
                pygame.draw.circle(self.screen, color, (int(pivot_x), int(pivot_y)), 4, 1)


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
            self.text_queue.append('W/S/A/D or mouse click to move')
            self.text_queue.append('R to rotate')
            self.text_queue.append('C: pivot-set mode (click origin, rotation 0)')
            self.text_queue.append('X: reset pivot to image center')
            self.text_queue.append('1: print offsets relative to this object (rotation should be 0)')
            ox=round(self.selected_object.image_rotation_offset[0],1)
            oy=round(self.selected_object.image_rotation_offset[1],1)
            self.text_queue.append(f'image_rotation_offset: [{ox}, {oy}]')
            if self.pivot_set_mode:
                self.text_queue.append('PIVOT SET MODE - click the rotation origin')

            if self.selected_object!=self.image_objects[0]:
                offset=[self.selected_object.world_coords[0]-self.image_objects[0].world_coords[0],self.selected_object.world_coords[1]-self.image_objects[0].world_coords[1]]
                adjusted_offset=self.get_vector_rotation(offset,self.image_objects[0].rotation_angle)
                self.text_queue.append(f'relative offset: {adjusted_offset}')

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
        x, y = pygame.mouse.get_pos()
        translation = self.get_translation()
        world_x = (x - translation[0]) / self.scale
        world_y = (y - translation[1]) / self.scale
        return [world_x, world_y]

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

        try:
            image=self.images[wo.image_list[wo.image_index]]
            wo.image=pygame.transform.rotozoom(image, wo.rotation_angle, obj_scale)
            wo.image_size=wo.image.get_size()
            wo.image_center=[round(wo.image_size[0]*0.5,1),round(wo.image_size[1]*0.5,1)]
            self.update_image_blit_offset(wo, obj_scale)
        except:
            print('error','graphics_2d_pygame.reset_pygame_image: image transform error with image '+wo.image_list[wo.image_index])

    #------------------------------------------------------------------------------
    def reset_selected_pivot(self):
        '''move rotation origin back to the source image center'''
        obj=self.selected_object
        if obj is None:
            return
        if obj.rotation_angle!=0:
            print('reset pivot: set rotation to 0 first (R)')
            return
        obj.world_coords=[
            obj.world_coords[0]-obj.image_rotation_offset[0],
            obj.world_coords[1]-obj.image_rotation_offset[1],
        ]
        obj.image_rotation_offset=[0,0]
        print('pivot reset to image center')

    #------------------------------------------------------------------------------
    def set_selected_pivot(self, click_world):
        '''set rotation origin to the clicked point. rotation must be 0'''
        obj=self.selected_object
        if obj is None:
            return
        if obj.rotation_angle!=0:
            print('set pivot: set rotation to 0 first (R)')
            return
        old=obj.image_rotation_offset
        obj.image_rotation_offset=[
            click_world[0]-obj.world_coords[0]+old[0],
            click_world[1]-obj.world_coords[1]+old[1],
        ]
        obj.world_coords=[click_world[0], click_world[1]]
        ox=round(obj.image_rotation_offset[0],1)
        oy=round(obj.image_rotation_offset[1],1)
        print(f'pivot set image_rotation_offset=[{ox}, {oy}]')

    #------------------------------------------------------------------------------
    def update_image_blit_offset(self, wo, obj_scale):
        '''set blit offset so image_rotation_offset stays on screen_coords'''
        center=wo.image_center
        offset=wo.image_rotation_offset
        if center is None or (offset[0]==0 and offset[1]==0):
            wo.image_blit_offset=[center[0], center[1]] if center is not None else None
            return
        scaled=pygame.math.Vector2(offset[0]*obj_scale, offset[1]*obj_scale)
        rotated=scaled.rotate(-wo.rotation_angle)
        wo.image_blit_offset=[center[0]+rotated.x, center[1]+rotated.y]


    #------------------------------------------------------------------------------
    def zoom_out(self):
        '''zoom out'''
        try:
            idx = self.zoom_levels.index(round(self.scale, 3))
        except ValueError:
            idx = min(range(len(self.zoom_levels)),
                      key=lambda i: abs(self.zoom_levels[i] - self.scale))
        if idx > 0:
            self.scale = self.zoom_levels[idx - 1]
            self.view_adjust += self.view_adjustment
            print('zoom out', self.scale)

    #------------------------------------------------------------------------------
    def zoom_in(self):
        ''' zoom in'''
        try:
            idx = self.zoom_levels.index(round(self.scale, 3))
        except ValueError:
            idx = min(range(len(self.zoom_levels)),
                      key=lambda i: abs(self.zoom_levels[i] - self.scale))
        if idx < len(self.zoom_levels) - 1:
            self.scale = self.zoom_levels[idx + 1]
            self.view_adjust -= self.view_adjustment
            # otherwise stuff starts getting clipped when its <0
            if self.view_adjust < self.view_adjust_minimum:
                self.view_adjust = self.view_adjust_minimum
            print('zoom in', self.scale)

#------------------------------------------------------------------------------

class ImageObject():

    def __init__(self,image_list,rotation_angle):
        self.image_list=image_list
        self.image_index=0
        self.image=None
        self.image_size=None
        self.image_center=None
        self.image_rotation_offset=[0,0]
        self.image_blit_offset=None
        self.world_coords=[0,0]
        self.screen_coords=[0,0]
        self.rotation_angle=rotation_angle
        self.scale_modifier=0


#------------------------------------------------------------------------------
# startup code
#------------------------------------------------------------------------------
screen_size = (1200,900)
image_tool=ImageTool(screen_size)
image_tool.collision_radius=100

#image_tool.image_objects.append(ImageObject(['t20'],0))
#image_tool.image_objects.append(ImageObject(['german_soldier'],90))
#image_tool.image_objects.append(ImageObject(['german_soldier'],90))
#image_tool.image_objects.append(ImageObject(['german_soldier'],90))
#image_tool.image_objects.append(ImageObject(['german_soldier'],270))
#image_tool.image_objects.append(ImageObject(['german_soldier'],270))
#image_tool.image_objects.append(ImageObject(['german_soldier'],270))

#image_tool.image_objects.append(ImageObject(['elefant'],0))
#image_tool.image_objects.append(ImageObject(['panzer_iv_hull_mg'],0))
#image_tool.image_objects.append(ImageObject(['elefant_turret'],0))

#image_tool.image_objects.append(ImageObject(['pak40_carriage_deployed'],0))
#image_tool.image_objects.append(ImageObject(['pak40_turret'],0))
#image_tool.image_objects.append(ImageObject(['german_soldier'],0))
#image_tool.image_objects.append(ImageObject(['german_soldier'],0))

#image_tool.image_objects.append(ImageObject(['ba_64_chassis'],0))
#image_tool.image_objects.append(ImageObject(['ba_64_turret'],0))

#image_tool.image_objects.append(ImageObject(['warehouse-outside'],0))
#image_tool.image_objects.append(ImageObject(['251_2_turret'],0))

#image_tool.image_objects.append(ImageObject(['warehouse-outside'],0))
#image_tool.image_objects.append(ImageObject(['crate'],0))

#image_tool.image_objects.append(ImageObject(['rso_pak'],0))
image_tool.image_objects.append(ImageObject(['pak40_vehicle_turret'],0))

#image_tool.image_objects.append(ImageObject(['rso_pak'],0))
#image_tool.image_objects.append(ImageObject(['smg42_gun'],0))

image_tool.image_objects.append(ImageObject(['german_soldier'],0))
image_tool.image_objects.append(ImageObject(['german_soldier'],0))
image_tool.image_objects.append(ImageObject(['german_soldier'],0))


# -----
# bounding box markers
#image_tool.image_objects.append(ImageObject(['bound_circle_r100'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r100'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r100'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r100'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r100'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r100'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r100'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r100'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r25'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r25'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r25'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r25'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r25'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r25'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r25'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r25'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r25'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r45'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r45'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r45'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r10'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r10'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r10'],0))
#image_tool.image_objects.append(ImageObject(['bound_circle_r10'],0))



while image_tool.quit==False:

    image_tool.update()
    image_tool.render()
