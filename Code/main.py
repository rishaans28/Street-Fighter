import pygame
from sprites import *
from random import randint

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((1350, 800), vsync=1)
        pygame.display.set_caption("Street Fighter")
        self.clock = pygame.time.Clock()
        self.running = True
        self.bgnum = randint(1,2)
        if self.bgnum == 1:
            self.background = pygame.image.load(join("Images", "background1.png"))
        if self.bgnum == 2:
            self.background = pygame.image.load(join("Images", "background2.png"))
        self.background = pygame.transform.scale(self.background, (1350, 800))
        self.all_sprites = pygame.sprite.Group()
        self.punch_sound = pygame.mixer.Sound(join("Audio", "punch.mp3"))
        self.player1 = Player1((100,550), self.all_sprites, None, self.punch_sound)
        self.player2 = Player2((1200,550), self.all_sprites, None, self.punch_sound)
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1
        self.player1_wins_img = pygame.image.load(join("Images", "player1wins.png"))
        self.player1_wins_rect = self.player1_wins_img.get_frect(center = (1350/2, 800/2))
        self.player2_wins_img = pygame.image.load(join("Images", "player2wins.png"))
        self.player2_wins_rect = self.player2_wins_img.get_frect(center = (1350/2, 800/2))

    def show_countdown(self):
        self.one = pygame.image.load(join("Images", "1.png"))
        self.one_rect = self.one.get_frect(center = (1350/2, 800/2))
        
        self.two = pygame.image.load(join("Images", "2.png"))
        self.two_rect = self.two.get_frect(center = (1350/2, 800/2))
        
        self.three = pygame.image.load(join("Images", "3.png"))
        self.three_rect = self.three.get_frect(center = (1350/2, 800/2))
        
        self.fight = pygame.image.load(join("Images", "fight.png"))
        self.fight_rect = self.fight.get_frect(center = (1350/2, 800/2))
        countdown = [
            (self.three, self.three_rect),
            (self.two, self.two_rect),
            (self.one, self.one_rect),
            (self.fight, self.fight_rect)
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
    
    def display_winner(self):
        if self.player1.winner == "player2":
            self.display_surface.blit(self.player2_wins_img, self.player2_wins_rect)
        if self.player2.winner == "player1":
            self.display_surface.blit(self.player1_wins_img, self.player1_wins_rect)

    def run(self):
        self.show_countdown()
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.display_surface.blit(self.background, (0,0))
            self.all_sprites.draw(self.display_surface)
            self.all_sprites.update(dt, self.display_surface)
            self.display_winner()
            pygame.display.update()
        pygame.quit()

if __name__ == "__main__":
    Game().run()
