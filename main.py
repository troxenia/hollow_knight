import pygame
import os
import sys

pygame.init()
screen_size = WIDTH, HEIGHT = (550, 550)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Hollow Knight')
clock = pygame.time.Clock()
FPS = 50
tile_width = tile_height = 50
tile_images = {'empty': 'empty.jpg'}

tiles = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
coins = pygame.sprite.Group()
enemies = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except FileNotFoundError as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


def load_level(filename):
    filename = 'data/' + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(level):
    hero, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile(x, y, tile_images['empty'])
            elif level[y][x] == '@':
                Tile(x, y, tile_images['empty'])
                hero = Knight(x, y)
                level[y][x] = '.'
            elif level[y][x] == '#':
                Tile(x, y, tile_images['empty'])
                CrystalEnemy(x, y)
                level[y][x] = '.'
    return hero, x, y


def close():
    pygame.quit()
    sys.exit()


def display_text(text: list, text_coord: int, font=pygame.font.Font(None, 30), color=pygame.Color('white')):
    for line in text:
        string_rendered = font.render(line, True, color)
        text_rect = string_rendered.get_rect()
        text_coord += 10
        text_rect.top = text_coord
        text_rect.x = 10
        text_coord += text_rect.height
        screen.blit(string_rendered, text_rect)


class Button:  # class for buttons on operational screens: opening, closing, levels, etc.

    def __init__(self, x, y, width, height, action, color=(248, 222, 173)):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.color = color
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=5)
        font = pygame.font.Font(None, 30)
        string_rendered = font.render(self.action, True, (0, 0, 0))
        string_rect = (self.x, self.y + 5)
        screen.blit(string_rendered, string_rect)

    def update(self, event):  # update when clicked
        if self.x <= event.pos[0] <= self.x + self.width and self.y <= event.pos[1] <= self.y + self.height:
            return self.action


class Tile(pygame.sprite.Sprite):

    def __init__(self, x, y, filename):
        super().__init__(tiles)
        self.image = load_image(filename)
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, group, x, y, sheet_dict):
        super().__init__(group)
        self.sheet_dict = dict()
        for name, value in sheet_dict.items():
            sheet, columns, rows = value
            self.frames = []
            self.cut_sheet(sheet, columns, rows)
            self.sheet_dict[name] = self.frames
        self.key = name
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x * tile_width, y * tile_height)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                for _ in range(3):  # slow down frames
                    self.frames.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))

    def switch_frames(self, key):
        if key == self.key:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        else:
            self.key = key
            self.frames = self.sheet_dict[self.key]
            self.cur_frame = 0
        self.image = self.frames[self.cur_frame]

    def update(self):
        pass


class Knight(AnimatedSprite):

    def __init__(self, x, y):
        super().__init__(hero_group, x, y, {'right': (load_image('running_right.png'), 6, 1),
                                            'left': (load_image('running_left.png'), 6, 1),
                                            'up': (load_image('running_up.png'), 6, 1),
                                            'down': (load_image('running_down.png'), 6, 1)})

    def update(self):
        delta = 5
        if keys[pygame.K_LEFT]:
            super().switch_frames('left')
            self.rect.x -= delta
        elif keys[pygame.K_RIGHT]:
            super().switch_frames('right')
            self.rect.x += delta
        elif keys[pygame.K_UP]:
            super().switch_frames('up')
            self.rect.y -= delta
        elif keys[pygame.K_DOWN]:
            super().switch_frames('down')
            self.rect.y += delta
        # if pygame.sprite.spritecollideany(self, enemies):
        #     end_game()


class CrystalEnemy(AnimatedSprite):
    """Враг кристальный жук."""

    def __init__(self, x, y, turn='right'):
        super().__init__(enemies, x, y,
                         {'right': (load_image('going_right.png'), 5, 1), 'left': (load_image('going_left.png'), 5, 1)})
        self.turn = turn  # more flexible
        self.delta_x = 0
        self.vx = 2
        # Расстояние на которое в одну сторону пердвигается жук
        self.length = 60

    def update(self):
        if self.turn == 'right':
            if self.delta_x < self.length:
                self.rect.x += self.vx
                self.delta_x += self.vx
            else:
                self.turn = 'left'
        elif self.turn == 'left':
            if self.delta_x > 0:
                self.rect.x -= self.vx
                self.delta_x -= self.vx
            else:
                self.turn = 'right'
        super().switch_frames(self.turn)


class Menu:  # start, between levels (fail & success), end(?), rules, levels, etc.

    def __init__(self, background, widgets: list):
        self.widgets = widgets
        self.background = pygame.transform.scale(load_image(background), (WIDTH, HEIGHT))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    close()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for widget in self.widgets:
                        action = widget.update(event)
                        if action is not None:
                            return action
            for widget in self.widgets:
                widget.draw()
            pygame.display.flip()
            clock.tick(FPS)


class Start(Menu):

    def __init__(self, background, widgets: list):
        super().__init__(background, widgets)
        self.actions = ['start', 'help', 'levels']

    def run(self):
        screen.blit(self.background, (0, 0))
        intro_text = ['Game Name', '', '', 'Something else']
        font = pygame.font.Font(None, 30)  # change to aesthetically pleasing font + figure out size
        text_coord = 50  # figure out best text placement
        display_text(intro_text, text_coord, font)
        return super().run()


class Help(Menu):

    def __init__(self, background, widgets: list):
        super().__init__(background, widgets)
        self.actions = ['back']

    def run(self):
        screen.blit(self.background, (0, 0))
        help_text = ['Help', '', '', 'How to play']
        font = pygame.font.Font(None, 30)  # change to aesthetically pleasing font + figure out size
        text_coord = 50  # figure out best text placement
        display_text(help_text, text_coord, font)
        return super().run()


def game(level_map):
    global keys  # I really don't like this...
    level_map = load_level(level_map)
    hero, max_x, max_y = generate_level(level_map)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        hero.update()
        tiles.draw(screen)
        enemies.update()
        enemies.draw(screen)
        hero_group.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()


start_buttons = [Button(10, 300, 50, 30, 'start'), Button(80, 300, 50, 30, 'help'), Button(150, 300, 60, 30, 'levels')]
help_buttons = [Button(10, 10, 50, 30, 'back')]

screens = [Start('background.jpg', start_buttons), Help('background.jpg', help_buttons)]
cur_screen = screens[0]
action = cur_screen.run()
if action == 'start':
    keys = ()
    game('map.txt')
elif action == 'help':
    pass
pygame.quit()
