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
enemies = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
coins = pygame.sprite.Group()


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
                new_player = Knight(x, y, 6, 1)
                level[y][x] = '.'
    return new_player, x, y


class Sprite(pygame.sprite.Sprite):

    def __init__(self, group, x, y, filename):
        super().__init__(group)
        self.image = load_image(filename)
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)

    def update(self, event):  # move
        pass


class Button(Sprite):  # class for buttons on operational screens: opening, closing, levels, etc.

    def __init__(self, x, y):
        super().__init__(buttons, x, y, 'button.png')


class Tile(Sprite):

    def __init__(self, x, y, filename):
        super().__init__(tiles, x, y, filename)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, group, x, y, sheet, columns, rows):
        super().__init__(group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                for _ in range(3):
                    self.frames.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Knight(AnimatedSprite):

    def __init__(self, x, y, columns, rows):
        super().__init__(hero_group, x, y, load_image('running_right.png'), columns, rows)

    def update(self):
        delta = 5
        if keys[pygame.K_LEFT]:
            super().update()
            self.rect.x -= delta
        elif keys[pygame.K_RIGHT]:
            super().update()
            self.rect.x += delta
        elif keys[pygame.K_UP]:
            super().update()
            self.rect.y -= delta
        elif keys[pygame.K_DOWN]:
            super().update()
            self.rect.y += delta
        # if pygame.sprite.spritecollideany(self, enemies):
        #     end_game()


class Enemy(Sprite):

    def __init__(self, x, y):
        super().__init__(enemies, x, y, 'enemy.png')

    def update(self, pattern):  # meaningless for now; will move by a certain pattern on a field
        delta = 5
        for tile in pattern:
            self.rect.x += delta


start_screen()
level_map = load_level('map.txt')
hero, max_x, max_y = generate_level(level_map)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    hero.update()
    tiles.draw(screen)
    hero_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
