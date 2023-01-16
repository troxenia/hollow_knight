import pygame
import os
import sys

pygame.init()
screen_size = WIDTH, HEIGHT = (550, 600)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Hollow Knight')
clock = pygame.time.Clock()
FPS = 50
tile_width = tile_height = 50
tile_images = {'empty': 'empty.png'}

tiles = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
coins = pygame.sprite.Group()
enemies = pygame.sprite.Group()
portal = pygame.sprite.Group()
sound_group = pygame.sprite.Group()


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
            elif level[y][x] == '*':
                Tile(x, y, tile_images['empty'])
                GruzzerEnemy(x, y)
                level[y][x] = '.'
            elif level[y][x] == '$':
                Tile(x, y, tile_images['empty'])
                Coin(x, y)
                level[y][x] = '.'
            elif level[y][x] == '/':
                Tile(x, y, tile_images['empty'])
                Portal(x, y)
                level[y][x] = '.'
            elif level[y][x] in ['1', '2', '3']:
                # Препятствия в одну клетку разных видов
                Tile(x, y, tile_images['empty'])
                Obstacle(x, y, 'obstacle{}.png'.format(level[y][x]))
                level[y][x] = '.'
    return hero, x, y


def close():
    pygame.quit()
    sys.exit()


def display_text(text: list, text_coord: int, font=pygame.font.Font(None, 30), color=pygame.Color(248, 222, 173)):
    for line in text:
        string_rendered = font.render(line, True, color)
        text_rect = string_rendered.get_rect()
        text_coord += 10
        text_rect.top = text_coord
        text_rect.x = 10
        text_coord += text_rect.height
        screen.blit(string_rendered, text_rect)


class Button:

    def __init__(self, x, y, width, height, action, color=(248, 222, 173)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        font = pygame.font.Font(None, 30)
        string_rendered = font.render(self.action, True, (0, 0, 0))
        string_rect = (self.rect.x + 5, self.rect.y + 5)
        screen.blit(string_rendered, string_rect)

    def update(self, event):
        if self.rect.collidepoint(event.pos):
            return self.action


class Tile(pygame.sprite.Sprite):

    def __init__(self, x, y, filename):
        super().__init__(tiles)
        self.image = load_image(filename)
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)


class Obstacle(pygame.sprite.Sprite):

    def __init__(self, x, y, filename):
        super().__init__(obstacles)
        self.image = load_image(filename)
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)
        self.mask = pygame.mask.from_surface(self.image)


class Portal(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__(portal)
        self.image = load_image('portal.png')
        self.rect = self.image.get_rect().move(tile_width * x + 6, tile_height * y)


class Sound(pygame.sprite.Sprite):
    image_on, image_off = (load_image('sound_on.png'), load_image('sound_off.png'))

    def __init__(self, x, y):
        super().__init__(sound_group)
        self.image = self.image_on
        self.rect = self.image.get_rect().move(x, y)

    def update(self, event):
        if self.rect.collidepoint(event.pos):
            global sound_on
            if sound_on:
                self.image = self.image_off
                pygame.mixer.music.stop()
            else:
                self.image = self.image_on
                pygame.mixer.music.play(-1)
            sound_on = not sound_on


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
        self.mask = pygame.mask.from_surface(self.image)  # for better collision detection

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

    def collide_with_group(self, group):
        """Столкновение с группой по маске"""
        for sprite in group:
            if pygame.sprite.collide_mask(self, sprite):
                return True

    def update(self):
        delta = 5
        x, y = self.rect.x, self.rect.y
        if keys[pygame.K_LEFT]:
            super().switch_frames('left')
            if self.rect.x >= delta:
                self.rect.x -= delta
        elif keys[pygame.K_RIGHT]:
            super().switch_frames('right')
            if self.rect.x + self.rect.width + delta <= WIDTH:
                self.rect.x += delta
        elif keys[pygame.K_UP]:
            super().switch_frames('up')
            if self.rect.y >= delta:
                self.rect.y -= delta
        elif keys[pygame.K_DOWN]:
            super().switch_frames('down')
            if self.rect.y + self.rect.height + delta <= HEIGHT - 50:
                self.rect.y += delta
        if self.collide_with_group(obstacles):
            self.rect.x, self.rect.y = x, y
        if self.collide_with_group(enemies):
            return False, False
        if any(pygame.sprite.spritecollide(self, coins, True)) and sound_on:
            coin_music.play()
        if pygame.sprite.spritecollideany(self, portal):
            return True, False
        return True, True


class CrystalEnemy(AnimatedSprite):
    """Враг кристальный жук."""
    def __init__(self, x, y):
        super().__init__(enemies, x, y,
                         {'right': (load_image('going_right.png'), 5, 1),
                          'left': (load_image('going_left.png'), 5, 1)})
        # Traffic pattern of the bug
        self.pattern = ['right'] * 60 + ['left'] * 60
        self.index = 0
        self.turn = self.pattern[self.index]
        self.vx = 2

    def update(self):
        if self.turn == 'right':
            self.rect.x += self.vx
        elif self.turn == 'left':
            self.rect.x -= self.vx
        self.index = (self.index + 1) % len(self.pattern)
        self.turn = self.pattern[self.index]
        super().switch_frames(self.turn)


class GruzzerEnemy(AnimatedSprite):
    """Враг летающая муха Gruzzer."""
    def __init__(self, x, y):
        super().__init__(enemies, x, y,
                         {'move': (load_image('flying.png'), 4, 1)})
        self.length = 10
        self.pattern = ['right', 'right', 'right', 'down', 'right', 'down', 'right', 'down', 'down', 'down',
                        'left', 'down', 'left', 'down', 'left', 'left', 'left', 'up', 'left', 'up', 'left',
                        'up', 'up', 'up', 'right', 'up', 'right', 'up']
        self.result = []
        for value in self.pattern:
            self.result += [value] * self.length
        self.pattern = self.result[::]

        self.index = 0
        self.turn = self.pattern[self.index]
        self.vx = 2

    def update(self):
        if self.turn == 'right':
            self.rect.x += self.vx
        elif self.turn == 'left':
            self.rect.x -= self.vx
        elif self.turn == 'up':
            self.rect.y -= self.vx
        elif self.turn == 'down':
            self.rect.y += self.vx
        self.index = (self.index + 1) % len(self.pattern)
        self.turn = self.pattern[self.index]
        super().switch_frames('move')


class Coin(AnimatedSprite):

    def __init__(self, x, y):
        super().__init__(coins, x, y, {'coin': (load_image('coin.png'), 10, 1)})
        self.rect = self.image.get_rect().move(x * tile_width + 10, y * tile_height + 10)

    def update(self):
        super().switch_frames('coin')


class Menu:

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

    def run(self):
        screen.blit(self.background, (0, 0))
        text = ['Hollow Knight', '', '', 'Run for your life', '(and coins)']
        font = pygame.font.SysFont('roboto', 30, True)
        text_coord = 50
        display_text(text, text_coord, font)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    close()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for widget in self.widgets:
                        action = widget.update(event)
                        if action is not None:
                            return action
                    sound_group.update(event)
            screen.blit(self.background, (0, 0))
            display_text(text, text_coord, font)
            for widget in self.widgets:
                widget.draw()
            sound_group.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)


class Help(Menu):

    def __init__(self, background, widgets: list):
        super().__init__(background, widgets)

    def run(self):
        screen.blit(self.background, (0, 0))
        title = ['How to play']
        text = ['Use arrows to move.', '', 'Your main goal: reach the portal before ', 'confronting the enemy.', '',
                'Collect coins to make score higher.']
        title_font = pygame.font.SysFont('roboto', 30, True)
        text_font = pygame.font.SysFont('roboto', 25)
        title_coord, text_coord = 50, 120
        display_text(title, title_coord, title_font)
        display_text(text, text_coord, text_font)
        return super().run()


class Levels(Menu):

    def __init__(self, background, widgets: list):
        super().__init__(background, widgets)

    def run(self):
        screen.blit(self.background, (0, 0))
        text = ['Levels']
        font = pygame.font.SysFont('roboto', 30, True)
        text_coord = 50
        display_text(text, text_coord, font)
        return super().run()


class End(Menu):

    def __init__(self, background, widgets: list):
        super().__init__(background, widgets)

    def run(self):
        screen.blit(self.background, (0, 0))
        if passed_level:
            title = ['Congratulations!']
            text = [f'You passed level {cur_level + 1}',
                    f'Coins captured: {coins_captured}/{coins_number}']
        else:
            title = ['Try harder!']
            text = [f'Level {cur_level + 1} not passed']
        title_font = pygame.font.SysFont('roboto', 30, True)
        text_font = pygame.font.SysFont('roboto', 30)
        title_coord, text_coord = 50, 120
        display_text(title, title_coord, title_font)
        display_text(text, text_coord, text_font)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    close()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for widget in self.widgets:
                        if (cur_level == 0 and widget.action == 'prev' or
                                cur_level == len(level_maps) - 1 and widget.action == 'next'):
                            continue
                        action = widget.update(event)
                        if action is not None:
                            return action
            for widget in self.widgets:
                if (cur_level == 0 and widget.action == 'prev' or
                        cur_level == len(level_maps) - 1 and widget.action == 'next'):
                    continue
                widget.draw()
            pygame.display.flip()
            clock.tick(FPS)


def game():
    global keys, passed_level, coins_number
    level_map = load_level(level_maps[cur_level])
    hero, max_x, max_y = generate_level(level_map)
    coins_number = len(coins.sprites())
    running = True
    while running and passed_level:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if quit_btn.update(event) is not None:
                    passed_level = False
                    return
        keys = pygame.key.get_pressed()
        passed_level, running = hero.update()
        tiles.draw(screen)
        obstacles.draw(screen)
        enemies.update()
        enemies.draw(screen)
        coins.update()
        coins.draw(screen)
        portal.draw(screen)
        hero_group.draw(screen)
        quit_btn.draw()
        clock.tick(FPS)
        pygame.display.flip()


start_btns = [Button(20, 450, 100, 50, 'start'), Button(140, 450, 100, 50, 'help'), Button(260, 450, 100, 50, 'levels')]
help_btns = [Button(10, 10, 60, 30, 'back')]
levels_btns = [Button(10, 10, 60, 30, 'back'), Button(10, 120, 530, 50, '1'), Button(10, 190, 530, 50, '2'),
               Button(10, 260, 530, 50, '3'), Button(10, 330, 530, 50, '4'), Button(10, 400, 530, 50, '5')]
end_btns = [Button(10, 10, 60, 30, 'back'), Button(20, 450, 100, 50, 'prev'), Button(140, 450, 100, 50, 'replay'),
            Button(260, 450, 100, 50, 'next')]
quit_btn = Button(10, 560, 50, 30, 'quit')

screens = [Start('background.jpg', start_btns), Help('background.jpg', help_btns),
           Levels('background.jpg', levels_btns), End('background.jpg', end_btns)]
cur_screen = screens[0]

cur_level = 0
level_maps = ['map1.txt', 'map2.txt', 'map3.txt', 'map4.txt', 'map5.txt']

sound_on = True
pygame.mixer.music.load('data/music.wav')
pygame.mixer.music.play(-1)
coin_music = pygame.mixer.Sound('data/coin_music.wav')
Sound(420, 445)
while True:
    action = cur_screen.run()
    if action == 'help':
        cur_screen = screens[1]
    elif action == 'levels':
        cur_screen = screens[2]
    elif action == 'back':
        cur_screen = screens[0]
    else:
        for group in (tiles, hero_group, obstacles, coins, enemies, portal):
            group.empty()
        coins_number = 0
        passed_level = True
        if action in ('1', '2', '3', '4', '5'):
            cur_level = int(action) - 1
        elif action == 'prev':
            cur_level -= 1
        elif action == 'next':
            cur_level += 1
        keys = ()
        game()
        coins_captured = coins_number - len(coins.sprites())
        cur_screen = screens[3]
