
'''
module : module_template.py
version : see module_version variable
Language : Python 3.x
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
#import custom packages

# module specific variables
module_version='0.0' #module software version
module_last_update_date='July 16 2021' #date of last update

#global variables


class Graphics_2D_Pygame(object):
    ''' 2D Graphics Engine using PyGame '''

    def __init__(self,Screen_size,World):
        # called by World.__init__

        self.images=dict()
        self.screen_size=Screen_size
        pygame.init()
        self.screen=pygame.display.set_mode(self.screen_size,0,32)
        
        self.background = pygame.surface.Surface(self.screen_size).convert()
        self.background.fill((255, 255, 255))
        
        # render level kind of a 'z' layer
        # 0 - ground cover
        # 1 - man made ground cover (cement, building insides)
        # 2 - objects laying on the ground (weapons,etc)
        # 3 - objects walking on the ground (humans, animals, vehicles)
        # 4 - objects above ground (birds, planes, clouds, etc)
        self.renderlists=[[],[],[],[],[]]

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

        # used for temporary text. max 3 lines displayed
        # used like this : self.text_queue.insert(0,('player world coords : '+str(self.world.player.world_coords)))
        self.text_queue=[]

        # used for the menu system. no limits enforced by this class
        self.menu_text_queue=[]

        # debug info queue
        self.debug_mode=True
        self.debug_text_queue=[]

        # vehicle text 
        self.display_vehicle_text=False
        self.vehicle_text_queue=[]

        # draw collision circles
        self.draw_collision=False

        # will cause everything to exit
        self.quit=False


        # max_fps max frames for every second.
        self.max_fps=40

        # scale. normal is 1
        self.scale=1

        # adjustment to viewing area
        self.view_adjust=0

#------------------------------------------------------------------------------
    def handleInput(self):

        # usefull for single button presses where you don't 
        # need to know if the button is still pressed
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                #pygame.quit()
                self.quit=True
            if event.type==pygame.KEYDOWN:
                #print(str(event.key))
                # send number events to world_menu for ingame menus 
                # translate to a string corresponding to the actual key to simplify the code
                # on the other end
                # tilde
                if event.key==96:
                    self.world.world_menu.handle_input("tilde")
                elif event.key==91: # [
                    self.scale-=0.1
                    self.view_adjust+=500
                    print('scale down')
                    self.reset_all()
                elif event.key==93: # ]
                    self.scale+=0.1
                    self.view_adjust-=500
                    print('scale up')
                    self.reset_all()
                elif event.key==48:
                    self.world.world_menu.handle_input("0")
                elif event.key==49:
                    self.world.world_menu.handle_input("1")
                elif event.key==50:
                    self.world.world_menu.handle_input("2")
                elif event.key==51:
                    self.world.world_menu.handle_input("3")
                elif event.key==52:
                    self.world.world_menu.handle_input("4")
                elif event.key==53:
                    self.world.world_menu.handle_input("5")
                elif event.key==54:
                    self.world.world_menu.handle_input("6")
                elif event.key==55:
                    self.world.world_menu.handle_input("7")
                elif event.key==56:
                    self.world.world_menu.handle_input("8")
                elif event.key==57:
                    self.world.world_menu.handle_input("9")
                elif event.key==27:
                    self.world.world_menu.handle_input("esc")
                    

            if event.type==pygame.MOUSEBUTTONDOWN:
                # left click
                if event.button==1:
                    b=self.world.select_with_mouse(10)
                    if b!=None:
                        print(b.name)
                        # send it over to world menu to figure out
                        self.world.world_menu.activate_menu(b)
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
        else:
            return False

#------------------------------------------------------------------------------
    def loadImage(self,imageName,imageURL):
        self.images[imageName]=pygame.image.load(imageURL).convert_alpha()


#------------------------------------------------------------------------------
    def render(self):
        self.update_render_info()

        self.screen.blit(self.background, (0, 0))
        for b in self.renderlists:
            for c in b:
                if c.reset_image:
                    c.reset_image=False
                    c.image_size=self.images[c.image_list[c.image_index]].get_size()
                    c.image_size=[int(c.image_size[0]*self.scale),int(c.image_size[1]*self.scale)]
                    c.image=self.get_rotated_scaled_image(self.images[c.image_list[c.image_index]],c.image_size,c.rotation_angle)
                self.screen.blit(c.image, (c.screen_coords[0]-c.image_size[0]/2, c.screen_coords[1]-c.image_size[1]/2))

                c.render_pass_2()

                if(self.draw_collision):
                    pygame.draw.circle(self.screen,(236,64,122),c.screen_coords,c.collision_radius)


        # text stuff 
        self.h=0
        for b in islice(self.text_queue,3):
            self.h+=15
            self.small_font.render_to(self.screen, (40, self.h), b, (255, 51, 51))

        self.h+=20
        for b in self.menu_text_queue:
            self.h+=15
            self.small_font.render_to(self.screen, (40, self.h), b, (255, 51, 51))

        if(self.debug_mode):
            self.h=0
            for b in self.debug_text_queue:
                self.h+=15
                self.small_font.render_to(self.screen, (540, self.h), b, (255, 51, 51))

        if(self.display_vehicle_text):
            self.h=0
            for b in self.vehicle_text_queue:
                self.h+=15
                self.small_font.render_to(self.screen, (300, self.h), b, (255, 51, 51))

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

        if(self.debug_mode):
            self.update_debug_info()


        # update time
        self.time_passed=self.clock.tick(self.max_fps)
        self.time_passed_seconds=self.time_passed / 1000.0

#------------------------------------------------------------------------------
    def update_debug_info(self):
        self.debug_text_queue=[]
        self.debug_text_queue.append('FPS: '+str(int(self.clock.get_fps())))
        self.debug_text_queue.append('World Objects: '+ str(len(self.world.wo_objects)))
        self.debug_text_queue.append('Rendered Objects: '+ str(self.renderCount))
        self.debug_text_queue.append('Germans: '+ str(len(self.world.wo_objects_german)))
        self.debug_text_queue.append('Soviets: '+ str(len(self.world.wo_objects_soviet)))
        self.debug_text_queue.append('Americans: '+ str(len(self.world.wo_objects_american)))
        self.debug_text_queue.append('Player World Coords: '+str(self.world.player.world_coords))

        # world area data
        for b in self.world.world_areas:
            self.debug_text_queue.append('Area '+b.name+' is controlled by : '+b.faction)

#------------------------------------------------------------------------------
    def update_render_info(self):
        '''
            -checks if world objects are within the viewable
             screen area, and if so, translates their world coordinates
             to screen coordinates
        '''
        # note - i wonder if computing this is slower than just rendering everything
        # should add an ability to toggle this once i get a FPS count setup

        # note - this does not check world_object.render bool but maybe it should

        viewrange_x=((self.world.player.world_coords[0]+
            self.screen_size[0]+self.view_adjust), (self.world.player.world_coords[0]-
            self.screen_size[0]-self.view_adjust))
        viewrange_y=((self.world.player.world_coords[1]+
            self.screen_size[1]+self.view_adjust), (self.world.player.world_coords[1]-
            self.screen_size[1])-self.view_adjust)

        #clear out the render levels
        self.renderlists=[[],[],[],[],[]]
        translation=self.get_translation()

        self.renderCount=0
        for b in self.world.wo_objects:
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
    def get_translation(self):
        ''' returns the translation for world to screen coords '''
        center_x=self.screen_size[0]/2
        center_y=self.screen_size[1]/2
        player_x=self.world.player.world_coords[0]*self.scale
        player_y=self.world.player.world_coords[1]*self.scale
        translate=[center_x-player_x,center_y-player_y]
        return translate
#------------------------------------------------------------------------------


