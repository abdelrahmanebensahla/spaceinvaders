import pygame
import time
import os
import random
pygame.font.init()

# Game Window
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# Enemy Ship Images
ENEMY_SHIP0 = pygame.transform.scale(pygame.image.load(os.path.join("IMAGES", "E_SHIP0.png")), (50, 50))
ENEMY_SHIP1 = pygame.transform.scale(pygame.image.load(os.path.join("IMAGES", "E_SHIP1.png")), (50, 50))
ENEMY_SHIP2 = pygame.transform.scale(pygame.image.load(os.path.join("IMAGES", "E_SHIP2.png")), (50, 50))

# Player Ship Images
PLAYER_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("IMAGES", "P_SHIP.png")), (60, 60))

# Bullets
RED_BULLET = None
BLUE_BULLET = None
YELLOW_BULLET = pygame.transform.scale(pygame.image.load(os.path.join("IMAGES", "YELLOW_BULLET.png")), (50, 50))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("IMAGES", "SPACE_BACKGROUND.png")), (WIDTH, HEIGHT))

# Bullet
class Bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    def move(self, vel):
        self.y -= vel
    
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)

# Ship Class, Allows For Multiple Definitions Of A "Ship", Including Player Ship AND Enemy Ships
class Ship:
    COOLDOWN = 30
    # Initializes All Necessary Variables
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.bullet_img = None
        self.bullets = []
        self.cooldown_counter = 0
    
    # Drawing Player Related Objects
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(window)
    
    # Handles The Bullets Interaction
    def bullet_projectile(self, vel, obj):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            else:
                if bullet.collision():
                    obj.health -= 10
                    self.bullets.remove(bullet)
        
    # Cooldown
    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        else:
            if self.cooldown_counter > 0:
                self.cooldown_counter += 1        
    
    # Shooting
    def shoot(self):
        if self.cooldown_counter == 0:
            bullet = Bullet(self.x, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.cooldown_counter = 1
    
    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()

# Player Ship
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP
        self.bullet_img = YELLOW_BULLET
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    
    def bullet_projectile(self, vel, objs):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        objs.remove(obj)
                        self.bullets.remove(bullet)
                        
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
    
    def healthbar(self, window):
        pygame.draw.rect(window, (100,100,100), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (50,200,50), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

# Enemy Ship
class Enemy(Ship):
    COLOR_MAP = {
    "enemy0" : (ENEMY_SHIP0, RED_BULLET),
    "enemy1" : (ENEMY_SHIP1, RED_BULLET),
    "enemy2" : (ENEMY_SHIP2, RED_BULLET)
    }
    
    def __init__(self, x, y, color, health=100):
        "enemy0", "enemy1", "enemy2"
        super().__init__(x, y, health)
        self.ship_img, self.bullet_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def move(self, vel):
        self.y += vel

# Collision Mechanic
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# Define Main Function
def main():
    run = True
    FPS = 144
    stage = 0
    hp = 5
    main_font = pygame.font.Font(os.path.join("FONTS", "ARCADECLASSIC.TTF"), 50)
    
    # Projectiles
    bullet_vel = 4
    
    # Enemy Mechanics
    enemies = []
    wave_length = 5
    enemy_vel = 1
    
    # Player Ship Attributes
    player_vel = 5
    player = Player(WIDTH/2 - 20, HEIGHT - 150) # Calls Ship Class On x, y Location
    
    clock = pygame.time.Clock()
    
    lost = False
    
    lost_count = 0
    
    def redraw_window():
        WIN.blit(BG, (0, 0))
        
        # Draw Text
        UI_hp = main_font.render(f"HP   {hp}", 1, (255,255,255))
        UI_stage = main_font.render(f"STAGE   {stage}", 1, (255,255,255))
        
        WIN.blit(UI_hp, (10,10))
        WIN.blit(UI_stage, (WIDTH - UI_stage.get_width() - 10, 10))
        
        for enemy in enemies:
            enemy.draw(WIN)
        
        player.draw(WIN)
        
        if lost:
            lost_label = main_font.render("YOU LOSE", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
        
        pygame.display.update()
    
    # Handles ON/OFF of Program
    while run:
        clock.tick(FPS)
        redraw_window()
        
        if hp <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        
        if lost:
            if lost_count > FPS * 5:
                run = False
            else:
                continue
            
        
        if len(enemies) == 0:
            stage += 1
            wave_length += 5
            for i in range(wave_length):
                grunt0 = Enemy(random.randrange(50, WIDTH-50), random.randrange(-1500, -100), "enemy0")
                grunt1 = Enemy(random.randrange(50, WIDTH-50), random.randrange(-3000, -1500), "enemy1")
                elite0 = Enemy(random.randrange(50, WIDTH-50), random.randrange(-3000, -1500), "enemy2", 200)
                enemies.append(grunt0)
                enemies.append(grunt1)
                enemies.append(elite0)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player.y - player_vel > 0: # Up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: # Down
            player.y += player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # Right
            player.x += player_vel
        if keys[pygame.K_a] and player.x - player_vel > 0: # Left
            player.x -= player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        if keys[pygame.K_ESCAPE]:
            run = False
            
        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.bullet_projectile(bullet_vel, player)
            
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            else:
                if enemy.y + enemy.get_height() > HEIGHT:
                    hp -= 1
                    enemies.remove(enemy)
        
        player.bullet_projectile(bullet_vel, enemies)

def main_menu():
    clock = pygame.time.Clock()

    keys = pygame.key.get_pressed()
    main_font = pygame.font.Font(os.path.join("FONTS", "ARCADECLASSIC.TTF"), 50)
    run = True
    while run:
        clock.tick(60)
        pygame.display.update
        WIN.blit(BG, (0,0))
        title_label = main_font.render("C li c k      T o      B e g i n", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_height()/2, HEIGHT/2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
        
        if keys[pygame.K_ESCAPE]:
            quit()
                
    
# On Launch
main_menu()