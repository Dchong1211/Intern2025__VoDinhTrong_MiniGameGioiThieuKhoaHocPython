import os
import pygame
from player.animation import Animation
from player.skills import Skills


class Player:
    SIZE = 32

    # ===== STATES =====
    IDLE = "idle"
    RUN = "run"
    JUMP = "jump"
    DOUBLE = "double"
    FALL = "fall"
    SLIDE = "slide"
    DASH = "dash"

    HIT = "hit"
    DISAPPEAR = "disappear"
    APPEAR = "appear"

    def __init__(self, x, y, character="Virtual Guy"):
        # ===== CHARACTER =====
        self.character = character
        self.base_path = f"assets/Main Characters/{self.character}"

        # ===== RECT (HITBOX) =====
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.spawn_pos = (x, y)

        # ===== ANIMATIONS =====
        self.animations = {
            # 32x32
            self.IDLE:   self._load_anim("Idle.png", 0.25),
            self.RUN:    self._load_anim("Run.png", 0.25),
            self.JUMP:   self._load_anim("Jump.png", 0.25, loop=False),
            self.DOUBLE: self._load_anim("Double Jump.png", 0.25, loop=False),
            self.FALL:   self._load_anim("Fall.png", 0.25),
            self.SLIDE:  self._load_anim("Wall Slide.png", 0.15),
            self.DASH:   self._load_anim("Dash.png", 0.2, loop=False),
            self.HIT:    self._load_anim("Hit.png", 0.2, loop=False),

            # 96x96 (QUAN TRỌNG)
            self.DISAPPEAR: self._load_anim(
                "Desappearing (96x96).png", 0.3, loop=False, size=96
            ),
            self.APPEAR: self._load_anim(
                "Appearing (96x96).png", 0.3, loop=False, size=96
            ),
        }

        self.state = self.IDLE
        self.current_anim = self.animations[self.state]

        # ===== PHYSICS =====
        self.vel_x = 0
        self.vel_y = 0

        self.speed = 3
        self.gravity = 0.35
        self.max_fall_speed = 10

        # ===== JUMP =====
        self.jump_force = -6
        self.jump_count = 0
        self.jump_key_down = False
        self.is_double_jumping = False

        # ===== GROUND / WALL =====
        self.on_ground = False
        self.ground_buffer = 0
        self.ground_buffer_time = 4

        self.on_wall = False
        self.wall_dir = 0

        # ===== DROP =====
        self.drop_timer = 0
        self.drop_duration = 12

        # ===== DASH =====
        self.dash_force = 10
        self.dash_time = 8
        self.dash_timer = 0
        self.can_dash = True
        self.dash_dir = 1
        self.dash_key_down = False

        # ===== DAMAGE / RESPAWN =====
        self.control_lock = False
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_time = 30

        # ===== OTHER =====
        self.skills = Skills()
        self.facing_right = True

    # ==================================================
    # LOAD ANIMATION (HỖ TRỢ NHIỀU SIZE)
    # ==================================================
    def _load_anim(self, name, speed, loop=True, size=None):
        sheet = pygame.image.load(
            os.path.join(self.base_path, name)
        ).convert_alpha()

        if size is None:
            size = self.SIZE

        return Animation(sheet, size, size, speed, loop)

    # ==================================================
    # INPUT
    # ==================================================
    def _handle_input(self, keys):
        if self.control_lock or self.dash_timer > 0:
            return

        self.vel_x = 0

        left = keys[pygame.K_a]
        right = keys[pygame.K_d]

        if left and self.skills.has("move"):
            self.vel_x = -self.speed
            self.facing_right = False
        elif right and self.skills.has("move"):
            self.vel_x = self.speed
            self.facing_right = True

        if keys[pygame.K_s]:
            self.drop_timer = self.drop_duration

        self._handle_jump(keys)
        self._handle_dash(keys)

    def _handle_jump(self, keys):
        space = keys[pygame.K_SPACE]
        pressed = space and not self.jump_key_down

        if pressed:
            if self.on_wall and not self.on_ground and self.skills.has("wall_jump"):
                self.vel_y = self.jump_force
                self.vel_x = 6 * (-self.wall_dir)
                self.jump_count = 1
                self.is_double_jumping = False

            elif self.jump_count == 0 and self.skills.has("jump"):
                self.vel_y = self.jump_force
                self.jump_count = 1

            elif self.jump_count == 1 and self.skills.has("double_jump"):
                self.vel_y = self.jump_force
                self.jump_count = 2
                self.is_double_jumping = True

        self.jump_key_down = space

    def _handle_dash(self, keys):
        shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        pressed = shift and not self.dash_key_down

        if pressed and self.skills.has("dash") and self.can_dash:
            self.dash_dir = 1 if self.facing_right else -1
            self.vel_x = self.dash_force * self.dash_dir
            self.vel_y = 0
            self.dash_timer = self.dash_time
            self.can_dash = False

        self.dash_key_down = shift

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self, dt, keys, tiles, one_way):
        # Khoá physics khi teleport
        if self.state in (self.DISAPPEAR, self.APPEAR):
            self._update_animation()
            self._handle_respawn_flow()
            return

        self._handle_input(keys)

        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        if self.drop_timer > 0:
            self.drop_timer -= 1

        self._apply_gravity()
        self._move_x(tiles)
        self._move_y(tiles, one_way)

        self._update_state()
        self._update_animation()
        self._handle_respawn_flow()

    # ==================================================
    # PHYSICS
    # ==================================================
    def _apply_gravity(self):
        if self.dash_timer <= 0:
            self.vel_y = min(self.vel_y + self.gravity, self.max_fall_speed)
        else:
            self.vel_y = 0
            self.vel_x = self.dash_force * self.dash_dir

        if self.is_double_jumping and self.vel_y >= 0:
            self.is_double_jumping = False

        if self.dash_timer > 0:
            self.dash_timer -= 1

    def _move_x(self, tiles):
        self.rect.x += self.vel_x
        self.on_wall = False

        for t in tiles:
            if self.rect.colliderect(t):
                if self.vel_x > 0:
                    self.rect.right = t.left
                    self.on_wall = True
                    self.wall_dir = 1
                elif self.vel_x < 0:
                    self.rect.left = t.right
                    self.on_wall = True
                    self.wall_dir = -1

    def _move_y(self, tiles, one_way):
        prev_bottom = self.rect.bottom
        self.rect.y += self.vel_y
        self.on_ground = False

        for t in tiles:
            if self.rect.colliderect(t):
                if self.vel_y > 0:
                    self.rect.bottom = t.top
                    self.vel_y = 0
                    self._land()
                elif self.vel_y < 0:
                    self.rect.top = t.bottom
                    self.vel_y = 0

        if self.vel_y > 0 and self.drop_timer <= 0:
            for p in one_way:
                if self.rect.colliderect(p) and prev_bottom <= p.top:
                    self.rect.bottom = p.top
                    self.vel_y = 0
                    self._land()

        self.ground_buffer = (
            self.ground_buffer_time if self.on_ground
            else max(0, self.ground_buffer - 1)
        )

    def _land(self):
        self.on_ground = True
        self.jump_count = 0
        self.is_double_jumping = False
        self.can_dash = True
        self.dash_timer = 0

    # ==================================================
    # STATE
    # ==================================================
    def _update_state(self):
        if self.state in (self.HIT, self.DISAPPEAR, self.APPEAR):
            return

        grounded = self.ground_buffer > 0
        wall_slide = (
            self.on_wall and not grounded
            and self.vel_y > 0
            and self.skills.has("wall_slide")
            and self.dash_timer <= 0
        )

        if wall_slide:
            self.vel_y = min(self.vel_y, 1.5)

        if self.dash_timer > 0:
            self.state = self.DASH
        elif grounded:
            self.state = self.RUN if self.vel_x != 0 else self.IDLE
        elif wall_slide:
            self.state = self.SLIDE
        elif self.is_double_jumping:
            self.state = self.DOUBLE
        else:
            self.state = self.JUMP if self.vel_y < 0 else self.FALL

    def _update_animation(self):
        anim = self.animations[self.state]
        if anim != self.current_anim:
            self.current_anim = anim
            self.current_anim.reset()
        self.current_anim.update()

    # ==================================================
    # DAMAGE / RESPAWN FLOW
    # ==================================================
    def take_damage(self):
        if self.invincible or self.state in (
            self.HIT, self.DISAPPEAR, self.APPEAR
        ):
            return

        self.invincible = True
        self.invincible_timer = self.invincible_time

        self.control_lock = True
        self.vel_x = 0
        self.vel_y = 0

        self.state = self.HIT
        self.current_anim = self.animations[self.HIT]
        self.current_anim.reset()

    def _handle_respawn_flow(self):
        anim = self.current_anim

        if self.state == self.HIT and anim.finished:
            self.state = self.DISAPPEAR
            self.current_anim = self.animations[self.DISAPPEAR]
            self.current_anim.reset()

        elif self.state == self.DISAPPEAR and anim.finished:
            self.rect.topleft = self.spawn_pos
            self.vel_x = 0
            self.vel_y = 0

            self.state = self.APPEAR
            self.current_anim = self.animations[self.APPEAR]
            self.current_anim.reset()

        elif self.state == self.APPEAR and anim.finished:
            self.control_lock = False
            self.state = self.IDLE
            self.current_anim = self.animations[self.IDLE]
            self.current_anim.reset()

    # ==================================================
    # STOMP (ENEMY GỌI)
    # ==================================================
    def on_stomp(self):
        self.vel_y = -4
        self.jump_count = 1
        self.is_double_jumping = False

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self, surf):
        if self.invincible and pygame.time.get_ticks() % 200 < 100:
            return

        img = self.current_anim.get_image()
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)

        img_rect = img.get_rect(center=self.rect.center)
        surf.blit(img, img_rect)
