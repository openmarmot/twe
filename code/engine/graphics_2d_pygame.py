
'''
module : module_template.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
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
module_last_update_date='April 10 2021' #date of last update

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

        # draw collision circles
        self.draw_collision=False

        # will cause everything to exit
        self.quit=False


        # max_fps max frames for every second.
        self.max_fps=40

#------------------------------------------------------------------------------
    def handleInput(self):

        # usefull for single button presses where you don't 
        # need to know if the button is still pressed
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                #pygame.quit()
                self.quit=True
            if event.type==pygame.KEYDOWN:
                print(str(event.key))
                # send number events to world_menu for ingame menus 
                # translate to a string corresponding to the actual key to simplify the code
                # on the other end
                # tilde
                if event.key==96:
                    self.text_queue.insert(0,('player world coords : '+str(self.world.player.world_coords)))
                    self.text_queue.insert(0,('player screen coords : '+str(self.world.player.screen_coords)))
                    self.text_queue.insert(0,('mouse screen coords : '+ str(pygame.mouse.get_pos())))
                    self.world.world_menu.handle_input("tilde")
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
                    b=self.selectFromScreen(15)
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
        # not sure whether this works great or not
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
                x, y = c.screen_coords
            #    print(str(c.rotation_angle))
                #this calculation would be better done in the world object
                #and probably only done once
                w, h = self.images[c.image_list[c.image_index]].get_size()
                self.screen.blit(self.get_rotated_image(self.images[c.image_list[c.image_index]],c.rotation_angle), (x-w/2, y-h/2))
                #print('rendering : '+c.name+' coords : '+str(c.screen_coords))
                #do any special rendering for the object
                c.render_pass_2()

                if(self.draw_collision):
                    pygame.draw.circle(self.screen,(236,64,122),c.screen_coords,c.collision_radius)


        # text stuff 
        self.h=0
        for b in islice(self.text_queue,3):
            self.h+=13
            self.small_font.render_to(self.screen, (40, self.h), b, (0, 0, 255))

        self.h+=20
        for b in self.menu_text_queue:
            self.h+=15
            self.small_font.render_to(self.screen, (40, self.h), b, (0, 0, 255))

        if(self.debug_mode):
            self.h=0
            for b in self.debug_text_queue:
                self.h+=15
                self.small_font.render_to(self.screen, (540, self.h), b, (0, 0, 255))

        pygame.display.update()


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

        viewrange_x=(self.world.player.world_coords[0]+
            self.screen_size[0], self.world.player.world_coords[0]-
            self.screen_size[0])
        viewrange_y=(self.world.player.world_coords[1]+
            self.screen_size[1], self.world.player.world_coords[1]-
            self.screen_size[1])

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
                    b.screen_coords[0]=b.world_coords[0]+translation[0]
                    b.screen_coords[1]=b.world_coords[1]+translation[1]

#------------------------------------------------------------------------------
    def get_mouse_screen_coords(self):
        return pygame.mouse.get_pos()

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
    def get_rotated_image(self, image, angle):
        """
        rotate an image while keeping its center and size
        image must be square
        adapted from : http://pygame.org/wiki/RotateCenter?parent=
        """
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image
#------------------------------------------------------------------------------
    def get_translation(self):
        ''' returns the translation for world to screen coords '''
        center_x=self.screen_size[0]/2
        center_y=self.screen_size[1]/2
        player_x=self.world.player.world_coords[0]
        player_y=self.world.player.world_coords[1]
        translate=[center_x-player_x,center_y-player_y]

        return translate
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
    def selectFromScreen(self, radius):
        '''
        return a object that is 'under' the mouse cursor
        radius is actually the side of a square. kind of. >100 works best
        '''
        x,y=pygame.mouse.get_pos()
        collided=None
        # just checking the 'object lying on ground' render level for now
        for b in self.renderlists[2]:
            if x+radius > b.screen_coords[0]:
                if x < b.screen_coords[0]+b.collision_radius:
                    if y+radius > b.screen_coords[1]:
                        if y < b.screen_coords[1]+b.collision_radius:
                            collided=b
                            break
        return collided
