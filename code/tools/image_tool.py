'''
repo : https://github.com/openmarmot/twe

notes :
A special tool for working with images.

Load an object definition and place its sprites using the currently
defined offsets (image_rotation_offset, turret/rotor position_offset,
visible seat_offset, bounding_circles).

Usage (from code/tools, code/, or the repo root):
    python image_tool.py german_stug_iii_ausf_g
    python image_tool.py path/to/object_def.py
'''


# import built in modules
import math
import os
import re
import sys

# import pip packages
import pygame
import pygame.freetype


REGISTER_RE = re.compile(r'@register_object\(\s*["\']([^"\']+)["\']\s*\)')


class DummyWorld():
    '''minimal world so object_def create() can spawn nested objects'''

    def __init__(self):
        self.add_queue=[]
        self.remove_queue=[]
        self.world_seconds=0
        self.time_passed_seconds=0


class ImageTool():
    ''' 2D Graphics Engine using PyGame '''

    def __init__(self,screen_size):
        # called by World.__init__


        self.image_objects=[]
        self.selected_object=None
        self.selection_index=0
        self.base_object=None

        self.object_type=''
        self.object_name=''

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
        self.draw_collision=True
        self.collision_radius=50

        # draw alignment lines (new)
        self.draw_alignment_lines=True

        # click sets image_rotation_offset instead of moving the object
        self.pivot_set_mode=False

        # bounding-circle sprites can be hidden without dropping them from the list
        self.show_bound_circles=True

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
    def add_image_object(self,image_list,kind,label,world_coords,rotation_angle=0,
            image_rotation_offset=None,offset_parent=None,bound_radius=None,
            role_name=None,def_position_offset=None):
        '''create an ImageObject, append it, and return it'''
        obj=ImageObject(image_list,rotation_angle)
        obj.kind=kind
        obj.label=label
        obj.world_coords=[world_coords[0],world_coords[1]]
        if image_rotation_offset is not None:
            obj.image_rotation_offset=[image_rotation_offset[0],image_rotation_offset[1]]
        obj.offset_parent=offset_parent
        obj.bound_radius=bound_radius
        obj.role_name=role_name
        if def_position_offset is not None:
            obj.def_position_offset=[def_position_offset[0],def_position_offset[1]]
        self.image_objects.append(obj)
        return obj

    #------------------------------------------------------------------------------
    def cycle_selected_image(self):
        '''cycle image_index for buildings / humans with multiple sprites'''
        obj=self.selected_object
        if obj is None or len(obj.image_list)<2:
            return
        obj.image_index=(obj.image_index+1)%len(obj.image_list)
        print('image',obj.image_list[obj.image_index])

    #------------------------------------------------------------------------------
    def crew_image_name(self,object_type):
        '''soldier sprite used as a visible-seat marker'''
        name='german_soldier'
        if object_type.startswith('soviet') or '_soviet' in object_type:
            name='soviet_soldier'
        elif object_type.startswith('civilian') or 'civilian' in object_type:
            name='civilian_man'
        if name not in self.images:
            if 'german_soldier' in self.images:
                return 'german_soldier'
        return name

    #------------------------------------------------------------------------------
    def ensure_bound_circle_image(self,radius):
        '''return an image key for a bounding circle of this radius'''
        radius=int(radius)
        name='bound_circle_r'+str(radius)
        if name in self.images:
            return name
        size=max(int(radius*2)+4,8)
        if size%2==1:
            size+=1
        surf=pygame.Surface((size,size),pygame.SRCALPHA)
        pygame.draw.circle(surf,(220,20,60,220),(size//2,size//2),radius,1)
        self.images[name]=surf
        return name

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
                if event.key==114: #r
                    if self.selected_object!=None:
                        self.selected_object.rotation_angle+=90
                        self.selected_object.rotation_angle=self.selected_object.rotation_angle % 360

                if event.key==113: #q
                    self.select_adjacent(-1)

                if event.key==101: #e
                    self.select_adjacent(1)


                if event.key==49: #1
                    self.print_offsets()

                if event.key==99: #c
                    self.pivot_set_mode=not self.pivot_set_mode

                if event.key==120: #x
                    self.reset_selected_pivot()

                if event.key==105: #i
                    self.cycle_selected_image()

                if event.key==98: #b
                    self.show_bound_circles=not self.show_bound_circles
                    print('bound circles',self.show_bound_circles)

                if event.key==108: #l
                    self.draw_alignment_lines=not self.draw_alignment_lines

                if event.key==102: #f
                    self.draw_collision=not self.draw_collision

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
        skip_dirs={'__pycache__','gimp','paint_net','diagrams'}
        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
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
    def load_object_def(self,object_type):
        '''spawn an object_def and place its images using current values'''
        import engine.world_builder

        world=DummyWorld()
        wo=engine.world_builder.spawn_object(world,[0.0,0.0],object_type,False)
        if wo is None:
            print('error','spawn_object returned None for '+object_type)
            return False

        # defs often randomize facing. alignment work is done at rotation 0
        wo.rotation_angle=0

        self.object_type=object_type
        self.object_name=wo.name or object_type
        self.collision_radius=wo.collision_radius
        pygame.display.set_caption('TWE Image Tool - '+self.object_name)

        used_labels=set()

        base=self.add_image_object(
            list(wo.image_list),
            'base',
            self.unique_label(self.object_name,used_labels),
            [0.0,0.0],
            image_rotation_offset=wo.image_rotation_offset,
            def_position_offset=getattr(wo.ai,'position_offset',None),
        )
        self.base_object=base
        self.warn_missing_images(base)

        turret_map={}
        if hasattr(wo.ai,'turrets'):
            for turret in wo.ai.turrets:
                offset=getattr(turret.ai,'position_offset',[0,0])
                label=self.unique_label(turret.name or turret.image_list[0],used_labels)
                img=self.add_image_object(
                    list(turret.image_list),
                    'turret',
                    label,
                    self.offset_to_world(base,offset),
                    image_rotation_offset=turret.image_rotation_offset,
                    offset_parent=base,
                    def_position_offset=offset,
                )
                turret_map[turret]=img
                self.warn_missing_images(img)

        if hasattr(wo.ai,'rotors'):
            for rotor in wo.ai.rotors:
                offset=getattr(rotor.ai,'position_offset',[0,0])
                label=self.unique_label(rotor.name or rotor.image_list[0],used_labels)
                img=self.add_image_object(
                    list(rotor.image_list),
                    'rotor',
                    label,
                    self.offset_to_world(base,offset),
                    image_rotation_offset=rotor.image_rotation_offset,
                    offset_parent=base,
                    def_position_offset=offset,
                )
                self.warn_missing_images(img)

        if hasattr(wo.ai,'vehicle_crew'):
            crew_image=self.crew_image_name(object_type)
            for role in wo.ai.vehicle_crew:
                if not role.seat_visible:
                    continue
                parent=base
                if role.seat_rotates_with_turret and role.turret is not None:
                    parent=turret_map.get(role.turret,base)
                label=self.unique_label('crew '+role.role_name,used_labels)
                self.add_image_object(
                    [crew_image],
                    'crew',
                    label,
                    self.offset_to_world(parent,role.seat_offset),
                    rotation_angle=role.seat_rotation,
                    offset_parent=parent,
                    role_name=role.role_name,
                )

        for circle in wo.bounding_circles:
            offset=circle[0]
            radius=circle[1]
            image_name=self.ensure_bound_circle_image(radius)
            label=self.unique_label('bound r'+str(int(radius)),used_labels)
            self.add_image_object(
                [image_name],
                'bound_circle',
                label,
                self.offset_to_world(base,offset),
                offset_parent=base,
                bound_radius=radius,
            )

        if self.image_objects:
            self.selection_index=0
            self.selected_object=self.image_objects[0]

        print('loaded',object_type,'parts:',len(self.image_objects))
        return True

    #------------------------------------------------------------------------------
    def offset_to_world(self,parent,offset):
        '''world coords for a def-space offset.

        matches engine.math_2d.calculate_relative_position, including the
        x/y swap that get_vector_rotation applies at rotation 0. that is
        why a StuG position_offset of [-60.4, 2.8] appears at the front
        of the hull in game, not to its left.
        '''
        parent_coords=[0.0,0.0]
        parent_rot=0
        if parent is not None:
            parent_coords=parent.world_coords
            parent_rot=parent.rotation_angle
        rotated=self.get_vector_rotation(offset,parent_rot)
        return [parent_coords[0]+rotated[0],parent_coords[1]+rotated[1]]

    #------------------------------------------------------------------------------
    def local_offset(self,obj):
        '''def-space offset of obj relative to its parent (or the base).

        inverse of offset_to_world: get_vector_rotation is an involution,
        so applying it again converts visual world delta back to the
        values stored on the object_def.
        '''
        parent=obj.offset_parent
        if parent is None:
            parent=self.base_object
        if parent is None or parent is obj:
            return [obj.world_coords[0],obj.world_coords[1]]
        offset=[
            obj.world_coords[0]-parent.world_coords[0],
            obj.world_coords[1]-parent.world_coords[1],
        ]
        return self.get_vector_rotation(offset,parent.rotation_angle)

    #------------------------------------------------------------------------------
    def print_offsets(self):
        if self.selected_object==None:
            return
        print('----------------------------------')
        print('object:',self.object_type,self.object_name)
        print('offsets (rotation should be 0)')
        print('----------------------------------')

        for b in self.image_objects:
            if b.kind in ['bound_circle','crew']:
                continue
            ox=round(b.image_rotation_offset[0],1)
            oy=round(b.image_rotation_offset[1],1)
            print('['+b.kind+']',b.label,'('+b.image_list[b.image_index]+')')
            print('z.image_rotation_offset = ['+str(ox)+', '+str(oy)+']')
            if b.kind=='base' and b.def_position_offset is not None and b is self.base_object:
                px=round(b.def_position_offset[0],1)
                py=round(b.def_position_offset[1],1)
                print('z.ai.position_offset = ['+str(px)+', '+str(py)+']')
            print('')

        for b in self.image_objects:
            if b.kind in ['turret','rotor']:
                offset=self.local_offset(b)
                ox=round(offset[0],1)
                oy=round(offset[1],1)
                print('['+b.kind+']',b.label)
                print('z.ai.position_offset = ['+str(ox)+', '+str(oy)+']')
            elif b.kind=='crew':
                offset=self.local_offset(b)
                ox=round(offset[0],1)
                oy=round(offset[1],1)
                rot=round(b.rotation_angle,1)
                print('[crew]',b.role_name or b.label)
                print('role.seat_offset = ['+str(ox)+', '+str(oy)+']')
                print('role.seat_rotation = '+str(rot))
        print('')

        for b in self.image_objects:
            if b.kind!='bound_circle':
                continue
            offset=self.local_offset(b)
            ox=round(offset[0],1)
            oy=round(offset[1],1)
            radius=b.bound_radius
            if radius is None:
                radius=b.image_list[b.image_index].split('r')[-1]
            print('z.bounding_circles.append([['+str(ox)+', '+str(oy)+'], '+str(radius)+'])')

        print('----------------------------------')

    #------------------------------------------------------------------------------
    def render(self):
        self.update_render_info()

        self.screen.blit(self.background, (0, 0))

        if self.draw_collision and self.image_objects :
            coords=self.image_objects[0].screen_coords
            radius=max(1,int(self.collision_radius*self.scale))
            pygame.draw.circle(self.screen,(236,64,122),coords,radius,1)

        for i, b in enumerate(self.image_objects):
            if b.kind=='bound_circle' and not self.show_bound_circles:
                continue
            self.reset_pygame_image(b)
            if b.image is None or b.image_center is None:
                continue
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
    def select_adjacent(self,direction):
        '''q/e selection, skipping hidden bound circles'''
        if not self.image_objects:
            self.selected_object=None
            return
        n=len(self.image_objects)
        for _ in range(n):
            self.selection_index=(self.selection_index+direction)%n
            obj=self.image_objects[self.selection_index]
            if obj.kind=='bound_circle' and not self.show_bound_circles:
                continue
            self.selected_object=obj
            return
        self.selected_object=self.image_objects[self.selection_index]

    #---------------------------------------------------------------------------
    def select_closest_object_with_mouse(self,mouse_coords):

        object_distance=50
        closest_object=None

        for b in self.image_objects:
            if b.kind=='bound_circle' and not self.show_bound_circles:
                continue
            distance=self.get_distance(mouse_coords,b.screen_coords)
            if distance<object_distance:
                object_distance=distance
                closest_object=b

        if closest_object != None:
            self.selected_object=closest_object
            self.selection_index=self.image_objects.index(closest_object)



    #------------------------------------------------------------------------------
    def unique_label(self,base,used):
        if base not in used:
            used.add(base)
            return base
        i=2
        while True:
            label=base+' #'+str(i)
            if label not in used:
                used.add(label)
                return label
            i+=1

    #------------------------------------------------------------------------------
    def update(self):
        '''
            any misc updating that needs to be done
        '''
        self.handleInput()

        self.text_queue=[]
        title='TWE Image Tool'
        if self.object_type:
            title=title+' : '+self.object_type
        self.text_queue.append(title)
        self.text_queue.append('Q/E select  I cycle image  B bounds  L lines  F collision')
        if self.selected_object!=None:
            sel=self.selected_object
            self.text_queue.append('Object: ['+sel.kind+'] '+sel.label+' ('+sel.image_list[sel.image_index]+')')
            self.text_queue.append('Rotation angle: '+str(round(sel.rotation_angle,2)))
            self.text_queue.append('W/S/A/D or mouse click to move')
            self.text_queue.append('R to rotate')
            self.text_queue.append('C: pivot-set mode (click origin, rotation 0)')
            self.text_queue.append('X: reset pivot to image center')
            self.text_queue.append('1: print offsets (rotation should be 0)')
            ox=round(sel.image_rotation_offset[0],1)
            oy=round(sel.image_rotation_offset[1],1)
            self.text_queue.append(f'image_rotation_offset: [{ox}, {oy}]')
            if sel.kind in ['turret','rotor','crew','bound_circle']:
                offset=self.local_offset(sel)
                self.text_queue.append('relative offset: '+str([round(offset[0],1),round(offset[1],1)]))
            if self.pivot_set_mode:
                self.text_queue.append('PIVOT SET MODE - click the rotation origin')

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
    def warn_missing_images(self,obj):
        for name in obj.image_list:
            if name not in self.images:
                print('warn','missing image '+name+' for '+obj.label)

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
        self.kind='base'
        self.label=''
        self.offset_parent=None
        self.bound_radius=None
        self.role_name=None
        self.def_position_offset=None


#------------------------------------------------------------------------------
# startup code
#------------------------------------------------------------------------------

def setup_code_path():
    '''put code/ on sys.path and chdir there so sqlite paths in engine work'''
    tools_dir=os.path.dirname(os.path.abspath(__file__))
    code_dir=os.path.dirname(tools_dir)
    if code_dir not in sys.path:
        sys.path.insert(0,code_dir)
    os.chdir(code_dir)
    return tools_dir,code_dir


def resolve_object_type(arg):
    '''registry key from a file path or an object_type string'''
    from engine.object_registry import OBJECT_REGISTRY

    if arg in OBJECT_REGISTRY:
        return arg

    path=os.path.abspath(arg)
    if os.path.isfile(path) and path.endswith('.py'):
        with open(path,'r') as handle:
            text=handle.read()
        names=REGISTER_RE.findall(text)
        if not names:
            print('error','no @register_object() in '+path)
            return None
        stem=os.path.splitext(os.path.basename(path))[0]
        if stem in names:
            return stem
        return names[0]

    print('error','unknown object type or file: '+arg)
    matches=[]
    for key in sorted(OBJECT_REGISTRY.keys()):
        if arg.lower() in key.lower():
            matches.append(key)
            if len(matches)>=12:
                break
    if matches:
        print('similar:')
        for key in matches:
            print('  '+key)
    return None


def print_usage():
    print('Usage: python image_tool.py <object_def.py | object_type>')
    print('  python image_tool.py german_stug_iii_ausf_g')
    print('  python image_tool.py ../engine/object_defs/vehicles/german/german_stug_iii/german_stug_iii_ausf_g.py')


def main():
    raw_arg=None
    if len(sys.argv)>=2:
        raw_arg=sys.argv[1]
        if raw_arg in ['-h','--help']:
            print_usage()
            return
        if os.path.exists(raw_arg):
            raw_arg=os.path.abspath(raw_arg)

    setup_code_path()

    if raw_arg is None:
        print_usage()
        return

    # world_builder import loads every object_def into the registry
    import engine.world_builder
    _ = engine.world_builder

    object_type=resolve_object_type(raw_arg)
    if object_type is None:
        sys.exit(1)

    screen_size = (1200,900)
    image_tool=ImageTool(screen_size)
    if not image_tool.load_object_def(object_type):
        sys.exit(1)

    while image_tool.quit==False:

        image_tool.update()
        image_tool.render()


if __name__=='__main__':
    main()
