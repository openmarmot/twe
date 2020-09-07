
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

 ref:
 # pygame.key.get_pressed() and general input theory
 https://stackoverflow.com/questions/17372314/is-it-me-or-is-pygame-key-get-pressed-not-working
'''


#import built in modules
import pygame
from pygame.locals import *
#import custom packages

# module specific variables
module_version='0.0' #module software version
module_last_update_date='Sept 06 2020' #date of last update

#global variables


class Graphics_2D_Pygame(object):
    ''' 2D Graphics Engine using PyGame '''

    def __init__(self,screen_size):
        self.images=dict()
        self.screen_size=screen_size
        pygame.init()
        self.screen=pygame.display.set_mode(self.screen_size,0,32)
        
        self.background = pygame.surface.Surface(self.screen_size).convert()
        self.background.fill((255, 255, 255))
        #pygame.draw.circle(self.background, (200, 255, 200), NEST_POSITION, int(NEST_SIZE))
        self.renderlists=[[],[],[]]
        self.world=None
        
        # time stuff
        self.clock=pygame.time.Clock()
        self.time_passed=None
        self.time_passed_seconds=None

        # will cause everything to exit
        self.quit=False

    def add_object(self,obj):
        self.renderlists[obj.render_level].append(obj)

    def remove_object(self,obj):
        self.renderlists[obj.render_level].remove(obj)

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
                
                #print(str(pygame.key.get_pressed()))
            if event.type==pygame.MOUSEBUTTONDOWN:
                if event.button==1:
                    print("left click!")
                if event.button==2:
                    print("some other mouse button?")
                if event.button==3:
                    print("right click!")
            if event.type==pygame.MOUSEMOTION:
                #print(str(event.pos))
                pass
        #print(self.keyPressed('w'))

#------------------------------------------------------------------------------
    def keyPressed(self, KEY):
        # returns bool as to whether keyPressed is KEY
        # not sure whether this works great or not

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
                w, h = self.images[c.image_name].get_size()
                self.screen.blit(self.get_rotated_image(self.images[c.image_name],c.rotation_angle), (x-w/2, y-h/2))
                #print('rendering : '+c.name+' coords : '+str(c.screen_coords))
                #do any special rendering for the object
                c.render_pass_2()

        pygame.display.update()


#------------------------------------------------------------------------------
    def update(self):
        '''
            any misc updating that needs to be done
        '''
        self.handleInput()

        # update time
        self.time_passed=self.clock.tick(30)
        self.time_passed_seconds=self.time_passed / 1000.0


#------------------------------------------------------------------------------
    def update_render_info(self):
        '''
            -checks if world objects are within the viewable
             screen area, and if so, translates their world coordinates
             to screen coordinates
        '''

        viewrange_x=(self.world.player.world_coords[0]+
            self.screen_size[0], self.world.player.world_coords[0]-
            self.screen_size[0])
        viewrange_y=(self.world.player.world_coords[1]+
            self.screen_size[1], self.world.player.world_coords[1]-
            self.screen_size[1])

        #clear out the render levels
        self.renderlists=[[],[],[]]
        translation=self.get_translation()
       # print(str(translation))
        for b in self.world.wo_objects:
            #determine whether object 'b' world_coords are within
            #the viewport bounding box
            if(b.world_coords[0]<viewrange_x[0] and
                b.world_coords[0]>viewrange_x[1]):
                if(b.world_coords[1]<viewrange_y[0] and
                    b.world_coords[1]>viewrange_y[1]):
                    #object is within the viewport, add it to the render list
                    self.renderlists[b.render_level].append(b)

                    #apply transform to generate screen coords
                    b.screen_coords[0]=b.world_coords[0]+translation[0]
                    b.screen_coords[1]=b.world_coords[1]+translation[1]

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
        #translate=[0.,0.]
        # if player_x<center_x:
        #     translate[0]=center_x-player_x
        # elif player_x>center_x:
        #     translate[0]=player_x-center_x
        # if player_y<center_y:
        #     translate[1]=center_y-player_y
        # elif player_y>center_y:
        #     translate[1]=player_y-center_y
        # print('translate '+str(translate))
        return translate
#------------------------------------------------------------------------------
