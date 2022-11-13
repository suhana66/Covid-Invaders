from os import listdir
from random import choice

import pygame

em = 16

def enviornment(sky_color, ground_color):
    screen = pygame.display.get_surface()
    screen.fill(sky_color)
    return pygame.draw.rect(screen, ground_color, pygame.Rect(0, screen.get_height() - em * 2, screen.get_width(), em * 2))

def font(font_name, size):
    return pygame.font.Font(font_name, em * size)

def text(font, text, color = (0, 0, 0)):
    return font.render(text, True, color)

def emoji_text(text, emoji):
    surf = pygame.Surface((text.get_width() + emoji.get_width() + em * 0.5, max(text.get_height(), emoji.get_height())), pygame.SRCALPHA)
    surf.blit(text, (0, surf.get_height() // 5))
    surf.blit(emoji, (text.get_width() + em * 0.5, 0))
    return surf

def text_screen(texts):

    # semi transparent screen
    screen = pygame.display.get_surface()
    screen_filter = screen.convert_alpha()
    screen_filter.fill((255,255,255, 128))           
    screen.blit(screen_filter, (0,0))

    # box for texts
    box = pygame.Rect(0, 0, max(text.get_width() for text in texts) + em * 10, sum(text.get_height() for text in texts) + em)
    box.center = (screen.get_width() // 2, screen.get_height() // 2)
    pygame.draw.rect(screen, (255, 255, 255), box)
    pygame.draw.rect(screen, (0, 0, 0), box, 2)

    for i, text in enumerate(texts):
        screen.blit(text, text.get_rect(midtop = (box.x + box.w // 2, box.y + sum(text.get_height() for text in texts[:i]) + em * 0.5)))

class Sprite:
    all = []
    def __init__(self):
        self.__class__.screen = pygame.display.get_surface()
        self.__class__.display = { 
            "width": self.screen.get_width(),
            "height": self.screen.get_height()
        }
        self.__class__.__bases__[0].all.append(self)

    @classmethod
    def clear(cls):
        for instance in cls.all: instance.all.clear()
        cls.all.clear()

class Player(Sprite):
    all = []
    dx = 4
    def __init__(self, folder_name: str):
        super().__init__()
        
        self.img = pygame.image.load(f"{folder_name}//player.png")
        self.height = self.img.get_height()
        self.width = self.img.get_width()
        self.x = self.display["width"] // 2 - self.width // 2
        self.y = self.display["height"] - self.height - em

        self.__class__.all.append(self)

    def draw(self):
        self.screen.blit(self.img, (self.x, self.y))
    
    def move(self, x):
        self.x = x

        # boundary
        if self.x < 0:
            self.x = 0
        elif self.x > self.display["width"] - self.width:
            self.x = self.display["width"] - self.width

class Enemy(Sprite):
    dx = 1
    all = []
    def __init__(self, folder_name: str, points = 10):
        super().__init__()

        # all enemy images are of the same width and height
        self.img = pygame.image.load(f"{folder_name}//enemy1.png")
        self.height = self.img.get_height()
        self.width = self.img.get_width()
        self.visible = True
        self.pts = points

        if not self.__class__.all:
            self.x = 0
            self.y = em * 3
        elif self.__class__.all[-1].x <= self.display["width"] // 2:
            self.x = self.__class__.all[-1].x + self.width + em
            self.y = self.__class__.all[-1].y
        else:
            length = self.width + em
            self.x = self.__class__.all[-1].x - length * (self.display["width"] // 2 // length + 1)
            self.y = self.__class__.all[-1].y + self.height

        self.__class__.all.append(self)

        self.row = (self.y - self.__class__.all[0].y) // self.height + 1
        self.img = pygame.image.load(f"{folder_name}//enemy{self.row}.png")

    @classmethod
    def types_surfs(cls, names, font):
        res = []
        rows = set()
        for instance, name in zip([rows.add(obj.row) or obj for obj in cls.all if obj.row not in rows], names):
            txt_surf = text(font, f" - {name}- {instance.pts}")
            tmp = pygame.Surface((instance.width + txt_surf.get_width(), max(instance.height, txt_surf.get_height()) + em), pygame.SRCALPHA)
            tmp.blit(instance.img, (0, 0))
            tmp.blit(txt_surf, (instance.width, tmp.get_height() // 4))
            res.append(tmp)
        return res

    @classmethod
    def instantiate(cls, folder_name):
        img_count = sum(1 for i in listdir(folder_name) if i.startswith("enemy"))
        while True:
            cls(folder_name)
            instance = cls.all[-1]
            instance.pts = (img_count - instance.row + 1) * 10
            if instance.row == img_count and instance.x > instance.display["width"] // 2:
                break

    def draw(self):
        if self.visible:
            self.screen.blit(self.img, (self.x, self.y))

    @classmethod
    def move(cls):
        end = cls.display["width"] - cls.all[-1].width
        for instance in cls.all:
            instance.x += instance.dx

            # boundary
            if instance.x >= end:
                instance.x = end
            if instance.x <= 0:
                instance.x = 0
        
        if cls.all[-1].x == end: cls.dx = -abs(cls.dx)
        if cls.all[0].x == 0: cls.dx = abs(cls.dx)

        if cls.all[-1].x == end or cls.all[0].x == 0 and cls.all[0].y > em * 3:
            for instance in cls.all: instance.y += instance.height
    
    @classmethod
    def attack(cls, color = (0, 0, 0)):
        free = []
        for instance in cls.all:
            if instance.visible:
                below = [i for i in cls.all if i.x == instance.x and i.row > instance.row]
                if not below or all(not i.visible for i in below): free.append(instance)
        attacker = choice(free)
        hit = Projectile(attacker.width, (attacker.x, attacker.y), color)
        hit.dy *= -1
        hit.fire = True
        return hit, attacker.x, attacker.y

class Projectile(Sprite):
    all = []
    dy = 4
    length = 48
    thickness = 5
    def __init__(self, player_w: int, player_xy: tuple, color = (0, 0, 0)):
        assert player_w > 0 
        assert player_xy[0] >= 0
        assert player_xy[1] >= 0

        super().__init__()

        self.__player_w = player_w
        self.x = player_xy[0] + self.__player_w // 2
        self.y = player_xy[1]
        self.color = color
        self.fire = False
    
    def draw(self):
        pygame.draw.line(self.screen, self.color, (self.x, self.y), (self.x, self.y + self.length), self.thickness)

    def move(self, x):
        if not self.fire: self.x = x + self.__player_w // 2
        else: self.y -= self.dy

    def reset(self, y, fire = False):
        self.fire = fire
        self.y = y


    def collide(self, rect, up = False):
        if up: return rect.colliderect(self.x, self.y, self.thickness, 1)
        return rect.colliderect(self.x, self.y + self.length, self.thickness, 1)
