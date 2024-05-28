
'''
module : module_template.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
This class should hold as much of the pygame specifc code as possibe.
The idea is to keep the graphics engine seperate from the rest of the code,
 so it is portable to different graphics engines

currently instantiated by the world class

 ref:
 # pygame.key.get_pressed() and general input theory
 https://stackoverflow.com/questions/17372314/is-it-me-or-is-pygame-key-get-pressed-not-working
'''


#import built in modules
import pygame
from pygame.locals import *
import pygame.freetype
from itertools import islice
import os 

#import custom packages


class Graphics_2D_Pygame(object):
    ''' 2D Graphics Engine using PyGame '''

    def __init__(self,Screen_size,World):
        # called by World.__init__

        self.images=dict()
        self.screen_size=Screen_size
        pygame.init()

        # this seems to significantly improve visual quality when on 
        self.double_buffering=True
        if self.double_buffering:
            self.screen = pygame.display.set_mode(self.screen_size, pygame.DOUBLEBUF, 32)
        else:
            self.screen=pygame.display.set_mode(self.screen_size,0,32)
        
        self.background = pygame.surface.Surface(self.screen_size).convert()
        self.background.fill((255, 255, 255))
        
        # render level kind of a 'z' layer
        # 0 - ground cover
        # 1 - man made ground cover (cement, building insides)
        # 2 - objects laying on the ground (weapons,etc)
        # 3 - objects slightly elevated above ground (vehicles, animals??)
        # 4 - objects that are slightly above object level 3 (humans who can ride in vehicles, vehicle turrets)
        # 5 - objects above ground (birds, planes, clouds, etc)
        
        self.render_level_count=6
        self.renderlists=[[] for _ in range(self.render_level_count)]

        # count of rendered objects
        self.renderCount=0

        self.world=World
        
        # time stuff
        self.clock=pygame.time.Clock()
        self.time_passed=None
        self.time_passed_seconds=None

        # text stuff
        # Different text sizes for in menus
        self.small_font = pygame.freetype.SysFont(pygame.font.get_default_font(), 12)
        self.medium_font = pygame.freetype.SysFont(pygame.font.get_default_font(), 18)
        self.large_font = pygame.freetype.SysFont(pygame.font.get_default_font(), 30)

        self.menu_color=(50, 51, 51)

        # used for temporary text. call add_text to add 
        self.text_queue=[]
        self.text_queue_clear_rate=4
        self.text_queue_display_size=5
        self.time_since_last_text_clear=0

        # used for the menu system. no limits enforced by this class
        self.menu_text_queue=[]


        # draw collision circles
        self.draw_collision=False

        # converts things to int to try and smooth jitter 
        self.smooth_jitter=False

        # will cause everything to exit
        self.quit=False


        # max_fps max frames for every second.
        self.max_fps=60

        # scale. normal is 1. this is set by the player with []
        self.scale=1
        # stuff under this doesn't get rendered
        self.minimum_visible_scale=0.1 


        # adjustment to viewing area
        self.view_adjust=0

        # load all images
        self.load_all_images('images')

#------------------------------------------------------------------------------
    def add_text(self,TEXT):
        ''' add text to the text queue'''
        self.text_queue.append(TEXT)
        if len(self.text_queue)<4:
            self.time_since_last_text_clear=-1

#------------------------------------------------------------------------------
    def handleInput(self):

        # usefull for single button presses where you don't 
        # need to know if the button is still pressed
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                #pygame.quit()
                self.quit=True
            if event.type==pygame.KEYDOWN:
                # logic for handling these keys has been shifted to world
                self.world.handle_keydown(event.key)

            if event.type==pygame.MOUSEBUTTONDOWN:
                # left click
                if event.button==1:
                    self.world.select_with_mouse(self.get_mouse_screen_coords())
                # middle button click
                if event.button==2:
                    pass
                # right click
                if event.button==3:
                    pass
            if event.type==pygame.MOUSEMOTION:
                #print(str(event.pos))
                pass
        #print(self.keyPressed('w'))

#------------------------------------------------------------------------------
    def keyPressed(self, KEY):
        # returns bool as to whether keyPressed is KEY
        # the point of this is to translate pygame methods into generic keys 
        # in order to keep all pygame references in this class 
        # used by ai_player for movement

        # mouse support - returns list of three bools [left, middle, right]
       # print(str(pygame.mouse.get_pressed()))

        keys=pygame.key.get_pressed()
        if KEY=='w':
            if keys[pygame.K_w]:
                return True
            else:
                return False
        elif KEY=='s':
            if keys[pygame.K_s]:
                return True
            else:
                return False
        elif KEY=='a':
            if keys[pygame.K_a]:
                return True
            else:
                return False
        elif KEY=='d':
            if keys[pygame.K_d]:
                return True
            else:
                return False
        elif KEY=='f':
            if keys[pygame.K_f]:
                return True
            else:
                return False
        elif KEY=='g':
            if keys[pygame.K_g]:
                return True
            else:
                return False
        elif KEY=='t':
            if keys[pygame.K_t]:
                return True
            else:
                return False
        elif KEY=='b':
            if keys[pygame.K_b]:
                return True
            else:
                return False
        elif KEY=='p':
            if keys[pygame.K_p]:
                return True
            else:
                return False
        elif KEY=='up':
            if keys[pygame.K_UP]:
                return True
            else:
                return False
        elif KEY=='down':
            if keys[pygame.K_DOWN]:
                return True
            else:
                return False
        elif KEY=='left':
            if keys[pygame.K_LEFT]:
                return True
            else:
                return False
        elif KEY=='right':
            if keys[pygame.K_RIGHT]:
                return True
            else:
                return False
        else:
            print('keydown error, key is not recognized: ',KEY)
            return False

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
                    c.reset_image=False
                    obj_scale=self.scale+c.scale_modifier
                    c.image_size=self.images[c.image_list[c.image_index]].get_size()
                    c.image_size=[int(c.image_size[0]*obj_scale),int(c.image_size[1]*obj_scale)]
                    c.image=self.get_rotated_scaled_image(self.images[c.image_list[c.image_index]],c.image_size,c.rotation_angle)
                    #c.image=self.get_rotated_scaled_image_v2(self.images[c.image_list[c.image_index]],self.scale,c.rotation_angle)
                self.screen.blit(c.image, (c.screen_coords[0]-c.image_size[0]/2, c.screen_coords[1]-c.image_size[1]/2))

                c.render_pass_2()

                if(self.draw_collision):
                    pygame.draw.circle(self.screen,(236,64,122),c.screen_coords,c.collision_radius)


        # text stuff 
        self.h=0
        for b in islice(self.text_queue,self.text_queue_display_size):
            self.h+=15
            self.small_font.render_to(self.screen, (40, self.h), b, self.menu_color)

        self.h+=20
        for b in self.menu_text_queue:
            self.h+=15
            self.small_font.render_to(self.screen, (40, self.h), b, self.menu_color)

        if(self.world.debug_mode):
            self.h=0
            for b in self.world.debug_text_queue:
                self.h+=15
                self.small_font.render_to(self.screen, (750, self.h), b,self.menu_color )

        if(self.world.display_vehicle_text):
            self.h=0
            for b in self.world.vehicle_text_queue:
                self.h+=15
                self.small_font.render_to(self.screen, (500, self.h), b, self.menu_color)

        if self.double_buffering:
            pygame.display.flip()
        else:
            pygame.display.update()

#------------------------------------------------------------------------------
    def reset_all(self):
        ''' resize all world_objects'''
        for b in self.world.wo_objects:
            b.reset_image=True

#------------------------------------------------------------------------------
    def update(self):
        '''
            any misc updating that needs to be done
        '''
        self.handleInput()

        # update time
        self.time_passed=self.clock.tick(self.max_fps)
        self.time_passed_seconds=self.time_passed / 1000.0

        # cycle the text queue
        self.time_since_last_text_clear+=self.time_passed_seconds
        if self.time_since_last_text_clear>self.text_queue_clear_rate:
            self.time_since_last_text_clear=0
            if len(self.text_queue)>0:
                self.text_queue.pop(0)



#------------------------------------------------------------------------------
    def update_render_info(self):
        '''
            -checks if world objects are within the viewable
             screen area, and if so, translates their world coordinates
             to screen coordinates
        '''
        # note - i wonder if computing this is slower than just rendering everything
        # should add an ability to toggle this once i get a FPS count setup

        viewrange_x=((self.world.player.world_coords[0]+
            self.screen_size[0]+self.view_adjust), (self.world.player.world_coords[0]-
            self.screen_size[0]-self.view_adjust))
        viewrange_y=((self.world.player.world_coords[1]+
            self.screen_size[1]+self.view_adjust), (self.world.player.world_coords[1]-
            self.screen_size[1])-self.view_adjust)

        #clear out the render levels
        self.renderlists=[[] for _ in range(self.render_level_count)]

        translation=self.get_translation()

        self.renderCount=0
        for b in self.world.wo_objects:

            if b.render:
                
                # check if the relative scale of the object is enough to make it visible
                if (self.scale+b.scale_modifier)>self.minimum_visible_scale:

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

                            b.screen_coords[0]=(b.world_coords[0]*self.scale+translation[0])
                            b.screen_coords[1]=(b.world_coords[1]*self.scale+translation[1])

                            # honestly can't tell if this is better or not
                            if self.smooth_jitter:
                                b.screen_coords=[int(b.screen_coords[0]),int(b.screen_coords[1])]

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
    def get_rotated_scaled_image(self, image, IMAGE_SIZE, angle):
        """
        rotate an image while keeping its center and size
        image must be square
        adapted from : http://pygame.org/wiki/RotateCenter?parent=

        new : also scale image

        note : this method can cause the corners of images to be clipped
         this is a result of using subsurface

        """
        # not sure if i should rotate or resize first

        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        resize_image=pygame.transform.scale(rot_image,IMAGE_SIZE)
        return resize_image
    
#------------------------------------------------------------------------------
    def get_rotated_scaled_image_v2(self, image, scale, angle):
        """
        this doesn't work but should. the image grows and shrinks as it rotates
        """
        padding = max(image.get_width(), image.get_height())
        padded_surface = pygame.Surface((padding*2, padding*2), pygame.SRCALPHA)

        # Blit the original surface onto the padded surface with an offset
        offset = ((padding*2 - image.get_width()) // 2, (padding*2 - image.get_height()) // 2)
        padded_surface.blit(image, offset)

        # Rotate the padded surface
        rotated_surface = pygame.transform.rotate(padded_surface, angle)

        # Scale the image
        scaled_image = pygame.transform.scale(rotated_surface, (int(image.get_width() * scale), int(image.get_height() * scale)))
        return scaled_image
#------------------------------------------------------------------------------
    def get_translation(self):
        ''' returns the translation for world to screen coords '''
        center_x=self.screen_size[0]/2
        center_y=self.screen_size[1]/2
        player_x=self.world.player.world_coords[0]*self.scale
        player_y=self.world.player.world_coords[1]*self.scale
        
        translate=[center_x-player_x,center_y-player_y]
        return translate

#------------------------------------------------------------------------------
    def zoom_out(self):
        '''zoom out'''
        if self.scale>0.2:
            self.scale=round(self.scale-0.1,1)
            self.view_adjust+=500
            print('zoom out',self.scale)
            self.reset_all()
#------------------------------------------------------------------------------
    def zoom_in(self):
        ''' zoom in'''
        if self.scale<1.1:
            self.scale=round(self.scale+0.1,1)
            self.view_adjust-=500
            print('zoom in',self.scale)
            self.reset_all()


