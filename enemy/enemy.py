import os
import pygame
from player.animation import Animation


class Enemy:
    SIZE = 32

    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    HIT = "hit"

    def __init__(self, x, y, name, props, tile_size):
        # ================= BASIC =================
        self.name = name
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.pos_x = float(self.rect.x)

        # ================= TILE / ZONE =================
        self.tile = tile_size  # 16
        self.off_neg = float(props.get("offNeg", 4)) * self.tile
        self.off_pos = float(props.get("offPos", 4)) * self.tile

        self.start_x = self.rect.centerx
        self.left_zone = self.start_x - self.off_neg
        self.right_zone = self.start_x + self.off_pos

        # ================= MOVE =================
        self.dir = -1
        self.facing = -1              # sprite gốc nhìn TRÁI
        self.speed_walk = 0.8
        self.speed_run = 1.1

        # ================= MODE =================
        self.chasing = False
        self.waiting = False

        # ================= PAUSE =================
        self.pause_time = 90
        self.pause_timer = 0

        # ================= DAMAGE =================
        self.damage_cd = 45
        self.damage_timer = 0

        # ================= STATE =================
        self.state = self.IDLE
        self.alive = True

        # ================= ANIMATION =================
        base = f"assets/Enemies/{name}"

        self.animations = {
            self.IDLE: Animation(
                pygame.image.load(os.path.join(base, "Idle (36x30).png")).convert_alpha(),
                36, 30, 0.25
            ),
            self.WALK: Animation(
                pygame.image.load(os.path.join(base, "Walk (36x30).png")).convert_alpha(),
                36, 30, 0.25
            ),
            self.RUN: Animation(
                pygame.image.load(os.path.join(base, "Run (36x30).png")).convert_alpha(),
                36, 30, 0.15
            ),
            self.HIT: Animation(
                pygame.image.load(os.path.join(base, "Hit (36x30).png")).convert_alpha(),
                36, 30, 0.2,
                loop=False
            ),
        }

        self.current_anim = self.animations[self.state]

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self, player):
        if not self.alive:
            return

        # ===== HIT STATE =====
        if self.state == self.HIT:
            self.current_anim.update()
            if self.current_anim.finished:
                self.alive = False
            return

        # ===== DAMAGE COOLDOWN =====
        if self.damage_timer > 0:
            self.damage_timer -= 1

        # ===== ZONE RECT (RECT-BASED DETECT) =====
        zone_rect = pygame.Rect(
            self.left_zone,
            self.rect.top - self.rect.height,
            self.right_zone - self.left_zone,
            self.rect.height * 3
        )

        player_in_zone = zone_rect.colliderect(player.rect)

        if player_in_zone:
            self.chasing = True
            self._chase(player)
        else:
            if self.chasing:
                self._reset_patrol()
            self._patrol()

        self.current_anim.update()

    # ==================================================
    # CHASE
    # ==================================================
    def _chase(self, player):
        dx = player.rect.centerx - self.rect.centerx
        self.dir = 1 if dx > 0 else -1
        self.facing = self.dir

        self.waiting = False
        self.pause_timer = 0

        # MOVE
        self.pos_x += self.dir * self.speed_run
        self.pos_x = max(self.left_zone, min(self.right_zone, self.pos_x))
        self.rect.x = int(self.pos_x)

        self._set_state(self.RUN)

        # ===== COLLISION WITH PLAYER =====
        if self.rect.colliderect(player.rect):

            # ===== STOMP (ƯU TIÊN CAO NHẤT) =====
            if (
                player.vel_y > 0 and
                player.rect.bottom <= self.rect.top + 8
            ):
                self.take_hit()
                player.on_stomp()
                return

            # ===== BODY DAMAGE =====
            if self.damage_timer <= 0:
                player.take_damage()
                self.damage_timer = self.damage_cd

    # ==================================================
    # PATROL
    # ==================================================
    def _patrol(self):
        if self.waiting:
            self.pause_timer -= 1
            self._set_state(self.IDLE)

            if self.pause_timer <= 0:
                self.waiting = False
                self.dir *= -1
                self.facing = self.dir

                # đẩy nhẹ để tránh kẹt mốc
                self.pos_x += self.dir * 2
                self.rect.x = int(self.pos_x)
            return

        self.pos_x += self.dir * self.speed_walk
        self.rect.x = int(self.pos_x)
        self._set_state(self.WALK)

        if self.rect.centerx <= self.left_zone:
            self.rect.centerx = self.left_zone
            self.pos_x = self.rect.x
            self._pause()

        elif self.rect.centerx >= self.right_zone:
            self.rect.centerx = self.right_zone
            self.pos_x = self.rect.x
            self._pause()

    def _pause(self):
        self.waiting = True
        self.pause_timer = self.pause_time

    def _reset_patrol(self):
        self.chasing = False
        self.waiting = True
        self.pause_timer = self.pause_time
        self._set_state(self.IDLE)

    # ==================================================
    # HIT BY PLAYER (STOMP)
    # ==================================================
    def take_hit(self):
        if self.state == self.HIT:
            return

        self.chasing = False
        self.waiting = False
        self._set_state(self.HIT)

    # ==================================================
    # STATE / DRAW
    # ==================================================
    def _set_state(self, state):
        if self.state != state:
            self.state = state
            self.current_anim = self.animations[state]
            self.current_anim.reset()

    def draw(self, surf):
        if not self.alive:
            return

        img = self.current_anim.get_image()

        # sprite gốc nhìn TRÁI → flip khi quay PHẢI
        if self.facing > 0:
            img = pygame.transform.flip(img, True, False)

        img_rect = img.get_rect(midbottom=self.rect.midbottom)
        surf.blit(img, img_rect)
