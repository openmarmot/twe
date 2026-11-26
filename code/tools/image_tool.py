'''
repo : https://github.com/openmarmot/twe

notes :
A special tool for working with images.

Load an object definition and place its sprites using the currently
defined offsets (image_rotation_offset, turret/rotor position_offset,
visible seat_offset, bounding_circles).

A turret gun with cannon smoke gets a small_smoke sprite on
smoke_offset, parented to that turret. A vehicle that leaves tracks
gets a tank_tracks sprite on tracks_left_offset and tracks_right_offset.

Press 1 to print the lines to paste into the object def.

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

# kinds whose image_rotation_offset is a real def value
PIVOT_KINDS = ('base', 'turret', 'rotor')
# kinds whose rotation_angle is stored (crew) or used as a preview spin
ROTATE_KINDS = ('base', 'turret', 'rotor', 'crew')


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
        self.image_errors=set()

        self.screen_size=screen_size
        pygame.init()
        # hold-to-repeat is handled for nudge keys only. a global key
        # repeat would spin rotation and reprint offsets.
        pygame.key.set_repeat(0)

        # this seems to significantly improve visual quality when on
        self.double_buffering=True
        if self.double_buffering:
            self.screen = pygame.display.set_mode(self.screen_size, pygame.DOUBLEBUF, 32)
        else:
            self.screen=pygame.display.set_mode(self.screen_size,0,32)

        # mid gray so dark track marks and pale smoke both read
        self.background_color=(78, 80, 84)
        self.background = pygame.surface.Surface(self.screen_size).convert()
        self.background.fill(self.background_color)


        # time stuff
        self.clock=pygame.time.Clock()
        self.time_passed=None
        self.time_passed_seconds=None
        self.elapsed=0
        self.nudge_next=None

        # text stuff
        self.small_font = pygame.freetype.SysFont(pygame.font.get_default_font(), 13)
        self.ui_font = pygame.freetype.SysFont(pygame.font.get_default_font(), 16)

        self.color_text=(236, 236, 232)
        self.color_dim=(186, 190, 196)
        self.color_accent=(255, 198, 72)
        self.color_warn=(255, 126, 96)
        self.color_ok=(150, 214, 150)
        self.hud_lines=[]

        # draw collision circles
        self.draw_collision=True
        self.collision_radius=50

        # guides: 'selected', 'all', or 'off'
        self.guide_mode='selected'

        # click sets image_rotation_offset instead of moving the object
        self.pivot_set_mode=False

        # layers that can be hidden without dropping them from the list
        self.show_bound_circles=True
        self.show_tracks=True
        self.show_smoke=True

        self.drag_object=None
        self.drag_grab=[0, 0]

        self.notice=''
        self.notice_until=0
        self.show_help=False

        # colors for different images
        self.colors = [(255,0,0), (0,255,0), (0,0,255), (255,165,0), (128,0,128), (0,255,255), (255,0,255), (255,255,0)]

        # will cause everything to exit
        self.quit=False

        # max_fps max frames for every second.
        self.max_fps=60

        # Same steps as the game through 2.5. The extra steps are for
        # placing muzzle smoke and track marks, which are only a few pixels.
        self.zoom_levels = [
            0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.075,
            0.1, 0.125, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5,
            0.6, 0.75, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5,
            3.0, 4.0, 5.0, 6.0, 8.0
        ]
        self.scale_limit = [self.zoom_levels[0], self.zoom_levels[-1]]

        # open on the old maximum. wheel and [ ] still reach 8.
        self.scale=2.5

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
            role_name=None,def_position_offset=None,local_offset=None,
            config_attr=None):
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
        obj.config_attr=config_attr
        if def_position_offset is not None:
            obj.def_position_offset=[def_position_offset[0],def_position_offset[1]]
        if local_offset is not None:
            obj.local_offset=[local_offset[0],local_offset[1]]
        elif offset_parent is not None and def_position_offset is not None:
            obj.local_offset=[def_position_offset[0],def_position_offset[1]]
        self.image_objects.append(obj)
        return obj

    #------------------------------------------------------------------------------
    def add_turret_smoke(self,turret,parent,used_labels):
        '''small_smoke at each cannon smoke_offset, parented to the turret'''
        for offset, config_attr, label in self.iter_cannon_smoke(turret):
            name=self.unique_label(label,used_labels)
            img=self.add_image_object(
                ['small_smoke'],
                'smoke',
                name,
                self.offset_to_world(parent,offset),
                offset_parent=parent,
                local_offset=offset,
                config_attr=config_attr,
            )
            self.warn_missing_images(img)

    #------------------------------------------------------------------------------
    def add_tracks(self,vehicle,parent,used_labels):
        '''tank_tracks sprites for a vehicle that leaves them'''
        if self.vehicle_leaves_tracks(vehicle) is False:
            return
        sides=(
            ('left', vehicle.ai.tracks_left_offset, 'z.ai.tracks_left_offset'),
            ('right', vehicle.ai.tracks_right_offset, 'z.ai.tracks_right_offset'),
        )
        for side, offset, config_attr in sides:
            label=self.unique_label(side+' track',used_labels)
            img=self.add_image_object(
                ['tank_tracks'],
                'track',
                label,
                self.offset_to_world(parent,offset),
                offset_parent=parent,
                role_name=side,
                local_offset=offset,
                config_attr=config_attr,
            )
            self.warn_missing_images(img)

    #------------------------------------------------------------------------------
    def apply_held_nudge(self):
        '''repeat wasd / arrows after a short hold, without repeating every key'''
        vector=self.held_nudge_vector()
        if vector is None:
            self.nudge_next=None
            return
        if self.nudge_next is None:
            # the key-down event already stepped once
            self.nudge_next=self.elapsed+0.26
            return
        if self.elapsed<self.nudge_next:
            return
        self.nudge_next=self.elapsed+0.045
        self.nudge_selected(vector[0],vector[1])

    #------------------------------------------------------------------------------
    def build_hud(self):
        '''corner panel: the selected part and the line 1 will print'''
        lines=[]
        title=self.object_name or 'image tool'
        lines.append((title,self.color_text))
        sel=self.selected_object
        if sel is None:
            lines.append(('nothing selected',self.color_dim))
        else:
            index=self.selection_index+1
            count=len(self.image_objects)
            sprite=sel.image_list[sel.image_index]
            lines.append((
                '['+sel.kind+'] '+sel.label+'   '+str(index)+'/'+str(count),
                self.color_accent,
            ))
            lines.append((sprite,self.color_dim))
            for text in self.config_lines(sel):
                lines.append((text,self.color_text))
            lines.append((
                'rotation '+str(round(sel.rotation_angle,1))+'    zoom '+str(self.scale),
                self.color_dim,
            ))
            stacked=self.stacked_smoke_note(sel)
            if stacked:
                lines.append((stacked,self.color_warn))
        if self.pivot_set_mode:
            lines.append(('pivot set: click the rotation origin. rotation must be 0',self.color_warn))
        if self.notice and self.elapsed<self.notice_until:
            lines.append((self.notice,self.color_ok))
        lines.append(('drag move    wasd nudge    shift x5    r +90    shift-r -90',self.color_dim))
        lines.append(('q/e select    wheel zoom    1 print    h help',self.color_dim))
        if self.show_help:
            lines.append(('click a part to select it. drag moves that part.',self.color_dim))
            lines.append(('parts follow the hull or turret they are attached to',self.color_dim))
            lines.append(('c pivot mode    x reset pivot    i next sprite',self.color_dim))
            lines.append(('b bounds    t tracks    m muzzle smoke',self.color_dim))
            lines.append(('l guides (selected / all / off)    f collision circle',self.color_dim))
            lines.append(('smoke rings and L/R marks are the muzzle and the track marks',self.color_dim))
            lines.append(('esc quits',self.color_dim))
        self.hud_lines=lines

    #------------------------------------------------------------------------------
    def cannon_smoke(self,weapon):
        '''true when this gun spawns muzzle smoke from smoke_offset'''
        ai=getattr(weapon,'ai',None)
        if ai is None:
            return False
        # a multi-barrel mount fires the barrels. the mount itself has no puff
        if getattr(ai,'multi_barrel',False):
            return False
        if getattr(ai,'smoke_on_fire',False) is False:
            return False
        return getattr(ai,'smoke_type','')=='cannon'

    #------------------------------------------------------------------------------
    def capture_child_offsets(self,parent):
        '''keep children where they are and store the new relative offsets.

        used when the pivot moves under a sprite that stays visually put.
        children stay on the art. their def offsets change with the origin.
        '''
        for obj in self.image_objects:
            if obj.offset_parent is not parent or obj.local_offset is None:
                continue
            obj.local_offset=self.world_to_offset(obj)
            self.capture_child_offsets(obj)

    #------------------------------------------------------------------------------
    def config_lines(self,obj):
        '''the def lines for the selected part'''
        lines=[]
        if obj.config_attr and obj.local_offset is not None:
            lines.append(obj.config_attr+' = '+self.format_pair(obj.local_offset))
            return lines
        if obj.kind in ('turret','rotor') and obj.local_offset is not None:
            lines.append('z.ai.position_offset = '+self.format_pair(obj.local_offset))
        if obj.kind=='crew' and obj.local_offset is not None:
            lines.append('role.seat_offset = '+self.format_pair(obj.local_offset))
            lines.append('role.seat_rotation = '+str(round(obj.rotation_angle,1)))
            return lines
        if obj.kind=='bound_circle' and obj.local_offset is not None:
            radius=obj.bound_radius
            lines.append(
                'z.bounding_circles.append(['+self.format_pair(obj.local_offset)+', '+str(radius)+'])'
            )
            return lines
        if obj.kind in PIVOT_KINDS:
            lines.append('z.image_rotation_offset = '+self.format_pair(obj.image_rotation_offset))
        if obj.kind=='base' and obj.def_position_offset is not None and obj is self.base_object:
            lines.append('z.ai.position_offset = '+self.format_pair(obj.def_position_offset))
        return lines

    #------------------------------------------------------------------------------
    def cycle_guides(self):
        order=('selected','all','off')
        index=order.index(self.guide_mode)
        self.guide_mode=order[(index+1)%len(order)]
        self.notify('guides: '+self.guide_mode)

    #------------------------------------------------------------------------------
    def cycle_selected_image(self):
        '''cycle image_index for buildings / humans with multiple sprites'''
        obj=self.selected_object
        if obj is None or len(obj.image_list)<2:
            return
        obj.image_index=(obj.image_index+1)%len(obj.image_list)
        name=obj.image_list[obj.image_index]
        print('image',name)
        self.notify('image '+name)

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
    def drawable_objects(self):
        '''hull and fittings first, then tracks, then muzzle smoke on top'''
        hull=[]
        tracks=[]
        smoke=[]
        for obj in self.image_objects:
            if self.layer_visible(obj) is False:
                continue
            if obj.kind=='track':
                tracks.append(obj)
            elif obj.kind=='smoke':
                smoke.append(obj)
            else:
                hull.append(obj)
        return hull+tracks+smoke

    #------------------------------------------------------------------------------
    def draw_guides(self,obj,color):
        '''cross and box through the rotation origin'''
        origin=self.image_top_left(obj)
        if origin is None or obj.image_size is None:
            return
        blit_x,blit_y=origin
        pivot_x,pivot_y=obj.screen_coords
        pygame.draw.line(self.screen,color,(pivot_x,blit_y),(pivot_x,blit_y+obj.image_size[1]),1)
        pygame.draw.line(self.screen,color,(blit_x,pivot_y),(blit_x+obj.image_size[0],pivot_y),1)
        pygame.draw.rect(self.screen,color,(blit_x,blit_y,obj.image_size[0],obj.image_size[1]),1)
        pygame.draw.circle(self.screen,color,(int(pivot_x),int(pivot_y)),4,1)

    #------------------------------------------------------------------------------
    def draw_marker(self,obj):
        '''screen-space handle. smoke and track art is only a few pixels'''
        if obj.kind not in ('smoke','track'):
            return
        color,tag=self.marker_style(obj)
        x=int(obj.screen_coords[0])
        y=int(obj.screen_coords[1])
        # the art is only a few pixels. keep the center clear so the
        # sprite stays visible, and put the ring just outside it.
        sprite_r=0
        if obj.image_size is not None:
            sprite_r=int(max(obj.image_size)*0.5)
        radius=max(11,sprite_r+3)
        gap=max(6,sprite_r+1)
        reach=radius+4
        width=1
        if obj is self.selected_object:
            color=self.color_accent
            width=2
            tag=obj.label
        parent=obj.offset_parent
        if parent is not None:
            px=int(parent.screen_coords[0])
            py=int(parent.screen_coords[1])
            end=self.point_toward((px,py),(x,y),radius)
            pygame.draw.line(self.screen,color,(px,py),end,1)
        pygame.draw.circle(self.screen,color,(x,y),radius,width)
        pygame.draw.line(self.screen,color,(x-reach,y),(x-gap,y),width)
        pygame.draw.line(self.screen,color,(x+gap,y),(x+reach,y),width)
        pygame.draw.line(self.screen,color,(x,y-reach),(x,y-gap),width)
        pygame.draw.line(self.screen,color,(x,y+gap),(x,y+reach),width)
        self.small_font.render_to(self.screen,(x+radius+2,y-16),tag,color)

    #------------------------------------------------------------------------------
    def draw_origin(self):
        '''faint cross at world 0,0'''
        center=self.get_translation()
        color=(62, 64, 68)
        x=int(center[0])
        y=int(center[1])
        pygame.draw.line(self.screen,color,(x,0),(x,self.screen_size[1]),1)
        pygame.draw.line(self.screen,color,(0,y),(self.screen_size[0],y),1)

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
    def facing(self,obj):
        '''world rotation this part is drawn at, including parent preview spins'''
        if obj is None:
            return 0
        angle=obj.rotation_angle
        parent=obj.offset_parent
        while parent is not None:
            angle+=parent.rotation_angle
            parent=parent.offset_parent
        return angle % 360

    #------------------------------------------------------------------------------
    def format_pair(self,pair):
        return '['+str(round(pair[0],1))+', '+str(round(pair[1],1))+']'

    #------------------------------------------------------------------------------
    def handle_key(self,event):
        key=event.key
        if key==pygame.K_ESCAPE:
            self.quit=True
            return
        if key in (pygame.K_w,pygame.K_UP):
            self.nudge_selected(0,-1)
        elif key in (pygame.K_s,pygame.K_DOWN):
            self.nudge_selected(0,1)
        elif key in (pygame.K_a,pygame.K_LEFT):
            self.nudge_selected(-1,0)
        elif key in (pygame.K_d,pygame.K_RIGHT):
            self.nudge_selected(1,0)
        elif key==pygame.K_r:
            direction=-1 if event.mod & pygame.KMOD_SHIFT else 1
            self.rotate_selected(90*direction)
        elif key==pygame.K_q:
            self.select_adjacent(-1)
        elif key==pygame.K_e:
            self.select_adjacent(1)
        elif key==pygame.K_1:
            self.print_offsets()
        elif key==pygame.K_c:
            self.pivot_set_mode=not self.pivot_set_mode
            if self.pivot_set_mode:
                self.notify('pivot set on. click the rotation origin')
            else:
                self.notify('pivot set off')
        elif key==pygame.K_x:
            self.reset_selected_pivot()
        elif key==pygame.K_i:
            self.cycle_selected_image()
        elif key==pygame.K_b:
            self.show_bound_circles=not self.show_bound_circles
            self.notify('bounds '+('on' if self.show_bound_circles else 'off'))
            self.skip_hidden_selection()
        elif key==pygame.K_t:
            self.show_tracks=not self.show_tracks
            self.notify('tracks '+('on' if self.show_tracks else 'off'))
            self.skip_hidden_selection()
        elif key==pygame.K_m:
            self.show_smoke=not self.show_smoke
            self.notify('muzzle smoke '+('on' if self.show_smoke else 'off'))
            self.skip_hidden_selection()
        elif key==pygame.K_l:
            self.cycle_guides()
        elif key==pygame.K_f:
            self.draw_collision=not self.draw_collision
            self.notify('collision circle '+('on' if self.draw_collision else 'off'))
        elif key==pygame.K_h:
            self.show_help=not self.show_help
        elif key==pygame.K_LEFTBRACKET:
            self.zoom_out()
        elif key==pygame.K_RIGHTBRACKET:
            self.zoom_in()

    #------------------------------------------------------------------------------
    def handle_mouse_down(self,event):
        if event.button==1:
            if self.pivot_set_mode:
                self.set_selected_pivot(self.get_mouse_world_coords())
                return
            picked=self.pick_object(event.pos)
            if picked is None:
                return
            self.selected_object=picked
            self.selection_index=self.image_objects.index(picked)
            world=self.get_mouse_world_coords()
            self.drag_object=picked
            self.drag_grab=[
                picked.world_coords[0]-world[0],
                picked.world_coords[1]-world[1],
            ]
        elif event.button==3 and self.pivot_set_mode:
            self.pivot_set_mode=False
            self.notify('pivot set off')

    #------------------------------------------------------------------------------
    def handle_mouse_up(self,event):
        if event.button==1:
            self.drag_object=None

    #------------------------------------------------------------------------------
    def handle_mouse_motion(self):
        if self.drag_object is None or self.pivot_set_mode:
            return
        world=self.get_mouse_world_coords()
        self.place_object(self.drag_object,[
            world[0]+self.drag_grab[0],
            world[1]+self.drag_grab[1],
        ])

    #------------------------------------------------------------------------------
    def handleInput(self):

        # single presses. hold-to-repeat for nudge keys is apply_held_nudge
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.quit=True
            elif event.type==pygame.KEYDOWN:
                self.handle_key(event)
            elif event.type==pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)
            elif event.type==pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)
            elif event.type==pygame.MOUSEMOTION:
                self.handle_mouse_motion()
            elif event.type==pygame.MOUSEWHEEL:
                if event.y>0:
                    self.zoom_in()
                elif event.y<0:
                    self.zoom_out()

    #------------------------------------------------------------------------------
    def held_nudge_vector(self):
        keys=pygame.key.get_pressed()
        dx=0
        dy=0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx-=1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx+=1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy-=1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy+=1
        if dx==0 and dy==0:
            return None
        return [dx,dy]

    #------------------------------------------------------------------------------
    def image_top_left(self,obj):
        if obj.image_size is None:
            return None
        blit=obj.image_blit_offset
        if blit is None:
            blit=obj.image_center
        if blit is None:
            return None
        return [
            obj.screen_coords[0]-blit[0],
            obj.screen_coords[1]-blit[1],
        ]

    #------------------------------------------------------------------------------
    def iter_cannon_smoke(self,turret):
        '''yield (offset, config assignment, label) for turret muzzle smoke'''
        ai=getattr(turret,'ai',None)
        if ai is None:
            return
        weapon=getattr(ai,'primary_weapon',None)
        if weapon is not None:
            weapon_ai=weapon.ai
            if getattr(weapon_ai,'multi_barrel',False):
                for index, barrel in enumerate(getattr(weapon_ai,'barrels',[])):
                    if self.cannon_smoke(barrel) is False:
                        continue
                    attr='z.ai.primary_weapon.ai.barrels['+str(index)+'].ai.smoke_offset'
                    yield (list(barrel.ai.smoke_offset), attr, 'barrel '+str(index)+' smoke')
            elif self.cannon_smoke(weapon):
                yield (
                    list(weapon_ai.smoke_offset),
                    'z.ai.primary_weapon.ai.smoke_offset',
                    'muzzle smoke',
                )
        coax=getattr(ai,'coaxial_weapon',None)
        if coax is not None and self.cannon_smoke(coax):
            yield (
                list(coax.ai.smoke_offset),
                'z.ai.coaxial_weapon.ai.smoke_offset',
                'coax smoke',
            )

    #------------------------------------------------------------------------------
    def layer_visible(self,obj):
        if obj.kind=='bound_circle' and self.show_bound_circles is False:
            return False
        if obj.kind=='track' and self.show_tracks is False:
            return False
        if obj.kind=='smoke' and self.show_smoke is False:
            return False
        return True

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

        self.image_objects=[]
        self.selected_object=None
        self.base_object=None
        self.selection_index=0

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
        self.add_tracks(wo,base,used_labels)

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
                self.add_turret_smoke(turret,img,used_labels)

        # the loaded object is the turret itself (opened the turret def)
        if getattr(wo,'is_turret',False):
            self.add_turret_smoke(wo,base,used_labels)

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
                    local_offset=role.seat_offset,
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
                local_offset=offset,
            )

        if self.image_objects:
            self.selection_index=0
            self.selected_object=self.image_objects[0]

        print('loaded',object_type,'parts:',len(self.image_objects))
        return True

    #------------------------------------------------------------------------------
    def marker_style(self,obj):
        if obj.kind=='smoke':
            tag='smoke'
            if obj.label.startswith('barrel'):
                parts=obj.label.split()
                if len(parts)>1:
                    tag='b'+parts[1]
            elif obj.label.startswith('coax'):
                tag='coax'
            return (236, 232, 214), tag
        if obj.role_name=='left':
            return (255, 168, 64), 'L'
        return (110, 198, 255), 'R'

    #------------------------------------------------------------------------------
    def notify(self,text):
        self.notice=text
        self.notice_until=self.elapsed+2.4

    #------------------------------------------------------------------------------
    def nudge_selected(self,dx,dy):
        obj=self.selected_object
        if obj is None:
            return
        step=5 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
        self.place_object(obj,[
            obj.world_coords[0]+dx*step,
            obj.world_coords[1]+dy*step,
        ])

    #------------------------------------------------------------------------------
    def offset_to_world(self,parent,offset):
        '''world coords for a def-space offset.

        matches engine.math_2d.calculate_relative_position, including the
        x/y swap that get_vector_rotation applies at rotation 0. that is
        why a StuG position_offset of [-60.4, 2.8] appears at the front
        of the hull in game, not to its left.

        parent facing includes a preview spin, so a muzzle puff stays on
        the barrel while the turret is rotated.
        '''
        parent_coords=[0.0,0.0]
        parent_rot=0
        if parent is not None:
            parent_coords=parent.world_coords
            parent_rot=self.facing(parent)
        rotated=self.get_vector_rotation(offset,parent_rot)
        return [parent_coords[0]+rotated[0],parent_coords[1]+rotated[1]]

    #------------------------------------------------------------------------------
    def world_to_offset(self,obj):
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
        delta=[
            obj.world_coords[0]-parent.world_coords[0],
            obj.world_coords[1]-parent.world_coords[1],
        ]
        return self.get_vector_rotation(delta,self.facing(parent))

    #------------------------------------------------------------------------------
    def pick_object(self,screen_pos):
        '''marker first, then the sprite under the cursor, then a nearby pivot'''
        best=None
        best_dist=22
        for obj in self.image_objects:
            if self.layer_visible(obj) is False:
                continue
            if obj.kind not in ('smoke','track','crew','bound_circle'):
                continue
            dist=self.get_distance(screen_pos,obj.screen_coords)
            if dist<best_dist:
                best_dist=dist
                best=obj
        if best is not None:
            return best

        hit=None
        for obj in self.drawable_objects():
            origin=self.image_top_left(obj)
            if origin is None or obj.image_size is None:
                continue
            rect=pygame.Rect(origin[0],origin[1],obj.image_size[0],obj.image_size[1])
            if rect.collidepoint(screen_pos):
                hit=obj
        if hit is not None:
            return hit

        best_dist=36
        for obj in self.image_objects:
            if self.layer_visible(obj) is False:
                continue
            dist=self.get_distance(screen_pos,obj.screen_coords)
            if dist<best_dist:
                best_dist=dist
                best=obj
        return best

    #------------------------------------------------------------------------------
    def point_toward(self,start,end,stop_radius):
        '''point on the segment from start to end, stop_radius short of end'''
        dx=start[0]-end[0]
        dy=start[1]-end[1]
        dist=math.sqrt(dx*dx+dy*dy)
        if dist<=stop_radius or dist==0:
            return (int(end[0]),int(end[1]))
        scale=stop_radius/dist
        return (int(end[0]+dx*scale),int(end[1]+dy*scale))

    #------------------------------------------------------------------------------
    def place_object(self,obj,coords):
        '''move one part. attached parts keep their offsets and follow on sync'''
        obj.world_coords=[coords[0],coords[1]]
        if obj.offset_parent is not None:
            obj.local_offset=self.world_to_offset(obj)

    #------------------------------------------------------------------------------
    def preview_rotated(self):
        for obj in self.image_objects:
            if obj.kind in ROTATE_KINDS and obj.rotation_angle!=0:
                return True
        return False

    #------------------------------------------------------------------------------
    def print_offsets(self):
        if self.selected_object is None and not self.image_objects:
            return
        print('----------------------------------')
        print('object:',self.object_type,self.object_name)
        if self.preview_rotated():
            print('warning: set rotation to 0 before copying image_rotation_offset')
        print('position offsets stay parent-relative while you preview a spin')
        print('----------------------------------')

        for obj in self.image_objects:
            if obj.kind not in PIVOT_KINDS:
                continue
            print('['+obj.kind+']',obj.label,'('+obj.image_list[obj.image_index]+')')
            print('z.image_rotation_offset = '+self.format_pair(obj.image_rotation_offset))
            if obj.kind=='base' and obj.def_position_offset is not None and obj is self.base_object:
                print('z.ai.position_offset = '+self.format_pair(obj.def_position_offset))
            if obj.kind in ('turret','rotor') and obj.local_offset is not None:
                print('z.ai.position_offset = '+self.format_pair(obj.local_offset))
            for child in self.image_objects:
                if child.kind!='smoke' or child.offset_parent is not obj:
                    continue
                if child.local_offset is None or not child.config_attr:
                    continue
                print(child.config_attr+' = '+self.format_pair(child.local_offset))
            print('')

        for obj in self.image_objects:
            if obj.kind!='crew' or obj.local_offset is None:
                continue
            print('[crew]',obj.role_name or obj.label)
            print('role.seat_offset = '+self.format_pair(obj.local_offset))
            print('role.seat_rotation = '+str(round(obj.rotation_angle,1)))
            print('')

        tracks=[obj for obj in self.image_objects if obj.kind=='track' and obj.local_offset is not None]
        if tracks:
            print('[tracks]')
            for obj in tracks:
                print(obj.config_attr+' = '+self.format_pair(obj.local_offset))
            print('')

        for obj in self.image_objects:
            if obj.kind!='bound_circle' or obj.local_offset is None:
                continue
            radius=obj.bound_radius
            if radius is None:
                radius=obj.image_list[obj.image_index].split('r')[-1]
            pair=self.format_pair(obj.local_offset)
            print('z.bounding_circles.append(['+pair+', '+str(radius)+'])')

        print('----------------------------------')
        self.notify('printed offsets to the console')

    #------------------------------------------------------------------------------
    def render(self):
        self.update_render_info()
        for obj in self.image_objects:
            obj.render_rotation=self.facing(obj)

        self.screen.blit(self.background, (0, 0))
        self.draw_origin()

        if self.draw_collision and self.base_object is not None:
            coords=self.base_object.screen_coords
            radius=max(1,int(self.collision_radius*self.scale))
            pygame.draw.circle(self.screen,(236,64,122),coords,radius,1)

        drawn=self.drawable_objects()
        for obj in drawn:
            self.reset_pygame_image(obj)
            if obj.image is None or obj.image_center is None:
                continue
            origin=self.image_top_left(obj)
            if origin is None:
                continue
            self.screen.blit(obj.image, (origin[0], origin[1]))

        if self.guide_mode!='off':
            for index, obj in enumerate(self.image_objects):
                if self.layer_visible(obj) is False:
                    continue
                if obj.kind not in PIVOT_KINDS:
                    continue
                selected=obj is self.selected_object
                if self.guide_mode=='selected' and selected is False:
                    continue
                color=self.color_accent if selected else self.colors[index % len(self.colors)]
                self.draw_guides(obj,color)

        for obj in drawn:
            if obj.kind in ('smoke','track'):
                self.draw_marker(obj)

        if self.selected_object is not None and self.selected_object.kind not in ('smoke','track'):
            pivot=self.selected_object.screen_coords
            pygame.draw.circle(self.screen,self.color_accent,(int(pivot[0]),int(pivot[1])),6,2)
            self.small_font.render_to(
                self.screen,(pivot[0]+10,pivot[1]-18),
                self.selected_object.label,self.color_accent,
            )

        self.render_hud()

        if self.double_buffering:
            pygame.display.flip()
        else:
            pygame.display.update()

    #------------------------------------------------------------------------------
    def render_hud(self):
        if not self.hud_lines:
            return
        pad_x=12
        pad_y=8
        line_h=20
        width=320
        for text, _color in self.hud_lines:
            rect=self.ui_font.get_rect(text)
            width=max(width,rect.width+pad_x*2)
        width=min(width,640)
        height=pad_y*2+line_h*len(self.hud_lines)
        panel=pygame.Surface((width,height),pygame.SRCALPHA)
        panel.fill((18, 20, 24, 214))
        pygame.draw.rect(panel,(255,255,255,28),panel.get_rect(),1)
        self.screen.blit(panel,(14,14))
        y=14+pad_y
        for text, color in self.hud_lines:
            self.ui_font.render_to(self.screen,(14+pad_x,y),text,color)
            y+=line_h

    #------------------------------------------------------------------------------
    def reset_pygame_image(self, wo):
        '''reset the image for a world object'''
        name=wo.image_list[wo.image_index]
        image=self.images.get(name)
        if image is None:
            wo.image=None
            if name not in self.image_errors:
                self.image_errors.add(name)
                print('error','missing image '+name)
            return

        obj_scale=self.scale+wo.scale_modifier
        angle=wo.render_rotation
        try:
            wo.image=pygame.transform.rotozoom(image, angle, obj_scale)
        except pygame.error:
            wo.image=None
            if name not in self.image_errors:
                self.image_errors.add(name)
                print('error','image transform failed for '+name)
            return
        wo.image_size=wo.image.get_size()
        wo.image_center=[round(wo.image_size[0]*0.5,1),round(wo.image_size[1]*0.5,1)]
        self.update_image_blit_offset(wo, obj_scale, angle)

    #------------------------------------------------------------------------------
    def reset_selected_pivot(self):
        '''move rotation origin back to the source image center'''
        obj=self.selected_object
        if obj is None:
            return
        if obj.kind not in PIVOT_KINDS:
            self.notify('pivot is for the hull, turret, or rotor')
            return
        if self.facing(obj)!=0:
            self.notify('set rotation to 0 first')
            return
        new_world=[
            obj.world_coords[0]-obj.image_rotation_offset[0],
            obj.world_coords[1]-obj.image_rotation_offset[1],
        ]
        obj.image_rotation_offset=[0,0]
        obj.world_coords=new_world
        if obj.offset_parent is not None:
            obj.local_offset=self.world_to_offset(obj)
        # the art stays put. children stay on the art, so their offsets change
        self.capture_child_offsets(obj)
        self.notify('pivot reset to image center')

    #------------------------------------------------------------------------------
    def rotate_selected(self,degrees):
        obj=self.selected_object
        if obj is None:
            return
        if obj.kind not in ROTATE_KINDS:
            self.notify('this part has no rotation to set')
            return
        obj.rotation_angle=(obj.rotation_angle+degrees) % 360

    #------------------------------------------------------------------------------
    def select_adjacent(self,direction):
        '''q/e selection, skipping hidden layers'''
        self.drag_object=None
        if not self.image_objects:
            self.selected_object=None
            return
        count=len(self.image_objects)
        for _ in range(count):
            self.selection_index=(self.selection_index+direction)%count
            obj=self.image_objects[self.selection_index]
            if self.layer_visible(obj) is False:
                continue
            self.selected_object=obj
            return
        self.selected_object=self.image_objects[self.selection_index]

    #------------------------------------------------------------------------------
    def set_selected_pivot(self, click_world):
        '''set rotation origin to the clicked point. rotation must be 0'''
        obj=self.selected_object
        if obj is None:
            return
        if obj.kind not in PIVOT_KINDS:
            self.notify('pivot is for the hull, turret, or rotor')
            return
        if self.facing(obj)!=0:
            self.notify('set rotation to 0 first')
            return
        old=obj.image_rotation_offset
        obj.image_rotation_offset=[
            click_world[0]-obj.world_coords[0]+old[0],
            click_world[1]-obj.world_coords[1]+old[1],
        ]
        obj.world_coords=[click_world[0], click_world[1]]
        if obj.offset_parent is not None:
            obj.local_offset=self.world_to_offset(obj)
        self.capture_child_offsets(obj)
        print('pivot set image_rotation_offset='+self.format_pair(obj.image_rotation_offset))
        self.notify('pivot '+self.format_pair(obj.image_rotation_offset))

    #------------------------------------------------------------------------------
    def skip_hidden_selection(self):
        if self.selected_object is not None and self.layer_visible(self.selected_object) is False:
            self.select_adjacent(1)

    #------------------------------------------------------------------------------
    def stacked_smoke_note(self,obj):
        if obj.kind!='smoke':
            return None
        for other in self.image_objects:
            if other is obj or other.kind!='smoke':
                continue
            if self.get_distance(obj.world_coords,other.world_coords)<1:
                return 'stacked on another muzzle. q/e switches which one'
        return None

    #------------------------------------------------------------------------------
    def sync_attached(self):
        '''place attached parts from their stored offsets.

        repeated so a muzzle puff follows a turret that follows the hull.
        the part being dragged keeps the pointer position.
        '''
        for _ in range(3):
            for obj in self.image_objects:
                if obj is self.drag_object:
                    continue
                if obj.offset_parent is None or obj.local_offset is None:
                    continue
                obj.world_coords=self.offset_to_world(obj.offset_parent,obj.local_offset)

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
        self.time_passed=self.clock.tick(self.max_fps)
        self.time_passed_seconds=self.time_passed / 1000.0
        self.elapsed+=self.time_passed_seconds

        self.handleInput()
        self.apply_held_nudge()
        self.sync_attached()
        self.build_hud()

    #------------------------------------------------------------------------------
    def update_image_blit_offset(self, wo, obj_scale, angle):
        '''set blit offset so image_rotation_offset stays on screen_coords'''
        center=wo.image_center
        offset=wo.image_rotation_offset
        if center is None or (offset[0]==0 and offset[1]==0):
            wo.image_blit_offset=[center[0], center[1]] if center is not None else None
            return
        scaled=pygame.math.Vector2(offset[0]*obj_scale, offset[1]*obj_scale)
        rotated=scaled.rotate(-angle)
        wo.image_blit_offset=[center[0]+rotated.x, center[1]+rotated.y]

    #------------------------------------------------------------------------------
    def update_render_info(self):
        '''
            -checks if world objects are within the viewable
             screen area, and if so, translates their world coordinates
             to screen coordinates
        '''

        translation=self.get_translation()

        for b in self.image_objects:
            b.screen_coords[0]=(b.world_coords[0]*self.scale+translation[0])
            b.screen_coords[1]=(b.world_coords[1]*self.scale+translation[1])

    #------------------------------------------------------------------------------
    def vehicle_leaves_tracks(self,wo):
        '''same gate as ai_vehicle.update: heavy enough, and it has wheels'''
        if getattr(wo,'is_vehicle',False) is False:
            return False
        ai=getattr(wo,'ai',None)
        if ai is None:
            return False
        if getattr(ai,'max_wheels',0)<=0:
            return False
        if getattr(wo,'weight',0)<=500:
            return False
        if hasattr(ai,'tracks_left_offset') is False:
            return False
        return True

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
        self.render_rotation=rotation_angle
        self.scale_modifier=0
        self.kind='base'
        self.label=''
        self.offset_parent=None
        self.bound_radius=None
        self.role_name=None
        self.def_position_offset=None
        # def-space offset from offset_parent. source of truth for print
        self.local_offset=None
        # assignment printed by 1, for smoke and tracks
        self.config_attr=None


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

    while image_tool.quit is False:

        image_tool.update()
        image_tool.render()


if __name__=='__main__':
    main()
