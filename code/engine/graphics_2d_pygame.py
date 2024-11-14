
'''
module : graphics_2d_pygame.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
This should hold as much of the pygame specifc code as possibe.
The idea is to keep the graphics engine seperate from the rest of the code,
 so it is portable to different graphics engines

 ref:
 # pygame.key.get_pressed() and general input theory
 https://stackoverflow.com/questions/17372314/is-it-me-or-is-pygame-key-get-pressed-not-working
'''


#import built in modules
from itertools import islice
import os 

# import pip packages
import pygame
from pygame.locals import *
import pygame.freetype

#import custom packages
import engine.math_2d
from engine.game_menu import GameMenu
from engine.world import World
from engine.strategic_map import StrategicMap
import engine.log

class Graphics_2D_Pygame(object):
    ''' 2D Graphics Engine using PyGame '''

    def __init__(self,screen_size):
        # called by World.__init__

        self.images=dict()
        self.image_cache={}

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

        self.mode=0
        # 0 - game menu
        # 1 - world 
        # 2 - strategic_map

        self.game_menu=GameMenu(self)
        self.world=World()
        self.strategic_map=StrategicMap(self)


        # render level kind of a 'z' layer
        # 0 - ground cover
        # 1 - man made ground cover (cement, building insides)
        # 2 - objects laying on the ground (weapons,etc)
        # 3 - objects slightly elevated above ground (vehicles, animals??)
        # 4 - vehicle turrets
        # 5 - humans
        # 6 - objects above ground (birds, planes, clouds, etc)
        
        self.render_level_count=10
        self.renderlists=[[] for _ in range(self.render_level_count)]

        # count of rendered objects
        self.renderCount=0

        
        
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
        self.load_all_images('images')


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
                if event.key==96:
                    translated_key="tilde"
                elif event.key==48:
                    translated_key="0"
                elif event.key==49:
                    translated_key="1"
                elif event.key==50:
                    translated_key="2"
                elif event.key==51:
                    translated_key="3"
                elif event.key==52:
                    translated_key="4"
                elif event.key==53:
                    translated_key="5"
                elif event.key==54:
                    translated_key="6"
                elif event.key==55:
                    translated_key="7"
                elif event.key==56:
                    translated_key="8"
                elif event.key==57:
                    translated_key="9"
                elif event.key==27:
                    translated_key="esc"
                elif event.key==9:
                    translated_key='tab'
                elif event.key==112:
                    translated_key='p'
                elif event.key==116:
                    translated_key='t'
                elif event.key==103:
                    translated_key='g'
                elif event.key==114:
                    translated_key='r'
                elif event.key==45:
                    translated_key='-'
                elif event.key==61:
                    translated_key='+'
                elif event.key==122:
                    translated_key='z'
                elif event.key==120:
                    translated_key='x'

                if self.mode==0:
                    self.game_menu.handle_input(translated_key)
                elif self.mode==1:
                    if event.key==91: # [
                        self.zoom_out()
                    elif event.key==93: # ]
                        self.zoom_in()
                    else:
                        self.world.handle_keydown(translated_key,self.get_mouse_screen_coords())
                elif self.mode==2:
                    self.strategic_map.handle_keydown(translated_key)
                else:
                    engine.log.add_data('error','graphic_engine.mode unknown '+str(self.mode),True)

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
        
        # handle key press
        # i think more than one can be down at once, that is why we don't do if/elif
        if self.mode==1:
            keys=pygame.key.get_pressed()

            if keys[pygame.K_w]:
                self.world.handle_key_press('w')

            if keys[pygame.K_s]:
                self.world.handle_key_press('s')

            if keys[pygame.K_a]:
                self.world.handle_key_press('a')

            if keys[pygame.K_d]:
                self.world.handle_key_press('d')

            if keys[pygame.K_f]:
                self.world.handle_key_press('f',self.get_mouse_screen_coords())

            if keys[pygame.K_g]:
                self.world.handle_key_press('g',self.get_mouse_screen_coords())

            if keys[pygame.K_t]:
                self.world.handle_key_press('t',self.get_mouse_screen_coords())

            if keys[pygame.K_b]:
                self.world.handle_key_press('b')

            if keys[pygame.K_p]:
                self.world.handle_key_press('p')

            if keys[pygame.K_UP]:
                self.world.handle_key_press('up')

            if keys[pygame.K_DOWN]:
                self.world.handle_key_press('down')

            if keys[pygame.K_LEFT]:
                self.world.handle_key_press('left')

            if keys[pygame.K_RIGHT]:
                self.world.handle_key_press('right')


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
    def render(self):
        self.update_render_info()

        self.screen.blit(self.background, (0, 0))
        for b in self.renderlists:
            for c in b:
                if c.reset_image:
                    self.reset_pygame_image(c)
                self.screen.blit(c.image, (c.screen_coords[0]-c.image_size[0]/2, c.screen_coords[1]-c.image_size[1]/2))

                if(self.draw_collision):
                    pygame.draw.circle(self.screen,(236,64,122),c.screen_coords,c.collision_radius)

                if self.mode==2:
                    # special text stuff for map mode

                    if c.airport:
                        self.small_font.render_to(self.screen, (c.screen_coords[0],c.screen_coords[1]), 'A', self.color_black)
                    if c.rail_yard:
                        self.small_font.render_to(self.screen, (c.screen_coords[0]+10,c.screen_coords[1]), 'R', self.color_black)
                    if c.town:
                        self.small_font.render_to(self.screen, (c.screen_coords[0]-10,c.screen_coords[1]), 'T', self.color_black)

                    # german count 
                    if c.german_count>0:
                        self.small_font.render_to(self.screen, (c.screen_coords[0]-25,c.screen_coords[1]+20), str(c.german_count), self.color_black)
                    if c.soviet_count>0:
                        self.small_font.render_to(self.screen, (c.screen_coords[0]+15,c.screen_coords[1]+20), str(c.soviet_count), self.color_black)

        # text stuff
        if self.mode==0:
            self.h=0
            for b in self.game_menu.text_queue:
                self.h+=15
                self.small_font.render_to(self.screen, (40, self.h), b, self.color_black)
        elif self.mode==1: 
            self.h=0
            for b in islice(self.world.text_queue,self.world.text_queue_display_size):
                self.h+=15
                self.small_font.render_to(self.screen, (40, self.h), b, self.menu_color)

            self.h+=20
            for b in self.world.world_menu.text_queue:
                self.h+=15
                self.small_font.render_to(self.screen, (40, self.h), b, self.menu_color)

            if(self.world.debug_mode):
                self.h=0
                for b in self.world.debug_text_queue:
                    self.h+=15
                    self.small_font.render_to(self.screen, (900, self.h), b,self.menu_color )

            if(self.world.display_vehicle_text):
                self.h=0
                for b in self.world.vehicle_text_queue:
                    self.h+=15
                    self.small_font.render_to(self.screen, (500, self.h), b, self.menu_color)

        elif self.mode==2:
            self.h=0
            for b in self.strategic_map.strategic_menu.text_queue:
                self.h+=15
                self.small_font.render_to(self.screen, (40, self.h), b, self.color_black)

        if self.double_buffering:
            pygame.display.flip()
        else:
            pygame.display.update()

#------------------------------------------------------------------------------
    def reset_all(self):
        ''' resize all world_objects'''
        for b in self.world.wo_objects:
            b.reset_image=True

#---------------------------------------------------------------------------
    def select_closest_object_with_mouse(self,mouse_coords):
        possible_objects=[]

        # sort through the objects that are rendered (visible)
        for b in self.renderlists:
            for c in b:
                if self.mode==0:
                    pass
                elif self.mode==1:
                    # filter out a couple things we don't want to click on
                    if c.is_player==False and c!=self.world.player.ai.large_pickup and c.is_turret==False and c.can_be_deleted==False:
                        possible_objects.append(c)
                elif self.mode==2:
                    # for strategic map we want everything
                    possible_objects.append(c)

        object_distance=50
        closest_object=None

        for b in possible_objects:
            distance=engine.math_2d.get_distance(mouse_coords,b.screen_coords)
            if distance<object_distance:
                object_distance=distance
                closest_object=b
        
        if closest_object != None:
            #engine.log.add_data('debug','mouse distance: '+str(object_distance),True)
            #engine.log.add_data('debug','mouse select: '+closest_object.name,True)

            if self.mode==0:
                pass
            elif self.mode==1:
                self.world.world_menu.activate_menu(closest_object)
            elif self.mode==2:
                self.strategic_map.strategic_menu.activate_menu(closest_object)

#------------------------------------------------------------------------------
    def update(self):
        '''
            any misc updating that needs to be done
        '''
        self.handleInput()

        # update time
        self.time_passed=self.clock.tick(self.max_fps)
        self.time_passed_seconds=self.time_passed / 1000.0

        if self.mode==0:
            pass
            #self.game_menu.update(self.time_passed_seconds)
        elif self.mode==1:
            self.world.update(self.time_passed_seconds)
            # insert graphic engine specific debug text (after world.update populated it)
            if self.world.debug_mode and self.world.is_paused==False:
                self.world.debug_text_queue.insert(0,'FPS: '+str(int(self.clock.get_fps())))
                self.world.debug_text_queue.insert(1,'World scale: '+str(self.scale))
                self.world.debug_text_queue.insert(2,'View Adjust: '+str(self.view_adjust))
                self.world.debug_text_queue.insert(3,'Rendered Objects: '+ str(self.renderCount))

                
                # image cache debug info 
                #for key, value in self.image_cache.items():
                #    self.world.debug_text_queue.insert(4,f"Image cache {key} - size: {len(value)}")
            
            if self.world.exit_world:
                self.strategic_map.unload_world()
                self.mode=2
        elif self.mode==2:
            self.strategic_map.update()

            

#------------------------------------------------------------------------------
    def update_render_info(self):
        '''
            -checks if world objects are within the viewable
             screen area, and if so, translates their world coordinates
             to screen coordinates
        '''
        # note - i wonder if computing this is slower than just rendering everything
        # should add an ability to toggle this once i get a FPS count setup

        
        #clear out the render levels
        self.renderlists=[[] for _ in range(self.render_level_count)]

        self.renderCount=0
        if self.mode==0:
            pass
        elif self.mode==1:

            viewrange_x=((self.world.player.world_coords[0]+
                self.screen_size[0]+self.view_adjust), (self.world.player.world_coords[0]-
                self.screen_size[0]-self.view_adjust))
            viewrange_y=((self.world.player.world_coords[1]+
                self.screen_size[1]+self.view_adjust), (self.world.player.world_coords[1]-
                self.screen_size[1])-self.view_adjust)
            
            translation=self.get_translation()

            for b in self.world.wo_objects:

                if b.render:
                    
                    # check if the relative scale of the object is enough to make it visible
                    if (self.scale+b.scale_modifier)>=b.minimum_visible_scale:
                        
                        #determine whether object 'b' world_coords are within
                        #the viewport bounding box
                        if(b.world_coords[0]<viewrange_x[0] and
                            b.world_coords[0]>viewrange_x[1]):
                            if(b.world_coords[1]<viewrange_y[0] and
                                b.world_coords[1]>viewrange_y[1]):
                                #object is within the viewport, add it to the render list
                                self.renderlists[b.render_level].append(b)
                                self.renderCount+=1
                                #apply transform to generate screen coords

                                # player screen coords are set by get_translation
                                if b.is_player==False:
                                    b.screen_coords[0]=(b.world_coords[0]*self.scale+translation[0])
                                    b.screen_coords[1]=(b.world_coords[1]*self.scale+translation[1])

        elif self.mode==2:
            for b in self.strategic_map.map_squares:
                self.renderlists[0].append(b)

#------------------------------------------------------------------------------
    def get_mouse_screen_coords(self):
        x,y=pygame.mouse.get_pos()
        return [x,y]

#------------------------------------------------------------------------------
    def get_mouse_world_coords(self):
        ''' return world coords of mouse'''
        # pretty sure this math doesnt make any sense
        x,y=pygame.mouse.get_pos()
        player_x=self.world.player.world_coords[0]
        player_y=self.world.player.world_coords[1]
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
        player_x=self.world.player.world_coords[0]*self.scale
        player_y=self.world.player.world_coords[1]*self.scale
        
        self.world.player.screen_coords=[center_x,center_y]

        translate=[center_x-player_x,center_y-player_y]
        return translate
    
#------------------------------------------------------------------------------
    def reset_pygame_image(self, wo):
        '''reset the image for a world object'''
        wo.reset_image=False
        obj_scale=self.scale+wo.scale_modifier
        wo.image_size=self.images[wo.image_list[wo.image_index]].get_size()
        wo.image_size=[int(wo.image_size[0]*obj_scale),int(wo.image_size[1]*obj_scale)]
        
        # check if the correct image is already in the cache
        
        # rounding the angle should massively reduce the amount of images we need to hash 
        # without much of a visual loss, and zero angle math lass as we are only doing it for 
        # the key
        key = wo.image_list[wo.image_index]+str(wo.image_size)+str(round(wo.rotation_angle,1))
        if self.scale in self.image_cache:
            if key in self.image_cache[self.scale]:
                wo.image=self.image_cache[self.scale][key]
                #print('cache hit')
                return
        else:
            self.image_cache[self.scale]={}

        image=self.images[wo.image_list[wo.image_index]]
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, wo.rotation_angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        resize_image=pygame.transform.scale(rot_image,wo.image_size)
        wo.image=resize_image

        self.image_cache[self.scale][key]=resize_image
            #print('cache miss ',key)

#------------------------------------------------------------------------------
    def zoom_out(self):
        '''zoom out'''
        if self.scale>self.scale_limit[0]:
            self.scale=round(self.scale-0.1,1)
            self.view_adjust+=self.view_adjustment
            #print('zoom out',self.scale)
            self.reset_all()
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
            self.reset_all()


