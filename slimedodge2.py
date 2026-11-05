import pygame
import time
import math
import pygame.font
import gif_pygame
pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("03. E1M1 - At Doom's Gate [03. E1M1 - At Doom's Gate].mp3")

pygame.mixer.music.set_volume(0.5)

pygame.mixer.music.play(loops=-2)

jump_sound = pygame.mixer.Sound("jump.mp3.mp3")

jump_sound.set_volume(0.5)

WIDTH = 2000
HEIGHT = 800
BG = pygame.transform.scale(pygame.image.load("doomb.jpeg"),(WIDTH, HEIGHT))
FPS = 60

GRAVITY = 0.5
JUMP_STRENGTH = -20
ENEMY_SPEED = 6
y_velocity = 0
is_jumping = False
FLOOR_Y = HEIGHT - 80
game_over = False
win = False

WALK_SPEED = 5
SPRINT_SPEED = 11

sprint_timer = 0
cooldown_end_time = 0
MAX_SPRINT_FRAMES = 120

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("slime dodge2")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont
PLAYER_WIDTH, PLAYER_HEIGHT = 95, 90
ENEMY_SIZE = 80
player = pygame.Rect(100, HEIGHT - PLAYER_HEIGHT - 100, PLAYER_WIDTH, PLAYER_HEIGHT)
player_image = pygame.image.load("doom2.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (PLAYER_WIDTH, PLAYER_HEIGHT))


enemy_gif = gif_pygame.load("caca.gif")
gif_pygame.transform.scale(enemy_gif, (ENEMY_SIZE, ENEMY_SIZE))
for frame, duration in enemy_gif.frames:
    frame.set_colorkey((0,0,0))
    enemy = pygame.Rect(WIDTH - ENEMY_SIZE - 100, 100, ENEMY_SIZE, ENEMY_SIZE)

enemy_hitbox = enemy.inflate(-45, -45)
platforms = [
    pygame.Rect(300, FLOOR_Y - 150, 250, 20),
    pygame.Rect(700, FLOOR_Y - 280, 250, 20),
    pygame.Rect(1150, FLOOR_Y - 150, 250, 20),
    pygame.Rect(1500, FLOOR_Y - 300, 250, 20),
]

    

start_time = time.time()
FONT = pygame.font.SysFont("timesnewroman", 30)
  
running = True
while running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()


    current_speed = WALK_SPEED
    on_cooldown = current_time < cooldown_end_time

    if not on_cooldown:
        if keys[pygame.K_LSHIFT] and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            current_speed = SPRINT_SPEED
            sprint_timer  += 1

            if sprint_timer >= MAX_SPRINT_FRAMES:
               cooldown_end_time = current_time + 1000
               
           
        
        else:       
             if sprint_timer > 0:
                  sprint_timer -= 1

    else:
        
        if sprint_timer == 0:
            sprint_timer -= 2
        if sprint_timer < 0:
            sprint_timer = 0


    if keys[pygame.K_LEFT] and player.x - current_speed > 0:
        player.x -= current_speed
    if keys[pygame.K_RIGHT] and player.x + current_speed + player.width < WIDTH:
        player.x += current_speed
    

    for event in pygame.event.get():
         if event.type == pygame.QUIT:
             running = False
         elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE and not is_jumping:
                jump_sound.play()
                y_velocity = JUMP_STRENGTH
                is_jumping = True
                
            if (game_over or win) and event.key == pygame.K_r:
                reset_round()

    direction_x = player.centerx - enemy.centerx
    direction_y = player.centery - enemy.centery
    distance = math.hypot(direction_x, direction_y)       
        
    if distance > 0:
        enemy.x += round(direction_x / distance * ENEMY_SPEED)
        enemy.y += round(direction_y / distance * ENEMY_SPEED)

        enemy_hitbox.center = enemy.center

        if enemy_hitbox.colliderect(player):
            print("HIT!")
            running = False
        if time.time() - start_time >= 60:
            print("YES YOU MADE IT!")
            running = False
            


  
    y_velocity += GRAVITY
    player.y += y_velocity

    
    on_ground = False


    if y_velocity >= 0:
       for plat in platforms:
            if player.colliderect(plat) and player.bottom - y_velocity <= plat.top + 1:
                player.bottom = plat.top
                y_velocity = 0
                on_ground = True
    

    if player.bottom >= FLOOR_Y + 17:
        player.bottom = FLOOR_Y + 17
        y_velocity = 0
        on_ground = True


    is_jumping = not on_ground



            


    screen.blit(BG)
    pygame.draw.rect(screen, (101, 67, 33), (0, FLOOR_Y, WIDTH, HEIGHT -  FLOOR_Y))
    pygame.draw.rect(screen, (144, 238, 144), (0, FLOOR_Y, WIDTH, 20))

    for plat in platforms:
        pygame.draw.rect(screen, (101, 67, 33), plat)
        pygame.draw.rect(screen, (144, 238, 144), (plat.x, plat.y, plat.width, 6))

    screen.blit(player_image, (player.x, player.y))
    enemy_gif.render(screen, (enemy.x, enemy.y))
    
    elapsed = int(time.time() - start_time)
    time_text = FONT.render(f"clock: {elapsed}s", True, "white")
    screen.blit(time_text, (10, 10))
    

        

    pygame.display.flip()


pygame.quit()
