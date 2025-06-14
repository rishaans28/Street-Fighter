import pygame
from os.path import join
from custom_timer import Timer

class BasePlayer(pygame.sprite.Sprite):
    def __init__(self, pos, groups, opponent, idle_img, punch_img, kick_img, duck_size, controls, duck_y, health_bar_y, winner_name):
        super().__init__(groups)
        self.opponent = opponent
        self.pos = pos
        self.speed = 200
        self.health = 200
        self.direction = pygame.Vector2()
        self.idle_stance = pygame.image.load(join("Images", idle_img)).convert_alpha()
        self.punch_state = pygame.image.load(join("Images", punch_img)).convert_alpha()
        self.kick_state = pygame.image.load(join("Images", kick_img)).convert_alpha()
        self.duck_state = pygame.transform.scale(self.idle_stance, duck_size).convert_alpha()
        self.is_attacking = False
        self.is_ducking = False
        self.can_attack = True
        self.winner = None
        self.image = self.idle_stance
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_frect(center=pos)
        self.reset_timer = Timer(1000, self.reset_image, False, False)
        self.attack_timer = Timer(1000, self.reset_attack, False, False)
        self.health_bar = pygame.Surface((self.health, 20))
        self.health_bar_rect = self.health_bar.get_frect(midbottom = (self.rect.centerx, self.rect.top - 20))
        self.controls = controls
        self.duck_y = duck_y
        self.health_bar_y = health_bar_y
        self.winner_name = winner_name

    def display_health_bar(self, screen):
        if self.health >= 100:
            color = (0,255,0)
        elif self.health >= 50:
            color = (255,255,0)
        else:
            color = (255,0,0)
        bar_rect = pygame.Rect(0,0,self.health,20)
        bar_rect.midbottom = (self.rect.centerx, self.rect.top - 20)
        pygame.draw.rect(screen, color, bar_rect)
        if self.health <= 1:
            self.kill()
            self.winner = self.winner_name

    def reset_image(self):
        self.is_attacking = False
        self.is_ducking = False
        self.image = self.idle_stance
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.centery = self.health_bar_y
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
        if pygame.sprite.collide_mask(self, self.opponent) and self.is_attacking:
            if self.image == self.kick_state and self.opponent.image == self.opponent.kick_state:
                return
            if self.image == self.punch_state and self.opponent.image == self.opponent.punch_state:
                return
            self.opponent.health -= 1

    def input(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[self.controls['right']]) - int(keys[self.controls['left']])
        self.direction.y = 0
        if keys[self.controls['kick']] and self.can_attack:
            self.can_attack = False
            self.is_attacking = True
            self.image = self.kick_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = self.health_bar_y
            self.reset_timer.activate()
        if keys[self.controls['punch']] and self.can_attack:
            self.can_attack = False
            self.is_attacking = True
            self.image = self.punch_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = self.health_bar_y
            self.reset_timer.activate()
        if keys[self.controls['duck']] and self.can_attack:
            self.can_attack = False
            self.is_ducking = True
            self.image = self.duck_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = self.duck_y
            self.reset_timer.activate()
        self.rect.center += self.direction * self.speed * dt

    def update(self, dt, screen):
        self.attack_timer.update()
        self.reset_timer.update()
        self.input(dt)
        self.boundaries()
        self.collisions()
        self.display_health_bar(screen)

class Player1(BasePlayer):
    def __init__(self, pos, groups, player2):
        controls = {
            'left': pygame.K_a,
            'right': pygame.K_d,
            'kick': pygame.K_LSHIFT,
            'punch': pygame.K_q,
            'duck': pygame.K_s
        }
        super().__init__(
            pos, groups, player2,
            idle_img="ryu_idle_stance.png",
            punch_img="ryu_punch.png",
            kick_img="ryu_kick.png",
            duck_size=(231, 200),
            controls=controls,
            duck_y=650,
            health_bar_y=550,
            winner_name="player2"
        )

class Player2(BasePlayer):
    def __init__(self, pos, groups, player1):
        controls = {
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'kick': pygame.K_RSHIFT,
            'punch': pygame.K_SPACE,
            'duck': pygame.K_DOWN
        }
        super().__init__(
            pos, groups, player1,
            idle_img="ken_idle_stance.png",
            punch_img="ken_punch.png",
            kick_img="ken_kick.png",
            duck_size=(232, 200),
            controls=controls,
            duck_y=650,
            health_bar_y=550,
            winner_name="player1"
        )
