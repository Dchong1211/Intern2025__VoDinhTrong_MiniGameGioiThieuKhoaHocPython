# player/player.py

import pygame
from player.animation import Animation
from player.skills import Skills

GRAVITY = 1800

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, anim_data):
        super().__init__()

        # position & physics
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_right = True

        # skills
        self.skills = Skills()
        self.can_double_jump = True

        # animation set truyền vào từ main
        self.animations = anim_data  
        self.current_anim = "idle"

        # first frame = default image
        self.image = self.animations[self.current_anim].get_image()
        self.rect = self.image.get_rect(topleft=(x, y))

    # --------------------------------------------------
    # Animation handler
    # --------------------------------------------------
    def set_anim(self, name):
        if self.current_anim != name:
            self.current_anim = name
            self.animations[name].reset()

    # --------------------------------------------------
    # Input
    # --------------------------------------------------
    def handle_input(self, keys):
        self.vx = 0

        # Move
        if self.skills.move:
            if keys[pygame.K_a]:
                self.vx = -250
                self.facing_right = False
            if keys[pygame.K_d]:
                self.vx = 250
                self.facing_right = True

        # Jump + Double Jump
        if keys[pygame.K_SPACE]:
            if self.on_ground and self.skills.jump:
                self.vy = -650
                self.on_ground = False
                self.can_double_jump = True

            elif not self.on_ground and self.skills.double_jump and self.can_double_jump:
                self.vy = -650
                self.can_double_jump = False

        # Dash
        if keys[pygame.K_LSHIFT] and self.skills.dash:
            dash_speed = 450
            self.vx = dash_speed if self.facing_right else -dash_speed
            self.set_anim("dash")

        # Attack
        if keys[pygame.K_j] and self.skills.attack:
            self.set_anim("attack")

    # --------------------------------------------------
    # Physics update
    # --------------------------------------------------
    def update(self, dt, tiles, keys):
        self.handle_input(keys)

        # gravity
        if not self.on_ground:
            self.vy += GRAVITY * dt

        # apply movement
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.topleft = (self.x, self.y)

        # collision
        self.on_ground = False
        for t in tiles:
            if self.rect.colliderect(t):

                # vertical
                if self.vy > 0:
                    self.rect.bottom = t.top
                    self.y = self.rect.y
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = t.bottom
                    self.y = self.rect.y
                    self.vy = 0

                # horizontal
                if self.vx > 0:
                    self.rect.right = t.left
                    self.x = self.rect.x
                elif self.vx < 0:
                    self.rect.left = t.right
                    self.x = self.rect.x

        # select animation
        if not self.on_ground:
            self.set_anim("jump")
        elif self.vx != 0:
            self.set_anim("run")
        else:
            self.set_anim("idle")

        # update anim frame
        anim = self.animations[self.current_anim]
        anim.update()

        img = anim.get_image()
        self.image = img if self.facing_right else pygame.transform.flip(img, True, False)
