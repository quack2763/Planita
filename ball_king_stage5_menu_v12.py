import pygame
import sys
import random
import time
import math
from pathlib import Path

pygame.init()

WIDTH, HEIGHT = 1000, 600
FPS = 60

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Platformer")
CLOCK = pygame.time.Clock()

ASSET_DIR = Path(__file__).parent / "assets"

PLAYER_SIZE = (72, 60)
ENEMY_SIZE = (70, 55)
SLOW_ENEMY_SIZE = (115, 90)
SPEEDY_ENEMY_SIZE = (82, 62)
FLYING_ENEMY_SIZE = (150, 72)
FIREBALL_SIZE = (32, 50)
GRAVITY_SWITCH_SIZE = (90, 90)

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

    image_path = ASSET_DIR / filename

    if not image_path.exists():
        image_path = Path(__file__).parent / filename

    image = pygame.image.load(
        image_path
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

slow_enemy_image = load_image(
    "slow_enemie.png",
    SLOW_ENEMY_SIZE
)

speedy_enemy_image = load_image(
    "Speedy_enemy.png",
    SPEEDY_ENEMY_SIZE
)

flying_enemy_image1 = load_image(
    "flying_enemy1.png",
    FLYING_ENEMY_SIZE
)

flying_enemy_image2 = load_image(
    "flying_enemy2.png",
    FLYING_ENEMY_SIZE
)

fireball_image = load_image(
    "fireball.png",
    FIREBALL_SIZE
)

gravity_switch_image = load_image(
    "gravity_switch.png",
    GRAVITY_SWITCH_SIZE
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

flag1 = load_image(
    "black_flag.png",
    FLAG_SIZE
)

flag2 = load_image(
    "green_flag.png",
    FLAG_SIZE
)

try:
    ball_king_image = load_image(
        "ball_king.png",
        (190, 165)
    )
except (FileNotFoundError, pygame.error):
    ball_king_image = pygame.Surface(
        (190, 165),
        pygame.SRCALPHA
    )
    pygame.draw.circle(
        ball_king_image,
        (55, 110, 220),
        (95, 92),
        74
    )
    pygame.draw.polygon(
        ball_king_image,
        (255, 205, 55),
        [
            (44, 38),
            (64, 10),
            (88, 34),
            (115, 8),
            (138, 40),
            (168, 25),
            (154, 73),
            (42, 73)
        ]
    )


FLAG1_POSITION = (
    3320,
    200
)

FLAG2_POSITION = (
    4620,
    200
)

FLAG3_POSITION = (
    5250,
    200
)

FLAG4_POSITION = (
    6370,
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

        self.previous_x = self.x
        self.previous_y = self.y
        self.anim_time = 0.0


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

        self.anim_time += 0.12

        self.previous_x = old_x
        self.previous_y = old_y

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

        self.previous_x = self.x
        self.previous_y = self.y
        self._collision_old_rect = self.rect


    def draw(
        self,
        surface,
        camera_x
    ):

        # Keep the platform sprite exactly aligned with its collision rect.
        # Previous visual bob/rotation made vertical platforms look like they
        # were jumping independently of their hitbox.
        surface.blit(
            moving_platform_image,
            (
                round(self.x - camera_x),
                round(self.y)
            )
        )

        # Animation is applied only to a small highlight that does not move
        # the collision surface.
        shimmer = int(2 + 2 * abs(math.sin(self.anim_time * 2.0)))
        pygame.draw.line(
            surface,
            (255, 255, 255),
            (round(self.x - camera_x + 12), round(self.y + 3)),
            (round(self.x - camera_x + self.w - 12), round(self.y + 3)),
            1 + shimmer // 3
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
# LEVEL 4 VISUALS
# ============================================================

level4_platform_tile = pygame.transform.smoothscale(
    grass,
    PLATFORM_TILE_SIZE
)


def draw_level4_background(surface, camera_x):
    draw_background(surface)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((35, 16, 55, 28))
    surface.blit(overlay, (0, 0))

    haze = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    for index in range(8):
        radius = 90 + index * 18
        alpha = max(0, 34 - index * 3)
        pygame.draw.circle(
            haze,
            (175, 105, 220, alpha),
            (
                int((index * 180 - camera_x * 0.12) % (WIDTH + 220) - 110),
                90 + (index % 4) * 115
            ),
            radius
        )

    surface.blit(haze, (0, 0))


def draw_level4_platform(surface, rect, ceiling=False):
    image = level4_platform_tile

    if ceiling:
        image = pygame.transform.flip(
            image,
            False,
            True
        )

    shadow_offset = 5 if not ceiling else -5

    shadow = pygame.Surface(
        (rect.width + 8, rect.height + 8),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        shadow,
        (15, 10, 25, 90),
        (
            4,
            4 + shadow_offset,
            rect.width,
            rect.height
        ),
        border_radius=10
    )

    surface.blit(
        shadow,
        (
            rect.x - 4,
            rect.y - 4
        )
    )

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

    outline = pygame.Rect(
        rect.x,
        rect.y,
        rect.width,
        rect.height
    )

    pygame.draw.rect(
        surface,
        (35, 26, 44),
        outline,
        2,
        border_radius=9
    )

    if ceiling:
        edge_y = rect.bottom - 5
    else:
        edge_y = rect.top + 4

    pygame.draw.line(
        surface,
        (255, 255, 255),
        (rect.left + 10, edge_y),
        (rect.right - 10, edge_y),
        1
    )



# ============================================================
# BALL KING ARENA VISUALS
# ============================================================

def draw_boss_arena_background(surface, camera_x):
    draw_background(surface)

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (22, 15, 38, 125)
    )

    surface.blit(
        overlay,
        (0, 0)
    )

    glow_surface = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    pulse = (
        0.5 +
        0.5 *
        math.sin(
            pygame.time.get_ticks() * 0.003
        )
    )

    for x in (
        170,
        520,
        870,
        1220,
        1570,
        1920
    ):
        screen_x = int(
            x -
            camera_x * 0.45
        )

        pygame.draw.circle(
            glow_surface,
            (
                255,
                205,
                70,
                int(24 + 16 * pulse)
            ),
            (screen_x, 150),
            80
        )

    surface.blit(
        glow_surface,
        (0, 0)
    )

    for world_x in (
        35,
        2165
    ):
        x = int(
            world_x -
            camera_x
        )

        pygame.draw.rect(
            surface,
            (45, 34, 55),
            (
                x,
                80,
                48,
                455
            ),
            border_radius=12
        )

        pygame.draw.rect(
            surface,
            (255, 210, 70),
            (
                x + 8,
                96,
                32,
                14
            ),
            border_radius=6
        )

        pygame.draw.line(
            surface,
            (255, 235, 140),
            (
                x + 12,
                120
            ),
            (
                x + 12,
                515
            ),
            3
        )

    crest_x = int(
        1805 -
        camera_x
    )

    crest_y = 150

    pygame.draw.circle(
        surface,
        (60, 42, 74),
        (crest_x, crest_y),
        105
    )

    pygame.draw.circle(
        surface,
        (255, 215, 85),
        (crest_x, crest_y),
        105,
        4
    )

    crest_points = [
        (
            crest_x - 62,
            crest_y + 30
        ),
        (
            crest_x - 48,
            crest_y - 40
        ),
        (
            crest_x - 20,
            crest_y - 12
        ),
        (
            crest_x + 5,
            crest_y - 58
        ),
        (
            crest_x + 28,
            crest_y - 12
        ),
        (
            crest_x + 54,
            crest_y - 42
        ),
        (
            crest_x + 67,
            crest_y + 30
        )
    ]

    pygame.draw.polygon(
        surface,
        (255, 210, 65),
        crest_points
    )

    pygame.draw.polygon(
        surface,
        (120, 76, 24),
        crest_points,
        3
    )


def draw_boss_ui(surface):
    if current_level != 5 or boss is None:
        return

    bar_w = 430
    bar_h = 26

    bar_x = (
        WIDTH // 2 -
        bar_w // 2
    )

    bar_y = 18

    pygame.draw.rect(
        surface,
        (22, 18, 28),
        (
            bar_x - 6,
            bar_y - 6,
            bar_w + 12,
            bar_h + 12
        ),
        border_radius=10
    )

    pygame.draw.rect(
        surface,
        (255, 220, 90),
        (
            bar_x,
            bar_y,
            bar_w,
            bar_h
        ),
        3,
        border_radius=8
    )

    hp_progress = max(
        0.0,
        min(
            1.0,
            boss.hp /
            boss.max_hp
        )
    )

    if hp_progress > 0:
        pygame.draw.rect(
            surface,
            (225, 75, 65),
            (
                bar_x + 3,
                bar_y + 3,
                int(
                    (bar_w - 6) *
                    hp_progress
                ),
                bar_h - 6
            ),
            border_radius=6
        )

    title = small_font.render(
        "BALL KING",
        True,
        WHITE
    )

    surface.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                bar_y + bar_h + 24
            )
        )
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
# BALL KING BOSS
# ============================================================

BOSS_ARENA_LEFT = 80
BOSS_ARENA_RIGHT = 2150


boss_dialogue_lines = [
    ("BALL KING", "HALT, TINY TRAVELER."),
    ("BALL KING", "YOU HAVE REACHED THE ROYAL BALL ARENA."),
    ("BALL KING", "FOUR STAGES? IMPRESSIVE."),
    ("PLAYER", "So... you're just a ball with a crown?"),
    ("BALL KING", "SILENCE! THAT CROWN IS VERY IMPORTANT."),
    ("BALL KING", "WITNESS MY ROYAL ATTACKS!"),
    ("PLAYER", "Uh oh.")
]


class BossOrb:
    def __init__(self, x, y, vx, vy, radius=13, homing=False, phase_angle=0.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.radius = radius
        self.homing = homing
        self.phase_angle = phase_angle
        self.timer = 0
        self.alive = True

    @property
    def rect(self):
        r = self.radius + 5
        return pygame.Rect(
            int(self.x - r),
            int(self.y - r),
            r * 2,
            r * 2
        )

    def update(self):
        if not self.alive:
            return

        self.timer += 1

        if self.homing and self.timer < 150:
            target = pygame.Vector2(
                player.rect.centerx,
                player.rect.centery
            )
            direction = target - pygame.Vector2(
                self.x,
                self.y
            )

            if direction.length() > 1:
                direction = direction.normalize()

                self.vx += direction.x * 0.055
                self.vy += direction.y * 0.055

                velocity = pygame.Vector2(
                    self.vx,
                    self.vy
                )

                if velocity.length() > 7.5:
                    velocity.scale_to_length(7.5)
                    self.vx = velocity.x
                    self.vy = velocity.y

        velocity = pygame.Vector2(
            self.vx,
            self.vy
        )

        if velocity.length() > 0:
            side = pygame.Vector2(
                -velocity.y,
                velocity.x
            ).normalize()

            sway = math.sin(
                self.timer * 0.16 +
                self.phase_angle
            ) * 0.22

            self.x += velocity.x + side.x * sway
            self.y += velocity.y + side.y * sway
        else:
            self.x += self.vx
            self.y += self.vy

        if (
            self.timer > 240
            or self.x < -200
            or self.x > LEVEL_ENDS.get(5, 2300) + 200
            or self.y < -250
            or self.y > HEIGHT + 250
        ):
            self.alive = False

    def collides(self, target_rect):
        return self.rect.colliderect(
            target_rect.inflate(-14, -12)
        )

    def draw(self, surface, camera_x):
        if not self.alive:
            return

        pulse = 1.0 + math.sin(self.timer * 0.35 + self.phase_angle) * 0.12
        visual_radius = max(2, int(self.radius * pulse))

        glow = pygame.Surface(
            (visual_radius * 5, visual_radius * 5),
            pygame.SRCALPHA
        )

        center = glow.get_width() // 2

        for extra, alpha in (
            (visual_radius + 13, 28),
            (visual_radius + 7, 55)
        ):
            pygame.draw.circle(
                glow,
                (255, 220, 80, alpha),
                (center, center),
                extra
            )

        surface.blit(
            glow,
            glow.get_rect(
                center=(
                    int(self.x - camera_x),
                    int(self.y)
                )
            )
        )

        pygame.draw.circle(
            surface,
            (255, 225, 95),
            (
                int(self.x - camera_x),
                int(self.y)
            ),
            visual_radius
        )

        pygame.draw.circle(
            surface,
            (120, 70, 20),
            (
                int(self.x - camera_x),
                int(self.y)
            ),
            visual_radius,
            2
        )


class BossShockwave:
    def __init__(self, x, y, direction, speed=8.0, scale=1.0):
        self.x = float(x)
        self.y = float(y)
        self.direction = direction
        self.speed = speed
        self.w = int(74 * scale)
        self.h = int(32 * scale)
        self.timer = 0
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.w / 2),
            int(self.y - self.h),
            self.w,
            self.h
        )

    def update(self):
        if not self.alive:
            return

        self.timer += 1
        self.x += self.speed * self.direction

        if (
            self.timer > 160
            or self.x < -200
            or self.x > LEVEL_ENDS.get(5, 2300) + 200
        ):
            self.alive = False

    def collides(self, target_rect):
        return self.rect.colliderect(
            target_rect.inflate(-12, -8)
        )

    def draw(self, surface, camera_x):
        if not self.alive:
            return

        screen_x = int(
            self.x - camera_x
        )
        bottom = int(self.y)

        pulse = 1.0 + math.sin(self.timer * 0.28) * 0.08
        visual_w = int(self.w * pulse)
        visual_h = int(self.h * (1.0 + 0.08 * abs(math.sin(self.timer * 0.24))))

        points = [
            (
                screen_x - visual_w // 2,
                bottom
            ),
            (
                screen_x - visual_w // 4,
                bottom - visual_h
            ),
            (
                screen_x,
                bottom - self.h // 3
            ),
            (
                screen_x + visual_w // 4,
                bottom - self.h
            ),
            (
                screen_x + visual_w // 2,
                bottom
            )
        ]

        pygame.draw.polygon(
            surface,
            (255, 215, 75),
            points
        )

        pygame.draw.line(
            surface,
            (255, 255, 255),
            points[1],
            points[3],
            2
        )


class BossBeam:
    def __init__(self, x, warning=46, active=18, width=72):
        self.x = float(x)
        self.width = width
        self.warning = warning
        self.active = active
        self.timer = 0
        self.alive = True

    @property
    def is_active(self):
        return (
            self.timer >= self.warning
            and
            self.timer < self.warning + self.active
        )

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.width / 2),
            30,
            int(self.width),
            505
        )

    def update(self):
        if not self.alive:
            return

        self.timer += 1

        if (
            self.timer >=
            self.warning +
            self.active
        ):
            self.alive = False

    def collides(self, target_rect):
        if not self.is_active:
            return False

        return self.rect.colliderect(
            target_rect.inflate(-14, -12)
        )

    def draw(self, surface, camera_x):
        if not self.alive:
            return

        screen_x = int(
            self.x - camera_x
        )

        rect = pygame.Rect(
            int(
                screen_x -
                self.width / 2
            ),
            28,
            int(self.width),
            510
        )

        if self.is_active:
            beam = pygame.Surface(
                rect.size,
                pygame.SRCALPHA
            )
            beam.fill(
                (255, 230, 95, 110)
            )

            surface.blit(
                beam,
                rect.topleft
            )

            pygame.draw.rect(
                surface,
                (255, 250, 185),
                rect,
                3
            )

            pygame.draw.line(
                surface,
                (255, 255, 255),
                (
                    rect.centerx,
                    rect.top
                ),
                (
                    rect.centerx,
                    rect.bottom
                ),
                4
            )

        else:
            pulse = int(
                32 +
                28 *
                abs(
                    math.sin(
                        self.timer * 0.22
                    )
                )
            )

            telegraph = pygame.Surface(
                rect.size,
                pygame.SRCALPHA
            )

            telegraph.fill(
                (255, 210, 70, pulse)
            )

            surface.blit(
                telegraph,
                rect.topleft
            )

            pygame.draw.rect(
                surface,
                (255, 235, 90),
                rect,
                2
            )


class BallKing:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

        self.w = 190
        self.h = 165

        self.max_hp = 10
        self.hp = self.max_hp

        self.attack_name = None
        self.attack_timer = 0
        self.attack_cooldown = 70
        self.last_attack = None

        self.phase = 1

        self.hurt_cooldown = 0
        self.hurt_flash = 0

        self.dash_vx = 0
        self.rotation = 0

        self.defeated = False
        self.death_timer = 0
        self.anim_time = 0.0
        self.hit_bounce = 0.0

        self.orbs = []
        self.shockwaves = []
        self.beams = []

        self.attack_label = ""
        self.attack_label_timer = 0

    @property
    def rect(self):
        return pygame.Rect(
            round(self.x),
            round(self.y),
            self.w,
            self.h
        )

    @property
    def hurt_rect(self):
        return self.rect.inflate(
            -42,
            -32
        )

    @property
    def is_dashing(self):
        return (
            self.attack_name == "dash"
            and
            20 <= self.attack_timer < 52
        )

    def clear_attacks(self):
        self.attack_name = None
        self.attack_timer = 0
        self.dash_vx = 0
        self.beams.clear()

    def start_attack(self):
        pool = [
            "orbs",
            "beam",
            "shockwave",
            "dash"
        ]

        if self.phase == 2:
            pool += [
                "spiral",
                "rain"
            ]

        choices = [
            name
            for name in pool
            if name != self.last_attack
        ]

        self.attack_name = random.choice(
            choices
        )
        self.last_attack = self.attack_name
        self.attack_timer = 0

        labels = {
            "orbs": "ROYAL ORBS!",
            "beam": "CROWN JUDGEMENT!",
            "shockwave": "ROYAL STOMP!",
            "dash": "KING'S CHARGE!",
            "spiral": "CROWN CYCLONE!",
            "rain": "GOLDEN RAIN!"
        }

        self.attack_label = labels[
            self.attack_name
        ]

        self.attack_label_timer = 42

        if self.attack_name == "beam":
            count = (
                4 if self.phase == 2
                else 3
            )

            base_x = (
                player.rect.centerx
            )

            if count == 3:
                offsets = [
                    -260,
                    0,
                    260
                ]
            else:
                offsets = [
                    -390,
                    -130,
                    130,
                    390
                ]

            used = []

            for offset in offsets:
                beam_x = max(
                    BOSS_ARENA_LEFT + 55,
                    min(
                        BOSS_ARENA_RIGHT - 55,
                        base_x + offset
                    )
                )

                if all(
                    abs(
                        beam_x -
                        old_x
                    ) > 70
                    for old_x in used
                ):
                    self.beams.append(
                        BossBeam(
                            beam_x,
                            warning=(
                                42 if self.phase == 1
                                else 34
                            ),
                            active=(
                                18 if self.phase == 1
                                else 22
                            ),
                            width=70
                        )
                    )
                    used.append(
                        beam_x
                    )

    def finish_attack(self):
        self.attack_name = None
        self.attack_timer = 0
        self.attack_cooldown = (
            32 if self.phase == 2
            else 48
        )

    def update(self):
        self.anim_time += 0.12

        if self.hurt_cooldown > 0:
            self.hurt_cooldown -= 1

        if self.hurt_flash > 0:
            self.hurt_flash -= 1

        if self.hit_bounce > 0:
            self.hit_bounce *= 0.82
            if self.hit_bounce < 0.05:
                self.hit_bounce = 0.0

        if self.attack_label_timer > 0:
            self.attack_label_timer -= 1

        if self.defeated:
            self.death_timer += 1
            return

        self.phase = (
            2 if self.hp <= 5
            else 1
        )

        if self.attack_name is None:
            if self.attack_cooldown > 0:
                self.attack_cooldown -= 1
                return

            self.start_attack()
            return

        self.attack_timer += 1

        if self.attack_name == "orbs":
            interval = (
                22 if self.phase == 1
                else 16
            )

            if (
                self.attack_timer == 1
                or
                self.attack_timer % interval == 0
            ):
                target = pygame.Vector2(
                    player.rect.center
                )

                origin = pygame.Vector2(
                    self.x + self.w / 2,
                    self.y + 78
                )

                direction = (
                    target - origin
                )

                if direction.length() == 0:
                    direction = pygame.Vector2(
                        -1,
                        0
                    )

                direction = direction.normalize()

                speed = (
                    5.6 if self.phase == 1
                    else 6.5
                )

                self.orbs.append(
                    BossOrb(
                        origin.x,
                        origin.y,
                        direction.x * speed,
                        direction.y * speed,
                        radius=(
                            14 if self.phase == 1
                            else 15
                        ),
                        homing=(
                            self.phase == 2
                        ),
                        phase_angle=(
                            self.attack_timer * 0.2
                        )
                    )
                )

            if self.attack_timer >= (
                76 if self.phase == 1
                else 92
            ):
                self.finish_attack()

        elif self.attack_name == "beam":
            if self.attack_timer >= 72:
                self.finish_attack()

        elif self.attack_name == "shockwave":
            if self.attack_timer == 5:
                scale = (
                    1.0 if self.phase == 1
                    else 1.15
                )

                speed = (
                    8.0 if self.phase == 1
                    else 9.3
                )

                self.shockwaves.append(
                    BossShockwave(
                        self.x + self.w * 0.22,
                        self.y + self.h,
                        -1,
                        speed,
                        scale
                    )
                )

                self.shockwaves.append(
                    BossShockwave(
                        self.x + self.w * 0.78,
                        self.y + self.h,
                        1,
                        speed,
                        scale
                    )
                )

            if (
                self.phase == 2
                and
                self.attack_timer == 20
            ):
                self.shockwaves.append(
                    BossShockwave(
                        self.x + self.w * 0.22,
                        self.y + self.h,
                        -1,
                        10.2,
                        1.0
                    )
                )

                self.shockwaves.append(
                    BossShockwave(
                        self.x + self.w * 0.78,
                        self.y + self.h,
                        1,
                        10.2,
                        1.0
                    )
                )

            if self.attack_timer >= (
                52 if self.phase == 1
                else 65
            ):
                self.finish_attack()

        elif self.attack_name == "dash":
            if self.attack_timer == 1:
                direction = (
                    1
                    if player.rect.centerx >
                    self.rect.centerx
                    else -1
                )

                self.dash_vx = (
                    11.0 *
                    direction
                )

            if 20 <= self.attack_timer < 52:
                self.x += self.dash_vx

                if self.x <= BOSS_ARENA_LEFT:
                    self.x = BOSS_ARENA_LEFT
                    self.dash_vx *= -1

                if self.x >= (
                    BOSS_ARENA_RIGHT -
                    self.w
                ):
                    self.x = (
                        BOSS_ARENA_RIGHT -
                        self.w
                    )
                    self.dash_vx *= -1

                self.rotation = (
                    self.rotation +
                    22 *
                    (
                        1 if self.dash_vx > 0
                        else -1
                    )
                ) % 360

            if self.attack_timer >= 66:
                self.rotation = 0
                self.finish_attack()

        elif self.attack_name == "spiral":
            if (
                self.attack_timer <= 54
                and
                self.attack_timer % 6 == 0
            ):
                base_angle = (
                    self.attack_timer *
                    0.22
                )

                for branch in range(2):
                    angle = (
                        base_angle +
                        branch *
                        math.pi
                    )

                    direction = pygame.Vector2(
                        math.cos(angle),
                        math.sin(angle)
                    )

                    origin = pygame.Vector2(
                        self.x + self.w / 2,
                        self.y + self.h / 2
                    )

                    self.orbs.append(
                        BossOrb(
                            origin.x,
                            origin.y,
                            direction.x * 5.2,
                            direction.y * 5.2,
                            radius=12,
                            phase_angle=angle
                        )
                    )

            if self.attack_timer >= 65:
                self.finish_attack()

        elif self.attack_name == "rain":
            if (
                self.attack_timer <= 84
                and
                self.attack_timer % 9 == 0
            ):
                for _ in range(2):
                    x = random.randint(
                        BOSS_ARENA_LEFT + 40,
                        BOSS_ARENA_RIGHT - 40
                    )

                    direction = pygame.Vector2(
                        player.rect.centerx - x,
                        player.rect.centery - 70
                    )

                    if direction.length() < 0.5:
                        direction = pygame.Vector2(
                            0,
                            1
                        )

                    direction = direction.normalize()

                    self.orbs.append(
                        BossOrb(
                            x,
                            40 + random.randint(0, 60),
                            direction.x * 3.2,
                            direction.y * 3.2,
                            radius=13,
                            phase_angle=random.random() * 6.28
                        )
                    )

            if self.attack_timer >= 98:
                self.finish_attack()

    def take_hit(self):
        if (
            self.defeated
            or
            self.hurt_cooldown > 0
        ):
            return False

        self.hp -= 1
        self.hurt_cooldown = 30
        self.hurt_flash = 12
        self.hit_bounce = 10.0

        effects.append(
            ExplosionEffect(
                self.rect.centerx,
                self.rect.centery
            )
        )

        self.clear_attacks()

        if self.hp <= 0:
            self.defeated = True
            self.death_timer = 0
            self.orbs.clear()
            self.shockwaves.clear()
            self.beams.clear()
            self.attack_label_timer = 0

        return True

    def draw(self, surface, camera_x):
        if self.defeated:
            progress = min(
                1.0,
                self.death_timer / 55
            )

            scale = max(
                0.18,
                1.0 - progress * 0.82
            )

            w = max(
                20,
                int(self.w * scale)
            )

            h = max(
                20,
                int(self.h * scale)
            )

            image = pygame.transform.smoothscale(
                ball_king_image,
                (w, h)
            )

            rotated = pygame.transform.rotate(
                image,
                self.death_timer * 10
            )

            center = (
                int(
                    self.x +
                    self.w / 2 -
                    camera_x
                ),
                int(
                    self.y +
                    self.h / 2
                )
            )

            surface.blit(
                rotated,
                rotated.get_rect(
                    center=center
                )
            )

            return

        image = ball_king_image

        idle_bob = 0.0
        scale_x = 1.0
        scale_y = 1.0

        if self.attack_name is None:
            idle_bob = math.sin(self.anim_time * 1.5) * 4.0
            scale_x += math.sin(self.anim_time * 1.5) * 0.025
            scale_y -= math.sin(self.anim_time * 1.5) * 0.025
        else:
            idle_bob = math.sin(self.anim_time * 2.2) * 2.0

        if self.attack_name == "dash":
            scale_x = 1.08
            scale_y = 0.90
        elif self.attack_name == "shockwave":
            scale_x = 1.04
            scale_y = 0.96
        elif self.attack_name == "orbs":
            scale_x = 1.02
            scale_y = 0.98
        elif self.attack_name == "spiral":
            scale_x = 0.96 + 0.06 * abs(math.sin(self.attack_timer * 0.22))
            scale_y = 1.04 - 0.06 * abs(math.sin(self.attack_timer * 0.22))

        if self.hit_bounce > 0:
            scale_x += self.hit_bounce / 90.0
            scale_y -= self.hit_bounce / 90.0

        if self.hurt_flash % 2 == 1:
            image = pygame.Surface(
                ball_king_image.get_size(),
                pygame.SRCALPHA
            )
            image.blit(
                ball_king_image,
                (0, 0)
            )
            image.fill(
                (255, 255, 255, 110),
                special_flags=pygame.BLEND_RGBA_ADD
            )

        if self.is_dashing:
            angle = (
                math.sin(
                    self.attack_timer * 0.35
                ) * 8
            )
        elif self.attack_name == "spiral":
            angle = (
                self.attack_timer * 7
            )
        else:
            angle = (
                math.sin(
                    self.attack_timer * 0.08
                ) * 2
            )

        animated_boss = pygame.transform.smoothscale(
            image,
            (
                max(1, int(self.w * scale_x)),
                max(1, int(self.h * scale_y))
            )
        )

        rotated = pygame.transform.rotate(
            animated_boss,
            angle
        )

        center = (
            int(
                self.x +
                self.w / 2 -
                camera_x
            ),
            int(
                self.y +
                self.h / 2 +
                idle_bob
            )
        )

        surface.blit(
            rotated,
            rotated.get_rect(
                center=center
            )
        )

        if self.attack_label_timer > 0:
            label = small_font.render(
                self.attack_label,
                True,
                WHITE
            )

            bubble = label.get_rect(
                center=(
                    int(
                        self.x +
                        self.w / 2 -
                        camera_x
                    ),
                    int(
                        self.y - 24
                    )
                )
            ).inflate(
                18,
                10
            )

            pygame.draw.rect(
                surface,
                (20, 18, 28),
                bubble,
                border_radius=10
            )

            pygame.draw.rect(
                surface,
                (255, 220, 90),
                bubble,
                2,
                border_radius=10
            )

            surface.blit(
                label,
                label.get_rect(
                    center=bubble.center
                )
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
        self.gravity_direction = 1

        self.jump_power = -15

        self.max_fall_speed = 18

        self.on_ground = False

        self.coyote_time = 0
        self.jump_buffer = 0

        self.rotation = 0
        self.rotation_speed = 8

        self.anim_time = 0.0
        self.land_anim = 0
        self.was_on_ground = False
        self.visual_scale_x = 1.0
        self.visual_scale_y = 1.0
        self.riding_platform = False

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
        self.gravity_direction = 1

        self.rotation = 0
        self.anim_time = 0.0
        self.land_anim = 0
        self.was_on_ground = False
        self.visual_scale_x = 1.0
        self.visual_scale_y = 1.0
        self.riding_platform = False

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

            self.vy = self.jump_power * self.gravity_direction

            self.on_ground = False

            self.coyote_time = 0

            self.jump_buffer = 0


    def update(
        self,
        collision_platforms,
        carried_by_moving_platform=False
    ):

        keys = pygame.key.get_pressed()

        self.vx = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx -= self.speed

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx += self.speed

        self.x += self.vx

        current = self.rect

        for platform in collision_platforms:
            if current.colliderect(platform):
                if self.vx > 0:
                    self.x = platform.left - self.w
                elif self.vx < 0:
                    self.x = platform.right
                current = self.rect

        old_rect = self.rect

        # A moving platform owns the player's vertical position while the
        # player is riding it. Do not apply gravity for that frame: gravity
        # plus platform motion was the source of the visible snap/teleport.
        if carried_by_moving_platform:
            self.vy = 0
            self.on_ground = True
        else:
            self.vy += self.gravity * self.gravity_direction
            self.vy = max(
                -self.max_fall_speed,
                min(self.vy, self.max_fall_speed)
            )

            self.y += self.vy
            current = self.rect
            self.on_ground = False

            if self.gravity_direction == 1:
                for platform in collision_platforms:
                    if not current.colliderect(platform):
                        continue

                    if self.vy >= 0 and old_rect.bottom <= platform.top + 3:
                        self.y = platform.top - self.h
                        self.vy = 0
                        self.on_ground = True
                        break

                    if self.vy < 0 and old_rect.top >= platform.bottom - 3:
                        self.y = platform.bottom
                        self.vy = 0
                        break

            else:
                for platform in collision_platforms:
                    if not current.colliderect(platform):
                        continue

                    if self.vy <= 0 and old_rect.top >= platform.bottom - 3:
                        self.y = platform.bottom
                        self.vy = 0
                        self.on_ground = True
                        break

                    if self.vy > 0 and old_rect.bottom <= platform.top + 3:
                        self.y = platform.top - self.h
                        self.vy = 0
                        break

        just_landed = (
            self.on_ground
            and
            not self.was_on_ground
        )

        if just_landed:
            self.land_anim = 10

        self.was_on_ground = self.on_ground
        self.anim_time += 0.22

        if self.land_anim > 0:
            self.land_anim -= 1

        if self.on_ground:
            self.coyote_time = 8
        else:
            self.coyote_time = max(0, self.coyote_time - 1)

        self.jump_buffer = max(0, self.jump_buffer - 1)

        if self.jump_buffer > 0 and self.on_ground:
            self.vy = self.jump_power * self.gravity_direction
            self.on_ground = False
            self.jump_buffer = 0

        if not self.on_ground:
            self.rotation = (
                self.rotation +
                self.rotation_speed * self.gravity_direction
            ) % 360
        else:
            self.rotation *= 0.68
            if abs(self.rotation) < 0.75:
                self.rotation = 0


    def draw(
        self,
        surface,
        camera_x
    ):

        oriented_image = player_image

        if self.gravity_direction == -1:
            oriented_image = pygame.transform.flip(
                oriented_image,
                False,
                True
            )

        speed_amount = min(1.0, abs(self.vx) / max(1, self.speed))
        if self.on_ground:
            if self.riding_platform:
                walk_bob = 0.0
                target_scale_x = 1.0 + 0.018 * speed_amount
                target_scale_y = 1.0 - 0.018 * speed_amount
            else:
                walk_bob = math.sin(self.anim_time * (8.0 if speed_amount > 0 else 3.5)) * 1.8 * speed_amount
                target_scale_x = 1.0 + 0.025 * speed_amount
                target_scale_y = 1.0 - 0.025 * speed_amount
        else:
            walk_bob = 0.0
            target_scale_x = 1.0
            target_scale_y = 1.0

        if self.land_anim > 0:
            land_progress = self.land_anim / 10.0
            target_scale_x += 0.10 * land_progress
            target_scale_y -= 0.10 * land_progress

        self.visual_scale_x += (target_scale_x - self.visual_scale_x) * 0.25
        self.visual_scale_y += (target_scale_y - self.visual_scale_y) * 0.25

        draw_w = max(1, int(self.w * self.visual_scale_x))
        draw_h = max(1, int(self.h * self.visual_scale_y))

        animated_image = pygame.transform.smoothscale(
            oriented_image,
            (draw_w, draw_h)
        )

        rotated = pygame.transform.rotate(
            animated_image,
            self.rotation
        )

        center = (
            int(self.x + self.w / 2 - camera_x),
            int(self.y + self.h / 2 + walk_bob)
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

        self.hits_remaining = 3

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
# SPEEDY ENEMY
# ============================================================

class SpeedyEnemy:

    def __init__(
        self,
        x,
        y,
        left_bound,
        right_bound
    ):

        self.x = float(x)
        self.y = float(y)

        self.w, self.h = SPEEDY_ENEMY_SIZE

        # MUCH FASTER THAN NORMAL ENEMIES
        self.speed = 4.2

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

        # Faster wobble than the normal enemy
        self.rotation = (
            self.direction *
            7 *
            pygame.math.Vector2(
                1,
                0
            ).rotate(
                self.walk_timer * 32
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
                    speedy_enemy_image,
                    (
                        self.w + 16,
                        20
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
            speedy_enemy_image,
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
# FLYING FIRE ENEMY
# ============================================================

class Fireball:

    def __init__(self, x, y, target_x, target_y):

        self.x = float(x)
        self.y = float(y)
        self.w, self.h = FIREBALL_SIZE

        direction = pygame.Vector2(
            target_x - self.x,
            target_y - self.y
        )

        if direction.length() == 0:
            direction = pygame.Vector2(-1, 0)

        direction = direction.normalize()

        self.vx = direction.x * 7.0
        self.vy = direction.y * 7.0
        self.gravity = 0.30
        self.rotation = 0
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(
            round(self.x),
            round(self.y),
            self.w,
            self.h
        )

    def update(self, ground_rects):

        if not self.alive:
            return

        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.rotation -= self.vx * 2

        if self.y + self.h >= 535:
            self.y = 535 - self.h
            self.alive = False
            return True

        for ground in ground_rects:
            if self.rect.colliderect(ground):
                if self.vy >= 0:
                    self.y = ground.top - self.h
                    self.alive = False
                    return True

        if self.x < -300 or self.x > LEVEL_ENDS.get(3, 5350) + 500:
            self.alive = False

        return False

    def draw(self, surface, camera_x):

        if not self.alive:
            return

        rotated = pygame.transform.rotate(
            fireball_image,
            self.rotation
        )

        surface.blit(
            rotated,
            rotated.get_rect(
                center=(
                    int(self.x + self.w / 2 - camera_x),
                    int(self.y + self.h / 2)
                )
            )
        )


class FlyingEnemy:

    def __init__(self, x, y, left_bound, right_bound):

        self.x = float(x)
        self.y = float(y)
        self.w, self.h = FLYING_ENEMY_SIZE
        self.start_x = float(x)
        self.start_y = float(y)
        self.left_bound = float(left_bound)
        self.right_bound = float(right_bound)
        self.direction = 1
        self.float_timer = random.randint(0, 100)
        self.shoot_timer = random.randint(55, 100)
        self.shoot_animation_timer = 0
        self.frame_timer = 0
        self.frame = 0
        self.alive = True
        self.squash_timer = 0
        self.respawn_timer = 0
        self.respawn_delay = 120

    @property
    def rect(self):
        return pygame.Rect(
            round(self.x),
            round(self.y),
            self.w,
            self.h
        )

    @property
    def hitbox(self):
        return pygame.Rect(
            round(self.x + 40),
            round(self.y + 5),
            70,
            62
        )

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.direction = 1
        self.float_timer = random.randint(0, 100)
        self.shoot_timer = random.randint(55, 100)
        self.shoot_animation_timer = 0
        self.frame_timer = 0
        self.frame = 0
        self.alive = True
        self.squash_timer = 0
        self.respawn_timer = 0

    def squash(self):
        if self.alive:
            self.alive = False
            self.squash_timer = 18
            self.respawn_timer = self.respawn_delay

    def update(self, fireballs):

        if not self.alive:
            if self.squash_timer > 0:
                self.squash_timer -= 1

            if self.respawn_timer > 0:
                self.respawn_timer -= 1

            if self.respawn_timer <= 0:
                self.reset()

            return

        self.float_timer += 1
        self.frame_timer += 1
        self.shoot_timer -= 1

        if self.shoot_animation_timer > 0:
            self.shoot_animation_timer -= 1

        self.x += 0.8 * self.direction

        if self.x <= self.left_bound:
            self.x = self.left_bound
            self.direction = 1
        elif self.x >= self.right_bound:
            self.x = self.right_bound
            self.direction = -1

        self.y = (
            self.start_y +
            math.sin(self.float_timer * 0.045) * 25
        )

        if self.frame_timer >= 10:
            self.frame_timer = 0
            self.frame = 1 - self.frame

        if self.shoot_timer <= 0:
            self.shoot_timer = 105
            self.shoot_animation_timer = 14

            mouth_x = self.x + self.w * 0.55
            mouth_y = self.y + self.h * 0.77

            fireballs.append(
                Fireball(
                    mouth_x - FIREBALL_SIZE[0] / 2,
                    mouth_y - FIREBALL_SIZE[1] / 2,
                    player.rect.centerx,
                    player.rect.centery
                )
            )

    def draw(self, surface, camera_x):

        if not self.alive:
            if self.squash_timer <= 0:
                return

            squash_width = self.w + 28
            squash_height = 18
            progress = self.squash_timer / 18
            squeeze = max(0.55, progress)

            squashed = pygame.transform.smoothscale(
                flying_enemy_image1,
                (
                    int(squash_width * squeeze + self.w * (1 - squeeze)),
                    squash_height
                )
            )

            rect = squashed.get_rect(
                midbottom=(
                    int(self.x + self.w / 2 - camera_x),
                    int(self.y + self.h)
                )
            )

            surface.blit(squashed, rect)
            return

        if self.shoot_animation_timer > 0:
            image = flying_enemy_image2
        else:
            image = flying_enemy_image1

        if self.direction < 0:
            image = pygame.transform.flip(
                image,
                True,
                False
            )

        surface.blit(
            image,
            image.get_rect(
                center=(
                    int(self.x + self.w / 2 - camera_x),
                    int(self.y + self.h / 2)
                )
            )
        )


# ============================================================
# GRAVITY SWITCH
# ============================================================

class GravitySwitch:

    def __init__(self, x, y, ceiling=False):

        self.x = float(x)
        self.y = float(y)
        self.w, self.h = GRAVITY_SWITCH_SIZE
        self.ceiling = ceiling
        self.cooldown = 0
        self.active = True

    @property
    def rect(self):
        return pygame.Rect(
            round(self.x),
            round(self.y),
            self.w,
            self.h
        )

    @property
    def hitbox(self):
        return self.rect.inflate(-18, -18)

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def try_activate(self, player_rect):
        if self.cooldown > 0:
            return False

        if not player_rect.colliderect(self.hitbox):
            return False

        self.cooldown = 30
        return True

    def draw(self, surface, camera_x):
        image = gravity_switch_image

        if self.cooldown > 0:
            image = pygame.transform.smoothscale(
                image,
                (82, 82)
            )

        if self.ceiling:
            image = pygame.transform.flip(
                image,
                False,
                True
            )

        center_x = int(
            self.x +
            self.w / 2 -
            camera_x
        )

        center_y = int(
            self.y +
            self.h / 2
        )

        surface.blit(
            image,
            image.get_rect(
                center=(
                    center_x,
                    center_y
                )
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


level1_slow_enemies = [

    SlowEnemy(
        700,
        450,
        500,
        950
    ),

    SlowEnemy(
        3000,
        450,
        2850,
        3500
    )
]


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


level2_slow_enemies = [

    SlowEnemy(
        650,
        450,
        400,
        760
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
# LEVEL 3
# ============================================================

level3_platforms = [

    pygame.Rect(
        -100,
        535,
        700,
        70
    ),

    pygame.Rect(
        850,
        535,
        550,
        70
    ),

    pygame.Rect(
        1550,
        535,
        450,
        70
    ),

    pygame.Rect(
        2150,
        535,
        650,
        70
    ),

    pygame.Rect(
        2950,
        535,
        450,
        70
    ),

    pygame.Rect(
        3500,
        535,
        750,
        70
    ),

    pygame.Rect(
        4400,
        535,
        1000,
        70
    ),

    pygame.Rect(
        500,
        400,
        195,
        48
    ),

    pygame.Rect(
        750,
        320,
        195,
        48
    ),

    pygame.Rect(
        1150,
        420,
        195,
        48
    ),

    pygame.Rect(
        1450,
        300,
        195,
        48
    ),

    pygame.Rect(
        1750,
        380,
        195,
        48
    ),

    pygame.Rect(
        2000,
        250,
        195,
        48
    ),

    pygame.Rect(
        2350,
        400,
        195,
        48
    ),

    pygame.Rect(
        2700,
        300,
        195,
        48
    ),

    pygame.Rect(
        3100,
        390,
        195,
        48
    ),

    pygame.Rect(
        3350,
        280,
        195,
        48
    ),

    pygame.Rect(
        3800,
        350,
        195,
        48
    ),

    pygame.Rect(
        4100,
        240,
        195,
        48
    ),

    pygame.Rect(
        4550,
        360,
        195,
        48
    ),

    pygame.Rect(
        4850,
        280,
        195,
        48
    )
]


level3_collision_platforms = [

    pygame.Rect(
        -100,
        540,
        700,
        68
    ),

    pygame.Rect(
        850,
        540,
        550,
        68
    ),

    pygame.Rect(
        1550,
        540,
        450,
        68
    ),

    pygame.Rect(
        2150,
        540,
        650,
        68
    ),

    pygame.Rect(
        2950,
        540,
        450,
        68
    ),

    pygame.Rect(
        3500,
        540,
        750,
        68
    ),

    pygame.Rect(
        4400,
        540,
        1000,
        68
    ),

    pygame.Rect(
        507,
        420,
        181,
        28
    ),

    pygame.Rect(
        757,
        340,
        181,
        28
    ),

    pygame.Rect(
        1157,
        440,
        181,
        28
    ),

    pygame.Rect(
        1457,
        320,
        181,
        28
    ),

    pygame.Rect(
        1757,
        400,
        181,
        28
    ),

    pygame.Rect(
        2007,
        270,
        181,
        28
    ),

    pygame.Rect(
        2357,
        420,
        181,
        28
    ),

    pygame.Rect(
        2707,
        320,
        181,
        28
    ),

    pygame.Rect(
        3107,
        410,
        181,
        28
    ),

    pygame.Rect(
        3357,
        300,
        181,
        28
    ),

    pygame.Rect(
        3807,
        370,
        181,
        28
    ),

    pygame.Rect(
        4107,
        260,
        181,
        28
    ),

    pygame.Rect(
        4557,
        380,
        181,
        28
    ),

    pygame.Rect(
        4857,
        300,
        181,
        28
    )
]


level3_jump_pads = [

    pygame.Rect(
        580,
        497,
        125,
        40
    ),

    pygame.Rect(
        1330,
        497,
        125,
        40
    ),

    pygame.Rect(
        2000,
        497,
        125,
        40
    ),

    pygame.Rect(
        3400,
        497,
        125,
        40
    )
]


level3_moving_platforms = [

    MovingPlatform(
        620,
        450,
        180,
        2.8,
        True
    ),

    MovingPlatform(
        1400,
        400,
        260,
        3.0,
        True
    ),

    MovingPlatform(
        2800,
        350,
        260,
        3.1,
        True
    ),

    MovingPlatform(
        4200,
        390,
        220,
        3.2,
        True
    )
]


level3_enemies = [

    Enemy(
        250,
        480,
        120,
        520
    ),

    Enemy(
        900,
        480,
        850,
        1300
    ),

    Enemy(
        1650,
        480,
        1570,
        1930
    ),

    Enemy(
        2250,
        480,
        2180,
        2700
    ),

    Enemy(
        3000,
        480,
        2960,
        3350
    ),

    Enemy(
        3650,
        480,
        3520,
        4100
    ),

    Enemy(
        4500,
        480,
        4420,
        5000
    )
]


# ============================================================
# LEVEL 3 SPEEDY ENEMIES
# ============================================================

level3_speedy_enemies = [

    # Fast enemy early in the level
    SpeedyEnemy(
        1000,
        473,
        880,
        1250
    ),

    # Fast enemy on a high platform
    SpeedyEnemy(
        780,
        278,
        760,
        850
    ),

    # Fast enemy in the middle
    SpeedyEnemy(
        1780,
        340,
        1760,
        1880
    ),

    # Fast enemy later in the level
    SpeedyEnemy(
        2400,
        360,
        2370,
        2500
    ),

    # Fast enemy near the end
    SpeedyEnemy(
        3600,
        473,
        3520,
        4100
    ),

    # Final speedy enemy
    SpeedyEnemy(
        4580,
        320,
        4560,
        4750
    )
]


level3_slow_enemies = [

    SlowEnemy(
        2600,
        445,
        2250,
        2750
    )
]


level3_flying_enemies = [

    FlyingEnemy(
        1050,
        190,
        950,
        1350
    ),

    FlyingEnemy(
        2450,
        160,
        2250,
        2800
    ),

    FlyingEnemy(
        3650,
        180,
        3500,
        4200
    ),

    FlyingEnemy(
        4700,
        150,
        4500,
        5150
    )
]


level3_spikes = [

    Spike(
        520,
        472
    ),

    Spike(
        1120,
        472
    ),

    Spike(
        1850,
        472
    ),

    Spike(
        2500,
        472
    ),

    Spike(
        3300,
        472
    ),

    Spike(
        4000,
        472
    ),

    Spike(
        4700,
        472
    )
]


# ============================================================
# LEVEL 4
# ============================================================

level4_platforms = [
    pygame.Rect(-100, 535, 1150, 70),
    pygame.Rect(1450, 535, 950, 70),
    pygame.Rect(2800, 535, 1050, 70),
    pygame.Rect(4250, 535, 2250, 70),

    pygame.Rect(900, 90, 460, 48),
    pygame.Rect(1250, 185, 430, 48),
    pygame.Rect(1570, 90, 460, 48),
    pygame.Rect(1950, 185, 460, 48),
    pygame.Rect(2320, 90, 460, 48),
    pygame.Rect(2700, 185, 460, 48),
    pygame.Rect(3070, 90, 460, 48),
    pygame.Rect(3450, 185, 460, 48),
    pygame.Rect(3820, 90, 460, 48),
    pygame.Rect(4200, 185, 460, 48),
    pygame.Rect(4580, 90, 460, 48),
    pygame.Rect(4960, 185, 460, 48),
    pygame.Rect(5340, 90, 460, 48),
    pygame.Rect(5720, 185, 460, 48),
    pygame.Rect(6100, 90, 460, 48),
    pygame.Rect(6480, 185, 460, 48)
]

level4_collision_platforms = [
    pygame.Rect(-100, 540, 1150, 68),
    pygame.Rect(1450, 540, 950, 68),
    pygame.Rect(2800, 540, 1050, 68),
    pygame.Rect(4250, 540, 2250, 68),
]

for _platform in level4_platforms[4:]:
    level4_collision_platforms.append(
        pygame.Rect(
            _platform.x + 8,
            _platform.y + 20,
            _platform.width - 16,
            28
        )
    )

level4_ceiling_platform_indices = set(range(4, len(level4_platforms)))

level4_jump_pads = []

level4_moving_platforms = [
    MovingPlatform(1050, 390, 300, 2.2, True),
    MovingPlatform(2380, 330, 260, 2.5, True),
    MovingPlatform(3850, 330, 280, 2.7, True),
    MovingPlatform(5000, 330, 300, 2.8, True),
    MovingPlatform(6200, 330, 260, 3.0, True)
]

level4_enemies = [
    Enemy(430, 480, 220, 850),
    Enemy(1650, 480, 1480, 2200),
    Enemy(3000, 480, 2850, 3350),
    Enemy(4450, 480, 4300, 4700),
    Enemy(5550, 480, 5400, 5900),
    Enemy(6400, 480, 6250, 6430)
]

level4_slow_enemies = []

level4_speedy_enemies = [
    SpeedyEnemy(1760, 480, 1500, 2200),
    SpeedyEnemy(3210, 480, 2850, 3400),
    SpeedyEnemy(4660, 480, 4300, 4850),
    SpeedyEnemy(6150, 480, 5900, 6418)
]

level4_flying_enemies = []

level4_spikes = [
    Spike(800, 472),
    Spike(1900, 472),
    Spike(3150, 472),
    Spike(4550, 472),
    Spike(5650, 472),
    
]

level4_gravity_switches = [
    GravitySwitch(720, 445, False),
    GravitySwitch(1460, 233, True),
    GravitySwitch(2150, 445, False),
    GravitySwitch(2980, 233, True),
    GravitySwitch(3600, 445, False),
    GravitySwitch(4430, 233, True),
    GravitySwitch(5600, 445, False),
    GravitySwitch(6400, 138, True)
]



# ============================================================
# LEVEL 5 - BALL KING ARENA
# ============================================================

level5_platforms = [
    pygame.Rect(
        -100,
        535,
        2300,
        70
    ),

    pygame.Rect(
        265,
        390,
        190,
        48
    ),

    pygame.Rect(
        625,
        285,
        190,
        48
    ),

    pygame.Rect(
        975,
        390,
        190,
        48
    ),

    pygame.Rect(
        1325,
        285,
        190,
        48
    ),

    pygame.Rect(
        1665,
        390,
        190,
        48
    ),

    pygame.Rect(
        1930,
        285,
        160,
        48
    )
]

level5_collision_platforms = [
    pygame.Rect(
        -100,
        540,
        2300,
        68
    ),

    pygame.Rect(
        273,
        410,
        174,
        28
    ),

    pygame.Rect(
        633,
        305,
        174,
        28
    ),

    pygame.Rect(
        983,
        410,
        174,
        28
    ),

    pygame.Rect(
        1333,
        305,
        174,
        28
    ),

    pygame.Rect(
        1673,
        410,
        174,
        28
    ),

    pygame.Rect(
        1938,
        305,
        144,
        28
    )
]

level5_jump_pads = []

level5_moving_platforms = [
    MovingPlatform(
        420,
        455,
        180,
        2.3,
        True
    ),

    MovingPlatform(
        1020,
        230,
        140,
        2.5,
        False
    ),

    MovingPlatform(
        1460,
        455,
        210,
        2.8,
        True
    )
]

level5_enemies = []
level5_slow_enemies = []
level5_speedy_enemies = []
level5_flying_enemies = []
level5_spikes = []
level5_gravity_switches = []


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
speedy_enemies = []
flying_enemies = []
fireballs = []
spikes = level1_spikes
gravity_switches = []


LEVEL_ENDS = {
    1: 3500,
    2: 4800,
    3: 5350,
    4: 6500,
    5: 2300
}


def entity_before_finish(entity):
    return entity.x < LEVEL_ENDS[current_level]


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
# BOSS STATE
# ============================================================

boss = None
boss_dialogue_active = False
boss_dialogue_index = 0
boss_intro_timer = 0


def reset_boss_dialogue():
    global boss_dialogue_active
    global boss_dialogue_index
    global boss_intro_timer

    boss_dialogue_active = True
    boss_dialogue_index = 0
    boss_intro_timer = 0


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
    global speedy_enemies
    global flying_enemies
    global fireballs
    global spikes
    global gravity_switches
    global camera_x
    global boss
    global boss_dialogue_active
    global boss_dialogue_index
    global boss_intro_timer

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

        speedy_enemies = []
        flying_enemies = []
        fireballs = []

        spikes = level1_spikes
        gravity_switches = []

    elif level == 2:

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

        speedy_enemies = []
        flying_enemies = []
        fireballs = []

        spikes = level2_spikes
        gravity_switches = []

    elif level == 3:

        level_platforms = level3_platforms

        collision_platforms = (
            level3_collision_platforms
        )

        jump_pads = level3_jump_pads

        moving_platforms = (
            level3_moving_platforms
        )

        enemies = level3_enemies

        slow_enemies = (
            level3_slow_enemies
        )

        speedy_enemies = (
            level3_speedy_enemies
        )

        flying_enemies = level3_flying_enemies
        fireballs = []

        spikes = level3_spikes
        gravity_switches = []

    elif level == 4:

        level_platforms = level4_platforms
        collision_platforms = level4_collision_platforms
        jump_pads = level4_jump_pads
        moving_platforms = level4_moving_platforms
        enemies = level4_enemies
        slow_enemies = level4_slow_enemies
        speedy_enemies = level4_speedy_enemies
        flying_enemies = level4_flying_enemies
        fireballs = []
        spikes = level4_spikes
        gravity_switches = level4_gravity_switches

    else:

        level_platforms = level5_platforms
        collision_platforms = level5_collision_platforms
        jump_pads = level5_jump_pads
        moving_platforms = level5_moving_platforms
        enemies = level5_enemies
        slow_enemies = level5_slow_enemies
        speedy_enemies = level5_speedy_enemies
        flying_enemies = level5_flying_enemies
        fireballs = []
        spikes = level5_spikes
        gravity_switches = level5_gravity_switches

        boss = BallKing(
            1710,
            365
        )

        reset_boss_dialogue()

    if level != 5:
        boss = None
        boss_dialogue_active = False
        boss_dialogue_index = 0
        boss_intro_timer = 0

    player.spawn_x = 130
    player.spawn_y = 475

    player.reset()
    player.riding_platform = False
    player.gravity_direction = 1

    for switch in gravity_switches:
        switch.cooldown = 0

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

    # RESET SPEEDY ENEMIES

    for enemy in speedy_enemies:

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
# DRAW GRAVITY SWITCHES
# ============================================================

def draw_gravity_switches(surface, camera_x):

    for gravity_switch in gravity_switches:
        gravity_switch.draw(
            surface,
            camera_x
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

    elif current_level == 3:

        surface.blit(
            flag2,
            (
                FLAG3_POSITION[0] -
                round(camera_x),

                FLAG3_POSITION[1]
            )
        )

    elif current_level == 4:

        surface.blit(
            flag2,
            (
                FLAG4_POSITION[0] -
                round(camera_x),

                FLAG4_POSITION[1]
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
            "You defeated the Ball King!"
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

    if current_level == 1:

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

    elif current_level == 2:

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

    elif current_level == 3:

        text = big_font.render(
            "LEVEL 3",
            True,
            WHITE
        )

        subtitle = small_font.render(
            "WATCH OUT FOR SPEEDY!",
            True,
            WHITE
        )

    elif current_level == 4:

        text = big_font.render(
            "LEVEL 4",
            True,
            WHITE
        )

        subtitle = small_font.render(
            "FLIP GRAVITY!",
            True,
            WHITE
        )

    else:

        text = big_font.render(
            "LEVEL 5",
            True,
            WHITE
        )

        subtitle = small_font.render(
            "BALL KING ARENA!",
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

# ============================================================
# BOSS DIALOGUE
# ============================================================

def draw_boss_dialogue(surface):
    if not boss_dialogue_active:
        return

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 150)
    )

    surface.blit(
        overlay,
        (0, 0)
    )

    box = pygame.Rect(
        70,
        390,
        860,
        160
    )

    pygame.draw.rect(
        surface,
        (18, 16, 26),
        box,
        border_radius=18
    )

    pygame.draw.rect(
        surface,
        (255, 220, 90),
        box,
        3,
        border_radius=18
    )

    speaker, line = boss_dialogue_lines[
        boss_dialogue_index
    ]

    speaker_text = (
        "BALL KING"
        if speaker == "BALL KING"
        else "YOU"
    )

    speaker_surface = small_font.render(
        speaker_text,
        True,
        (255, 220, 90)
    )

    surface.blit(
        speaker_surface,
        (
            box.x + 24,
            box.y + 18
        )
    )

    words = line.split()
    wrapped = []
    current = ""

    for word in words:
        candidate = (
            word
            if not current
            else current + " " + word
        )

        if menu_text_font.size(
            candidate
        )[0] > 690:
            if current:
                wrapped.append(
                    current
                )
            current = word
        else:
            current = candidate

    if current:
        wrapped.append(
            current
        )

    for index, wrapped_line in enumerate(
        wrapped[:3]
    ):
        rendered = menu_text_font.render(
            wrapped_line,
            True,
            WHITE
        )

        surface.blit(
            rendered,
            (
                box.x + 24,
                box.y + 58 +
                index * 34
            )
        )

    if speaker == "PLAYER":
        portrait = pygame.transform.smoothscale(
            player_image,
            (110, 92)
        )
    else:
        portrait = pygame.transform.smoothscale(
            ball_king_image,
            (130, 113)
        )

    portrait_rect = portrait.get_rect(
        midright=(
            box.right - 24,
            box.centery
        )
    )

    surface.blit(
        portrait,
        portrait_rect
    )

    hint = small_font.render(
        "SPACE / ENTER",
        True,
        WHITE
    )

    surface.blit(
        hint,
        hint.get_rect(
            bottomright=(
                box.right - 20,
                box.bottom - 14
            )
        )
    )


def advance_boss_dialogue():
    global boss_dialogue_active
    global boss_dialogue_index
    global boss_intro_timer

    boss_dialogue_index += 1

    if (
        boss_dialogue_index >=
        len(boss_dialogue_lines)
    ):
        boss_dialogue_active = False
        boss_dialogue_index = 0
        boss_intro_timer = 90


# ============================================================
# MENU SYSTEM
# ============================================================

menu_play_image = load_image("play_button.png")
menu_level_selection_image = load_image("level_selection.png")
menu_settings_image = load_image("settings.png")
menu_quit_image = load_image("quit.png")
menu_lvl1_image = load_image("lvl1.png")
menu_lvl2_image = load_image("lvl2.png")
menu_lvl3_image = load_image("lvl3.png")
try:
    menu_lvl4_image = load_image("lvl4.png")
except (FileNotFoundError, pygame.error):
    menu_lvl4_image = load_image("gravity_switch.png")

try:
    menu_lvl5_image = load_image("lvl5.png")
except (FileNotFoundError, pygame.error):
    menu_lvl5_image = menu_lvl4_image

menu_title_font = pygame.font.Font(None, 72)
menu_text_font = pygame.font.Font(None, 36)
menu_small_font = pygame.font.Font(None, 28)


class MenuImageButton:
    def __init__(self, image, center, max_size):
        self.image = image
        self.center = pygame.Vector2(center)
        self.max_size = max_size
        self.scale = 1.0
        self.target_scale = 1.0
        self.pressed = False

    def get_draw_size(self):
        max_w, max_h = self.max_size
        image_w = self.image.get_width()
        image_h = self.image.get_height()

        if image_h <= 0:
            return max_w, max_h

        ratio = image_w / image_h

        if max_w / max_h > ratio:
            h = max_h
            w = int(h * ratio)
        else:
            w = max_w
            h = int(w / ratio)

        return max(1, int(w * self.scale)), max(1, int(h * self.scale))

    def get_rect(self):
        w, h = self.get_draw_size()
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (int(self.center.x), int(self.center.y))
        return rect

    def hit(self, pos):
        return self.get_rect().collidepoint(pos)

    def update(self, mouse_pos):
        if self.pressed:
            self.target_scale = 0.94
        elif self.hit(mouse_pos):
            self.target_scale = 1.07
        else:
            self.target_scale = 1.0

        self.scale += (self.target_scale - self.scale) * 0.22

    def draw(self, surface):
        image = pygame.transform.smoothscale(
            self.image,
            self.get_draw_size()
        )
        surface.blit(
            image,
            image.get_rect(center=(int(self.center.x), int(self.center.y)))
        )


class MenuTextButton:
    def __init__(self, title, subtitle, center, size=(165, 135)):
        self.title = title
        self.subtitle = subtitle
        self.center = pygame.Vector2(center)
        self.size = size
        self.scale = 1.0
        self.target_scale = 1.0
        self.pressed = False

    def get_rect(self):
        rect = pygame.Rect(
            0,
            0,
            int(self.size[0] * self.scale),
            int(self.size[1] * self.scale)
        )
        rect.center = (
            int(self.center.x),
            int(self.center.y)
        )
        return rect

    def hit(self, pos):
        return self.get_rect().collidepoint(pos)

    def update(self, mouse_pos):
        if self.pressed:
            self.target_scale = 0.94
        elif self.hit(mouse_pos):
            self.target_scale = 1.07
        else:
            self.target_scale = 1.0

        self.scale += (
            self.target_scale -
            self.scale
        ) * 0.22

    def draw(self, surface):
        rect = self.get_rect()

        hovered = rect.collidepoint(
            pygame.mouse.get_pos()
        )

        fill = (
            (92, 70, 40)
            if hovered
            else (48, 42, 55)
        )

        pygame.draw.rect(
            surface,
            fill,
            rect,
            border_radius=18
        )

        pygame.draw.rect(
            surface,
            (255, 220, 90),
            rect,
            3,
            border_radius=18
        )

        title = menu_text_font.render(
            self.title,
            True,
            WHITE
        )

        subtitle = menu_small_font.render(
            self.subtitle,
            True,
            (255, 220, 90)
        )

        surface.blit(
            title,
            title.get_rect(
                center=(
                    rect.centerx,
                    rect.centery - 18
                )
            )
        )

        surface.blit(
            subtitle,
            subtitle.get_rect(
                center=(
                    rect.centerx,
                    rect.centery + 24
                )
            )
        )


def draw_menu_background():
    SCREEN.blit(background, (0, 0))

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 125))
    SCREEN.blit(overlay, (0, 0))

    panel = pygame.Surface((900, 550), pygame.SRCALPHA)
    panel.fill((10, 15, 18, 80))
    SCREEN.blit(
        panel,
        panel.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    )


def draw_menu_title(text):
    title = menu_title_font.render(text, True, WHITE)
    SCREEN.blit(
        title,
        title.get_rect(center=(WIDTH // 2, 55))
    )


def draw_back_button(rect, mouse_pos):
    hovered = rect.collidepoint(mouse_pos)

    pygame.draw.rect(
        SCREEN,
        (60, 70, 75) if hovered else (35, 40, 45),
        rect,
        border_radius=12
    )

    pygame.draw.rect(
        SCREEN,
        WHITE,
        rect,
        2,
        border_radius=12
    )

    text = menu_text_font.render("BACK", True, WHITE)
    SCREEN.blit(text, text.get_rect(center=rect.center))


def level_selection_menu():
    level1 = MenuImageButton(
        menu_lvl1_image,
        (115, 245),
        (150, 135)
    )

    level2 = MenuImageButton(
        menu_lvl2_image,
        (300, 245),
        (150, 135)
    )

    level3 = MenuImageButton(
        menu_lvl3_image,
        (485, 245),
        (150, 135)
    )

    level4 = MenuImageButton(
        menu_lvl4_image,
        (680, 245),
        (205, 175)
    )

    level5 = MenuImageButton(
        menu_lvl5_image,
        (865, 245),
        (205, 175)
    )

    buttons = [
        level1,
        level2,
        level3,
        level4,
        level5
    ]

    back_rect = pygame.Rect(
        30,
        520,
        140,
        50
    )

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if (
                event.type == pygame.KEYDOWN
                and
                event.key == pygame.K_ESCAPE
            ):
                return -1

            if (
                event.type ==
                pygame.MOUSEBUTTONDOWN
                and
                event.button == 1
            ):
                if back_rect.collidepoint(
                    event.pos
                ):
                    return -1

                for button in buttons:
                    button.pressed = button.hit(
                        event.pos
                    )

            if (
                event.type ==
                pygame.MOUSEBUTTONUP
                and
                event.button == 1
            ):
                selected = None

                if level1.pressed and level1.hit(
                    event.pos
                ):
                    selected = 1
                elif level2.pressed and level2.hit(
                    event.pos
                ):
                    selected = 2
                elif level3.pressed and level3.hit(
                    event.pos
                ):
                    selected = 3
                elif level4.pressed and level4.hit(
                    event.pos
                ):
                    selected = 4
                elif level5.pressed and level5.hit(
                    event.pos
                ):
                    selected = 5

                for button in buttons:
                    button.pressed = False

                if selected is not None:
                    return selected

        for button in buttons:
            button.update(mouse_pos)

        draw_menu_background()
        draw_menu_title(
            "SELECT LEVEL"
        )

        for button in buttons:
            button.draw(SCREEN)

        draw_back_button(
            back_rect,
            mouse_pos
        )

        pygame.display.flip()
        CLOCK.tick(FPS)


def settings_menu():
    back_rect = pygame.Rect(30, 520, 140, 50)
    slider = pygame.Rect(300, 270, 400, 20)
    dragging_slider = False

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return -1

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return -1
                if slider.inflate(25, 35).collidepoint(event.pos):
                    dragging_slider = True

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_slider = False

            if event.type == pygame.MOUSEMOTION and dragging_slider:
                volume = (event.pos[0] - slider.x) / slider.width
                volume = max(0.0, min(1.0, volume))
                try:
                    pygame.mixer.music.set_volume(volume)
                except pygame.error:
                    pass

        try:
            volume = pygame.mixer.music.get_volume()
        except pygame.error:
            volume = 0.0

        draw_menu_background()
        draw_menu_title("SETTINGS")

        volume_text = menu_text_font.render(
            f"Music volume: {int(volume * 100)}%",
            True,
            WHITE
        )
        SCREEN.blit(
            volume_text,
            volume_text.get_rect(center=(WIDTH // 2, 210))
        )

        pygame.draw.rect(
            SCREEN,
            (35, 40, 45),
            slider,
            border_radius=10
        )

        fill_width = int(slider.width * volume)
        if fill_width > 0:
            fill = pygame.Rect(
                slider.x,
                slider.y,
                fill_width,
                slider.height
            )
            pygame.draw.rect(
                SCREEN,
                (90, 210, 110),
                fill,
                border_radius=10
            )

        pygame.draw.rect(
            SCREEN,
            WHITE,
            slider,
            2,
            border_radius=10
        )

        pygame.draw.circle(
            SCREEN,
            WHITE,
            (slider.x + int(slider.width * volume), slider.centery),
            10
        )

        draw_back_button(back_rect, mouse_pos)
        pygame.display.flip()
        CLOCK.tick(FPS)


def main_menu():
    play = MenuImageButton(menu_play_image, (300, 205), (320, 175))
    level_selection = MenuImageButton(menu_level_selection_image, (700, 205), (320, 175))
    settings = MenuImageButton(menu_settings_image, (300, 425), (320, 175))
    quit_button = MenuImageButton(menu_quit_image, (700, 425), (320, 175))
    buttons = [play, level_selection, settings, quit_button]

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    button.pressed = button.hit(event.pos)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                action = None

                if play.pressed and play.hit(event.pos):
                    action = "play"
                elif level_selection.pressed and level_selection.hit(event.pos):
                    action = "levels"
                elif settings.pressed and settings.hit(event.pos):
                    action = "settings"
                elif quit_button.pressed and quit_button.hit(event.pos):
                    action = "quit"

                for button in buttons:
                    button.pressed = False

                if action == "play":
                    result = level_selection_menu()
                    if result is None:
                        return None
                    if result != -1:
                        return result

                elif action == "levels":
                    result = level_selection_menu()
                    if result is None:
                        return None
                    if result != -1:
                        return result

                elif action == "settings":
                    result = settings_menu()
                    if result is None:
                        return None

                elif action == "quit":
                    return None

        for button in buttons:
            button.update(mouse_pos)

        draw_menu_background()
        draw_menu_title("MY PLATFORMER")

        for button in buttons:
            button.draw(SCREEN)

        pygame.display.flip()
        CLOCK.tick(FPS)


# START
# ============================================================

selected_level = main_menu()

if selected_level is None:
    pygame.quit()
    sys.exit()

load_level(selected_level)

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

            if event.key == pygame.K_ESCAPE:
                selected_level = main_menu()

                if selected_level is None:
                    running = False
                    continue

                load_level(selected_level)
                current_level = selected_level
                dead = False
                won = False
                score = 0
                level_message_timer = 0
                game_start_time = time.time()
                final_time = 0
                effects.clear()
                continue

            if (
                current_level == 5
                and
                boss_dialogue_active
                and
                event.key in (
                    pygame.K_SPACE,
                    pygame.K_RETURN
                )
            ):
                advance_boss_dialogue()
                continue

            if (
                event.key in (
                    pygame.K_SPACE,
                    pygame.K_UP
                )

                and

                not dead

                and

                not won

                and

                not boss_dialogue_active
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
        and
        not boss_dialogue_active
    ):

        if level_message_timer > 0:

            level_message_timer -= 1

        previous_bottom = (
            player.rect.bottom
        )


        # ====================================================
        # MOVING PLATFORMS
        # ====================================================

        # Decide support from the platform's OLD position, then move the
        # platform and carry the player by the exact displacement. The player
        # is not given the moving platform as a normal solid collider.
        player_rect_before_platforms = player.rect
        riding_platform = None

        for moving_platform in moving_platforms:
            old_rect = moving_platform.rect
            moving_platform._collision_old_rect = old_rect

            horizontal_overlap = (
                player_rect_before_platforms.right > old_rect.left + 4
                and
                player_rect_before_platforms.left < old_rect.right - 4
            )

            if not horizontal_overlap:
                continue

            if player.gravity_direction == 1:
                standing = (
                    player_rect_before_platforms.bottom >= old_rect.top - 9
                    and
                    player_rect_before_platforms.bottom <= old_rect.top + 9
                    and
                    player.vy >= -0.5
                )
            else:
                standing = (
                    player_rect_before_platforms.top >= old_rect.bottom - 9
                    and
                    player_rect_before_platforms.top <= old_rect.bottom + 9
                    and
                    player.vy <= 0.5
                )

            if standing:
                riding_platform = moving_platform
                break

        for moving_platform in moving_platforms:
            moving_platform.update()

        player.riding_platform = riding_platform is not None

        if riding_platform is not None:
            player.x += riding_platform.dx
            player.y += riding_platform.dy
            player.vy = 0

        # Static level geometry handles normal collision. A rider skips
        # gravity this frame so the platform's motion is the only vertical
        # movement applied to the player.
        player.update(
            collision_platforms,
            carried_by_moving_platform=(riding_platform is not None)
        )

        # One-way landing on moving platforms when the player jumps/falls onto
        # one. This uses the platform's old and new positions, so a platform
        # moving vertically cannot pull the player through it.
        if riding_platform is None:
            for moving_platform in moving_platforms:
                new_rect = moving_platform.rect
                old_rect = getattr(
                    moving_platform,
                    '_collision_old_rect',
                    new_rect
                )

                if not player.rect.colliderect(new_rect):
                    continue

                horizontal_overlap = (
                    player.rect.right > new_rect.left + 4
                    and
                    player.rect.left < new_rect.right - 4
                )

                if not horizontal_overlap:
                    continue

                if player.gravity_direction == 1:
                    crossed = (
                        player_rect_before_platforms.bottom <= old_rect.top + 2
                        and
                        player.rect.bottom >= new_rect.top
                        and
                        player.vy >= 0
                    )

                    if crossed:
                        player.y = new_rect.top - player.h
                        player.vy = 0
                        player.on_ground = True
                        player.riding_platform = True

                else:
                    crossed = (
                        player_rect_before_platforms.top >= old_rect.bottom - 2
                        and
                        player.rect.top <= new_rect.bottom
                        and
                        player.vy <= 0
                    )

                    if crossed:
                        player.y = new_rect.bottom
                        player.vy = 0
                        player.on_ground = True
                        player.riding_platform = True

        if current_level == 5:
            player.x = max(
                BOSS_ARENA_LEFT,
                min(
                    player.x,
                    LEVEL_ENDS[5] -
                    player.w -
                    30
                )
            )

            if boss_intro_timer > 0:
                boss_intro_timer -= 1


        # ====================================================
        # JUMP PADS
        # ====================================================

        check_jump_pads()


        # ====================================================
        # GRAVITY SWITCHES
        # ====================================================

        for gravity_switch in gravity_switches:
            gravity_switch.update()

            if gravity_switch.try_activate(player.rect):
                player.gravity_direction *= -1
                player.vy = 0
                player.on_ground = False
                player.coyote_time = 0

                effects.append(
                    ExplosionEffect(
                        gravity_switch.rect.centerx,
                        gravity_switch.rect.centery
                    )
                )


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

            if spike.x >= LEVEL_ENDS[current_level]:
                continue

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

            if not entity_before_finish(enemy):
                enemy.x = LEVEL_ENDS[current_level] - enemy.w
                enemy.direction = -1
                continue

            enemy.update()


        # ====================================================
        # BIG SLOW ENEMIES
        # ====================================================

        for enemy in slow_enemies:

            if not entity_before_finish(enemy):
                enemy.x = LEVEL_ENDS[current_level] - enemy.w
                enemy.direction = -1
                continue

            enemy.update()


        # ====================================================
        # SPEEDY ENEMIES
        # ====================================================

        for enemy in speedy_enemies:

            if not entity_before_finish(enemy):
                enemy.x = LEVEL_ENDS[current_level] - enemy.w
                enemy.direction = -1
                continue

            enemy.update()


        # ====================================================
        # FLYING ENEMIES
        # ====================================================

        for enemy in flying_enemies:

            enemy.update(
                fireballs
            )


        # ====================================================
        # FIREBALLS
        # ====================================================

        fireball_collision_platforms = (
            collision_platforms +
            [
                moving_platform.rect
                for moving_platform in moving_platforms
            ]
        )

        for fireball in fireballs[:]:

            exploded = fireball.update(
                fireball_collision_platforms
            )

            if exploded:
                effects.append(
                    ExplosionEffect(
                        fireball.rect.centerx,
                        fireball.rect.bottom
                    )
                )

            if not fireball.alive:
                if fireball in fireballs:
                    fireballs.remove(fireball)
                continue

            if fireball.rect.colliderect(
                player.rect.inflate(-18, -14)
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
                fireball.alive = False
                fireballs.remove(fireball)
                break


        # ====================================================
        # FLYING ENEMY COLLISIONS
        # ====================================================

        if not dead:

            for enemy in flying_enemies:

                if not enemy.alive:
                    continue

                player_rect = player.rect
                enemy_hit_rect = enemy.hitbox

                # STOMP FLYING ENEMY
                if is_stomping(
                    player_rect,
                    enemy_hit_rect,
                    previous_bottom,
                    player.vy
                ):
                    enemy.squash()
                    score += 250

                    player.y = (
                        enemy_hit_rect.top -
                        player.h
                    )

                    player.vy = -12
                    player.on_ground = False

                    effects.append(
                        PopEffect(
                            enemy_hit_rect.centerx,
                            enemy_hit_rect.top
                        )
                    )

                    continue

                # GET HIT BY FLYING ENEMY
                if player_hits_enemy(
                    player_rect,
                    enemy_hit_rect
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
        # BALL KING BOSS
        # ====================================================

        if current_level == 5 and boss is not None:
            if boss_intro_timer <= 0:
                boss.update()

            if (
                not boss.defeated
                and
                boss.is_dashing
                and
                player_hits_enemy(
                    player.rect,
                    boss.rect.inflate(
                        -28,
                        -20
                    )
                )
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

            if not dead:
                for orb in boss.orbs[:]:
                    orb.update()

                    if not orb.alive:
                        boss.orbs.remove(orb)
                        continue

                    if orb.collides(
                        player.rect
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

                        orb.alive = False
                        boss.orbs.remove(orb)
                        break

            if not dead:
                for wave in boss.shockwaves[:]:
                    wave.update()

                    if not wave.alive:
                        boss.shockwaves.remove(
                            wave
                        )
                        continue

                    if wave.collides(
                        player.rect
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

                        wave.alive = False
                        boss.shockwaves.remove(
                            wave
                        )
                        break

            if not dead:
                for beam in boss.beams[:]:
                    beam.update()

                    if not beam.alive:
                        boss.beams.remove(beam)
                        continue

                    if beam.collides(
                        player.rect
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

                        beam.alive = False
                        boss.beams.remove(beam)
                        break

            if (
                not dead
                and
                not boss.defeated
            ):
                if is_stomping(
                    player.rect,
                    boss.hurt_rect,
                    previous_bottom,
                    player.vy
                ):
                    if boss.take_hit():
                        score += 500

                        player.y = (
                            boss.rect.top -
                            player.h
                        )

                        player.vy = -14
                        player.on_ground = False

                        effects.append(
                            PopEffect(
                                boss.rect.centerx,
                                boss.rect.top
                            )
                        )

            if (
                boss.defeated
                and
                boss.death_timer >= 70
            ):
                won = True

                final_time = (
                    time.time() -
                    game_start_time
                )

                best_score = max(
                    best_score,
                    score
                )


        if dead:

            continue


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

            if not entity_before_finish(enemy):
                continue

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
        # SPEEDY ENEMY COLLISIONS
        # ====================================================

        for enemy in speedy_enemies:

            if not entity_before_finish(enemy):
                continue

            if not enemy.alive:

                continue

            player_rect = player.rect

            enemy_rect = enemy.rect


            # STOMP SPEEDY ENEMY

            if is_stomping(
                player_rect,
                enemy_rect,
                previous_bottom,
                player.vy
            ):

                enemy.squash()

                # Speedy enemies give more points
                score += 200

                player.y = (
                    enemy_rect.top -
                    player.h
                )

                player.vy = -12

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


        if dead:

            continue


        # ====================================================
        # BIG SLOW ENEMY COLLISIONS
        # ====================================================

        for enemy in slow_enemies:

            if not entity_before_finish(enemy):
                continue

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

                    score += 300

                else:

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

                load_level(2)

                level_message_timer = 75

            elif current_level == 2:

                load_level(3)

                level_message_timer = 90

            elif current_level == 3:

                load_level(4)

                level_message_timer = 90

            elif current_level == 4:

                load_level(5)

                level_message_timer = 0

            elif (
                current_level == 5
                and
                boss is not None
                and
                boss.defeated
            ):

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

        if current_level == 5:
            camera_limit = max(
                0,
                LEVEL_ENDS[5] -
                WIDTH +
                100
            )

            target_camera = max(
                0,
                min(
                    player.x - 280,
                    camera_limit
                )
            )

        else:
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

    if current_level == 4:
        draw_level4_background(
            SCREEN,
            camera_x
        )
    elif current_level == 5:
        draw_boss_arena_background(
            SCREEN,
            camera_x
        )
    else:
        draw_background(SCREEN)


    for index, platform in enumerate(level_platforms):

        visible_platform = (
            platform.move(
                -round(camera_x),
                0
            )
        )

        if current_level == 4:
            if index in level4_ceiling_platform_indices:
                draw_level4_platform(
                    SCREEN,
                    visible_platform,
                    True
                )
            else:
                draw_ground(
                    SCREEN,
                    visible_platform
                )
        elif current_level == 5:
            if index == 0:
                draw_ground(
                    SCREEN,
                    visible_platform
                )
            else:
                draw_platform(
                    SCREEN,
                    visible_platform
                )
        else:
            if current_level == 1:
                ground_count = 4
            elif current_level == 2:
                ground_count = 6
            else:
                ground_count = 7

            if index < ground_count:
                draw_ground(SCREEN, visible_platform)
            else:
                draw_platform(SCREEN, visible_platform)


    # ========================================================
    # MOVING PLATFORMS
    # ========================================================

    for moving_platform in moving_platforms:

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
    # GRAVITY SWITCHES
    # ========================================================

    draw_gravity_switches(
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

        if spike.x >= LEVEL_ENDS[current_level]:
            continue

        spike.draw(
            SCREEN,
            camera_x
        )


    # ========================================================
    # NORMAL ENEMIES
    # ========================================================

    for enemy in enemies:

        if not entity_before_finish(enemy):
            continue

        enemy.draw(
            SCREEN,
            camera_x
        )


    # ========================================================
    # SPEEDY ENEMIES
    # ========================================================

    for enemy in speedy_enemies:

        if not entity_before_finish(enemy):
            continue

        enemy.draw(
            SCREEN,
            camera_x
        )


    # ========================================================
    # BIG SLOW ENEMIES
    # ========================================================

    for enemy in slow_enemies:

        if not entity_before_finish(enemy):
            continue

        enemy.draw(
            SCREEN,
            camera_x
        )


    # ========================================================
    # FLYING ENEMIES
    # ========================================================

    for enemy in flying_enemies:

        enemy.draw(
            SCREEN,
            camera_x
        )


    # ========================================================
    # FIREBALLS
    # ========================================================

    for fireball in fireballs:

        fireball.draw(
            SCREEN,
            camera_x
        )


    # ========================================================
    # BALL KING
    # ========================================================

    if current_level == 5 and boss is not None:
        for orb in boss.orbs:
            orb.draw(
                SCREEN,
                camera_x
            )

        for wave in boss.shockwaves:
            wave.draw(
                SCREEN,
                camera_x
            )

        for beam in boss.beams:
            beam.draw(
                SCREEN,
                camera_x
            )

        boss.draw(
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

    draw_boss_ui(
        SCREEN
    )

    if (
        current_level == 5
        and
        boss_intro_timer > 0
        and
        not boss_dialogue_active
        and
        not dead
        and
        not won
    ):
        fight_text = big_font.render(
            "FIGHT!",
            True,
            (255, 225, 95)
        )

        SCREEN.blit(
            fight_text,
            fight_text.get_rect(
                center=(
                    WIDTH // 2,
                    HEIGHT // 2 - 70
                )
            )
        )

        fight_subtitle = small_font.render(
            "DEFEAT THE BALL KING",
            True,
            WHITE
        )

        SCREEN.blit(
            fight_subtitle,
            fight_subtitle.get_rect(
                center=(
                    WIDTH // 2,
                    HEIGHT // 2
                )
            )
        )

    if level_message_timer > 0:

        draw_level_message(
            SCREEN
        )


    if boss_dialogue_active:
        draw_boss_dialogue(
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