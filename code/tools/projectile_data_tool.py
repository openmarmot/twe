'''
repo : https://github.com/openmarmot/twe

notes :
Review tool for the projectile_data table in data/data.sqlite.
Draws each round's stored penetration columns, which is what the game
interpolates at impact. Velocity is stored on the row and is not applied.

Range columns are game units, every 500 from 0 through 5000.
Cannon rows use a compressed scale of about 2 game units per meter
(column 1000 is about 500 m, column 2000 is about 1000 m).
Rifle and machine-gun rows share those columns and are not on that scale.

Usage (from the repo root, code/, or code/tools/):
    python3 code/tools/projectile_data_tool.py
    python3 projectile_data_tool.py /path/to/data.sqlite

click a round to plot it. shift-click or right-click adds it to the comparison.
'''


# import built in modules
import math
import os
import sqlite3
import sys

# hide the pygame startup line. this has to be set before pygame is imported
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

# import pip packages
import pygame
import pygame.freetype


RANGE_COLUMNS = [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
ARMOR_GUIDES = [20, 40, 60, 80, 100, 120, 150, 200]
MAX_PLOT = 12

SCREEN_W = 1440
SCREEN_H = 960
MARGIN = 12
TOP_H = 86
DETAIL_H = 158
HELP_H = 22
BODY_Y = MARGIN + TOP_H + 8
BODY_H = SCREEN_H - BODY_Y - DETAIL_H - HELP_H - 16
DETAIL_Y = BODY_Y + BODY_H + 8
LIST_W = 478
LIST_HEADER_H = 28
TABLE_HEADER_H = 40
LIST_ROW_H = 24
TABLE_ROW_H = 22

BG = (236, 233, 226)
PANEL = (252, 251, 247)
INK = (42, 40, 36)
MUTED = (110, 104, 96)
LINE = (196, 190, 180)
GRID = (226, 222, 214)
ACCENT = (36, 72, 112)
WARN = (140, 72, 24)
FOCUS = (255, 244, 214)
WHITE = (255, 255, 255)

PLOT_COLORS = [
    (31, 119, 180),
    (214, 39, 40),
    (44, 160, 44),
    (230, 120, 14),
    (148, 103, 189),
    (140, 86, 75),
    (190, 70, 150),
    (16, 150, 166),
    (150, 150, 30),
    (80, 80, 80),
    (0, 120, 120),
    (170, 70, 40),
]

SCALE_NOTE = (
    'Bottom numbers are game units. Gray numbers are meters for cannon rows only '
    '(1000 units is about 500 m). Rifle and machine-gun rows share the columns and '
    'are not on that meter scale. Lines are the in-game interpolation between columns.'
)


#------------------------------------------------------------------------------
def database_path():
    '''default data.sqlite next to this script's code directory'''
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    code_dir = os.path.dirname(tools_dir)
    return os.path.join(code_dir, 'data', 'data.sqlite')


#------------------------------------------------------------------------------
def load_projectiles(path):
    '''read projectile_data. one dict per row, plus a pen list aligned to RANGE_COLUMNS'''
    if os.path.exists(path) is False:
        print('database not found: ' + path)
        sys.exit(1)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM projectile_data")
    columns = [description[0] for description in cursor.description]
    for distance in RANGE_COLUMNS:
        if str(distance) not in columns:
            print('projectile_data is missing column ' + str(distance))
            connection.close()
            sys.exit(1)

    rows = []
    seen = {}
    for record in cursor.fetchall():
        item = {}
        for column in columns:
            item[column] = record[column]
        pen = []
        for distance in RANGE_COLUMNS:
            value = item[str(distance)]
            if value is None:
                value = 0
            pen.append(value)
        item['pen'] = pen
        last = None
        for index, value in enumerate(pen):
            if value > 0:
                last = RANGE_COLUMNS[index]
        item['last_positive'] = last
        item['diameter_value'] = float(item['diameter'])
        name = item['name']
        if name in seen:
            print('warning: duplicate projectile name ' + name)
        seen[name] = True
        rows.append(item)
    connection.close()
    return rows


#------------------------------------------------------------------------------
def format_diameter(value):
    '''7.62 stays 7.62, 88 stays 88'''
    text = f"{float(value):.2f}".rstrip('0').rstrip('.')
    return text


#------------------------------------------------------------------------------
def heat_color(value):
    '''fixed color scale so 80 mm looks the same in every view'''
    if value is None or value <= 0:
        return (232, 230, 224)
    stops = (
        (0, (232, 230, 224)),
        (15, (255, 236, 196)),
        (40, (247, 184, 96)),
        (80, (224, 96, 62)),
        (130, (176, 42, 40)),
        (200, (110, 18, 28)),
        (250, (64, 8, 16)),
    )
    if value >= stops[-1][0]:
        return stops[-1][1]
    for index in range(1, len(stops)):
        start_value, start_color = stops[index - 1]
        end_value, end_color = stops[index]
        if value <= end_value:
            span = end_value - start_value
            blend = (value - start_value) / span
            channels = []
            for channel in range(3):
                start = start_color[channel]
                end = end_color[channel]
                channels.append(int(start + (end - start) * blend))
            return tuple(channels)
    return stops[-1][1]


#------------------------------------------------------------------------------
def readable_ink(color):
    '''dark text on pale cells, light text on deep red'''
    luminance = (color[0] * 0.30) + (color[1] * 0.59) + (color[2] * 0.11)
    if luminance < 150:
        return (255, 248, 242)
    return INK


#------------------------------------------------------------------------------
def text_width(font, text):
    if text == '':
        return 0
    return font.get_rect(text).width


#------------------------------------------------------------------------------
def fit_text(font, text, max_width):
    '''truncate with an ellipsis so a label stays inside its cell'''
    if text is None:
        text = ''
    if text_width(font, text) <= max_width:
        return text
    trimmed = text
    while trimmed and text_width(font, trimmed + '...') > max_width:
        trimmed = trimmed[:-1]
    return trimmed + '...'


#------------------------------------------------------------------------------
def wrap_text(font, text, max_width):
    '''word wrap. long single words are truncated'''
    lines = []
    current = ''
    for word in text.split(' '):
        trial = word if current == '' else current + ' ' + word
        if text_width(font, trial) <= max_width:
            current = trial
            continue
        if current != '':
            lines.append(current)
        if text_width(font, word) <= max_width:
            current = word
        else:
            lines.append(fit_text(font, word, max_width))
            current = ''
    if current != '':
        lines.append(current)
    return lines


#------------------------------------------------------------------------------
def curve_flags(row):
    '''short review notes that are properties of the stored columns'''
    flags = []
    pen = row['pen']
    for index in range(1, len(pen)):
        if pen[index] > pen[index - 1]:
            flags.append('penetration rises at ' + str(RANGE_COLUMNS[index]))
            break
    effect = row['contact_effect']
    if effect not in ('none', 'explosion', 'internal_burst'):
        flags.append('contact effect spawns ' + effect)
    return flags


#------------------------------------------------------------------------------
def series_end(pen):
    '''last index to draw. keep the first zero so the drop off the chart is visible'''
    if not any(value > 0 for value in pen):
        return 0
    last = len(pen) - 1
    while last > 0 and pen[last] <= 0:
        last -= 1
    return min(len(pen) - 1, last + 1)


#------------------------------------------------------------------------------
def axis_max(peak):
    '''round the penetration axis up so small arms and cannon shots both read.

    A 4% pad keeps the top point off the border. 237 mm stays on a 250 axis.
    '''
    padded = max(peak, 1) * 1.04
    for limit in (10, 20, 40, 60, 80, 100, 120, 150, 200, 250):
        if padded <= limit:
            return limit
    return int(math.ceil(padded / 50.0) * 50)


#------------------------------------------------------------------------------
def y_tick_step(y_max):
    if y_max <= 20:
        return 5
    if y_max <= 80:
        return 10
    if y_max <= 120:
        return 20
    return 50


#------------------------------------------------------------------------------
def draw_dashed_hline(surface, color, x0, x1, y, dash=7, gap=5):
    x = int(x0)
    x1 = int(x1)
    y = int(y)
    while x < x1:
        pygame.draw.line(surface, color, (x, y), (min(x + dash, x1), y), 1)
        x += dash + gap


#------------------------------------------------------------------------------
class ProjectileReview():
    '''pygame browser for projectile_data penetration columns'''

    def __init__(self, rows, visible):
        pygame.init()
        pygame.freetype.init()
        self.rows = rows
        self.by_name = {}
        for row in rows:
            self.by_name[row['name']] = row

        self.filter_text = ''
        self.filter_use = 'all'
        self.filter_size = 'all'
        self.mode = 'curves'
        self.armor_guides = True
        self.plotted = []
        self.focus_name = None
        self.sort_column = 'diameter'
        self.sort_reverse = False
        self.scroll = 0
        self.status = ''
        self.hover_distance = None
        self.plot_box = None
        self.y_max = None
        self.hot = []
        self.quit = False

        if visible:
            self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
            pygame.display.set_caption('TWE projectile data')
            pygame.key.set_repeat(400, 50)
            self.clock = pygame.time.Clock()
        else:
            self.screen = pygame.Surface((SCREEN_W, SCREEN_H))
            self.clock = None

        # None picks a real system font. get_default_font() warns on this machine
        self.font = pygame.freetype.SysFont(None, 14)
        self.font_small = pygame.freetype.SysFont(None, 12)
        self.font_title = pygame.freetype.SysFont(None, 20)
        self.font_value = pygame.freetype.SysFont(None, 16)

    #--------------------------------------------------------------------------
    def sort_value(self, row):
        key = self.sort_column
        if key == 'name':
            return row['name'].lower()
        if key == 'diameter':
            return row['diameter_value']
        if key == 'use':
            return row['use']
        if key == 'contact_effect':
            return row['contact_effect']
        if key == 'last_positive':
            if row['last_positive'] is None:
                return -1
            return row['last_positive']
        if key in [str(distance) for distance in RANGE_COLUMNS]:
            return row['pen'][RANGE_COLUMNS.index(int(key))]
        return row['name'].lower()

    #--------------------------------------------------------------------------
    def ordered_rows(self):
        rows = list(self.rows)
        rows.sort(
            key=lambda row: (self.sort_value(row), row['name'].lower()),
            reverse=self.sort_reverse,
        )
        return rows

    #--------------------------------------------------------------------------
    def matches(self, row, query):
        haystack = ' '.join([
            row['name'],
            str(row['projectile_material']),
            str(row['case_material']),
            str(row['contact_effect']),
            str(row['use']),
            str(row['notes'] or ''),
            format_diameter(row['diameter_value']),
            str(row['id']),
        ]).lower()
        return query in haystack

    #--------------------------------------------------------------------------
    def filtered_rows(self):
        query = self.filter_text.strip().lower()
        result = []
        for row in self.ordered_rows():
            if self.filter_use != 'all' and row['use'] != self.filter_use:
                continue
            diameter = row['diameter_value']
            if self.filter_size == 'small' and diameter >= 20:
                continue
            if self.filter_size == 'cannon' and diameter < 20:
                continue
            if query and self.matches(row, query) is False:
                continue
            result.append(row)
        return result

    #--------------------------------------------------------------------------
    def rows_on_screen(self):
        if self.mode == 'table':
            return max(1, (BODY_H - TABLE_HEADER_H) // TABLE_ROW_H)
        return max(1, (BODY_H - LIST_HEADER_H) // LIST_ROW_H)

    #--------------------------------------------------------------------------
    def clamp_scroll(self):
        window = self.rows_on_screen()
        limit = max(0, len(self.filtered_rows()) - window)
        if self.scroll < 0:
            self.scroll = 0
        if self.scroll > limit:
            self.scroll = limit

    #--------------------------------------------------------------------------
    def reveal_focus(self):
        names = [row['name'] for row in self.filtered_rows()]
        if self.focus_name not in names:
            return
        index = names.index(self.focus_name)
        window = self.rows_on_screen()
        if index < self.scroll:
            self.scroll = index
        elif index >= self.scroll + window:
            self.scroll = index - window + 1

    #--------------------------------------------------------------------------
    def move_focus(self, delta):
        rows = self.filtered_rows()
        if not rows:
            return
        names = [row['name'] for row in rows]
        if self.focus_name in names:
            index = names.index(self.focus_name) + delta
            index = max(0, min(len(names) - 1, index))
        elif delta < 0:
            index = len(names) - 1
        else:
            index = 0
        self.focus_name = names[index]
        self.reveal_focus()

    #--------------------------------------------------------------------------
    def plot_only(self, name):
        self.plotted = [name]
        self.focus_name = name
        self.status = ''

    #--------------------------------------------------------------------------
    def plot_toggle(self, name):
        self.focus_name = name
        if name in self.plotted:
            self.plotted.remove(name)
            self.status = ''
            return
        if len(self.plotted) >= MAX_PLOT:
            self.status = 'limit is ' + str(MAX_PLOT) + ' curves. remove one first'
            return
        self.plotted.append(name)
        self.status = ''

    #--------------------------------------------------------------------------
    def plot_visible(self):
        rows = self.filtered_rows()
        if not rows:
            self.status = 'nothing matches the filter'
            return
        self.plotted = [row['name'] for row in rows[:MAX_PLOT]]
        self.focus_name = self.plotted[0]
        if len(rows) > MAX_PLOT:
            self.status = (
                'plotted ' + str(MAX_PLOT) + ' of ' + str(len(rows))
                + ' matching rounds. narrow the filter to see the rest'
            )
        else:
            self.status = ''

    #--------------------------------------------------------------------------
    def color_for(self, name):
        if name not in self.plotted:
            return None
        return PLOT_COLORS[self.plotted.index(name) % len(PLOT_COLORS)]

    #--------------------------------------------------------------------------
    def set_sort(self, key):
        if self.sort_column == key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = key
            # text reads A to Z first. numbers read high to low first
            self.sort_reverse = key not in ('name', 'use', 'contact_effect')
        self.scroll = 0

    #--------------------------------------------------------------------------
    def mark_header(self, rect, key):
        '''tint the sorted column. a text arrow does not fit in the range columns'''
        if self.sort_column != key:
            return
        pygame.draw.rect(self.screen, (214, 226, 236), rect)
        pygame.draw.line(
            self.screen, ACCENT,
            (rect.left, rect.bottom - 1), (rect.right, rect.bottom - 1), 2,
        )

    #--------------------------------------------------------------------------
    def hit(self, pos):
        for rect, action, payload in reversed(self.hot):
            if rect.collidepoint(pos):
                return action, payload
        return None, None

    #--------------------------------------------------------------------------
    def handle_click(self, pos, toggle):
        action, payload = self.hit(pos)
        if action is None:
            return
        if action == 'use':
            self.filter_use = payload
            self.scroll = 0
        elif action == 'size':
            self.filter_size = payload
            self.scroll = 0
        elif action == 'mode':
            self.mode = payload
            self.hover_distance = None
            self.reveal_focus()
        elif action == 'armor':
            self.armor_guides = not self.armor_guides
        elif action == 'plot_visible':
            self.plot_visible()
        elif action == 'sort':
            self.set_sort(payload)
        elif action == 'row':
            if toggle:
                self.plot_toggle(payload)
            else:
                self.plot_only(payload)
        elif action == 'focus':
            self.focus_name = payload

    #--------------------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
            return
        if event.type == pygame.TEXTINPUT:
            mods = pygame.key.get_mods()
            if mods & (pygame.KMOD_CTRL | pygame.KMOD_META):
                return
            self.filter_text += event.text
            self.scroll = 0
            return
        if event.type == pygame.MOUSEWHEEL:
            self.scroll -= event.y
            self.clamp_scroll()
            return
        if event.type == pygame.MOUSEMOTION:
            self.hover_distance = self.hover_column(event.pos)
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mods = pygame.key.get_mods()
                toggle = bool(mods & (pygame.KMOD_SHIFT | pygame.KMOD_CTRL | pygame.KMOD_META))
                self.handle_click(event.pos, toggle)
            elif event.button == 3:
                self.handle_click(event.pos, True)
            return
        if event.type != pygame.KEYDOWN:
            return

        mods = event.mod
        if event.key == pygame.K_q and (mods & (pygame.KMOD_CTRL | pygame.KMOD_META)):
            self.quit = True
        elif event.key == pygame.K_p and (mods & (pygame.KMOD_CTRL | pygame.KMOD_META)):
            self.plot_visible()
        elif event.key == pygame.K_ESCAPE:
            if self.filter_text:
                self.filter_text = ''
                self.scroll = 0
            else:
                self.plotted = []
                self.status = ''
        elif event.key == pygame.K_BACKSPACE:
            self.filter_text = self.filter_text[:-1]
            self.scroll = 0
        elif event.key == pygame.K_DOWN:
            self.move_focus(1)
        elif event.key == pygame.K_UP:
            self.move_focus(-1)
        elif event.key == pygame.K_PAGEUP:
            self.move_focus(-self.rows_on_screen())
        elif event.key == pygame.K_PAGEDOWN:
            self.move_focus(self.rows_on_screen())
        elif event.key == pygame.K_HOME:
            self.scroll = 0
            rows = self.filtered_rows()
            if rows:
                self.focus_name = rows[0]['name']
        elif event.key == pygame.K_END:
            rows = self.filtered_rows()
            if rows:
                self.focus_name = rows[-1]['name']
                self.reveal_focus()
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.focus_name is None:
                return
            if mods & pygame.KMOD_SHIFT:
                self.plot_toggle(self.focus_name)
            else:
                self.plot_only(self.focus_name)

    #--------------------------------------------------------------------------
    def blit(self, font, text, pos, color):
        if text is None or text == '':
            return 0
        rendered, _rect = font.render(text, fgcolor=color)
        self.screen.blit(rendered, pos)
        return rendered.get_width()

    #--------------------------------------------------------------------------
    def blit_in(self, font, text, rect, color, align):
        if text is None:
            text = ''
        rendered, _rect = font.render(text, fgcolor=color)
        if align == 'center':
            x = rect.x + (rect.width - rendered.get_width()) // 2
        elif align == 'right':
            x = rect.right - rendered.get_width() - 6
        else:
            x = rect.x + 6
        y = rect.y + (rect.height - rendered.get_height()) // 2
        self.screen.blit(rendered, (x, y))

    #--------------------------------------------------------------------------
    def chip(self, label, x, y, active, action, payload):
        width = text_width(self.font, label) + 18
        rect = pygame.Rect(x, y, width, 26)
        if active:
            fill = ACCENT
            color = WHITE
            border = ACCENT
        else:
            fill = WHITE
            color = INK
            border = LINE
        pygame.draw.rect(self.screen, fill, rect, border_radius=5)
        pygame.draw.rect(self.screen, border, rect, 1, border_radius=5)
        self.blit_in(self.font, label, rect, color, 'center')
        self.hot.append((rect, action, payload))
        return width

    #--------------------------------------------------------------------------
    def render_top(self):
        self.blit(self.font_title, 'projectile data', (MARGIN, 12), INK)
        shown = len(self.filtered_rows())
        count = str(shown) + ' of ' + str(len(self.rows)) + ' shown'
        if self.plotted:
            count += '    ' + str(len(self.plotted)) + ' plotted'
        self.blit(self.font_small, count, (MARGIN, 42), MUTED)
        # status is drawn on the help line so a long warning has the full width

        search = pygame.Rect(210, 14, 270, 26)
        pygame.draw.rect(self.screen, WHITE, search, border_radius=5)
        pygame.draw.rect(self.screen, LINE, search, 1, border_radius=5)
        if self.filter_text:
            shown_text = fit_text(self.font, self.filter_text, search.width - 16)
            color = INK
        else:
            shown_text = 'name, material, notes'
            color = MUTED
        self.blit(self.font, shown_text, (search.x + 8, search.y + 5), color)
        if self.filter_text:
            caret_x = search.x + 8 + text_width(self.font, shown_text) + 1
            pygame.draw.line(
                self.screen, ACCENT,
                (caret_x, search.y + 5), (caret_x, search.bottom - 5), 1,
            )

        x = search.right + 12
        for value, label in (('all', 'all'), ('ap', 'ap'), ('at', 'at'), ('both', 'both')):
            x += self.chip(label, x, 14, self.filter_use == value, 'use', value) + 6

        mode_labels = (('curves', 'curves'), ('table', 'table'))
        mode_widths = [text_width(self.font, label) + 18 for _value, label in mode_labels]
        mode_x = SCREEN_W - MARGIN - sum(mode_widths) - 6 * (len(mode_labels) - 1)
        for index, (value, label) in enumerate(mode_labels):
            self.chip(label, mode_x, 14, self.mode == value, 'mode', value)
            mode_x += mode_widths[index] + 6

        x = 210
        size_items = (
            ('all', 'all calibers'),
            ('small', '< 20 mm'),
            ('cannon', '>= 20 mm'),
        )
        for value, label in size_items:
            x += self.chip(label, x, 50, self.filter_size == value, 'size', value) + 6

        right_labels = []
        if self.armor_guides:
            right_labels.append(('armor lines', 'armor', True))
        else:
            right_labels.append(('armor lines', 'armor', False))
        plot_label = 'plot shown (' + str(shown) + ')'
        right_labels.append((plot_label, 'plot_visible', False))
        right_widths = [text_width(self.font, label) + 18 for label, _action, _active in right_labels]
        right_x = SCREEN_W - MARGIN - sum(right_widths) - 6
        for index, (label, action, active) in enumerate(right_labels):
            self.chip(label, right_x, 50, active, action, None)
            right_x += right_widths[index] + 6

    #--------------------------------------------------------------------------
    def list_header_rects(self, panel):
        '''column headers inside the round list. values are (key, label, rect)'''
        y = panel.y
        height = LIST_HEADER_H
        specs = (
            ('name', 'name', 10, 236),
            ('diameter', 'mm', 246, 48),
            ('use', 'use', 294, 44),
            ('0', 'pen0', 338, 64),
            ('last_positive', 'holds', 402, 64),
        )
        headers = []
        for key, label, x, width in specs:
            rect = pygame.Rect(panel.x + x, y, width, height)
            headers.append((key, label, rect))
        return headers

    #--------------------------------------------------------------------------
    def render_list(self):
        panel = pygame.Rect(MARGIN, BODY_Y, LIST_W, BODY_H)
        pygame.draw.rect(self.screen, PANEL, panel)
        pygame.draw.rect(self.screen, LINE, panel, 1)

        for key, label, rect in self.list_header_rects(panel):
            self.mark_header(rect, key)
            self.blit_in(self.font_small, label, rect, MUTED, 'left')
            self.hot.append((rect, 'sort', key))
        pygame.draw.line(
            self.screen, LINE,
            (panel.x, panel.y + LIST_HEADER_H),
            (panel.right, panel.y + LIST_HEADER_H),
            1,
        )

        rows = self.filtered_rows()
        body = pygame.Rect(panel.x, panel.y + LIST_HEADER_H, panel.width, panel.height - LIST_HEADER_H)
        self.screen.set_clip(body)
        y = body.y
        for row in rows[self.scroll:]:
            if y + LIST_ROW_H > body.bottom:
                break
            row_rect = pygame.Rect(panel.x + 1, y, panel.width - 2, LIST_ROW_H)
            color = self.color_for(row['name'])
            if row['name'] == self.focus_name:
                pygame.draw.rect(self.screen, FOCUS, row_rect)
            if color is not None:
                pygame.draw.rect(
                    self.screen, color,
                    pygame.Rect(panel.x + 1, y + 3, 8, LIST_ROW_H - 6),
                )
            name = fit_text(self.font, row['name'], 220)
            name_color = INK
            if color is not None:
                name_color = color
            self.blit(self.font, name, (panel.x + 14, y + 4), name_color)
            self.blit_in(
                self.font_small,
                format_diameter(row['diameter_value']),
                pygame.Rect(panel.x + 246, y, 48, LIST_ROW_H),
                MUTED, 'left',
            )
            self.blit_in(
                self.font_small, row['use'],
                pygame.Rect(panel.x + 294, y, 44, LIST_ROW_H),
                MUTED, 'left',
            )
            pen0 = str(row['pen'][0])
            self.blit_in(
                self.font, pen0,
                pygame.Rect(panel.x + 338, y, 64, LIST_ROW_H),
                INK, 'left',
            )
            if row['last_positive'] is None:
                hold = '-'
            else:
                hold = str(row['last_positive'])
            self.blit_in(
                self.font_small, hold,
                pygame.Rect(panel.x + 402, y, 64, LIST_ROW_H),
                MUTED, 'left',
            )
            self.hot.append((row_rect, 'row', row['name']))
            y += LIST_ROW_H
        self.screen.set_clip(None)

        if not rows:
            self.blit(self.font, 'no rounds match', (panel.x + 14, body.y + 12), MUTED)

    #--------------------------------------------------------------------------
    def table_columns(self, panel):
        range_w = 50
        range_total = range_w * len(RANGE_COLUMNS)
        fixed_rest = panel.width - range_total
        name_w = int(fixed_rest * 0.46)
        mm_w = 52
        use_w = 46
        effect_w = fixed_rest - name_w - mm_w - use_w
        columns = [
            ('name', 'name', name_w),
            ('diameter', 'mm', mm_w),
            ('use', 'use', use_w),
            ('contact_effect', 'effect', effect_w),
        ]
        for distance in RANGE_COLUMNS:
            columns.append((str(distance), str(distance), range_w))
        laid = []
        x = panel.x
        for key, label, width in columns:
            # give leftover pixels to the last range column
            laid.append((key, label, pygame.Rect(x, panel.y, width, TABLE_HEADER_H)))
            x += width
        overflow = panel.right - x
        if laid and overflow != 0:
            last = laid[-1][2]
            laid[-1] = (laid[-1][0], laid[-1][1], pygame.Rect(last.x, last.y, last.width + overflow, last.height))
        return laid

    #--------------------------------------------------------------------------
    def render_table(self):
        panel = pygame.Rect(MARGIN, BODY_Y, SCREEN_W - MARGIN * 2, BODY_H)
        pygame.draw.rect(self.screen, PANEL, panel)
        pygame.draw.rect(self.screen, LINE, panel, 1)
        columns = self.table_columns(panel)

        for key, label, rect in columns:
            self.hot.append((rect, 'sort', key))
            self.mark_header(rect, key)
            if key in ('name', 'contact_effect'):
                align = 'left'
            else:
                align = 'center'
            self.blit_in(self.font_small, label, pygame.Rect(rect.x, rect.y, rect.width, 20), MUTED, align)
            if key.isdigit():
                meters = str(int(key) // 2) + ' m'
                meter_rect = pygame.Rect(rect.x, rect.y + 18, rect.width, 18)
                self.blit_in(self.font_small, meters, meter_rect, (168, 164, 156), 'center')
        pygame.draw.line(
            self.screen, LINE,
            (panel.x, panel.y + TABLE_HEADER_H),
            (panel.right, panel.y + TABLE_HEADER_H),
            1,
        )

        rows = self.filtered_rows()
        body = pygame.Rect(panel.x, panel.y + TABLE_HEADER_H, panel.width, panel.height - TABLE_HEADER_H)
        self.screen.set_clip(body)
        y = body.y
        for row in rows[self.scroll:]:
            if y + TABLE_ROW_H > body.bottom:
                break
            row_rect = pygame.Rect(panel.x + 1, y, panel.width - 2, TABLE_ROW_H)
            if row['name'] == self.focus_name:
                pygame.draw.rect(self.screen, FOCUS, row_rect)
            color = self.color_for(row['name'])
            if color is not None:
                pygame.draw.rect(self.screen, color, pygame.Rect(panel.x + 1, y + 3, 8, TABLE_ROW_H - 6))
            for key, _label, header in columns:
                cell = pygame.Rect(header.x, y, header.width, TABLE_ROW_H)
                if key == 'name':
                    label = fit_text(self.font_small, row['name'], cell.width - 16)
                    ink = color if color is not None else INK
                    self.blit_in(self.font_small, label, cell, ink, 'left')
                elif key == 'diameter':
                    self.blit_in(self.font_small, format_diameter(row['diameter_value']), cell, INK, 'center')
                elif key == 'use':
                    self.blit_in(self.font_small, row['use'], cell, INK, 'center')
                elif key == 'contact_effect':
                    label = fit_text(self.font_small, row['contact_effect'], cell.width - 10)
                    self.blit_in(self.font_small, label, cell, MUTED, 'left')
                else:
                    value = row['pen'][RANGE_COLUMNS.index(int(key))]
                    fill = heat_color(value)
                    inset = pygame.Rect(cell.x + 1, cell.y + 1, cell.width - 2, cell.height - 2)
                    pygame.draw.rect(self.screen, fill, inset)
                    self.blit_in(self.font_small, str(value), cell, readable_ink(fill), 'center')
            self.hot.append((row_rect, 'row', row['name']))
            y += TABLE_ROW_H
        self.screen.set_clip(None)
        if not rows:
            self.blit(self.font, 'no rounds match', (panel.x + 14, body.y + 12), MUTED)

    #--------------------------------------------------------------------------
    def layout_legend(self, width):
        chips = []
        if not self.plotted:
            return chips, 0
        x = 0
        y = 0
        line_h = 20
        for name in self.plotted:
            label = name
            chip_w = 22 + text_width(self.font_small, label)
            if chip_w > width:
                label = fit_text(self.font_small, label, width - 22)
                chip_w = width
            if x > 0 and x + chip_w > width:
                x = 0
                y += line_h
            chips.append((name, label, x, y, chip_w))
            x += chip_w + 8
        return chips, y + line_h

    #--------------------------------------------------------------------------
    def hover_column(self, pos):
        box = self.plot_box
        if box is None or box.collidepoint(pos) is False:
            return None
        if box.width <= 0:
            return None
        fraction = (pos[0] - box.left) / box.width
        fraction = min(1, max(0, fraction))
        distance = fraction * RANGE_COLUMNS[-1]
        nearest = RANGE_COLUMNS[0]
        nearest_gap = abs(distance - nearest)
        for value in RANGE_COLUMNS:
            gap = abs(distance - value)
            if gap < nearest_gap:
                nearest = value
                nearest_gap = gap
        return nearest

    #--------------------------------------------------------------------------
    def chart_point(self, box, y_max, distance, pen):
        x = box.x + (distance / RANGE_COLUMNS[-1]) * box.width
        y = box.bottom - (pen / y_max) * box.height
        return (int(x), int(y))

    #--------------------------------------------------------------------------
    def render_chart(self):
        panel = pygame.Rect(MARGIN + LIST_W + 10, BODY_Y, SCREEN_W - LIST_W - MARGIN * 2 - 10, BODY_H)
        pygame.draw.rect(self.screen, PANEL, panel)
        pygame.draw.rect(self.screen, LINE, panel, 1)

        self.blit(self.font, 'penetration (mm)', (panel.x + 12, panel.y + 6), INK)
        legend, legend_h = self.layout_legend(panel.width - 24)
        legend_top = panel.y + 30
        for name, label, x, y, chip_w in legend:
            color = self.color_for(name)
            chip = pygame.Rect(panel.x + 12 + x, legend_top + y, chip_w, 18)
            if name == self.focus_name:
                pygame.draw.rect(self.screen, FOCUS, chip, border_radius=3)
            pygame.draw.rect(self.screen, color, pygame.Rect(chip.x, chip.y + 4, 10, 10))
            self.blit(self.font_small, label, (chip.x + 14, chip.y + 2), color)
            self.hot.append((chip, 'focus', name))

        if legend_h == 0:
            plot_top = panel.y + 32
        else:
            plot_top = legend_top + legend_h + 14

        caption_lines = wrap_text(self.font_small, SCALE_NOTE, panel.width - 70)
        caption_h = 14 * len(caption_lines)
        # left pad for the mm ticks, right pad for the armor-line labels
        plot = pygame.Rect(panel.x + 52, plot_top, panel.width - 52 - 40, panel.bottom - plot_top - caption_h - 40)
        plot.height = max(plot.height, 80)
        self.plot_box = plot

        peak = 0
        for name in self.plotted:
            for value in self.by_name[name]['pen']:
                if value > peak:
                    peak = value
        if not self.plotted:
            peak = 200
        y_max = axis_max(peak)
        self.y_max = y_max

        pygame.draw.rect(self.screen, WHITE, plot)
        pygame.draw.rect(self.screen, LINE, plot, 1)

        step = y_tick_step(y_max)
        value = 0
        while value <= y_max:
            y = self.chart_point(plot, y_max, 0, value)[1]
            pygame.draw.line(self.screen, GRID, (plot.left, y), (plot.right, y), 1)
            label = str(value)
            self.blit(
                self.font_small, label,
                (plot.left - 8 - text_width(self.font_small, label), y - 7),
                MUTED,
            )
            value += step

        for distance in RANGE_COLUMNS:
            x = self.chart_point(plot, y_max, distance, 0)[0]
            pygame.draw.line(self.screen, GRID, (x, plot.top), (x, plot.bottom), 1)
            if distance % 1000 == 0:
                label = str(distance)
                self.blit(
                    self.font_small, label,
                    (x - text_width(self.font_small, label) // 2, plot.bottom + 4),
                    MUTED,
                )
                meters = str(distance // 2) + ' m'
                self.blit(
                    self.font_small, meters,
                    (x - text_width(self.font_small, meters) // 2, plot.bottom + 18),
                    (168, 164, 156),
                )

        if self.armor_guides:
            last_label_y = -100
            for thickness in ARMOR_GUIDES:
                if thickness >= y_max:
                    continue
                y = self.chart_point(plot, y_max, 0, thickness)[1]
                draw_dashed_hline(self.screen, (186, 150, 132), plot.left, plot.right, y)
                if abs(y - last_label_y) < 12:
                    continue
                label = str(thickness)
                self.blit(self.font_small, label, (plot.right + 6, y - 8), (160, 110, 90))
                last_label_y = y

        if not self.plotted:
            hint = 'Click a round to plot its penetration. Shift-click to compare.'
            hint_x = plot.centerx - text_width(self.font, hint) // 2
            self.blit(self.font, hint, (hint_x, plot.centery - 8), MUTED)
        else:
            ordered = [name for name in self.plotted if name != self.focus_name]
            if self.focus_name in self.plotted:
                ordered.append(self.focus_name)
            for name in ordered:
                row = self.by_name[name]
                end = series_end(row['pen'])
                points = []
                for index in range(end + 1):
                    points.append(self.chart_point(plot, y_max, RANGE_COLUMNS[index], row['pen'][index]))
                width = 3 if name == self.focus_name else 2
                if len(points) >= 2:
                    pygame.draw.lines(self.screen, self.color_for(name), False, points, width)
                for point in points:
                    pygame.draw.circle(self.screen, self.color_for(name), point, 3)

        for index, line in enumerate(caption_lines):
            self.blit(self.font_small, line, (plot.x, plot.bottom + 36 + index * 14), MUTED)

        self.render_hover(plot, y_max)

    #--------------------------------------------------------------------------
    def render_hover(self, plot, y_max):
        if self.hover_distance is None or self.mode != 'curves':
            return
        if self.plot_box is None:
            return
        x = self.chart_point(plot, y_max, self.hover_distance, 0)[0]
        pygame.draw.line(self.screen, ACCENT, (x, plot.top), (x, plot.bottom), 1)
        meters = self.hover_distance // 2
        lines = [str(self.hover_distance) + ' units, about ' + str(meters) + ' m for cannon rows']
        colors = [ACCENT]
        for name in self.plotted:
            row = self.by_name[name]
            value = row['pen'][RANGE_COLUMNS.index(self.hover_distance)]
            lines.append(name + '  ' + str(value) + ' mm')
            colors.append(self.color_for(name))
        width = 0
        for line in lines:
            width = max(width, text_width(self.font_small, line))
        box_w = width + 16
        box_h = 8 + 16 * len(lines)
        box_x = x + 10
        if box_x + box_w > plot.right:
            box_x = x - box_w - 10
        box_y = plot.top + 8
        box = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(self.screen, WHITE, box)
        pygame.draw.rect(self.screen, LINE, box, 1)
        for index, line in enumerate(lines):
            self.blit(self.font_small, line, (box.x + 8, box.y + 4 + index * 16), colors[index])

    #--------------------------------------------------------------------------
    def render_detail(self):
        rect = pygame.Rect(MARGIN, DETAIL_Y, SCREEN_W - MARGIN * 2, DETAIL_H)
        pygame.draw.rect(self.screen, PANEL, rect)
        pygame.draw.rect(self.screen, LINE, rect, 1)
        row = None
        if self.focus_name is not None:
            row = self.by_name.get(self.focus_name)
        if row is None:
            self.blit(self.font, 'Select a round.', (rect.x + 12, rect.y + 12), MUTED)
            return

        color = self.color_for(row['name'])
        name_color = color if color is not None else INK
        self.blit(self.font_title, row['name'], (rect.x + 12, rect.y + 8), name_color)

        stats = '   '.join([
            format_diameter(row['diameter_value']) + ' mm',
            str(row['projectile_material']),
            str(row['case_material']) + ' case',
            str(row['grain_weight']) + ' gr',
            str(row['velocity']) + ' ft/s',
            'use ' + str(row['use']),
            str(row['contact_effect']),
            'shrapnel ' + str(row['shrapnel_count']),
            'blast ' + str(row['explosion_radius']),
            'id ' + str(row['id']),
        ])
        self.blit(
            self.font_small,
            fit_text(self.font_small, stats, rect.width - 24),
            (rect.x + 12, rect.y + 34),
            INK,
        )

        note_y = rect.y + 52
        notes = row['notes'] or ''
        flags = curve_flags(row)
        if notes:
            wrapped = wrap_text(self.font_small, notes, rect.width - 24)
            for line in wrapped[:2]:
                self.blit(self.font_small, line, (rect.x + 12, note_y), MUTED)
                note_y += 14
        if flags:
            self.blit(self.font_small, '   '.join(flags), (rect.x + 12, note_y), WARN)

        cell_top = rect.bottom - 58
        label_w = 44
        cell_w = (rect.width - 24 - label_w) // len(RANGE_COLUMNS)
        self.blit(self.font_small, 'mm', (rect.x + 12, cell_top + 24), MUTED)
        for index, distance in enumerate(RANGE_COLUMNS):
            cell_x = rect.x + 12 + label_w + index * cell_w
            header = pygame.Rect(cell_x, cell_top, cell_w - 4, 16)
            self.blit_in(self.font_small, str(distance), header, MUTED, 'center')
            value = row['pen'][index]
            fill = heat_color(value)
            value_rect = pygame.Rect(cell_x, cell_top + 18, cell_w - 4, 26)
            pygame.draw.rect(self.screen, fill, value_rect, border_radius=3)
            if self.mode == 'curves' and distance == self.hover_distance:
                pygame.draw.rect(self.screen, ACCENT, value_rect, 2, border_radius=3)
            self.blit_in(self.font_value, str(value), value_rect, readable_ink(fill), 'center')

    #--------------------------------------------------------------------------
    def render_help(self):
        if self.status:
            self.blit(self.font_small, self.status, (MARGIN, SCREEN_H - 18), WARN)
            return
        help_text = (
            'click: plot one    shift-click or right-click: compare    '
            'ctrl-p: plot shown    arrows: move    enter: plot    '
            'esc: clear filter, then clear curves    ctrl-q: quit    '
            'holds: last column still above 0'
        )
        self.blit(self.font_small, help_text, (MARGIN, SCREEN_H - 18), MUTED)

    #--------------------------------------------------------------------------
    def render(self):
        self.hot = []
        self.clamp_scroll()
        self.screen.fill(BG)
        self.render_top()
        if self.mode == 'table':
            self.plot_box = None
            self.render_table()
        else:
            self.render_list()
            self.render_chart()
        self.render_detail()
        self.render_help()
        if self.clock is not None:
            pygame.display.flip()


#------------------------------------------------------------------------------
def print_usage():
    print('Usage: python projectile_data_tool.py [data.sqlite]')
    print('  python3 code/tools/projectile_data_tool.py')
    print('Opens a chart and table of projectile_data penetration columns.')


#------------------------------------------------------------------------------
def run_check(tool, folder):
    '''draw a few views to png files without opening a window'''
    tool.plot_only('PzGr39_75_L48')
    tool.plot_toggle('PzGr40_75_L48')
    tool.plot_toggle('PzGr39_88_L71')
    tool.plot_toggle('BR-365P')
    tool.plot_toggle('panzerfaust_100_HEAT')
    tool.focus_name = 'PzGr39_88_L71'
    tool.hover_distance = 2000
    tool.render()
    curves_path = os.path.join(folder, 'projectile_curves.png')
    pygame.image.save(tool.screen, curves_path)

    tool.plotted = []
    tool.filter_text = '7.92'
    tool.plot_visible()
    tool.hover_distance = None
    tool.render()
    small_path = os.path.join(folder, 'projectile_small.png')
    pygame.image.save(tool.screen, small_path)

    tool.mode = 'table'
    tool.filter_text = ''
    tool.set_sort('0')
    tool.focus_name = 'PzGr39_88_L71'
    tool.render()
    table_path = os.path.join(folder, 'projectile_table.png')
    pygame.image.save(tool.screen, table_path)
    print(curves_path)
    print(small_path)
    print(table_path)
    print('rounds ' + str(len(tool.rows)))


#------------------------------------------------------------------------------
def main():
    check = False
    path = database_path()
    for arg in sys.argv[1:]:
        if arg == '--check':
            check = True
        elif arg in ('-h', '--help'):
            print_usage()
            return
        else:
            path = arg

    rows = load_projectiles(path)
    tool = ProjectileReview(rows, visible=not check)
    if check:
        folder = os.environ.get('PROJECTILE_TOOL_OUT', '/tmp')
        run_check(tool, folder)
        return

    while tool.quit is False:
        for event in pygame.event.get():
            tool.handle_event(event)
        tool.render()
        tool.clock.tick(30)


if __name__ == '__main__':
    main()
