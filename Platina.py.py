import pygame
import sys
from pathlib import Path

pygame.init()

WIDTH, HEIGHT = 1000, 600
FPS = 60

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Platformer")
CLOCK = pygame.time.Clock()

ASSET_DIR = Path(__file__).parent / "assets"

# Load images
background = pygame.image.load(ASSET_DIR / "background.png").convert()
grass = pygame.image.load(ASSET_DIR / "grass.png").convert_alpha()
enemy_image = pygame.image.load(ASSET_DIR / "enemy.png").convert_alpha()
player_image = pygame.image.load(ASSET_DIR / "player.png").convert_alpha()

# Sizes
PLAYER_SIZE = (72, 60)
ENEMY_SIZE = (70, 55)

player_image = pygame.transform.smoothscale(
    player_image, PLAYER_SIZE
)

enemy_image = pygame.transform.smoothscale(
    enemy_image, ENEMY_SIZE
)

grass = pygame.transform.smoothscale(
    grass, (205, 48)
)

WHITE = (255, 255, 255)


def draw_background(surface):
    bg = pygame.transform.smoothscale(
        background,
        (WIDTH, HEIGHT)
    )
    surface.blit(bg, (0, 0))


def draw_grass_platform(surface, rect):
    x = rect.x

    while x < rect.right:
        w = min(
            grass.get_width(),
            rect.right - x
        )

        surface.blit(
            grass,
            (x, rect.y),
            pygame.Rect(
                0,
                0,
                w,
                grass.get_height()
            )
        )

        x += w


# =========================
# PLAYER
# =========================

class Player:

    def __init__(self, x, y):

        self.x = float(x)
        self.y = float(y)

        self.w, self.h = PLAYER_SIZE

        self.speed = 6
        self.vx = 0
        self.vy = 0

        self.gravity = 0.8
        self.jump_power = -15

        self.on_ground = False

        # Spin while jumping
        self.rotation = 0
        self.rotation_speed = 8

        self.spawn_x = x
        self.spawn_y = y

    @property
    def rect(self):
        return pygame.Rect(
            round(self.x),
            round(self.y),
            self.w,
            self.h
        )

    def reset(self):

        self.x = float(self.spawn_x)
        self.y = float(self.spawn_y)

        self.vx = 0
        self.vy = 0

        self.rotation = 0
        self.on_ground = False

    def jump(self):

        if self.on_ground:

            self.vy = self.jump_power
            self.on_ground = False

    def update(self, platforms):

        keys = pygame.key.get_pressed()

        # Normal platformer movement
        self.vx = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx -= self.speed

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx += self.speed

        # =========================
        # HORIZONTAL MOVEMENT
        # =========================

        self.x += self.vx

        current = self.rect

        for platform in platforms:

            if current.colliderect(platform):

                if self.vx > 0:
                    self.x = platform.left - self.w

                elif self.vx < 0:
                    self.x = platform.right

                current = self.rect

        # =========================
        # VERTICAL MOVEMENT
        # =========================

        old_rect = self.rect

        self.vy += self.gravity
        self.y += self.vy

        current = self.rect

        self.on_ground = False

        # Landing
        if self.vy >= 0:

            for platform in platforms:

                if (
                    current.right > platform.left
                    and current.left < platform.right
                    and old_rect.bottom <= platform.top
                    and current.bottom >= platform.top
                ):

                    self.y = platform.top - self.h
                    self.vy = 0
                    self.on_ground = True

                    break

        # Spin while jumping
        if not self.on_ground:

            self.rotation = (
                self.rotation +
                self.rotation_speed
            ) % 360

        else:

            self.rotation = 0

    def draw(self, surface, camera_x):

        rotated = pygame.transform.rotate(
            player_image,
            self.rotation
        )

        center = (
            self.x + self.w / 2 - camera_x,
            self.y + self.h / 2
        )

        surface.blit(
            rotated,
            rotated.get_rect(center=center)
        )


# =========================
# ENEMY
# =========================

class Enemy:

    def __init__(self, x, y):

        self.x = float(x)
        self.y = float(y)

        self.w, self.h = ENEMY_SIZE

        # Balls spin continuously
        self.rotation = 0
        self.rotation_speed = 4

        self.alive = True

        self.squash_timer = 0

    @property
    def rect(self):

        return pygame.Rect(
            round(self.x),
            round(self.y),
            self.w,
            self.h
        )

    def update(self):

        if self.alive:

            self.rotation = (
                self.rotation +
                self.rotation_speed
            ) % 360

        elif self.squash_timer > 0:

            self.squash_timer -= 1

    def squash(self):

        if self.alive:

            self.alive = False
            self.squash_timer = 12

    def draw(self, surface, camera_x):

        # Draw flattened enemy
        if not self.alive:

            if self.squash_timer <= 0:
                return

            squashed = pygame.transform.smoothscale(
                enemy_image,
                (self.w + 12, 18)
            )

            rect = squashed.get_rect(
                midbottom=(
                    self.x + self.w / 2 - camera_x,
                    self.y + self.h
                )
            )

            surface.blit(
                squashed,
                rect
            )

            return

        # Normal spinning enemy
        rotated = pygame.transform.rotate(
            enemy_image,
            self.rotation
        )

        center = (
            self.x + self.w / 2 - camera_x,
            self.y + self.h / 2
        )

        surface.blit(
            rotated,
            rotated.get_rect(center=center)
        )


# =========================
# LEVEL
# =========================

platforms = [

    # Ground
    pygame.Rect(
        -100,
        535,
        1200,
        70
    ),

    pygame.Rect(
        1080,
        535,
        700,
        70
    ),

    pygame.Rect(
        1860,
        535,
        850,
        70
    ),

    pygame.Rect(
        2790,
        535,
        900,
        70
    ),

    # Floating platforms
    pygame.Rect(
        650,
        430,
        230,
        48
    ),

    pygame.Rect(
        1280,
        390,
        230,
        48
    ),

    pygame.Rect(
        1620,
        470,
        190,
        48
    ),

    pygame.Rect(
        2200,
        420,
        260,
        48
    ),

    pygame.Rect(
        2500,
        335,
        210,
        48
    ),

    pygame.Rect(
        3100,
        430,
        260,
        48
    )
]


# Enemies
enemies = [

    Enemy(420, 480),

    Enemy(750, 375),

    Enemy(1160, 480),

    Enemy(1450, 480),

    Enemy(1700, 415),

    Enemy(2010, 480),

    Enemy(2300, 365),

    Enemy(2570, 280),

    Enemy(2920, 480),

    Enemy(3210, 375)
]


player = Player(
    130,
    475
)


# =========================
# CAMERA
# =========================

camera_x = 0.0


# =========================
# UI
# =========================

font = pygame.font.Font(
    None,
    30
)

big_font = pygame.font.Font(
    None,
    64
)


def draw_ui(surface):

    text = font.render(
        "A/D or ARROWS = MOVE    SPACE/UP = JUMP    R = RESTART",
        True,
        WHITE
    )

    surface.blit(
        text,
        (20, 18)
    )


def draw_game_over(surface):

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 125)
    )

    surface.blit(
        overlay,
        (0, 0)
    )

    msg = big_font.render(
        "CRASH!",
        True,
        WHITE
    )

    hint = font.render(
        "Press R to restart",
        True,
        WHITE
    )

    surface.blit(
        msg,
        msg.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 20
            )
        )
    )

    surface.blit(
        hint,
        hint.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 35
            )
        )
    )


# =========================
# COLLISION FUNCTIONS
# =========================

def player_hits_enemy(
    player_rect,
    enemy_rect
):

    smaller_player = player_rect.inflate(
        -14,
        -10
    )

    smaller_enemy = enemy_rect.inflate(
        -10,
        -8
    )

    return smaller_player.colliderect(
        smaller_enemy
    )


def is_stomping(
    player_rect,
    enemy_rect,
    previous_bottom,
    player_vy
):

    horizontal_overlap = (
        player_rect.right > enemy_rect.left
        and
        player_rect.left < enemy_rect.right
    )

    crossed_top = (
        previous_bottom <= enemy_rect.top
        and
        player_rect.bottom >= enemy_rect.top
    )

    falling = player_vy > 0

    return (
        horizontal_overlap
        and
        crossed_top
        and
        falling
    )


# =========================
# MAIN LOOP
# =========================

running = True
dead = False


while running:

    CLOCK.tick(FPS)

    # =========================
    # EVENTS
    # =========================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if (
                event.key in
                (pygame.K_SPACE, pygame.K_UP)
                and not dead
            ):

                player.jump()

            if event.key == pygame.K_r:

                player.reset()

                for enemy in enemies:

                    enemy.alive = True
                    enemy.squash_timer = 0

                dead = False
                camera_x = 0


    # =========================
    # UPDATE
    # =========================

    if not dead:

        # Save bottom before movement
        previous_bottom = player.rect.bottom

        player.update(platforms)

        # Update spinning enemies
        for enemy in enemies:
            enemy.update()

        # Enemy collisions
        for enemy in enemies:

            if not enemy.alive:
                continue

            player_rect = player.rect
            enemy_rect = enemy.rect

            # Mario-style stomp
            if is_stomping(
                player_rect,
                enemy_rect,
                previous_bottom,
                player.vy
            ):

                enemy.squash()

                # Bounce after stomping
                player.y = (
                    enemy_rect.top -
                    player.h
                )

                player.vy = -11

                player.on_ground = False

                continue

            # Side collision
            if player_hits_enemy(
                player_rect,
                enemy_rect
            ):

                dead = True

                break

        # Camera follows player
        target_camera = max(
            0,
            player.x - 280
        )

        camera_x += (
            target_camera -
            camera_x
        ) * 0.12

        # Fell off the map
        if player.y > HEIGHT + 150:

            dead = True


    # =========================
    # DRAW
    # =========================

    draw_background(SCREEN)

    # Platforms
    for platform in platforms:

        visible_platform = platform.move(
            -round(camera_x),
            0
        )

        draw_grass_platform(
            SCREEN,
            visible_platform
        )

    # Enemies
    for enemy in enemies:

        enemy.draw(
            SCREEN,
            camera_x
        )

    # Player
    player.draw(
        SCREEN,
        camera_x
    )

    # UI
    draw_ui(SCREEN)

    if dead:

        draw_game_over(SCREEN)

    pygame.display.flip()


pygame.quit()
sys.exit()