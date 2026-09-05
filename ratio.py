import pygame
import sys
import random
import time
from pathlib import Path

pygame.init()

WIDTH, HEIGHT = (1000, 600)
FPS = 60

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Platformer")
CLOCK = pygame.time.Clock()

ASSET_DIR = Path(__file__).parent / "assets"

PLAYER_SIZE = (72, 60)
ENEMY_SIZE = (70, 55)

# BIG slow enemy
SLOW_ENEMY_SIZE = (115, 90)

GROUND_TILE_SIZE = (205, 70)
PLATFORM_TILE_SIZE = (205, 48)

JUMP_PAD_SIZE = (125, 40)
MOVING_PLATFORM_SIZE = (205, 48)
SPIKE_SIZE = (90, 68)

FLAG_SIZE = (250, 350)

WHITE = (255, 255, 255)


# ============================================================
# MUSIC
# ============================================================

try:
    pygame.mixer.init()

    music_file = None

    for extension in (".mp3", ".wav", ".ogg"):
        possible_file = ASSET_DIR / ("gameMusic" + extension)

        if possible_file.exists():
            music_file = possible_file
            break

    if music_file is not None:
        pygame.mixer.music.load(str(music_file))
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)

except pygame.error:
    pass


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

# YOUR BIG SLOW ENEMY IMAGE
slow_enemy_image = load_image(
    "slow_enemie.png",
    SLOW_ENEMY_SIZE
)

jump_pad_image = load_image(
    "jump_pad.png",
    JUMP_PAD_SIZE
)

moving_platform_image = load_image(
    "moving_platform.png",
    MOVING_PLATFORM_SIZE
)

spike_image = load_image(
    "spikes.png",
    SPIKE_SIZE
)


# ============================================================
# FLAGS
# ============================================================

flag1 = load_image(
    "black_flag.png",
    FLAG_SIZE
)

flag2 = load_image(
    "green_flag.png",
    FLAG_SIZE
)


FLAG1_POSITION = (
    3420,
    200
)

FLAG2_POSITION = (
    4720,
    200
)


# ============================================================
# JUMP PAD
# ============================================================

JUMP_PAD_POWER = -24


# ============================================================
# MOVING PLATFORM
# ============================================================

class MovingPlatform:

    def __init__(
        self,
        x,
        y,
        distance,
        speed=2.0,
        horizontal=True
    ):

        self.x = float(x)
        self.y = float(y)

        self.start_x = float(x)
        self.start_y = float(y)

        self.w, self.h = MOVING_PLATFORM_SIZE

        self.distance = distance
        self.speed = speed

        self.horizontal = horizontal

        self.direction = 1

        self.dx = 0
        self.dy = 0

    @property
    def rect(self):

        return pygame.Rect(
            round(self.x),
            round(self.y),
            self.w,
            self.h
        )

    def update(self):

        old_x = self.x
        old_y = self.y

        if self.horizontal:

            self.x += (
                self.speed *
                self.direction
            )

            if self.x >= (
                self.start_x +
                self.distance
            ):

                self.x = (
                    self.start_x +
                    self.distance
                )

                self.direction = -1

            elif self.x <= self.start_x:

                self.x = self.start_x

                self.direction = 1

        else:

            self.y += (
                self.speed *
                self.direction
            )

            if self.y >= (
                self.start_y +
                self.distance
            ):

                self.y = (
                    self.start_y +
                    self.distance
                )

                self.direction = -1

            elif self.y <= self.start_y:

                self.y = self.start_y

                self.direction = 1

        self.dx = self.x - old_x
        self.dy = self.y - old_y

    def reset(self):

        self.x = self.start_x
        self.y = self.start_y

        self.direction = 1

        self.dx = 0
        self.dy = 0

    def draw(
        self,
        surface,
        camera_x
    ):

        surface.blit(
            moving_platform_image,
            (
                round(
                    self.x -
                    camera_x
                ),
                round(self.y)
            )
        )


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

def draw_tiled_texture(
    surface,
    image,
    rect
):

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


def draw_ground(
    surface,
    rect
):

    draw_tiled_texture(
        surface,
        grass,
        rect
    )


def draw_platform(
    surface,
    rect
):

    draw_tiled_texture(
        surface,
        platform_image,
        rect
    )


# ============================================================
# SPIKES
# ============================================================

class Spike:

    def __init__(
        self,
        x,
        y
    ):

        self.x = x
        self.y = y

        self.w, self.h = SPIKE_SIZE

    @property
    def rect(self):

        return pygame.Rect(
            self.x,
            self.y,
            self.w,
            self.h
        )

    @property
    def hitbox(self):

        return pygame.Rect(
            self.x + 10,
            self.y + 12,
            self.w - 20,
            self.h - 12
        )

    def draw(
        self,
        surface,
        camera_x
    ):

        surface.blit(
            spike_image,
            (
                self.x -
                round(camera_x),
                self.y
            )
        )


# ============================================================
# EFFECTS
# ============================================================

effects = []


class PopEffect:

    def __init__(
        self,
        x,
        y
    ):

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

    def draw(
        self,
        surface,
        camera_x
    ):

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


class JumpEffect:

    def __init__(
        self,
        x,
        y
    ):

        self.x = x
        self.y = y

        self.timer = 0
        self.max_timer = 15

    def update(self):

        self.timer += 1

    def draw(
        self,
        surface,
        camera_x
    ):

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
                (
                    int(x),
                    int(y + 15)
                ),
                (
                    int(x),
                    int(y)
                ),
                3
            )

        surface.blit(
            effect_surface,
            (0, 0)
        )


class ExplosionEffect:

    def __init__(
        self,
        x,
        y
    ):

        self.x = float(x)
        self.y = float(y)

        self.timer = 0
        self.max_timer = 28

        self.particles = []

        for _ in range(18):

            angle = random.uniform(
                0,
                6.28318
            )

            speed = random.uniform(
                2.5,
                7.0
            )

            direction = pygame.math.Vector2(
                1,
                0
            ).rotate(
                angle * 57.2958
            )

            self.particles.append({
                "x": 0.0,
                "y": 0.0,

                "vx": (
                    direction.x *
                    speed
                ),

                "vy": (
                    direction.y *
                    speed
                ),

                "size": random.randint(
                    3,
                    8
                )
            })

    def update(self):

        self.timer += 1

        for particle in self.particles:

            particle["x"] += (
                particle["vx"]
            )

            particle["y"] += (
                particle["vy"]
            )

            particle["vy"] += 0.25

    def draw(
        self,
        surface,
        camera_x
    ):

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

        radius = max(
            2,
            20 -
            self.timer
        )

        pygame.draw.circle(
            effect_surface,
            (
                255,
                220,
                70,
                alpha
            ),
            (
                int(
                    self.x -
                    camera_x
                ),
                int(self.y)
            ),
            radius
        )

        for particle in self.particles:

            pygame.draw.circle(
                effect_surface,
                (
                    255,
                    120,
                    30,
                    alpha
                ),
                (
                    int(
                        self.x +
                        particle["x"] -
                        camera_x
                    ),
                    int(
                        self.y +
                        particle["y"]
                    )
                ),
                max(
                    1,
                    particle["size"]
                )
            )

        surface.blit(
            effect_surface,
            (0, 0)
        )


# ============================================================
# PLAYER
# ============================================================

class Player:

    def __init__(
        self,
        x,
        y
    ):

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

    def update(
        self,
        collision_platforms
    ):

        keys = pygame.key.get_pressed()

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

            if current.colliderect(
                platform
            ):

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

        if self.on_ground:

            self.coyote_time = 8

        else:

            self.coyote_time = max(
                0,
                self.coyote_time - 1
            )

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
# NORMAL ENEMY
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
        self.start_y = float(y)

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
# BIG SLOW ENEMY
# ============================================================

class SlowEnemy:

    def __init__(
        self,
        x,
        y,
        left_bound,
        right_bound
    ):

        self.x = float(x)
        self.y = float(y)

        self.w, self.h = SLOW_ENEMY_SIZE

        # VERY SLOW
        self.speed = 0.65

        self.direction = 1

        self.start_x = float(x)
        self.start_y = float(y)

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

        # Needs THREE stomps
        self.hits_remaining = 3

        # Prevents instant repeated stomps
        self.hit_cooldown = 0

    @property
    def rect(self):

        return pygame.Rect(
            round(self.x),
            round(self.y),
            self.w,
            self.h
        )

    def update(self):

        if self.hit_cooldown > 0:

            self.hit_cooldown -= 1

        if not self.alive:

            if self.squash_timer > 0:

                self.squash_timer -= 1

            return

        # Slow movement
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

        # Chunky slow wobble
        self.rotation = (
            self.direction *
            3 *
            pygame.math.Vector2(
                1,
                0
            ).rotate(
                self.walk_timer * 8
            ).x
        )

    def stomp(self):

        if not self.alive:
            return False

        if self.hit_cooldown > 0:
            return False

        self.hits_remaining -= 1

        self.hit_cooldown = 12

        if self.hits_remaining <= 0:

            self.alive = False
            self.squash_timer = 18

            return True

        return False

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
                    slow_enemy_image,
                    (
                        self.w + 20,
                        28
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
            slow_enemy_image,
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


level1_jump_pads = [

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


level1_moving_platforms = [

    MovingPlatform(
        850,
        400,
        220,
        2.0,
        True
    ),

    MovingPlatform(
        1900,
        380,
        250,
        2.2,
        True
    )
]


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
# LEVEL 1 SLOW ENEMIES
# ============================================================

level1_slow_enemies = [

    # Big slow enemy on ground
    SlowEnemy(
        700,
        450,
        500,
        950
    ),

    # Big slow enemy later in the level
    SlowEnemy(
        3000,
        450,
        2850,
        3500
    )
]


# ============================================================
# LEVEL 2
# ============================================================

level2_platforms = [

    pygame.Rect(
        -100,
        535,
        900,
        70
    ),

    pygame.Rect(
        1050,
        535,
        500,
        70
    ),

    pygame.Rect(
        1650,
        535,
        350,
        70
    ),

    pygame.Rect(
        2250,
        535,
        500,
        70
    ),

    pygame.Rect(
        3000,
        535,
        550,
        70
    ),

    pygame.Rect(
        3800,
        535,
        1100,
        70
    ),

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


level2_collision_platforms = [

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


level2_jump_pads = [

    pygame.Rect(
        680,
        495,
        125,
        40
    ),

    pygame.Rect(
        820,
        310,
        125,
        40
    )
]


level2_moving_platforms = [

    MovingPlatform(
        700,
        460,
        250,
        2.2,
        True
    ),

    MovingPlatform(
        1500,
        430,
        300,
        2.4,
        True
    ),

    MovingPlatform(
        2750,
        350,
        300,
        2.5,
        True
    ),

    MovingPlatform(
        4200,
        430,
        300,
        2.5,
        True
    )
]


level2_enemies = [

    Enemy(
        300,
        480,
        150,
        700
    ),

    Enemy(
        540,
        383,
        510,
        620
    ),

    Enemy(
        820,
        313,
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
        353,
        1150,
        1280
    ),

    Enemy(
        1430,
        263,
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
        293,
        1860,
        1980
    ),

    Enemy(
        2080,
        203,
        2050,
        2180
    ),

    Enemy(
        2380,
        353,
        2360,
        2480
    ),

    Enemy(
        2610,
        263,
        2590,
        2720
    ),

    Enemy(
        2830,
        183,
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
        343,
        3160,
        3300
    ),

    Enemy(
        3430,
        253,
        3410,
        3530
    ),

    Enemy(
        4600,
        353,
        4570,
        4720
    )
]


# ============================================================
# LEVEL 2 SLOW ENEMIES
# ============================================================

level2_slow_enemies = [

    SlowEnemy(
        650,
        450,
        400,
        760
    ),

    SlowEnemy(
        820,
        310,
        3800,
        4500
    )
]


# ============================================================
# SPIKES
# ============================================================

level1_spikes = [

    Spike(
        1020,
        472
    ),

    Spike(
        2050,
        472
    )
]


level2_spikes = [

    Spike(
        600,
        472
    ),

    Spike(
        1400,
        472
    ),

    Spike(
        1850,
        472
    ),

    Spike(
        2610,
        472
    ),

    Spike(
        3400,
        472
    ),

    Spike(
        4380,
        472
    )
]


# ============================================================
# LEVEL SYSTEM
# ============================================================

current_level = 1

level_platforms = level1_platforms
collision_platforms = level1_collision_platforms
jump_pads = level1_jump_pads
moving_platforms = level1_moving_platforms
enemies = level1_enemies
slow_enemies = level1_slow_enemies
spikes = level1_spikes


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
# TIMER
# ============================================================

game_start_time = time.time()

final_time = 0


def get_game_time():

    if dead or won:

        return final_time

    return time.time() - game_start_time


def format_time(seconds):

    minutes = int(
        seconds // 60
    )

    secs = int(
        seconds % 60
    )

    milliseconds = int(
        (seconds % 1) * 100
    )

    return (
        f"{minutes:02d}:"
        f"{secs:02d}."
        f"{milliseconds:02d}"
    )


# ============================================================
# LEVEL LOADING
# ============================================================

def load_level(level):

    global current_level
    global level_platforms
    global collision_platforms
    global jump_pads
    global moving_platforms
    global enemies
    global slow_enemies
    global spikes
    global camera_x

    current_level = level

    if level == 1:

        level_platforms = level1_platforms

        collision_platforms = (
            level1_collision_platforms
        )

        jump_pads = level1_jump_pads

        moving_platforms = (
            level1_moving_platforms
        )

        enemies = level1_enemies

        slow_enemies = (
            level1_slow_enemies
        )

        spikes = level1_spikes

        player.spawn_x = 130
        player.spawn_y = 475

    else:

        level_platforms = level2_platforms

        collision_platforms = (
            level2_collision_platforms
        )

        jump_pads = level2_jump_pads

        moving_platforms = (
            level2_moving_platforms
        )

        enemies = level2_enemies

        slow_enemies = (
            level2_slow_enemies
        )

        spikes = level2_spikes

        player.spawn_x = 130
        player.spawn_y = 475

    player.reset()

    for platform in moving_platforms:

        platform.reset()

    for enemy in enemies:

        enemy.alive = True
        enemy.squash_timer = 0

        enemy.x = enemy.start_x
        enemy.y = enemy.start_y

        enemy.direction = 1
        enemy.rotation = 0
        enemy.walk_timer = 0

    # RESET BIG SLOW ENEMIES
    for enemy in slow_enemies:

        enemy.alive = True

        enemy.squash_timer = 0

        enemy.hits_remaining = 3

        enemy.hit_cooldown = 0

        enemy.x = enemy.start_x
        enemy.y = enemy.start_y

        enemy.direction = 1
        enemy.rotation = 0
        enemy.walk_timer = 0

    camera_x = 0


# ============================================================
# ENEMY COLLISION
# ============================================================

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

    falling = player_vy > 0

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

        hitbox = pad.inflate(
            -18,
            -12
        )

        if player.vy < 0:
            continue

        if player_rect.colliderect(
            hitbox
        ):

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
# DRAW FLAGS
# ============================================================

def draw_flags(
    surface,
    camera_x
):

    if current_level == 1:

        surface.blit(
            flag1,
            (
                FLAG1_POSITION[0] -
                round(camera_x),
                FLAG1_POSITION[1]
            )
        )

    elif current_level == 2:

        surface.blit(
            flag2,
            (
                FLAG2_POSITION[0] -
                round(camera_x),
                FLAG2_POSITION[1]
            )
        )


# ============================================================
# UI
# ============================================================

def draw_ui(surface):

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

    timer_text = font.render(
        f"Time: {format_time(get_game_time())}",
        True,
        WHITE
    )

    surface.blit(
        timer_text,
        (20, 120)
    )

    level_end = LEVEL_ENDS[current_level]

    progress = max(
        0,
        min(
            1,
            player.x /
            level_end
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
                (bar_width - 6) *
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

    final_time_text = font.render(
        f"Final Time: {format_time(final_time)}",
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
                HEIGHT // 2 - 80
            )
        )
    )

    surface.blit(
        sub,
        sub.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 20
            )
        )
    )

    surface.blit(
        final_time_text,
        final_time_text.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 25
            )
        )
    )

    surface.blit(
        hint,
        hint.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 75
            )
        )
    )


# ============================================================
# LEVEL MESSAGE
# ============================================================

level_message_timer = 0


def draw_level_message(surface):

    if level_message_timer <= 0:
        return

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (
            0,
            0,
            0,
            90
        )
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
# START
# ============================================================

load_level(1)

level_message_timer = 0

game_start_time = time.time()
final_time = 0


# ============================================================
# MAIN LOOP
# ============================================================

while running:

    CLOCK.tick(60)

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

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

            if event.key == pygame.K_r:

                if dead or won:

                    if won:

                        score = 0

                    dead = False
                    won = False

                    game_start_time = time.time()
                    final_time = 0

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

        previous_bottom = (
            player.rect.bottom
        )

        # ====================================================
        # MOVING PLATFORMS
        # ====================================================

        for moving_platform in (
            moving_platforms
        ):

            moving_platform.update()

        # ====================================================
        # CARRY PLAYER
        # ====================================================

        player_rect_before = (
            player.rect
        )

        for moving_platform in (
            moving_platforms
        ):

            platform_rect = (
                moving_platform.rect
            )

            standing_on_platform = (
                player_rect_before.bottom <=
                platform_rect.top + 8

                and

                player_rect_before.bottom >=
                platform_rect.top - 8

                and

                player_rect_before.right >
                platform_rect.left

                and

                player_rect_before.left <
                platform_rect.right

                and

                player.vy >= 0
            )

            if standing_on_platform:

                player.x += (
                    moving_platform.dx
                )

                player.y += (
                    moving_platform.dy
                )

        # ====================================================
        # COLLISION PLATFORMS
        # ====================================================

        all_collision_platforms = (
            collision_platforms +
            [
                moving_platform.rect
                for moving_platform
                in moving_platforms
            ]
        )

        # ====================================================
        # PLAYER
        # ====================================================

        player.update(
            all_collision_platforms
        )

        # ====================================================
        # JUMP PADS
        # ====================================================

        check_jump_pads()

        # ====================================================
        # SPIKES
        # ====================================================

        player_spike_rect = (
            player.rect.inflate(
                -12,
                -8
            )
        )

        for spike in spikes:

            if player_spike_rect.colliderect(
                spike.hitbox
            ):

                dead = True

                final_time = (
                    time.time() -
                    game_start_time
                )

                best_score = max(
                    best_score,
                    score
                )

                effects.append(
                    ExplosionEffect(
                        player.rect.centerx,
                        player.rect.centery
                    )
                )

                break

        if dead:

            continue

        # ====================================================
        # NORMAL ENEMIES
        # ====================================================

        for enemy in enemies:

            enemy.update()

        # ====================================================
        # BIG SLOW ENEMIES
        # ====================================================

        for enemy in slow_enemies:

            enemy.update()

        # ====================================================
        # EFFECTS
        # ====================================================

        for effect in effects[:]:

            effect.update()

            if (
                effect.timer >=
                effect.max_timer
            ):

                effects.remove(
                    effect
                )

        # ====================================================
        # NORMAL ENEMY COLLISIONS
        # ====================================================

        for enemy in enemies:

            if not enemy.alive:
                continue

            player_rect = player.rect
            enemy_rect = enemy.rect

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

            if player_hits_enemy(
                player_rect,
                enemy_rect
            ):

                dead = True

                final_time = (
                    time.time() -
                    game_start_time
                )

                best_score = max(
                    best_score,
                    score
                )

                break

        if dead:

            continue

        # ====================================================
        # BIG SLOW ENEMY COLLISIONS
        # ====================================================

        for enemy in slow_enemies:

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

                defeated = enemy.stomp()

                if defeated:

                    # Big enemy gives more points
                    score += 300

                else:

                    # Still give points for each hit
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

            # PLAYER GETS HIT
            if player_hits_enemy(
                player_rect,
                enemy_rect
            ):

                dead = True

                final_time = (
                    time.time() -
                    game_start_time
                )

                best_score = max(
                    best_score,
                    score
                )

                effects.append(
                    ExplosionEffect(
                        player.rect.centerx,
                        player.rect.centery
                    )
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

            final_time = (
                time.time() -
                game_start_time
            )

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

                current_level = 2

                load_level(2)

                level_message_timer = 75

            else:

                won = True

                final_time = (
                    time.time() -
                    game_start_time
                )

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

    for index, platform in enumerate(
        level_platforms
    ):

        visible_platform = (
            platform.move(
                -round(camera_x),
                0
            )
        )

        if current_level == 1:

            is_ground = (
                index < 4
            )

        else:

            is_ground = (
                index < 6
            )

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
    # MOVING PLATFORMS
    # ========================================================

    for moving_platform in (
        moving_platforms
    ):

        moving_platform.draw(
            SCREEN,
            camera_x
        )

    # ========================================================
    # JUMP PADS
    # ========================================================

    draw_jump_pads(
        SCREEN,
        camera_x
    )

    # ========================================================
    # FLAGS
    # ========================================================

    draw_flags(
        SCREEN,
        camera_x
    )

    # ========================================================
    # SPIKES
    # ========================================================

    for spike in spikes:

        spike.draw(
            SCREEN,
            camera_x
        )

    # ========================================================
    # NORMAL ENEMIES
    # ========================================================

    for enemy in enemies:

        enemy.draw(
            SCREEN,
            camera_x
        )

    # ========================================================
    # BIG SLOW ENEMIES
    # ========================================================

    for enemy in slow_enemies:

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

try:
    pygame.mixer.music.stop()
except pygame.error:
    pass

pygame.quit()
sys.exit()
