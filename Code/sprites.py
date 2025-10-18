import pygame
from os.path import join
from custom_timer import Timer
from random import randint, choice

class BasePlayer(pygame.sprite.Sprite):
    def __init__(self, pos, groups, opponent, player, idle_img, punch_img, kick_img, duck_img, controls, duck_y, health_bar_y, winner_name, punch_sound, kick_sound):
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
        self.duck_state = pygame.image.load(join("Images", duck_img)).convert_alpha()
        self.is_attacking = False
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
        self.is_stunned = False

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
            if self.image == self.kick_state and self.opponent.image == self.opponent.punch_state:
                self.opponent.health -= 25 * dt
                if not self.kick_landed:
                    self.kick_landed = True
                    self.kick_sound.play()
            if self.image == self.punch_state and self.opponent.image == self.opponent.idle_stance:
                self.opponent.health -= 35 * dt
                if not self.punch_landed:
                    self.punch_landed = True
                    self.punch_sound.play()
            if self.image == self.kick_state and self.opponent.image == self.opponent.idle_stance:
                self.opponent.health -= 50 * dt
                if not self.opponent.is_attacking and hasattr(self.opponent, "can_dodge") and self.opponent.can_dodge and hasattr(self.opponent, "execute_action"):
                    self.opponent.can_dodge = False
                    self.opponent.execute_action("duck")
                if not self.kick_landed:
                    self.kick_landed = True
                    self.kick_sound.play()

    def input(self, dt, group1, group2):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[self.controls["right"]]) - int(keys[self.controls["left"]])
        self.direction.y = 0
        if keys[self.controls['kick']] and self.can_attack and not self.is_stunned:
            self.can_attack = False
            self.is_attacking = True
            self.image = self.kick_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = self.health_bar_y
            self.kick_landed = False
            self.reset_timer.activate()
        if keys[self.controls['punch']] and self.can_attack and not self.is_stunned:
            self.can_attack = False
            self.is_attacking = True
            self.image = self.punch_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = self.health_bar_y
            self.punch_landed = False
            self.reset_timer.activate()
        if keys[self.controls['duck']] and self.can_attack and not self.is_stunned:
            self.image = self.duck_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = self.duck_y
            self.reset_timer.activate()
        if keys[self.controls["fireball"]] and self.fireball_available and not self.is_stunned:
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
            duck_img="ryu_duck.png",
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
            duck_img="ken_duck.png",
            controls=controls,
            duck_y=650,
            health_bar_y=550,
            winner_name="player1",
            punch_sound=punch_sound,
            kick_sound=kick_sound
        )

class Player2CPU(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player1, punch_sound, kick_sound):
        super().__init__(groups)
        self.idle_stance = pygame.image.load(join("Images", "ken_idle_stance.png")).convert_alpha()
        self.punch_state = pygame.image.load(join("Images", "ken_punch.png")).convert_alpha()
        self.kick_state = pygame.image.load(join("Images", "ken_kick.png")).convert_alpha()
        self.duck_state = pygame.image.load(join("Images", "ken_duck.png")).convert_alpha()
        self.direction = pygame.Vector2()
        self.image = self.idle_stance
        self.rect = self.image.get_frect(center = pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.player = "player2"
        self.opponent = player1
        self.health = 200
        self.speed = 200
        self.pos = pos
        self.can_attack = True
        self.is_attacking = False
        self.punch_sound = punch_sound
        self.punch_landed = False
        self.kick_sound = kick_sound
        self.kick_landed = False
        self.reset_timer = Timer(1000, self.reset_image, False, False)
        self.attack_timer = Timer(1000, self.reset_attack, False, False)
        self.unretreat_timer = Timer(2750, self.unretreat, False, False)
        self.dodge_timer = Timer(3000, self.reset_dodge, True, True)
        self.timers = [self.reset_timer, self.attack_timer, self.unretreat_timer, self.dodge_timer]
        self.health_bar = pygame.Surface((self.health, 20))
        self.health_bar_rect = self.health_bar.get_frect(midbottom = (self.rect.centerx, self.rect.top - 20))
        self.health_bar_y = 550
        self.duck_y = 650
        self.winner = None
        self.winner_name = "player1"
        self.fireball_available = False
        self.is_retreating = False
        self.has_retreated = False
        self.can_dodge = False

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
    
    def boundaries(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= 1350:
            self.rect.right = 1350
    
    def reset_image(self):
        self.is_attacking = False
        self.image = self.idle_stance
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.centery = self.health_bar_y
        self.rect = self.image.get_frect(center=self.rect.center)
        self.attack_timer.activate()
    
    def reset_attack(self):
        self.can_attack = True
    
    def unretreat(self):
        self.is_retreating = False
        self.direction.x = -1
    
    def reset_dodge(self):
        random_num = randint(1,2)
        if random_num == 1:
            self.can_dodge = True

    def collisions(self, dt):
        if pygame.sprite.collide_mask(self, self.opponent) and self.is_attacking:
            if self.image == self.kick_state and self.opponent.image == self.opponent.kick_state:
                return
            if self.image == self.punch_state and self.opponent.image == self.opponent.punch_state:
                return
            if self.image == self.kick_state and self.opponent.image == self.opponent.punch_state:
                self.opponent.health -= 25 * dt
                if not self.kick_landed:
                    self.kick_landed = True
                    self.kick_sound.play()
            if self.image == self.punch_state and self.opponent.image == self.opponent.idle_stance:
                self.opponent.health -= 35 * dt
                if not self.punch_landed:
                    self.punch_landed = True
                    self.punch_sound.play()
            if self.image == self.kick_state and self.opponent.image == self.opponent.idle_stance:
                self.opponent.health -= 50 * dt
                if not self.kick_landed:
                    self.kick_landed = True
                    self.kick_sound.play()

    def check_actions(self, group1, group2):
        if self.health <= 100 and not self.is_retreating and not self.has_retreated:
            self.is_retreating = True
            self.has_retreated = True
            self.execute_action("duck")
            self.direction.x = 1
            self.unretreat_timer.activate()
            return
        if self.is_retreating:
            self.direction.x = 1
            return
        if abs(self.opponent.rect.x - self.rect.x) < 300:
            self.direction.x = 0
            if self.can_attack:
                self.execute_action(choice(["kick", "punch", "duck"]))
        if abs(self.opponent.rect.x - self.rect.x) >= 300:
            self.direction.x = -1
        if abs(self.opponent.rect.x - self.rect.x) < 150:
            self.direction.x = 1
        if self.fireball_available:
            Fireball((group1, group2), (self.rect.left - 180, self.rect.centery - 150), "player2")
            self.fireball_available = False
        if self.health > 100:
            self.has_retreated = False

    def execute_action(self, action):
        if action == "kick":
            self.can_attack = False
            self.is_attacking = True
            self.image = self.kick_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = self.health_bar_y
            self.punch_landed = False
            self.reset_timer.activate()
        elif action == "punch":
            self.can_attack = False
            self.is_attacking = True
            self.image = self.punch_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = self.health_bar_y
            self.punch_landed = False
            self.reset_timer.activate()
        elif action == "duck":
            self.can_attack = False
            self.is_attacking = True
            self.image = self.duck_state
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_frect(center=self.rect.center)
            self.rect.centery = self.duck_y
            self.reset_timer.activate()

    def update(self, dt, screen, group1, group2):
        for timer in self.timers:
            timer.update()
        self.check_actions(group1, group2)
        self.display_health_bar(screen)
        self.boundaries()
        self.collisions(dt)
        self.rect.x += self.direction.x * self.speed * dt

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
        self.speed = 350
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
