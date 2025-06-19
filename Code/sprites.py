import pygame
from os.path import join
from custom_timer import Timer

class BasePlayer(pygame.sprite.Sprite):
    def __init__(self, pos, groups, opponent, player, idle_img, punch_img, kick_img, duck_size, controls, duck_y, health_bar_y, winner_name, punch_sound, kick_sound):
        super().__init__(groups)
        self.opponent = opponent
        self.player = player
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
        self.punch_sound = punch_sound
        self.punch_landed = False
        self.kick_sound = kick_sound
        self.kick_landed = False
        self.fireball_available = False

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

    def collisions(self, dt):
        if pygame.sprite.collide_mask(self, self.opponent) and self.is_attacking:
            if self.image == self.kick_state and self.opponent.image == self.opponent.kick_state:
                return
            if self.image == self.punch_state and self.opponent.image == self.opponent.punch_state:
                return
            if self.image == self.punch_state:
                self.opponent.health -= 35 * dt
                if not self.punch_landed:
                    self.punch_landed = True
                    self.punch_sound.play()
            if self.image == self.kick_state:
                self.opponent.health -= 50 * dt
                if not self.kick_landed:
                    self.kick_landed = True
                    self.kick_sound.play()

    def input(self, dt, group1, group2):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[self.controls["right"]]) - int(keys[self.controls['left']])
        self.direction.y = 0
        if keys[self.controls['kick']] and self.can_attack:
            self.can_attack = False
            self.is_attacking = True
            self.image = self.kick_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = self.health_bar_y
            self.kick_landed = False
            self.reset_timer.activate()
        if keys[self.controls['punch']] and self.can_attack:
            self.can_attack = False
            self.is_attacking = True
            self.image = self.punch_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = self.health_bar_y
            self.punch_landed = False
            self.reset_timer.activate()
        if keys[self.controls['duck']] and self.can_attack:
            self.is_ducking = True
            self.image = self.duck_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = self.duck_y
            self.reset_timer.activate()
        if keys[self.controls["fireball"]] and self.fireball_available:
            self.can_attack = False
            self.fireball_available = False
            if self.player == "player1":
                Fireball((group1, group2), (self.rect.right + 180, self.rect.centery - 150), "player1")
            elif self.player == "player2":
                Fireball((group1, group2), (self.rect.left - 180, self.rect.centery - 150), "player2")
            self.reset_timer.activate()
        self.rect.center += self.direction * self.speed * dt

    def update(self, dt, screen, group1, group2):
        self.attack_timer.update()
        self.reset_timer.update()
        self.input(dt, group1, group2)
        self.boundaries()
        self.collisions(dt)
        self.display_health_bar(screen)

class Player1(BasePlayer):
    def __init__(self, pos, groups, player2, punch_sound, kick_sound):
        controls = {
            'left': pygame.K_a,
            'right': pygame.K_d,
            'kick': pygame.K_LSHIFT,
            'punch': pygame.K_q,
            'duck': pygame.K_s,
            'fireball' : pygame.K_f
        }
        super().__init__(
            pos, groups, player2,
            player="player1",
            idle_img="ryu_idle_stance.png",
            punch_img="ryu_punch.png",
            kick_img="ryu_kick.png",
            duck_size=(231, 200),
            controls=controls,
            duck_y=650,
            health_bar_y=550,
            winner_name="player2",
            punch_sound=punch_sound,
            kick_sound=kick_sound,
        )

class Player2(BasePlayer):
    def __init__(self, pos, groups, player1, punch_sound, kick_sound):
        controls = {
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'kick': pygame.K_RSHIFT,
            'punch': pygame.K_SPACE,
            'duck': pygame.K_DOWN,
            'fireball' : pygame.K_SLASH
        }
        super().__init__(
            pos, groups, player1,
            player="player2",
            idle_img="ken_idle_stance.png",
            punch_img="ken_punch.png",
            kick_img="ken_kick.png",
            duck_size=(232, 200),
            controls=controls,
            duck_y=650,
            health_bar_y=550,
            winner_name="player1",
            punch_sound=punch_sound,
            kick_sound=kick_sound
        )

class HealthDrop(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.image = pygame.image.load(join("Images", "health.png"))
        self.rect = self.image.get_frect(midbottom = pos)
        self.speed = 400

    def update(self, dt, *args, **kwargs):
        self.rect.centery += self.speed * dt
        if self.rect.bottom >= 800:
            self.kill()

class FireballDrop(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.image = pygame.image.load(join("Images", "fireballdrop.png"))
        self.rect = self.image.get_frect(midbottom = pos)
        self.speed = 400
    
    def update(self, dt, *args, **kwargs):
        self.rect.centery += self.speed * dt
        if self.rect.bottom >= 800:
            self.kill()

class Fireball(pygame.sprite.Sprite):
    def __init__(self, groups, pos, player):
        super().__init__(groups)
        self.player = player
        self.speed = 500
        self.image = pygame.image.load(join("Images", "fireball.png"))
        if self.player == "player2":
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_frect(center = pos)
        self.direction = pygame.Vector2(1,0) if self.player == "player1" else pygame.Vector2(-1,0)
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_rect = self.mask.get_bounding_rects()[0].move(self.rect.topleft)

    def update(self, dt, *args, **kwargs):
        self.mask_rect = self.mask.get_bounding_rects()[0].move(self.rect.topleft)
        self.rect.centerx += self.direction.x * self.speed * dt
        if self.mask_rect.left <= 0:
            self.kill()
        if self.mask_rect.right >= 1350:
            self.kill()
