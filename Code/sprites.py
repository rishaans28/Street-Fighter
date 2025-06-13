import pygame
from os.path import join
from custom_timer import Timer

class Player1(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player2):
        super().__init__(groups)
        self.player2 = player2
        self.pos = pos
        self.speed = 150
        self.health = 200
        self.idle_stance = pygame.image.load(join("Images", "ryu_idle_stance.png")).convert_alpha()
        self.punch_state = pygame.image.load(join("Images", "ryu_punch.png")).convert_alpha()
        self.kick_state = pygame.image.load(join("Images", "ryu_kick.png")).convert_alpha()
        self.duck_state = pygame.transform.scale(self.idle_stance, (231, 200)).convert_alpha()
        self.image = self.idle_stance
        self.mask = pygame.mask.from_surface(self.image)
        self.is_attacking = False
        self.is_ducking = False
        self.can_attack = True
        self.rect = self.image.get_frect(center=pos)
        self.direction = pygame.Vector2()
        self.reset_timer = Timer(1000, self.reset_image, False, False)
        self.attack_timer = Timer(1000, self.reset_attack, False, False)
    
    def display_health_bar(self, screen):
        self.health_bar = pygame.Surface((self.health, 20))
        self.health_bar_rect = self.health_bar.get_frect(midbottom = (self.rect.centerx, self.rect.top - 20))
        if self.health >= 100 and self.health <= 200:
            pygame.Surface.fill(self.health_bar, (0,255,0))
        elif self.health < 100 and self.health >= 50:
            pygame.Surface.fill(self.health_bar, (255,255,0))
        elif self.health < 50:
            pygame.Surface.fill(self.health_bar, (255,0,0))
        screen.blit(self.health_bar, self.health_bar_rect)
    
    def reset_image(self):
        self.is_attacking = False
        self.is_ducking = False
        self.image = self.idle_stance
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.centery = 550
        self.rect = self.image.get_frect(center=self.rect.center)
        self.attack_timer.activate()
    
    def reset_attack(self):
        self.can_attack = True
    
    def boundaries(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= 1350:
            self.rect.right = 1350
    
    def collisions(self):
        if pygame.sprite.collide_mask(self, self.player2) and self.is_attacking:
            self.player2.health -= 1

    def input(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = 0
        if keys[pygame.K_LSHIFT] and self.can_attack:
            self.can_attack = False
            self.is_attacking = True
            self.image = self.kick_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = 550
            self.reset_timer.activate()
        if keys[pygame.K_q] and self.can_attack:
            self.can_attack = False
            self.is_attacking = True
            self.image = self.punch_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = 550
            self.reset_timer.activate()
        if keys[pygame.K_s] and self.can_attack:
            self.can_attack = False
            self.is_ducking = True
            self.rect = self.image.get_frect(center = self.rect.center)
            self.rect.centery = 700
            self.image = self.duck_state
            self.mask = pygame.mask.from_surface(self.image)
            self.reset_timer.activate()
        self.rect.center += self.direction * self.speed * dt

    def update(self, dt, screen):
        self.attack_timer.update()
        self.reset_timer.update()
        self.input(dt)
        self.boundaries()
        self.collisions()
        self.display_health_bar(screen)

class Player2(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player1):
        super().__init__(groups)
        self.player1 = player1
        self.pos = pos
        self.speed = 150
        self.health = 200
        self.direction = pygame.Vector2()
        self.idle_stance = pygame.image.load(join("Images", "ken_idle_stance.png")).convert_alpha()
        self.punch_state = pygame.image.load(join("Images", "ken_punch.png")).convert_alpha()
        self.kick_state = pygame.image.load(join("Images", "ken_kick.png")).convert_alpha()
        self.duck_state = pygame.transform.scale(self.idle_stance, (232, 200)).convert_alpha()
        self.is_attacking = False
        self.is_ducking = False
        self.can_attack = True
        self.image = self.idle_stance
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_frect(center=pos)
        self.reset_timer = Timer(1000, self.reset_image, False, False)
        self.attack_timer = Timer(1000, self.reset_attack, False, False)
    
    def display_health_bar(self, screen):
        self.health_bar = pygame.Surface((self.health, 20))
        if not self.image == self.kick_state:
            self.health_bar_rect = self.health_bar.get_frect(midbottom = (self.rect.centerx, self.rect.top - 20))
        else:
            self.health_bar_rect = self.health_bar.get_frect(midbottom = (self.rect.centerx + 150, self.rect.top - 20))
        if self.health >= 100 and self.health <= 200:
            pygame.Surface.fill(self.health_bar, (0,255,0))
        elif self.health < 100 and self.health >= 50:
            pygame.Surface.fill(self.health_bar, (255,255,0))
        elif self.health < 50:
            pygame.Surface.fill(self.health_bar, (255,0,0))
        screen.blit(self.health_bar, self.health_bar_rect)

    def reset_image(self):
        self.is_attacking = False
        self.is_ducking = False
        self.image = self.idle_stance
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.centery = 550
        self.rect = self.image.get_frect(center=self.rect.center)
        self.attack_timer.activate()

    def reset_attack(self):
        self.can_attack = True

    def boundaries(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= 1350:
            self.rect.right = 1350

    def collisions(self):
        if pygame.sprite.collide_mask(self, self.player1) and self.is_attacking:
            self.player1.health -= 1

    def input(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = 0
        if keys[pygame.K_RSHIFT] and self.can_attack:
            self.can_attack = False
            self.is_attacking = True
            self.image = self.kick_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = 500
            self.reset_timer.activate()
        if keys[pygame.K_SPACE] and self.can_attack:
            self.can_attack = False
            self.is_attacking = True
            self.image = self.punch_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = 500
            self.reset_timer.activate()
        if keys[pygame.K_DOWN] and self.can_attack:
            self.can_attack = False
            self.is_ducking = True
            self.image = self.duck_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = 650
            self.reset_timer.activate()
        self.rect.center += self.direction * self.speed * dt
    
    def update(self, dt, screen):
        self.attack_timer.update()
        self.reset_timer.update()
        self.input(dt)
        self.boundaries()
        self.collisions()
        self.display_health_bar(screen)
