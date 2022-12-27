import pygame
import os


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class Character(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)

    def update(self, event):  # move
        pass


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
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
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Knight(Character):

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = load_image('knight.png')
        self.rect = self.image.get_rect().move(x, y)

    def update(self, keys):
        delta = 5
        if keys[pygame.K_LEFT]:
            self.rect.x -= delta
        elif keys[pygame.K_RIGHT]:
            self.rect.x += delta
        elif keys[pygame.K_UP]:
            self.rect.y -= delta
        elif keys[pygame.K_DOWN]:
            self.rect.y += delta


pygame.init()
screen_size = width, height = (550, 550)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Hollow Knight')
clock = pygame.time.Clock()
FPS = 50


all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
coins = pygame.sprite.Group()


hero = Knight(0, 0)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # elif event.type == pygame.KEYDOWN:
        #     hero.update(event)
    keys = pygame.key.get_pressed()
    hero.update(keys)
    screen.fill((255, 255, 255))
    all_sprites.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
