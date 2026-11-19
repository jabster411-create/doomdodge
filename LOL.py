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

jump_sound = pygame.mixer.Sound("doomguy-unf-grunt.mp3")
jump_sound.set_volume(0.5)

DEAD_sound = pygame.mixer.Sound("classic_hurt.mp3")
DEAD_sound.set_volume(0.6)

WIDTH = 2000
HEIGHT = 800
BG = pygame.transform.scale(pygame.image.load("doomb.jpeg"), (WIDTH, HEIGHT))
FPS = 60

GRAVITY = 0.5
JUMP_STRENGTH = -20
ENEMY_SPEED = 7.5
y_velocity = 0
is_jumping = False
FLOOR_Y = HEIGHT - 80

WALK_SPEED = 5
SPRINT_SPEED = 11

sprint_timer = 0
cooldown_end_time = 0
MAX_SPRINT_FRAMES = 120

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doomdodge")

clock = pygame.time.Clock()
PLAYER_WIDTH, PLAYER_HEIGHT = 95, 80
ENEMY_SIZE = 90

PLAYER_START = (100, HEIGHT - PLAYER_HEIGHT - 100)
ENEMY_START = (WIDTH - ENEMY_SIZE - 100, 100)

player = pygame.Rect(PLAYER_START[0], PLAYER_START[1], PLAYER_WIDTH, PLAYER_HEIGHT)
player_gif = gif_pygame.load("doomguy.gif")
gif_pygame.transform.scale(player_gif, (PLAYER_WIDTH, PLAYER_HEIGHT))

enemy_gif = gif_pygame.load("caca.gif")
gif_pygame.transform.scale(enemy_gif, (ENEMY_SIZE, ENEMY_SIZE))
for frame, duration in enemy_gif.frames:
    frame.set_colorkey((0, 0, 0))

# --- PATROL & CHASE SETTINGS ---
patrol_waypoints = [
    (WIDTH - 150, 150),
    (300, 150),
    (300, 350),
    (WIDTH - 150, 350)
]
DETECT_RADIUS = 455  # How close the player must be for the enemy to chase
SPAWN_INTERVAL = 10  # Seconds between new enemy spawns
# -------------------------------

def create_enemy():
    rect = pygame.Rect(ENEMY_START[0], ENEMY_START[1], ENEMY_SIZE, ENEMY_SIZE)
    return {
        "rect": rect,
        "hitbox": rect.inflate(-45, -45),
        "waypoint": 0
    }

enemies = [create_enemy()]
last_spawn_time = time.time()

platforms = [
    pygame.Rect(300, FLOOR_Y - 150, 250, 20),
    pygame.Rect(700, FLOOR_Y - 280, 250, 20),
    pygame.Rect(1150, FLOOR_Y - 150, 250, 20),
    pygame.Rect(1500, FLOOR_Y - 300, 250, 20),
]

start_time = time.time()
FONT = pygame.font.SysFont("timesnewroman", 30, bold=True)

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
            sprint_timer += 1
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

    restart = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                restart = True
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE and not is_jumping:
                jump_sound.play()
                y_velocity = JUMP_STRENGTH
                is_jumping = True

    # --- SPAWN NEW ENEMY EVERY 60 SECONDS ---
    if time.time() - last_spawn_time >= SPAWN_INTERVAL:
        enemies.append(create_enemy())
        last_spawn_time = time.time()

    # --- ENEMY PATROL & CHASE LOGIC ---
    for e in enemies:
        rect = e["rect"]
        dist_to_player = math.hypot(player.centerx - rect.centerx, player.centery - rect.centery)

        if dist_to_player < DETECT_RADIUS:
            target_x, target_y = player.centerx, player.centery
            chasing = True
        else:
            target_x, target_y = patrol_waypoints[e["waypoint"]]
            chasing = False

        direction_x = target_x - rect.centerx
        direction_y = target_y - rect.centery
        distance = math.hypot(direction_x, direction_y)

        if distance > 0:
            rect.x += round(direction_x / distance * ENEMY_SPEED)
            rect.y += round(direction_y / distance * ENEMY_SPEED)

        if not chasing and distance < 10:
            e["waypoint"] = (e["waypoint"] + 1) % len(patrol_waypoints)

        e["hitbox"].center = rect.center

        if e["hitbox"].colliderect(player):
            restart = True
            DEAD_sound.play()
    # ----------------------------------

    if time.time() - start_time >= 500:
        restart = True

    if restart:
        player.x, player.y = PLAYER_START
        enemies = [create_enemy()]
        last_spawn_time = time.time()
        y_velocity = 0
        is_jumping = False
        sprint_timer = 0
        cooldown_end_time = 0
        start_time = time.time()

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

    screen.blit(BG, (0, 0))
    pygame.draw.rect(screen, (101, 67, 33), (0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y))
    pygame.draw.rect(screen, (101, 67, 33), (0, FLOOR_Y, WIDTH, 20))

    for plat in platforms:
        pygame.draw.rect(screen, (101, 67, 33), plat)
        pygame.draw.rect(screen, (101, 67, 33), (plat.x, plat.y, plat.width, 6))

    player_gif.render(screen, (player.x, player.y))
    for e in enemies:
        enemy_gif.render(screen, (e["rect"].x, e["rect"].y))

    elapsed = int(time.time() - start_time)
    time_text = FONT.render(f"Time: {elapsed}s | Enemies: {len(enemies)}", True, "white")
    screen.blit(time_text, (10, 10))

    pygame.display.flip()

pygame.quit()
