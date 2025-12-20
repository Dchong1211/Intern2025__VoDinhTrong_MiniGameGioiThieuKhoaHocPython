import pygame


class EnemyBase(pygame.sprite.Sprite):
    GRAVITY = 0.8

    def __init__(self, x, y, config, behavior):
        super().__init__()

        self.name = config["name"]
        self.animations = config["animations"]
        self.state = "idle"

        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.12

        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.hp = config.get("hp", 1)
        self.damage = config.get("damage", 1)
        self.speed = config.get("speed", 1)

        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

        self.dead = False
        self.invincible = False
        self.inv_timer = 0

        self.behavior = behavior
        self.behavior.owner = self

    # ===============================
    def update(self, player, tiles):
        if self.dead:
            return

        self.behavior.update(player, tiles)
        self.apply_gravity(tiles)
        self.update_animation()

        if self.invincible:
            self.inv_timer -= 1
            if self.inv_timer <= 0:
                self.invincible = False

    # ===============================
    def apply_gravity(self, tiles):
        self.vel_y += self.GRAVITY
        self.rect.y += self.vel_y
        self.on_ground = False

        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vel_y > 0:
                    self.rect.bottom = tile.top
                    self.vel_y = 0
                    self.on_ground = True

    # ===============================
    def update_animation(self):
        frames = self.animations[self.state]
        self.anim_timer += self.anim_speed
        if self.anim_timer >= 1:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(frames)

        self.image = frames[self.frame_index]

    # ===============================
    def take_damage(self, dmg, stomp=False):
        if self.invincible:
            return

        self.hp -= dmg
        self.state = "hit"
        self.frame_index = 0

        if stomp:
            self.on_stomped()

        if self.hp <= 0:
            self.dead = True
            self.kill()
        else:
            self.invincible = True
            self.inv_timer = 20

    # ===============================
    def on_stomped(self):
        pass
