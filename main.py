import pygame
from assets import *
from random import randint, choice
from sys import exit
from pygame import mixer
from pygame import surface

pygame.init()

# variables
WIDTH = 1300
HEIGHT = 700

shoot = False
mbt = False # mouse on button
death_type = 'default'
game_status = 'menu'
player_health = 100
death_anim_index = 0
score = 0

# loading and converting textures
def image_load(texture):
    image = pygame.image.load(texture).convert_alpha()
    return image

# rendeting any font
def render_font(font_type, name, color):
    rendred_font = font_type.render(name,False,color)
    return rendred_font

# font and text
game_font = pygame.font.Font(font,40)
huge_font = pygame.font.Font(font,100)
menu_font = pygame.font.Font(menu_font,150)
font_col = (206,205,205)

# preset some texts
score_text = render_font(game_font,'Score:',font_col)
g_over_text = render_font(huge_font,'Game Over !',font_col)
enter_menu = render_font(game_font,'Press "space" to go to the menu',font_col)
game_name = render_font(menu_font,'Rounded By',(14,14,14))
game_name_shadow = render_font(menu_font,'Rounded By',(44,44,44))
lost_text = render_font(huge_font,'Lost in the forest ', font_col)
game_ver = render_font(game_font,'0.0.1', font_col)

# screen window
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Rounded By')

# framerate
clock = pygame.time.Clock()
FPS = 60

# updating scoreboard
def updating_score():
    scores = render_font(game_font,f'{score}', font_col)
    screen.blit(scores,(175,20))

# load images
grass_surface = image_load(grass)
trees_ups = image_load(trees_up)
trees_downs = image_load(trees_down)
bullet_img = image_load(bullet_)
scoreboard = image_load(scoreboard_img)
light_beam = image_load(light)
menu_bg = image_load(menu_background)
play_button = image_load(buttons[0])
forest_death_pic = image_load(forest_death)

button_rect = play_button.get_rect(center = (615,350))

# soundtack and some sounds
def game_track():
    mixer.music.set_volume(0.4)
    if game_status == 'active':
        mixer.music.load(soundtrack)
        mixer.music.play(-1)
    elif game_status == 'menu':
        mixer.music.load(menu_track)
        mixer.music.play(-1)
    elif death_type == 'lost':
        mixer.music.load(lost_sound)
        mixer.music.play()
    elif death_type == 'default':
        mixer.music.load(game_over)
        mixer.music.play()

game_track()

# defining classes for making sprites
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.player_index = 0
        self.flip = False
        self.direction = 1
        self.cooldown = 10
        self.image = image_load(player_idle[int(self.player_index)])
        self.rect = self.image.get_rect(midbottom = (WIDTH/2,HEIGHT/2))

    # sound
        self.shoot_sound = pygame.mixer.Sound(shooting)
        self.shoot_sound.set_volume(0.2)

    # keyboard control
    def player_input(self):
        keys = pygame.key.get_pressed()
        if not keys[pygame.K_w] and not keys[pygame.K_s] and not keys[pygame.K_d] and not keys[pygame.K_a]:
            self.animation(player_idle)
        if keys[pygame.K_w]:
            if not keys[pygame.K_s]:
                self.animation(player_run)
            self.rect.y -= 4
        if keys[pygame.K_a]:
            self.flip = True
            self.direction = -1
            if not keys[pygame.K_s] and not keys[pygame.K_w]:
                if not keys[pygame.K_d]:
                    self.animation(player_run)
            if not self.rect.x < 0:
                self.rect.x -= 4.2
        if keys[pygame.K_s]:
            self.animation(player_run)
            self.rect.y += 4
        if keys[pygame.K_d]:
            self.direction = 1
            self.flip = False
            if not keys[pygame.K_s] and not keys[pygame.K_w] :
                self.animation(player_run)
            if not self.rect.x > 1196:
                self.rect.x += 4.2

    def shoot(self):
        if shoot == True and self.cooldown == 10:
            self.shoot_sound.play()
            bullet = Bullet(self.rect.centerx + 0.6*(self.direction*self.rect.size[0]) , self.rect.centery - 10, self.direction)
            bullets.add(bullet)
            self.cooldown -= 10
        else: pass
        
    def animation(self, condition):
        for slide in condition:
            self.player_index += 0.03
            if self.player_index >= len(condition):self.player_index = 0
            pic = image_load(condition[int(self.player_index)])
            self.image = pygame.transform.flip(pic, self.flip, False)

    # colision between player and enemies
    def collision(self):
        for enemy in enemies:
            if pygame.sprite.spritecollide(self, enemies, True):
                enemy.death()
                global game_status, death_anim_index, player_health
                player_health -= 25
                if player_health <= 0:
                    death_anim_index = 0
                    game_status = 'dead'
                    game_track()

    def lost_in_forest(self):
        if self.rect.y > 590 or self.rect.y < -20:
            global game_status, death_type
            game_status = 'dead'
            death_type = 'lost'
            game_track()

    def update(self):
        if self.cooldown < 10:
            self.cooldown += 0.5
        self.player_input()
        self.animation('')
        self.lost_in_forest()
        self.shoot()
        self.collision()
        
class Enemies(pygame.sprite.Sprite):
    def __init__(self,type,side):
        super().__init__()

        self.animation_index = 0
        self.side = side

        # sound
        self.explosion_sound = pygame.mixer.Sound(explode)
        self.explosion_sound.set_volume(0.3)

        if side == 'right':
            self.flip = True
        else: 
            self.flip = False

        # collects all textures into one list
        self.frames = []
        for path in type:
            frame = image_load(path)
            pic = pygame.transform.flip(frame, self.flip, False)
            self.frames.append(pic)

        self.image = self.frames[self.animation_index]

        if self.side == 'right':
            self.rect = self.image.get_rect(midbottom = (randint(WIDTH+100, WIDTH+300), randint(HEIGHT-500, HEIGHT-100)))
        else:
            self.rect = self.image.get_rect(midbottom = (randint(WIDTH-1600, WIDTH-1400), randint(HEIGHT-500, HEIGHT-100)))

    def animation(self):
       self.animation_index += 0.1
       if self.animation_index >= len(self.frames): self.animation_index = 0
       self.image = self.frames[int(self.animation_index)]

    # kills entities when they are out of the screen
    def destroy(self):
        if self.rect.x < -128 and self.side == 'right':
            self.kill()
        if self.rect.x > 1600 and self.side == 'left':
            self.kill()
    
    # plays death animation
    def death(self):
        explosion = Explosion(self.rect.centerx, self.rect.centery, self.side)
        explosions.add(explosion)
        self.explosion_sound.play()

    def update(self):
        self.animation()
        if self.side == 'right' :
            self.rect.x -= 4
        elif self.side == 'left' :
            self.rect.x += 4
        self.destroy()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.speed = 20
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
    
    def update(self):
        if self.direction == 1:
            self.image = bullet_img
            self.rect.x += self.speed
        if self.direction == -1:
            self.image = pygame.transform.flip(bullet_img, True, False)
            self.rect.x -= self.speed

        # deletes bullets when they go off the screen
        if self.rect.right < 0 or self.rect.right > WIDTH+20:
            self.kill()

        # collision between bullet and enemy
        for enemy in enemies:
            if pygame.sprite.spritecollide(enemy,bullets,True):
                global score
                score += 1
                enemy.death()
                enemy.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, side):
        super().__init__()

        self.animation_index = 0
        self.frames = []
        self.image = image_load(explosion1[0])
        self.rect = self.image.get_rect(center = (x,y))
        if side == 'right':
            self.flip = False
        else:
            self.flip = True

        # collects all textures into one list
        for path in explosion1:
            frame = image_load(path)
            pic = pygame.transform.flip(frame, self.flip, False)
            self.frames.append(pic)
        
    def animation(self):
       self.animation_index += 0.17
       if self.animation_index >= len(self.frames): self.animation_index = 0
       self.image = self.frames[int(self.animation_index)]
        #kills explosion after animation 
       if self.animation_index >= 5.5:
           self.kill()
    
    def update(self):
        self.animation()

# Groups
player = pygame.sprite.GroupSingle()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()
player.add(Player())

# Timer
enemies_timer = pygame.USEREVENT + 1
pygame.time.set_timer(enemies_timer, 1300)

while True:
    for event in pygame.event.get():

        # allows to close the gamed
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # timer controlling spawn of enemies
        if game_status == 'active':
            if event.type == enemies_timer:
                enemies.add(Enemies(choice([robot1_walk, robot2_walk]), choice(['right', 'left'])))

            # keyboard presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    shoot = True
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    shoot = False

        elif event.type == pygame.KEYDOWN and game_status == 'dead' and death_anim_index > 6.8:
            # going to main menu
            if event.key == pygame.K_SPACE:
                game_status = 'menu'
                
                game_track()
                score = 0
        
        # if button pressed, game will start
        elif event.type == pygame.MOUSEBUTTONDOWN and game_status == 'menu' and mbt == True:
            if event.button == pygame.BUTTON_LEFT:
                play_button = image_load(buttons[2])
                game_status = 'active'
                game_track()

    # game process
    if game_status == 'active':
        # background
        screen.blit(grass_surface,(0,0))
        screen.blit(trees_ups,(0,0))
        
        # drawing and updating entities
        enemies.draw(screen)
        enemies.update()
        player.draw(screen)
        player.update()
        bullets.draw(screen)
        bullets.update()
        explosions.draw(screen)
        explosions.update()

        black_under = pygame.Surface((270,50))
        black_under.fill((60,60,60))
        screen.blit(black_under,(14,60))
        
        #updating healthbar
        if player_health:
            healthbar = pygame.Surface((player_health*2.5,50))
            healthbar_shadow = pygame.Surface((player_health*2.5,15))
            healthbar.fill((2*player_health - 0.5*player_health,38,38))
            healthbar_shadow.fill((2.5*player_health - 0.4*player_health,38,38))
            screen.blit(healthbar,(14,60))
            screen.blit(healthbar_shadow,(14,80))

        screen.blit(trees_downs,(0,0))
        screen.blit(scoreboard,(0,0))
        screen.blit(score_text,(15,20))


    # game over screen
    elif game_status == 'dead':
        enemies.empty() # kills all enemies
        explosions.empty() # deletes all explosion effects
        bullets.empty() # deletes all the bullets
        player.sprite.rect = player.sprite.image.get_rect(midbottom = (WIDTH/2,HEIGHT/2)) # place player in the center 
        g_over_score = render_font(game_font,f'Your score: {score}',font_col) #overall score

        # creating 'end' screen
        screen.fill((24,24,24))

        # creating animated death of the player
        for slide in player_death:
            if death_anim_index <= 7:
                death_anim_index += 0.012
                death_surf = image_load(player_death[int(death_anim_index)])
            else:
                pass
        
        # output on the 'end' screen in realtion to type of death
        if death_type == 'lost':
            screen.blit(lost_text,(125,50))
            screen.blit(g_over_score,(455,170))
            screen.blit(forest_death_pic,(325,250))
            screen.blit(enter_menu,(240,630))
        else:
            if death_anim_index > 6.8:
                screen.blit(enter_menu,(250,625))
            screen.blit(g_over_score,(455,220))
            screen.blit(g_over_text,(305,100))
            screen.blit(light_beam,(485,275))
            screen.blit(death_surf, (570,385))

    # main menu
    elif game_status == 'menu':
        player_health = 100 
        death_type = 'default'
        screen.blit(menu_bg,(-100,-350))
        screen.blit(game_name_shadow,(185,105))
        screen.blit(game_name,(180,100))
        screen.blit(game_ver,(10,650))

        # creating 'play' button
        screen.blit(play_button,button_rect)
        if button_rect.collidepoint((pygame.mouse.get_pos())):
            mbt = True
            play_button = image_load(buttons[1])
        else:
            mbt = False
            play_button = image_load(buttons[0])

    if game_status == 'active':
        updating_score()

    # updating screen
    pygame.display.update()
    clock.tick(FPS)