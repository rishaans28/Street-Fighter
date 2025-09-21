import pygame
from sprites import *
from random import randint

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((1350, 800), vsync=1)
        pygame.display.set_caption("Street Fighter")
        self.clock = pygame.time.Clock()
        self.menu = True
        self.running = True
        self.bgnum = randint(1,5)
        self.background = pygame.image.load(join("Images", f"background{self.bgnum}.png"))
        self.background = pygame.transform.scale(self.background, (1350, 800))
        self.is_2_player = None
        
        self.all_sprites = pygame.sprite.Group()
        self.health_sprites = pygame.sprite.Group()
        self.fireball_drop_sprites = pygame.sprite.Group()
        self.fireball_sprites = pygame.sprite.Group()

        self.punch_sound = pygame.mixer.Sound(join("Audio", "punch.mp3"))
        self.kick_sound = pygame.mixer.Sound(join("Audio", "kick.mp3"))
        self.powerup_sound = pygame.mixer.Sound(join("Audio", "powerup.mp3"))
        
        self.player1_wins_img = pygame.image.load(join("Images", "player1wins.png"))
        self.player1_wins_rect = self.player1_wins_img.get_frect(center = (1350/2, 800/2))
        self.player2_wins_img = pygame.image.load(join("Images", "player2wins.png"))
        self.player2_wins_rect = self.player2_wins_img.get_frect(center = (1350/2, 800/2))
        
        self.health_drop_event = pygame.event.custom_type()
        pygame.time.set_timer(self.health_drop_event, 10000)
        
        self.fireball_drop_event = pygame.event.custom_type()
        pygame.time.set_timer(self.fireball_drop_event, 12000)
        
        self.paused = False

    def show_countdown(self):
        self.one = pygame.image.load(join("Images", "1.png"))
        self.one_rect = self.one.get_frect(center = (1350/2, 800/2))

        self.two = pygame.image.load(join("Images", "2.png"))
        self.two_rect = self.two.get_frect(center = (1350/2, 800/2))
        
        self.three = pygame.image.load(join("Images", "3.png"))
        self.three_rect = self.three.get_frect(center = (1350/2, 800/2))
        
        countdown = [
            (self.three, self.three_rect),
            (self.two, self.two_rect),
            (self.one, self.one_rect),
        ]
        for img, rect in countdown:
            start_time = pygame.time.get_ticks()
            while pygame.time.get_ticks() - start_time < 1000:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        return
                self.display_surface.blit(self.background, (0,0))
                self.all_sprites.draw(self.display_surface)
                self.display_surface.blit(img, rect)
                pygame.display.update()
    
    def check_collisions(self, dt):
        if pygame.sprite.spritecollide(self.player1, self.health_sprites, True):
            self.powerup_sound.play()
            if self.player1.health + 50 > 200:
                self.player1.health = 200
            else:
                self.player1.health += 50
        if pygame.sprite.spritecollide(self.player2, self.health_sprites, True):
            self.powerup_sound.play()
            if self.player2.health + 50 > 200:
                self.player2.health = 200
            else:
                self.player2.health += 50
        
        if pygame.sprite.spritecollide(self.player1, self.fireball_drop_sprites, True):
            self.powerup_sound.play()
            self.player1.fireball_available = True
        if pygame.sprite.spritecollide(self.player2, self.fireball_drop_sprites, True):
            self.powerup_sound.play()
            self.player2.fireball_available = True

        if pygame.sprite.spritecollide(self.player1, self.fireball_sprites, False, pygame.sprite.collide_mask):
            self.player1.health -= 125 * dt
            self.player1.is_stunned = choice([True, False, False, False])
        if pygame.sprite.spritecollide(self.player2, self.fireball_sprites, False, pygame.sprite.collide_mask):
            self.player2.health -= 125 * dt
            self.player1.is_stunned = choice([True, False, False, False])

    def display_winner(self):
        if self.player1.winner == "player2":
            self.display_surface.blit(self.player2_wins_img, self.player2_wins_rect)
        if self.player2.winner == "player1":
            self.display_surface.blit(self.player1_wins_img, self.player1_wins_rect)
    
    def display_menu_text(self):
        font = pygame.font.Font("Fonts/tanding.otf", 150)
        
        text2 = font.render("1 PLAYER OR 2 PLAYER", True, (255,255,255))
        text_rect2 = text2.get_rect(center = (1350//2, (800//2)-100))

        text = font.render("CLICK 1 OR 2", True, (255,255,255))
        text_rect = text.get_rect(center = (1350//2, (800//2)+100))
        
        self.display_surface.blit(text, text_rect)
        self.display_surface.blit(text2, text_rect2)
    
    def menu_loop(self):
        while self.menu:
            self.display_surface.fill((0,0,0))
            self.display_menu_text()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.is_2_player = False
                        self.menu = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_2:
                        self.is_2_player = True
                        self.menu = False
            pygame.display.update()

    def run(self):
        self.menu_loop()
        self.player1 = Player1((116,550), self.all_sprites, None, self.punch_sound, self.kick_sound)
        if self.is_2_player == True:
            self.player2 = Player2((1234,550), self.all_sprites, None, self.punch_sound, self.kick_sound)
        if self.is_2_player == False:
            self.player2 = Player2CPU((1234,550), self.all_sprites, None, self.punch_sound, self.kick_sound)
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1
        self.show_countdown()
        while self.running:
            dt = min(self.clock.tick() / 1000, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.health_drop_event:
                    HealthDrop((self.all_sprites, self.health_sprites), (randint(100,1200), 0))
                if event.type == self.fireball_drop_event:
                    FireballDrop((self.all_sprites, self.fireball_drop_sprites), (randint(100,1200), 0))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                        if not self.paused:
                            self.show_countdown()
            self.display_surface.blit(self.background, (0,0))
            self.all_sprites.draw(self.display_surface)
            self.display_winner()
            self.check_collisions(dt)
            if not self.paused:
                self.all_sprites.update(dt, self.display_surface, self.all_sprites, self.fireball_sprites)
                pygame.display.update()
        pygame.quit()

if __name__ == "__main__":
    Game().run()
