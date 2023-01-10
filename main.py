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

buttons = pygame.sprite.Group()
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


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ['Game Name', '', '', 'Something else']

    background = pygame.transform.scale(load_image('background.jpg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def end_game():  # end level
    terminate()  # заглушка


def load_level(filename):
    filename = 'data/' + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile(x, y, tile_images['empty'])
            elif level[y][x] == '@':
                Tile(x, y, tile_images['empty'])
                new_player = Knight(x, y)
                level[y][x] = '.'
    return new_player, x, y


class Sprite(pygame.sprite.Sprite):  # static sprites

    def __init__(self, group, x, y, filename):
        super().__init__(group)
        self.image = load_image(filename)
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)


class Button(Sprite):  # class for buttons on operational screens: opening, closing, levels, etc.

    def __init__(self, x, y):
        super().__init__(buttons, x, y, 'button.png')

    def update(self, event):  # update when clicked
        pass


class Tile(Sprite):

    def __init__(self, x, y, filename):
        super().__init__(tiles, x, y, filename)


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


start_screen()
level_map = load_level('map.txt')
hero, max_x, max_y = generate_level(level_map)
enemy1 = CrystalEnemy(1, 1)
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
pygame.quit()
