import pygame
import sys
import random
from pathlib import Path

pygame.init()

# ============================================================
# SETTINGS
# ============================================================

WIDTH, HEIGHT = 1000, 600
FPS = 60

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Platformer")
CLOCK = pygame.time.Clock()

ASSET_DIR = Path(__file__).parent / "assets"

PLAYER_SIZE = (72, 60)
ENEMY_SIZE = (70, 55)

GROUND_TILE_SIZE = (205, 70)
PLATFORM_TILE_SIZE = (205, 48)

# Jump pad visual size
JUMP_PAD_SIZE = (125, 40)

WHITE = (255, 255, 255)

# ============================================================
# LOAD IMAGES
# ============================================================

def load_image(filename, size=None):

    image = pygame.image.load(
        ASSET_DIR / filename
    ).convert_alpha()

    if size is not None:

        image = pygame.transform.smoothscale(
            image,
            size
        )

    return image


background = load_image(
    "background.png",
    (WIDTH, HEIGHT)
)

grass = load_image(
    "grass.png",
    GROUND_TILE_SIZE
)

platform_image = load_image(
    "platform.png",
    PLATFORM_TILE_SIZE
)

player_image = load_image(
    "player.png",
    PLAYER_SIZE
)

enemy_image = load_image(
    "enemy.png",
    ENEMY_SIZE
)

# ============================================================
# JUMP PAD
# ============================================================

jump_pad_image = load_image(
    "jump_pad.png",
    JUMP_PAD_SIZE
)

# Strong jump
JUMP_PAD_POWER = -24

# ============================================================
# BACKGROUND
# ============================================================

def draw_background(surface):

    surface.blit(
        background,
        (0, 0)
    )

# ============================================================
# PLATFORM DRAWING
# ============================================================

def draw_tiled_texture(surface, image, rect):

    x = rect.x

    while x < rect.right:

        width = min(
            image.get_width(),
            rect.right - x
        )

        surface.blit(
            image,
            (x, rect.y),
            pygame.Rect(
                0,
                0,
                width,
                image.get_height()
            )
        )

        x += width


def draw_ground(surface, rect):

    draw_tiled_texture(
        surface,
        grass,
        rect
    )


def draw_platform(surface, rect):

    draw_tiled_texture(
        surface,
        platform_image,
        rect
    )

# ============================================================
# CARTOONY EFFECT
# ============================================================

effects = []


class PopEffect:

    def __init__(self, x, y):

        self.x = float(x)
        self.y = float(y)

        self.timer = 0
        self.max_timer = 18

        self.dots = []

        for _ in range(8):

            self.dots.append({
                "x": 0.0,
                "y": 0.0,
                "vx": random.uniform(
                    -3.5,
                    3.5
                ),
                "vy": random.uniform(
                    -4.5,
                    -1.5
                ),
                "size": random.randint(
                    3,
                    7
                )
            })

    def update(self):

        self.timer += 1

        for dot in self.dots:

            dot["x"] += dot["vx"]
            dot["y"] += dot["vy"]

            dot["vy"] += 0.25

    def draw(self, surface, camera_x):

        if self.timer >= self.max_timer:
            return

        alpha = max(
            0,
            int(
                255 *
                (
                    1 -
                    self.timer /
                    self.max_timer
                )
            )
        )

        effect_surface = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        for dot in self.dots:

            pygame.draw.circle(
                effect_surface,
                (
                    255,
                    235,
                    80,
                    alpha
                ),
                (
                    int(
                        self.x +
                        dot["x"] -
                        camera_x
                    ),
                    int(
                        self.y +
                        dot["y"]
                    )
                ),
                max(
                    1,
                    dot["size"]
                )
            )

        radius = 8 + self.timer * 2

        pygame.draw.circle(
            effect_surface,
            (
                255,
                255,
                255,
                alpha
            ),
            (
                int(
                    self.x -
                    camera_x
                ),
                int(self.y)
            ),
            radius,
            3
        )

        surface.blit(
            effect_surface,
            (0, 0)
        )

# ============================================================
# JUMP PAD EFFECT
# ============================================================

class JumpEffect:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.timer = 0
        self.max_timer = 15

    def update(self):

        self.timer += 1

    def draw(self, surface, camera_x):

        if self.timer >= self.max_timer:
            return

        alpha = int(
            255 *
            (
                1 -
                self.timer /
                self.max_timer
            )
        )

        effect_surface = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        # Rising lines
        for i in range(5):

            x = (
                self.x -
                camera_x -
                25 +
                i * 13
            )

            y = (
                self.y -
                self.timer * 3 -
                abs(i - 2) * 4
            )

            pygame.draw.line(
                effect_surface,
                (
                    255,
                    255,
                    255,
                    alpha
                ),
                (int(x), int(y + 15)),
                (int(x), int(y)),
                3
            )

        surface.blit(
            effect_surface,
            (0, 0)
        )

# ============================================================
# PLAYER
# ============================================================

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
        self.max_fall_speed = 18

        self.on_ground = False

        self.coyote_time = 0
        self.jump_buffer = 0

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

        self.x = float(
            self.spawn_x
        )

        self.y = float(
            self.spawn_y
        )

        self.vx = 0
        self.vy = 0

        self.rotation = 0

        self.on_ground = False

        self.coyote_time = 0
        self.jump_buffer = 0

    def jump(self):

        self.jump_buffer = 8

        if (
            self.on_ground
            or
            self.coyote_time > 0
        ):

            self.vy = self.jump_power

            self.on_ground = False

            self.coyote_time = 0

            self.jump_buffer = 0

    def update(self, collision_platforms):

        keys = pygame.key.get_pressed()

        # ====================================================
        # HORIZONTAL MOVEMENT
        # ====================================================

        self.vx = 0

        if (
            keys[pygame.K_a]
            or
            keys[pygame.K_LEFT]
        ):

            self.vx -= self.speed

        if (
            keys[pygame.K_d]
            or
            keys[pygame.K_RIGHT]
        ):

            self.vx += self.speed

        self.x += self.vx

        current = self.rect

        for platform in collision_platforms:

            if current.colliderect(platform):

                if self.vx > 0:

                    self.x = (
                        platform.left -
                        self.w
                    )

                elif self.vx < 0:

                    self.x = (
                        platform.right
                    )

                current = self.rect

        # ====================================================
        # VERTICAL MOVEMENT
        # ====================================================

        old_rect = self.rect

        self.vy += self.gravity

        self.vy = min(
            self.vy,
            self.max_fall_speed
        )

        self.y += self.vy

        current = self.rect

        self.on_ground = False

        for platform in collision_platforms:

            if not current.colliderect(
                platform
            ):
                continue

            # Landing
            if (
                self.vy >= 0
                and
                old_rect.bottom <=
                platform.top
            ):

                self.y = (
                    platform.top -
                    self.h
                )

                self.vy = 0

                self.on_ground = True

                break

            # Underside
            if (
                self.vy < 0
                and
                old_rect.top >=
                platform.bottom
            ):

                self.y = (
                    platform.bottom
                )

                self.vy = 0

                break

        # ====================================================
        # COYOTE TIME
        # ====================================================

        if self.on_ground:

            self.coyote_time = 8

        else:

            self.coyote_time = max(
                0,
                self.coyote_time - 1
            )

        # ====================================================
        # JUMP BUFFER
        # ====================================================

        self.jump_buffer = max(
            0,
            self.jump_buffer - 1
        )

        if (
            self.jump_buffer > 0
            and
            self.on_ground
        ):

            self.vy = self.jump_power

            self.on_ground = False

            self.jump_buffer = 0

        # ====================================================
        # ROTATION
        # ====================================================

        if not self.on_ground:

            self.rotation = (
                self.rotation +
                self.rotation_speed
            ) % 360

        else:

            self.rotation = 0

    def draw(
        self,
        surface,
        camera_x
    ):

        rotated = pygame.transform.rotate(
            player_image,
            self.rotation
        )

        center = (
            self.x +
            self.w / 2 -
            camera_x,

            self.y +
            self.h / 2
        )

        surface.blit(
            rotated,
            rotated.get_rect(
                center=center
            )
        )

# ============================================================
# ENEMY
# ============================================================

class Enemy:

    def __init__(
        self,
        x,
        y,
        left_bound,
        right_bound
    ):

        self.x = float(x)
        self.y = float(y)

        self.w, self.h = ENEMY_SIZE

        self.speed = 1.5

        self.direction = 1

        self.start_x = float(x)

        self.left_bound = float(
            left_bound
        )

        self.right_bound = float(
            right_bound
        )

        self.walk_timer = 0

        self.rotation = 0

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

        if not self.alive:

            if self.squash_timer > 0:

                self.squash_timer -= 1

            return

        self.x += (
            self.speed *
            self.direction
        )

        if self.x <= self.left_bound:

            self.x = self.left_bound

            self.direction = 1

        elif self.x >= self.right_bound:

            self.x = self.right_bound

            self.direction = -1

        self.walk_timer += 1

        self.rotation = (
            self.direction *
            4 *
            pygame.math.Vector2(
                1,
                0
            ).rotate(
                self.walk_timer * 24
            ).x
        )

    def squash(self):

        if self.alive:

            self.alive = False

            self.squash_timer = 14

    def draw(
        self,
        surface,
        camera_x
    ):

        if not self.alive:

            if self.squash_timer <= 0:
                return

            squashed = (
                pygame.transform.smoothscale(
                    enemy_image,
                    (
                        self.w + 14,
                        18
                    )
                )
            )

            rect = squashed.get_rect(
                midbottom=(
                    self.x +
                    self.w / 2 -
                    camera_x,

                    self.y +
                    self.h
                )
            )

            surface.blit(
                squashed,
                rect
            )

            return

        rotated = pygame.transform.rotate(
            enemy_image,
            self.rotation
        )

        center = (
            self.x +
            self.w / 2 -
            camera_x,

            self.y +
            self.h / 2
        )

        surface.blit(
            rotated,
            rotated.get_rect(
                center=center
            )
        )

# ============================================================
# LEVEL 1
# ============================================================

level1_platforms = [

    # GROUND
    pygame.Rect(
        -100,
        535,
        1300,
        70
    ),

    pygame.Rect(
        1080,
        535,
        700,
        70
    ),

    pygame.Rect(
        1400,
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

    # FLOATING
    pygame.Rect(
        650,
        430,
        195,
        48
    ),

    pygame.Rect(
        1280,
        390,
        195,
        48
    ),

    pygame.Rect(
        1620,
        470,
        195,
        48
    ),

    pygame.Rect(
        2200,
        420,
        195,
        48
    ),

    pygame.Rect(
        2500,
        335,
        195,
        48
    ),

    pygame.Rect(
        3100,
        430,
        195,
        48
    )
]

# ============================================================
# LEVEL 1 HITBOXES
# ============================================================

level1_collision_platforms = [

    pygame.Rect(
        -100,
        540,
        1300,
        68
    ),

    pygame.Rect(
        1080,
        540,
        700,
        68
    ),

    pygame.Rect(
        1400,
        540,
        850,
        68
    ),

    pygame.Rect(
        2790,
        540,
        900,
        68
    ),

    pygame.Rect(
        657,
        450,
        181,
        26
    ),

    pygame.Rect(
        1287,
        410,
        181,
        28
    ),

    pygame.Rect(
        1627,
        490,
        181,
        28
    ),

    pygame.Rect(
        2207,
        440,
        181,
        28
    ),

    pygame.Rect(
        2507,
        355,
        181,
        28
    ),

    pygame.Rect(
        3107,
        450,
        181,
        26
    )
]

# ============================================================
# LEVEL 1 JUMP PADS
# ============================================================

level1_jump_pads = [

    # x, y
    pygame.Rect(
        920,
        497,
        125,
        40
    ),

    pygame.Rect(
        1830,
        497,
        125,
        40
    )
]

# ============================================================
# LEVEL 1 ENEMIES
# ============================================================

level1_enemies = [

    Enemy(
        420,
        480,
        220,
        850
    ),

    Enemy(
        750,
        393,
        675,
        760
    ),

    Enemy(
        1160,
        480,
        1100,
        1300
    ),

    Enemy(
        1450,
        480,
        1300,
        1650
    ),

    Enemy(
        1700,
        435,
        1640,
        1745
    ),

    Enemy(
        2010,
        480,
        1900,
        2200
    ),

    Enemy(
        2300,
        383,
        2230,
        2330
    ),

    Enemy(
        2570,
        300,
        2530,
        2600
    ),

    Enemy(
        2920,
        480,
        2850,
        3500
    ),

    Enemy(
        3210,
        395,
        3130,
        3200
    )
]

# ============================================================
# LEVEL 2
# LONGER + HARDER
# ============================================================

level2_platforms = [

    # ========================================================
    # GROUND
    # ========================================================

    pygame.Rect(
        -100,
        535,
        900,
        70
    ),

    # First large gap

    pygame.Rect(
        1050,
        535,
        500,
        70
    ),

    # Small ground section

    pygame.Rect(
        1650,
        535,
        350,
        70
    ),

    # Large gap

    pygame.Rect(
        2250,
        535,
        500,
        70
    ),

    # Another gap

    pygame.Rect(
        3000,
        535,
        550,
        70
    ),

    # Final section

    pygame.Rect(
        3800,
        535,
        1100,
        70
    ),

    # ========================================================
    # FLOATING PLATFORMS
    # ========================================================

    pygame.Rect(
        500,
        420,
        195,
        48
    ),

    pygame.Rect(
        780,
        350,
        195,
        48
    ),

    pygame.Rect(
        930,
        270,
        195,
        48
    ),

    pygame.Rect(
        1150,
        390,
        195,
        48
    ),

    pygame.Rect(
        1400,
        300,
        195,
        48
    ),

    pygame.Rect(
        1570,
        410,
        195,
        48
    ),

    pygame.Rect(
        1850,
        330,
        195,
        48
    ),

    pygame.Rect(
        2050,
        240,
        195,
        48
    ),

    pygame.Rect(
        2350,
        390,
        195,
        48
    ),

    pygame.Rect(
        2580,
        300,
        195,
        48
    ),

    pygame.Rect(
        2800,
        220,
        195,
        48
    ),

    pygame.Rect(
        3150,
        380,
        195,
        48
    ),

    pygame.Rect(
        3400,
        290,
        195,
        48
    ),

    pygame.Rect(
        3650,
        390,
        195,
        48
    ),

    pygame.Rect(
        4000,
        330,
        195,
        48
    ),

    pygame.Rect(
        4300,
        250,
        195,
        48
    ),

    pygame.Rect(
        4550,
        390,
        195,
        48
    )
]

# ============================================================
# LEVEL 2 COLLISION HITBOXES
# ============================================================

level2_collision_platforms = [

    # GROUND

    pygame.Rect(
        -100,
        540,
        900,
        68
    ),

    pygame.Rect(
        1050,
        540,
        500,
        68
    ),

    pygame.Rect(
        1650,
        540,
        350,
        68
    ),

    pygame.Rect(
        2250,
        540,
        500,
        68
    ),

    pygame.Rect(
        3000,
        540,
        550,
        68
    ),

    pygame.Rect(
        3800,
        540,
        1100,
        68
    ),

    # FLOATING

    pygame.Rect(
        507,
        440,
        181,
        28
    ),

    pygame.Rect(
        787,
        370,
        181,
        28
    ),

    pygame.Rect(
        937,
        290,
        181,
        28
    ),

    pygame.Rect(
        1157,
        410,
        181,
        28
    ),

    pygame.Rect(
        1407,
        320,
        181,
        28
    ),

    pygame.Rect(
        1577,
        430,
        181,
        28
    ),

    pygame.Rect(
        1857,
        350,
        181,
        28
    ),

    pygame.Rect(
        2057,
        260,
        181,
        28
    ),

    pygame.Rect(
        2357,
        410,
        181,
        28
    ),

    pygame.Rect(
        2587,
        320,
        181,
        28
    ),

    pygame.Rect(
        2807,
        240,
        181,
        28
    ),

    pygame.Rect(
        3157,
        400,
        181,
        28
    ),

    pygame.Rect(
        3407,
        310,
        181,
        28
    ),

    pygame.Rect(
        3657,
        410,
        181,
        28
    ),

    pygame.Rect(
        4007,
        350,
        181,
        28
    ),

    pygame.Rect(
        4307,
        270,
        181,
        28
    ),

    pygame.Rect(
        4557,
        410,
        181,
        28
    )
]

# ============================================================
# LEVEL 2 JUMP PADS
# ============================================================

level2_jump_pads = [

    # Start jump
    pygame.Rect(
        680,
        495,
        125,
        40
    ),

    # Big gap
    pygame.Rect(
        820,
        310,
        125,
        40
    ),

]

# ============================================================
# LEVEL 2 ENEMIES
# ============================================================

level2_enemies = [

    Enemy(
        300,
        480,
        150,
        700
    ),

    Enemy(
        540,
        365,
        510,
        620
    ),

    Enemy(
        820,
        295,
        790,
        920
    ),

    Enemy(
        1090,
        480,
        1050,
        1450
    ),

    Enemy(
        1170,
        335,
        1150,
        1280
    ),

    Enemy(
        1430,
        245,
        1410,
        1530
    ),

    Enemy(
        1700,
        480,
        1650,
        1950
    ),

    Enemy(
        1880,
        275,
        1860,
        1980
    ),

    Enemy(
        2080,
        185,
        2050,
        2180
    ),

    Enemy(
        2380,
        335,
        2360,
        2480
    ),

    Enemy(
        2610,
        245,
        2590,
        2720
    ),

    Enemy(
        2830,
        165,
        2810,
        2930
    ),

    Enemy(
        3100,
        480,
        3050,
        3400
    ),

    Enemy(
        3180,
        325,
        3160,
        3300
    ),

    Enemy(
        3430,
        235,
        3410,
        3530
    ),

    Enemy(
        4600,
        335,
        4570,
        4720
    )
]

# ============================================================
# LEVEL SYSTEM
# ============================================================

current_level = 1

level_platforms = level1_platforms
collision_platforms = level1_collision_platforms
jump_pads = level1_jump_pads
enemies = level1_enemies

LEVEL_ENDS = {
    1: 3500,
    2: 4800
}

# ============================================================
# PLAYER
# ============================================================

player = Player(
    130,
    475
)

# ============================================================
# CAMERA
# ============================================================

camera_x = 0.0

# ============================================================
# UI
# ============================================================

font = pygame.font.Font(
    None,
    30
)

big_font = pygame.font.Font(
    None,
    64
)

small_font = pygame.font.Font(
    None,
    24
)

# ============================================================
# GAME STATE
# ============================================================

running = True

dead = False
won = False

score = 0
best_score = 0

# ============================================================
# LEVEL LOADING
# ============================================================

def load_level(level):

    global current_level
    global level_platforms
    global collision_platforms
    global jump_pads
    global enemies
    global camera_x

    current_level = level

    if level == 1:

        level_platforms = level1_platforms
        collision_platforms = level1_collision_platforms
        jump_pads = level1_jump_pads
        enemies = level1_enemies

        player.spawn_x = 130
        player.spawn_y = 475

    else:

        level_platforms = level2_platforms
        collision_platforms = level2_collision_platforms
        jump_pads = level2_jump_pads
        enemies = level2_enemies

        player.spawn_x = 130
        player.spawn_y = 475

    player.reset()

    # Reset enemies
    for enemy in enemies:

        enemy.alive = True

        enemy.squash_timer = 0

        enemy.x = enemy.start_x

        enemy.direction = 1

        enemy.rotation = 0

        enemy.walk_timer = 0

    camera_x = 0

# ============================================================
# COLLISION FUNCTIONS
# ============================================================

def player_hits_enemy(
    player_rect,
    enemy_rect
):

    smaller_player = (
        player_rect.inflate(
            -14,
            -10
        )
    )

    smaller_enemy = (
        enemy_rect.inflate(
            -10,
            -8
        )
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
        player_rect.right >
        enemy_rect.left
        and
        player_rect.left <
        enemy_rect.right
    )

    crossed_top = (
        previous_bottom <=
        enemy_rect.top
        and
        player_rect.bottom >=
        enemy_rect.top
    )

    falling = (
        player_vy > 0
    )

    return (
        horizontal_overlap
        and
        crossed_top
        and
        falling
    )

# ============================================================
# JUMP PAD COLLISION
# ============================================================

def check_jump_pads():

    player_rect = player.rect

    for pad in jump_pads:

        # Smaller hitbox than the visual pad.
        # Only the center/top area activates it.
        hitbox = pad.inflate(
            -18,
            -12
        )

        # Only activate while falling
        if player.vy < 0:
            continue

        if player_rect.colliderect(hitbox):

            # Make sure player is actually landing
            if (
                player_rect.bottom <=
                hitbox.bottom + 15
            ):

                player.y = (
                    hitbox.top -
                    player.h
                )

                player.vy = JUMP_PAD_POWER

                player.on_ground = False

                effects.append(
                    JumpEffect(
                        pad.centerx,
                        pad.top
                    )
                )

                return True

    return False

# ============================================================
# DRAW JUMP PADS
# ============================================================

def draw_jump_pads(
    surface,
    camera_x
):

    for pad in jump_pads:

        visible = pad.move(
            -round(camera_x),
            0
        )

        surface.blit(
            jump_pad_image,
            visible
        )

# ============================================================
# UI
# ============================================================

def draw_ui(surface):

    # Level
    level_text = font.render(
        f"Level {current_level}",
        True,
        WHITE
    )

    surface.blit(
        level_text,
        (20, 18)
    )

    score_text = font.render(
        f"Score: {score}",
        True,
        WHITE
    )

    surface.blit(
        score_text,
        (20, 52)
    )

    best_text = font.render(
        f"Best: {best_score}",
        True,
        WHITE
    )

    surface.blit(
        best_text,
        (20, 86)
    )

    # ========================================================
    # PROGRESS
    # ========================================================

    level_end = LEVEL_ENDS[current_level]

    progress = max(
        0,
        min(
            1,
            player.x / level_end
        )
    )

    bar_width = 220

    bar_x = (
        WIDTH -
        bar_width -
        20
    )

    bar_y = 20

    pygame.draw.rect(
        surface,
        WHITE,
        (
            bar_x,
            bar_y,
            bar_width,
            14
        ),
        2
    )

    pygame.draw.rect(
        surface,
        WHITE,
        (
            bar_x + 3,
            bar_y + 3,
            int(
                (
                    bar_width -
                    6
                ) *
                progress
            ),
            8
        )
    )

# ============================================================
# GAME OVER
# ============================================================

def draw_game_over(surface):

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (
            0,
            0,
            0,
            125
        )
    )

    surface.blit(
        overlay,
        (0, 0)
    )

    if won:

        title = "YOU WIN!"

        subtitle = (
            "You beat both levels!"
        )

    elif dead:

        title = "GAME OVER!"

        subtitle = (
            "You got ratiod."
        )

    msg = big_font.render(
        title,
        True,
        WHITE
    )

    sub = small_font.render(
        subtitle,
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
                HEIGHT // 2 - 55
            )
        )
    )

    surface.blit(
        sub,
        sub.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 5
            )
        )
    )

    surface.blit(
        hint,
        hint.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 50
            )
        )
    )

# ============================================================
# LEVEL 2 INTRO
# ============================================================

level_message_timer = 0


def draw_level_message(surface):

    if level_message_timer <= 0:
        return

    alpha = min(
        255,
        level_message_timer * 8
    )

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 90)
    )

    surface.blit(
        overlay,
        (0, 0)
    )

    if current_level == 2:

        text = big_font.render(
            "LEVEL 2",
            True,
            WHITE
        )

        subtitle = small_font.render(
            "Things just got harder.",
            True,
            WHITE
        )

    else:

        text = big_font.render(
            "LEVEL 1",
            True,
            WHITE
        )

        subtitle = small_font.render(
            "Get ready!",
            True,
            WHITE
        )

    surface.blit(
        text,
        text.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 30
            )
        )
    )

    surface.blit(
        subtitle,
        subtitle.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 30
            )
        )
    )

# ============================================================
# MAIN LOOP
# ============================================================

load_level(1)

level_message_timer = 0

while running:

    CLOCK.tick(FPS)

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            # Jump
            if (
                event.key in (
                    pygame.K_SPACE,
                    pygame.K_UP
                )
                and
                not dead
                and
                not won
            ):

                player.jump()

            # Restart
            if event.key == pygame.K_r:

                if dead or won:

                    if won:

                        score = 0

                    dead = False
                    won = False

                load_level(
                    current_level
                )

                effects.clear()

    # ========================================================
    # UPDATE
    # ========================================================

    if (
        not dead
        and
        not won
    ):

        if level_message_timer > 0:

            level_message_timer -= 1

        # Save position before movement
        previous_bottom = (
            player.rect.bottom
        )

        # ====================================================
        # PLAYER
        # ====================================================

        player.update(
            collision_platforms
        )

        # ====================================================
        # JUMP PADS
        # ====================================================

        check_jump_pads()

        # ====================================================
        # ENEMIES
        # ====================================================

        for enemy in enemies:

            enemy.update()

        # ====================================================
        # EFFECTS
        # ====================================================

        for effect in effects[:]:

            effect.update()

            if isinstance(
                effect,
                PopEffect
            ):

                if effect.timer >= effect.max_timer:

                    effects.remove(
                        effect
                    )

            elif isinstance(
                effect,
                JumpEffect
            ):

                if effect.timer >= effect.max_timer:

                    effects.remove(
                        effect
                    )

        # ====================================================
        # ENEMY COLLISIONS
        # ====================================================

        for enemy in enemies:

            if not enemy.alive:
                continue

            player_rect = player.rect

            enemy_rect = enemy.rect

            # STOMP
            if is_stomping(
                player_rect,
                enemy_rect,
                previous_bottom,
                player.vy
            ):

                enemy.squash()

                score += 100

                player.y = (
                    enemy_rect.top -
                    player.h
                )

                player.vy = -11

                player.on_ground = False

                effects.append(
                    PopEffect(
                        enemy_rect.centerx,
                        enemy_rect.top
                    )
                )

                continue

            # SIDE HIT
            if player_hits_enemy(
                player_rect,
                enemy_rect
            ):

                dead = True

                best_score = max(
                    best_score,
                    score
                )

                break

        # ====================================================
        # FALLING
        # ====================================================

        if (
            player.y >
            HEIGHT + 150
        ):

            dead = True

            best_score = max(
                best_score,
                score
            )

        # ====================================================
        # LEVEL END
        # ====================================================

        if (
            player.x >=
            LEVEL_ENDS[current_level]
        ):

            if current_level == 1:

                # ==============================
                # GO TO LEVEL 2
                # ==============================

                current_level = 2

                load_level(2)

                level_message_timer = 75

            else:

                # ==============================
                # FINAL WIN
                # ==============================

                won = True

                best_score = max(
                    best_score,
                    score
                )

        # ====================================================
        # CAMERA
        # ====================================================

        target_camera = max(
            0,
            player.x - 280
        )

        camera_x += (
            target_camera -
            camera_x
        ) * 0.12

    # ========================================================
    # DRAW
    # ========================================================

    draw_background(
        SCREEN
    )

    # ========================================================
    # PLATFORMS
    # ========================================================

    for index, platform in enumerate(
        level_platforms
    ):

        visible_platform = (
            platform.move(
                -round(camera_x),
                0
            )
        )

        # Ground comes first
        # Number of ground platforms depends on level

        if current_level == 1:

            is_ground = index < 4

        else:

            is_ground = index < 6

        if is_ground:

            draw_ground(
                SCREEN,
                visible_platform
            )

        else:

            draw_platform(
                SCREEN,
                visible_platform
            )

    # ========================================================
    # JUMP PADS
    # ========================================================

    draw_jump_pads(
        SCREEN,
        camera_x
    )

    # ========================================================
    # ENEMIES
    # ========================================================

    for enemy in enemies:

        enemy.draw(
            SCREEN,
            camera_x
        )

    # ========================================================
    # PLAYER
    # ========================================================

    player.draw(
        SCREEN,
        camera_x
    )

    # ========================================================
    # EFFECTS
    # ========================================================

    for effect in effects:

        effect.draw(
            SCREEN,
            camera_x
        )

    # ========================================================
    # UI
    # ========================================================

    draw_ui(
        SCREEN
    )

    if level_message_timer > 0:

        draw_level_message(
            SCREEN
        )

    if dead or won:

        draw_game_over(
            SCREEN
        )

    pygame.display.flip()

# ============================================================
# EXIT
# ============================================================

pygame.quit()
sys.exit()