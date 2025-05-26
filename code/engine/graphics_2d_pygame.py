
'''
repo : https://github.com/openmarmot/twe
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
from datetime import datetime
import time


# import pip packages
import pygame
from pygame.locals import *
import pygame.freetype

#import custom packages
import engine.math_2d
from engine.game_menu import GameMenu
from engine.world import World
from engine.strategic_map import StrategicMap
from engine.vehicle_diagnostics import VehicleDiagnostics
import engine.log

class Graphics_2D_Pygame(object):
    ''' 2D Graphics Engine using PyGame '''

    def __init__(self,screen_size):
        # called by World.__init__

        self.images={}
        self.image_cache={}

        self.screen_size=screen_size
        self.screen_center=[self.screen_size[0]/2,self.screen_size[1]/2]
        pygame.init()
        pygame.display.set_caption("https://github.com/openmarmot/twe")

        # this seems to significantly improve visual quality when on
        self.double_buffering=True
        if self.double_buffering:
            self.screen = pygame.display.set_mode(self.screen_size, pygame.DOUBLEBUF, 32)
        else:
            self.screen=pygame.display.set_mode(self.screen_size,0,32)
        
        self.background = pygame.surface.Surface(self.screen_size).convert()
        self.background.fill((255, 255, 255))

        self.screenshot_folder=f"game_screenshots/{datetime.now().strftime('%Y_%m_%d_%H%M%S')}"
        os.makedirs(self.screenshot_folder, exist_ok=True)

        self.aar_screenshot_interval=10
        self.last_aar_screenshot_time=0

        self.mode=0
        # 0 - game menu
        # 1 - world 
        # 2 - strategic_map

        self.game_menu=GameMenu(self)
        self.world=World()
        self.strategic_map=StrategicMap(self)
        self.vehicle_diagnostics=VehicleDiagnostics()


        # render level kind of a 'z' layer
        # 0 - ground cover
        # 1 - man made ground cover (cement, building insides)
        # 2 - objects laying on the ground (weapons,etc)
        # 3 - objects slightly elevated above ground (vehicles, animals??)
        # 4 - vehicle turrets
        # 5 - humans
        # 6 - roofs (custom building ai)
        # 7 - objects above ground (birds, planes, clouds, etc)
        
        self.render_level_count=10
        self.renderlists=[[] for _ in range(self.render_level_count)]

        # count of rendered objects
        self.render_count=0

        # time stuff
        self.clock=pygame.time.Clock()
        self.time_passed=None
        self.time_passed_seconds=None

        # text stuff
        # Different text sizes for in menus
        self.small_font = pygame.freetype.SysFont(pygame.font.get_default_font(), 12)
        self.medium_font = pygame.freetype.SysFont(pygame.font.get_default_font(), 18)
        self.large_font = pygame.freetype.SysFont(pygame.font.get_default_font(), 30)

        self.menu_color='#ffffff'
        self.color_black='#000000'

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

        # -- key stuff --
        # https://www.pygame.org/docs/ref/key.html
        # continuous
        self.key_press_actions = {
            pygame.K_w: lambda: self.world.handle_key_press('w'),
            pygame.K_s: lambda: self.world.handle_key_press('s'),
            pygame.K_a: lambda: self.world.handle_key_press('a'),
            pygame.K_d: lambda: self.world.handle_key_press('d'),
            pygame.K_f: lambda: self.world.handle_key_press('f', self.get_mouse_screen_coords()),
            pygame.K_g: lambda: self.world.handle_key_press('g', self.get_mouse_screen_coords()),
            pygame.K_t: lambda: self.world.handle_key_press('t', self.get_mouse_screen_coords()),
            pygame.K_b: lambda: self.world.handle_key_press('b'),
            pygame.K_p: lambda: self.world.handle_key_press('p'),
            pygame.K_UP: lambda: self.world.handle_key_press('up'),
            pygame.K_DOWN: lambda: self.world.handle_key_press('down'),
            pygame.K_LEFT: lambda: self.world.handle_key_press('left'),
            pygame.K_RIGHT: lambda: self.world.handle_key_press('right'),
        }

        # one time
        self.key_down_translations = {
            pygame.K_BACKQUOTE: "tilde",
            pygame.K_0: "0",
            pygame.K_1: "1",
            pygame.K_2: "2",
            pygame.K_3: "3",
            pygame.K_4: "4",
            pygame.K_5: "5",
            pygame.K_6: "6",
            pygame.K_7: "7",
            pygame.K_8: "8",
            pygame.K_9: "9",
            pygame.K_ESCAPE: "esc",
            pygame.K_TAB: 'tab',
            pygame.K_p: 'p',
            pygame.K_t: 't',
            pygame.K_g: 'g',
            pygame.K_r: 'r',
            pygame.K_MINUS: '-',
            pygame.K_EQUALS: '+',
            pygame.K_z: 'z',
            pygame.K_x: 'x',
            pygame.K_LEFTBRACKET: '[',
            pygame.K_RIGHTBRACKET: ']',
            pygame.K_SPACE: 'space',
            pygame.K_LCTRL: 'l_ctrl'
        }


        # load all images
        self.load_all_images('images')

    #------------------------------------------------------------------------------
    def create_screenshot(self):
        pygame.image.save(self.screen, f"{self.screenshot_folder}/twe-{round(self.world.world_seconds,2)}.png")

    #------------------------------------------------------------------------------
    def get_mouse_screen_coords(self):
        '''return mouse screen coordinates'''
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
        return self.screen_center
    
    #------------------------------------------------------------------------------
    def get_translation(self):
        ''' returns the translation for world to screen coords '''
        player_x=self.world.player.world_coords[0]*self.scale
        player_y=self.world.player.world_coords[1]*self.scale
        
        self.world.player.screen_coords=self.screen_center

        translate=[self.screen_center[0]-player_x,self.screen_center[1]-player_y]
        return translate

    #------------------------------------------------------------------------------
    def handle_input(self):
        ''' handle input from user'''

        # usefull for single button presses where you don't 
        # need to know if the button is still pressed
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                #pygame.quit()
                self.quit=True
            if event.type==pygame.KEYDOWN:
                #print(event.key)
                translated_key=self.key_down_translations.get(event.key,'none')

                if self.mode==0:
                    self.game_menu.handle_input(translated_key)
                elif self.mode==1:
                    if translated_key=='[':
                        self.zoom_out()
                    elif translated_key==']':
                        self.zoom_in()
                    elif translated_key=='l_ctrl':
                        self.create_screenshot()
                    else:
                        self.world.handle_keydown(translated_key,self.get_mouse_screen_coords())
                elif self.mode==2:
                    self.strategic_map.handle_keydown(translated_key)
                elif self.mode==3:
                    self.vehicle_diagnostics.handle_keydown(translated_key)
                else:
                    engine.log.add_data('error','graphics_2d_pygame.handle_input graphic_engine.mode unknown '+str(self.mode),True)

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
        
        # handle key press (continuous input)
        # i think more than one can be down at once, that is why we don't do if/elif
        if self.mode==1:
            keys = pygame.key.get_pressed()
            
            for key, action in self.key_press_actions.items():
                if keys[key]:
                    action()

    #------------------------------------------------------------------------------
    def load_all_images(self,folder_path):
        '''load all the images into pygame'''
        try:
            for filename in os.listdir(folder_path):
                filepath = os.path.join(folder_path, filename)
                if os.path.isfile(filepath):
                    name, ext = os.path.splitext(filename)
                    # just loading png for now, but could add other formats later
                    if ext.lower() in ['.png']:
                        self.images[name] = pygame.image.load(filepath).convert_alpha()
            print('Image loading complete')
        except Exception as e:
            engine.log.add_data('error', f'Failed to load images: {e}', True)


    #------------------------------------------------------------------------------
    def render(self):

        if self.mode==0:
            self.render_mode_0()
        elif self.mode==1:
            self.render_mode_1()
        elif self.mode==2:
            self.render_mode_2()
        elif self.mode==3:
            self.render_mode_3()

    #------------------------------------------------------------------------------
    def render_mode_0(self):
        '''render mode 0 : main game menu'''
        self.screen.blit(self.background, (0, 0))
        h=0
        for b in self.game_menu.text_queue:
            h+=15
            self.small_font.render_to(self.screen, (40, h), b, self.color_black)

        if self.double_buffering:
            pygame.display.flip()
        else:
            pygame.display.update()
    #------------------------------------------------------------------------------
    def render_mode_1(self):
        '''render mode 1 : tactical mode'''

        self.update_render_info_new()

        self.screen.blit(self.background, (0, 0))
        for b in self.renderlists:
            for c in b:
                if c.reset_image:
                    self.reset_pygame_image(c)
                self.screen.blit(c.image, (c.screen_coords[0]-c.image_center[0], c.screen_coords[1]-c.image_center[1]))

                if self.draw_collision:
                    pygame.draw.circle(self.screen,(236,64,122),c.screen_coords,c.collision_radius*self.scale)

        h=0
        for b in islice(self.world.text_queue,self.world.text_queue_display_size):
            h+=15
            self.small_font.render_to(self.screen, (40, h), b, self.menu_color)

        h+=20
        for b in self.world.world_menu.text_queue:
            h+=15
            self.small_font.render_to(self.screen, (40, h), b, self.menu_color)

        if self.world.debug_mode :
            h=0
            for b in self.world.debug_text_queue:
                h+=15
                self.small_font.render_to(self.screen, (900, h), b,self.menu_color )

        if self.world.display_vehicle_text :
            h=0
            for b in self.world.vehicle_text_queue:
                h+=15
                self.small_font.render_to(self.screen, (500, h), b, self.menu_color)

        # might consider moving this to world and just returning a array of circles to draw
        if self.world.display_weapon_range:
            if self.world.player.ai.memory['current_task']=='task_vehicle_crew':
                vehicle=self.world.player.ai.memory['task_vehicle_crew']['vehicle']
                for turret in vehicle.ai.turrets:
                    if turret.ai.primary_weapon is not None:
                        radius=turret.ai.primary_weapon.ai.range*self.scale
                        pygame.draw.circle(self.screen,(236,64,122),turret.screen_coords,radius,width=5)
            else:
                if self.world.player.ai.primary_weapon is not None:
                    radius=self.world.player.ai.primary_weapon.ai.range*self.scale
                    pygame.draw.circle(self.screen,(236,64,122),self.world.player.screen_coords,radius,width=5)

                if self.world.player.ai.antitank is not None:
                    radius=self.world.player.ai.antitank.ai.range*self.scale
                    pygame.draw.circle(self.screen,(236,64,50),self.world.player.screen_coords,radius,width=5)

        if self.double_buffering:
            pygame.display.flip()
        else:
            pygame.display.update()

    #------------------------------------------------------------------------------
    def render_mode_2(self):
        '''render mode 3 : strategic mode'''


        self.screen.blit(self.background, (0, 0))
        for c in self.strategic_map.map_squares:
            if c.reset_image:
                self.reset_pygame_image(c)
            self.screen.blit(c.image, (c.screen_coords[0]-c.image_center[0], c.screen_coords[1]-c.image_center[1]))

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

        h=0
        for b in self.strategic_map.strategic_menu.text_queue:
            h+=15
            self.small_font.render_to(self.screen, (40, h), b, self.color_black)

        if self.double_buffering:
            pygame.display.flip()
        else:
            pygame.display.update()

    #------------------------------------------------------------------------------
    def render_mode_3(self):
        '''render mode 4 : vehicle diagnostic overlay'''
        self.screen.blit(self.background, (0, 0))
        for c in self.vehicle_diagnostics.image_objects:
            if c.reset_image:
                self.reset_pygame_image(c)
            self.screen.blit(c.image, (c.screen_coords[0]-c.image_center[0], c.screen_coords[1]-c.image_center[1]))

        for text in self.vehicle_diagnostics.text_queue:
            self.small_font.render_to(self.screen, text[1], text[0],text[2] )

        if self.double_buffering:
            pygame.display.flip()
        else:
            pygame.display.update()

    #------------------------------------------------------------------------------
    def reset_pygame_image(self, wo):
        '''Reset the image for a world object with caching'''
        wo.reset_image = False
        obj_scale = self.scale + wo.scale_modifier
        wo.image_size = (
            int(self.images[wo.image_list[wo.image_index]].get_width() * obj_scale),
            int(self.images[wo.image_list[wo.image_index]].get_height() * obj_scale)
        )
        wo.image_center=[round(wo.image_size[0]*0.5,1),round(wo.image_size[1]*0.5,1)]

        # Create a unique key based on image name, size, and rotation
        key = f"{wo.image_list[wo.image_index]}_{wo.image_size}_{round(wo.rotation_angle, 1)}"
        
        # Check if the image is already cached
        scale_cache = self.image_cache.setdefault(self.scale, {})
        if key in scale_cache:
            wo.image = scale_cache[key]
            return

        try:
            image=self.images[wo.image_list[wo.image_index]]
            orig_rect = image.get_rect()
            rot_image = pygame.transform.rotate(image, wo.rotation_angle)
            rot_rect = orig_rect.copy()
            rot_rect.center = rot_image.get_rect().center
            rot_image = rot_image.subsurface(rot_rect).copy()
            resize_image=pygame.transform.scale(rot_image,wo.image_size)
            wo.image=resize_image
            scale_cache[key] = resize_image
        except KeyError:
            engine.log.add_data(
                'error',
                f'graphics_2d_pygame.reset_pygame_image: image transform error with image {wo.image_list[wo.image_index]}',
                True
            )

    #------------------------------------------------------------------------------
    def reset_all(self):
        ''' resize all world_objects'''
        for b in self.world.wo_objects:
            b.reset_image=True

    #---------------------------------------------------------------------------
    def select_closest_object_with_mouse(self,mouse_coords):
        possible_objects=[]

        if self.mode==1:
            # sort through the objects that are rendered (visible)
            for b in self.renderlists:
                for c in b:
                    # filter out a couple things we don't want to click on
                    if (c.is_player is False 
                        and c != self.world.player.ai.large_pickup 
                        and c.is_turret is False 
                        and c.can_be_deleted is False
                        and c.is_ground_texture is False):
                        possible_objects.append(c)
        elif self.mode==2:
            # for strategic map we want everything
            possible_objects=self.strategic_map.map_squares

        object_distance=50
        closest_object=None

        for b in possible_objects:
            distance=engine.math_2d.get_distance(mouse_coords,b.screen_coords)
            if distance<object_distance:
                object_distance=distance
                closest_object=b
        
        if closest_object is not None:
            #engine.log.add_data('debug','mouse distance: '+str(object_distance),True)
            #engine.log.add_data('debug','mouse select: '+closest_object.name,True)

            if self.mode==0:
                pass
            elif self.mode==1:
                self.world.world_menu.activate_menu(closest_object)
            elif self.mode==2:
                self.strategic_map.strategic_menu.activate_menu(closest_object)

    #------------------------------------------------------------------------------
    def switch_mode(self,desired_mode):
        '''switch the graphic engine mode '''

        # reset scale to defaults
        self.scale=self.scale_limit[1]
        self.view_adjust=self.view_adjust_minimum
        self.reset_all()
        
        # main menu
        if desired_mode==0:
            self.mode=0
            self.background.fill((255, 255, 255))
        # tactical battle
        elif desired_mode==1:
            self.mode=1
            # this one has great constrast with the sprites
            # bullets are very visible
            self.background.fill((128, 102, 77))

            #self.background.fill((201,184,171))
            #self.background.fill((171,149,131))
        # strategic screen
        elif desired_mode==2:
            self.mode=2
            self.background.fill((255, 255, 255))
        # vehicle info
        elif desired_mode==3:
            self.mode=3
            self.background.fill((255, 255, 255))
        else:
            engine.log.add_data('Error','graphic_engine.switch_mode mode not recognized: '+str(desired_mode),True)


    #------------------------------------------------------------------------------
    def update(self):
        '''
            any misc updating that needs to be done
        '''
        self.handle_input()

        # update time
        self.time_passed=self.clock.tick(self.max_fps)
        self.time_passed_seconds=self.time_passed / 1000.0

        if self.mode==0:
            pass
            #self.game_menu.update(self.time_passed_seconds)
        elif self.mode==1:
            self.world.update(self.time_passed_seconds)

            if self.world.aar_mode_enabled:
                if self.world.world_seconds-self.last_aar_screenshot_time>self.aar_screenshot_interval:
                    self.last_aar_screenshot_time=self.world.world_seconds
                    self.create_screenshot()

            # insert graphic engine specific debug text (after world.update populated it)
            if self.world.debug_mode and self.world.is_paused==False:
                self.world.debug_text_queue.insert(0,'FPS: '+str(int(self.clock.get_fps())))
                self.world.debug_text_queue.insert(1,'World scale: '+str(self.scale))
                self.world.debug_text_queue.insert(2,'View Adjust: '+str(self.view_adjust))
                self.world.debug_text_queue.insert(3,'Rendered Objects: '+ str(self.render_count))

                
                # image cache debug info 
                #for key, value in self.image_cache.items():
                #    self.world.debug_text_queue.insert(4,f"Image cache {key} - size: {len(value)}")
            
            if self.world.exit_world:
                self.strategic_map.unload_world()
                self.switch_mode(2)

            if self.world.vehicle_diagnostics:
                self.world.vehicle_diagnostics=False
                self.vehicle_diagnostics.load(self.world.vehicle_diagnostics_vehicle,self.screen_center)
                self.switch_mode(3)

        elif self.mode==2:
            self.strategic_map.update()
        elif self.mode==3:
            self.vehicle_diagnostics.update()

            if self.vehicle_diagnostics.exit:
                self.vehicle_diagnostics.exit=False
                self.switch_mode(1)

            
    #------------------------------------------------------------------------------
    def update_render_info_new(self):
        '''
            checks if world objects are within the viewable screen area,
              and if so, translates their world coordinates to screen coordinates
              only used by tactical mode
        '''

        #clear out the render levels
        self.renderlists=[[] for _ in range(self.render_level_count)]

        self.render_count=0

        viewrange_x = (
            self.world.player.world_coords[0] + self.screen_size[0] + self.view_adjust,
            self.world.player.world_coords[0] - self.screen_size[0] - self.view_adjust
        )
        viewrange_y = (
            self.world.player.world_coords[1] + self.screen_size[1] + self.view_adjust,
            self.world.player.world_coords[1] - self.screen_size[1] - self.view_adjust
        )
        translation = self.get_translation()
        renderable_objects=[]

        # make a visibility determination per grid square. this worked well with grid square size set to 1000
        for grid_square in self.world.grid_manager.index_map.values():
            if (grid_square.top_left[0] < viewrange_x[0] and grid_square.bottom_right[0] > viewrange_x[1] and
                grid_square.top_left[1] < viewrange_y[0] and grid_square.bottom_right[1] > viewrange_y[1]):

                for obj in grid_square.wo_objects:
                    if (obj.render and (self.scale + obj.scale_modifier) >= obj.minimum_visible_scale ):
                        renderable_objects.append(obj)

        for obj in renderable_objects:
            self.renderlists[obj.render_level].append(obj)
            if not obj.is_player:
                obj.screen_coords[0] = obj.world_coords[0] * self.scale + translation[0]
                obj.screen_coords[1] = obj.world_coords[1] * self.scale + translation[1]
        
        self.render_count = len(renderable_objects)                

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


