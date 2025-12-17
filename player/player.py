import pygame
import os
from player.animation import Animation
from player.skills import Skills


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)

        # ===== LOAD ANIMATION =====
        BASE = "assets/Main Characters/Virtual Guy"

        def load(name):
            return pygame.image.load(
                os.path.join(BASE, name)
            ).convert_alpha()

        self.animations = {
            "idle":   Animation(load("Idle.png"), 32, 32, 0.25),
            "run":    Animation(load("Run.png"), 32, 32, 0.25),
            "jump":   Animation(load("Jump.png"), 32, 32, 0.25, loop=False),
            "double": Animation(load("Double Jump.png"), 32, 32, 0.25, loop=False),
            "fall":   Animation(load("Fall.png"), 32, 32, 0.25),
            "slide":  Animation(load("Wall Slide.png"), 32, 32, 0.15),
            "dash":   Animation(load("Dash.png"), 32, 32, 0.2, loop=False),
        }

        self.state = "idle"
        self.current_anim = self.animations[self.state]

        # ===== PHYSICS =====
        self.vel_x = 0
        self.vel_y = 0

        self.speed = 3
        self.gravity = 0.35
        self.max_fall_speed = 10

        # ===== JUMP =====
        self.jump_force = -6
        self.jump_key_down = False
        self.jump_count = 0
        self.on_ground = False
        self.is_double_jumping = False   # FLAG QUAN TRỌNG

        # ===== DROP THROUGH (ONE WAY) =====
        self.drop_timer = 0
        self.drop_duration = 12

        # ===== GROUND BUFFER =====
        self.ground_buffer = 0
        self.ground_buffer_time = 4

        # ===== WALL =====
        self.on_wall = False
        self.wall_dir = 0

        # ===== DASH =====
        self.dash_force = 10
        self.dash_time = 8
        self.dash_timer = 0
        self.can_dash = True
        self.dash_dir = 1
        self.dash_key_down = False

        # ===== SKILLS =====
        self.skills = Skills()
        self.facing_right = True

    # ====================================================
    def _handle_input(self, keys):

        if self.dash_timer > 0:
            return

        self.vel_x = 0

        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]

        if left and self.skills.move:
            self.vel_x = -self.speed
            self.facing_right = False
        elif right and self.skills.move:
            self.vel_x = self.speed
            self.facing_right = True

        # ---- DROP DOWN ----
        if keys[pygame.K_s]:
            self.drop_timer = self.drop_duration

        # ---- JUMP ----
        space = keys[pygame.K_SPACE]
        pressed = space and not self.jump_key_down

        if pressed:
            # WALL JUMP
            if self.on_wall and not self.on_ground and self.skills.wall_jump:
                self.vel_y = self.jump_force
                self.vel_x = 6 * (-self.wall_dir)
                self.jump_count = 1
                self.is_double_jumping = False

            else:
                # JUMP 1
                if self.jump_count == 0 and self.skills.jump:
                    self.vel_y = self.jump_force
                    self.jump_count = 1
                    self.is_double_jumping = False

                # DOUBLE JUMP
                elif self.jump_count == 1 and self.skills.double_jump:
                    self.vel_y = self.jump_force
                    self.jump_count = 2
                    self.is_double_jumping = True   # BẬT FLAG

        self.jump_key_down = space

        # ---- DASH ----
        shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        pressed = shift and not self.dash_key_down

        if pressed and self.skills.dash and self.can_dash:
            self.dash_dir = 1 if self.facing_right else -1
            self.vel_x = self.dash_force * self.dash_dir
            self.vel_y = 0
            self.dash_timer = self.dash_time
            self.can_dash = False

        self.dash_key_down = shift

    # ====================================================
    def update(self, dt, keys, tiles, one_way_platforms):

        self._handle_input(keys)

        # ===== DROP TIMER =====
        if self.drop_timer > 0:
            self.drop_timer -= 1

        # ===== GRAVITY =====
        if self.dash_timer <= 0:
            self.vel_y += self.gravity
            self.vel_y = min(self.vel_y, self.max_fall_speed)
        else:
            self.vel_y = 0
            self.vel_x = self.dash_force * self.dash_dir

        # >>> FIX QUAN TRỌNG: KẾT THÚC DOUBLE JUMP KHI BẮT ĐẦU RƠI <<<
        if self.is_double_jumping and self.vel_y >= 0:
            self.is_double_jumping = False

        # ===== MOVE X =====
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

        # ===== MOVE Y =====
        prev_bottom = self.rect.bottom
        self.rect.y += self.vel_y
        self.on_ground = False

        # ---- COLLISION CỨNG ----
        for t in tiles:
            if self.rect.colliderect(t):
                if self.vel_y > 0:
                    self.rect.bottom = t.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0
                    self.is_double_jumping = False
                    self.can_dash = True
                    self.dash_timer = 0
                elif self.vel_y < 0:
                    self.rect.top = t.bottom
                    self.vel_y = 0

        # ---- ONE WAY PLATFORM ----
        if self.vel_y > 0 and self.drop_timer <= 0:
            for p in one_way_platforms:
                if self.rect.colliderect(p):
                    if prev_bottom <= p.top:
                        self.rect.bottom = p.top
                        self.vel_y = 0
                        self.on_ground = True
                        self.jump_count = 0
                        self.is_double_jumping = False
                        self.can_dash = True

        # ===== GROUND BUFFER =====
        if self.on_ground:
            self.ground_buffer = self.ground_buffer_time
        else:
            self.ground_buffer = max(0, self.ground_buffer - 1)

        grounded = self.ground_buffer > 0

        # ===== WALL SLIDE =====
        wall_sliding = (
            self.on_wall and not grounded
            and self.vel_y > 0
            and self.skills.wall_slide
            and self.dash_timer <= 0
        )

        if wall_sliding:
            self.vel_y = min(self.vel_y, 1.5)

        # ===== DASH TIMER =====
        if self.dash_timer > 0:
            self.dash_timer -= 1

        # ===== STATE MACHINE =====
        if self.dash_timer > 0:
            self.state = "dash"

        elif grounded:
            self.state = "run" if self.vel_x != 0 else "idle"

        elif wall_sliding:
            self.state = "slide"

        else:
            if self.is_double_jumping:
                self.state = "double"
            else:
                self.state = "jump" if self.vel_y < 0 else "fall"

        # ===== ANIMATION UPDATE =====
        new_anim = self.animations[self.state]
        if new_anim != self.current_anim:
            self.current_anim = new_anim
            self.current_anim.reset()

        self.current_anim.update()

    # ====================================================
    def draw(self, surf):
        img = self.current_anim.get_image()
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        surf.blit(img, self.rect.topleft)
