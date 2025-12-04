import pygame
import os
from .animation import Animation
from .skills import Skills


class Player:
    def __init__(self, x, y, base_dir):
        self.width, self.height = 32, 32
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.x, self.y = x, y

        # =================== LOAD ANIM =================== #
        def load(name):
            return pygame.image.load(
                os.path.join(base_dir, "assets/Main Characters/Virtual Guy", name)
            ).convert_alpha()

        self.animations = {
            "idle":   Animation(load("Idle.png"), 32, 32, 0.3),
            "run":    Animation(load("Run.png"), 32, 32, 0.3),
            "jump":   Animation(load("Jump.png"), 32, 32, 0.3),
            "double": Animation(load("Double Jump.png"), 32, 32, 0.3),
            "fall":   Animation(load("Fall.png"), 32, 32, 0.3),
            "slide":  Animation(load("Wall Slide.png"), 32, 32, 0.15),
            "dash":   Animation(load("Dash.png"), 32, 32, 0.2),
        }

        self.state = "idle"
        self.current_anim = self.animations[self.state]

        # ===== MOVEMENT =====
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 3

        # ===== GRAVITY =====
        self.gravity = 0.3
        self.max_fall_speed = 10

        # ===== JUMP =====
        self.jump_force = -6
        self.jump_key_down = False
        self.jump_count = 0
        self.max_jump = 2
        self.on_ground = False

        # ===== GROUND BUFFER =====
        self.ground_buffer = 0
        self.ground_buffer_time = 3

        # ===== WALL =====
        self.on_wall = False
        self.wall_dir = 0

        # ===== DASH =====
        self.dash_force = 15
        self.dash_time = 15
        self.dash_timer = 0
        self.can_dash = True
        self.dash_key_down = False

        # ===== SKILLS =====
        self.skills = Skills()
        self.facing_right = True

        # ===== FRAGMENT + PUZZLE SYSTEM =====
        self.init_fragment_system()

    # =================== INPUT =================== #
    def _handle_input(self, keys):
        self.vel_x = 0

        moving_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        moving_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]

        if moving_left and self.skills.move:
            self.vel_x = -self.speed
            self.facing_right = False
        elif moving_right and self.skills.move:
            self.vel_x = self.speed
            self.facing_right = True

        # ===== JUMP =====
        space_now = keys[pygame.K_SPACE]
        space_pressed = space_now and not self.jump_key_down

        if space_pressed:

            # wall jump
            if self.on_wall and not self.on_ground and self.skills.wall_jump:
                self.vel_y = self.jump_force
                self.vel_x = 7 * (-self.wall_dir)
                self.jump_count = 1

            else:
                # normal jump
                if self.jump_count == 0 and self.skills.jump:
                    self.vel_y = self.jump_force
                    self.jump_count = 1

                # double jump
                elif self.jump_count == 1 and self.skills.double_jump:
                    self.vel_y = self.jump_force
                    self.jump_count = 2

        self.jump_key_down = space_now

        # ===== DASH =====
        shift_now = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        shift_pressed = shift_now and not self.dash_key_down

        if shift_pressed and self.skills.dash and self.can_dash:
            if moving_left:
                self.vel_x = -self.dash_force
                self.vel_y = 0
                self.dash_timer = self.dash_time
                self.can_dash = False
            elif moving_right:
                self.vel_x = self.dash_force
                self.vel_y = 0
                self.dash_timer = self.dash_time
                self.can_dash = False

        self.dash_key_down = shift_now

    # =================== UPDATE PUBLIC =================== #
    def update(self, tiles, keys):
        """
        Hàm public, main chỉ cần gọi:
        player.update(level.collisions, keys)
        """
        self.tiles = tiles

        # input
        self._handle_input(keys)

        # DASH phase
        if self.dash_timer > 0:
            self._finish_dash()
            return

        # GRAVITY
        self.vel_y += self.gravity
        self.vel_y = min(self.vel_y, self.max_fall_speed)

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

        # ===== WALL SLIDE =====
        moving_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        moving_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        wall_sliding = False

        if (
            self.on_wall and not self.on_ground and self.skills.wall_slide and
            (
                (self.wall_dir == 1 and moving_right) or
                (self.wall_dir == -1 and moving_left)
            )
        ):
            if self.vel_y > 0:
                self.vel_y = min(self.vel_y, 1.5)
                wall_sliding = True
                self.state = "slide"

        # ===== MOVE Y =====
        self.rect.y += self.vel_y
        self.on_ground = False

        for t in tiles:
            if self.rect.colliderect(t):

                if self.vel_y > 0:  # landing
                    self.rect.bottom = t.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0
                    self.can_dash = True

                elif self.vel_y < 0:  # head hit
                    self.rect.top = t.bottom
                    self.vel_y = 0

        # ===== GROUND BUFFER =====
        if self.on_ground:
            self.ground_buffer = self.ground_buffer_time
        else:
            self.ground_buffer = max(0, self.ground_buffer - 1)

        really_on_ground = self.ground_buffer > 0

        # ===== STATE MACHINE =====
        if really_on_ground:
            self.state = "run" if self.vel_x != 0 else "idle"
        else:
            if not wall_sliding:
                if self.vel_y < 0:
                    self.state = "double" if self.jump_count == 2 else "jump"
                else:
                    self.state = "fall"

        self.current_anim = self.animations[self.state]
        self.current_anim.update()

        self.x, self.y = self.rect.x, self.rect.y

    # =================== DASH PHYSICS =================== #
    def _finish_dash(self):
        self.dash_timer -= 1
        self.rect.x += self.vel_x

        for t in self.tiles:
            if self.rect.colliderect(t):
                if self.vel_x > 0:
                    self.rect.right = t.left
                else:
                    self.rect.left = t.right

        self.state = "dash"
        self.current_anim = self.animations["dash"]
        self.current_anim.update()

        self.x, self.y = self.rect.x, self.rect.y

    # =================== DRAW =================== #
    def draw(self, surf, cam_x, cam_y):
        img = self.current_anim.get_image()

        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)

        surf.blit(img, (self.rect.x - cam_x, self.rect.y - cam_y))

    # ====================================================
    #      FRAGMENT + PUZZLE SYSTEM
    # ====================================================
    def init_fragment_system(self):
        # Lưu mảnh đã nhặt cho từng skill
        # vd: {
        #   "jump": {
        #       "count": 2,
        #       "req": 3,
        #       "rows": 1,
        #       "cols": 3,
        #       "pieces": {0, 2}
        #   }
        # }
        self.skill_fragments = {}
        # Skill đã mở
        self.unlocked_skills = set()
        # Skill đang chờ mở puzzle (tên skill)
        self.pending_puzzle = None

    def add_fragment(self, skill_name, required, index=None, rows=None, cols=None):
        """
        Được gọi từ Item.on_pick() khi item_type == 'fragment'
        """
        if not skill_name:
            return

        # tạo data mới nếu chưa có skill này
        if skill_name not in self.skill_fragments:
            self.skill_fragments[skill_name] = {
                "count": 0,
                "req": required,
                "rows": rows,
                "cols": cols,
                "pieces": set()
            }

        data = self.skill_fragments[skill_name]

        # cập nhật rows/cols/req nếu có truyền từ item
        if rows is not None:
            data["rows"] = rows
        if cols is not None:
            data["cols"] = cols
        if required is not None:
            data["req"] = required

        # lưu index mảnh (dùng cho puzzle)
        if index is not None:
            data["pieces"].add(index)

        # tăng đếm mảnh
        data["count"] += 1
        print(f"Nhặt mảnh {skill_name}: {data['count']}/{data['req']}")

        # đủ mảnh -> chờ ghép puzzle (không unlock trực tiếp)
        if data["count"] >= data["req"]:
            print(f"Đã đủ mảnh cho skill [{skill_name}] → chờ ghép puzzle")
            self.pending_puzzle = skill_name

    def unlock_skill(self, skill_name):
        """
        Gọi khi ghép puzzle xong (PuzzleUI gọi hàm này)
        """
        if not skill_name:
            return

        if skill_name in self.unlocked_skills:
            return

        self.unlocked_skills.add(skill_name)
        print(f"*** UNLOCK SKILL [{skill_name}] ***")

        # map tên skill sang flags trong self.skills
        if skill_name == "jump":
            self.skills.jump = True
        elif skill_name == "double_jump":
            self.skills.double_jump = True
        elif skill_name == "dash":
            self.skills.dash = True
        elif skill_name == "wall_jump":
            self.skills.wall_jump = True
        elif skill_name == "wall_slide":
            self.skills.wall_slide = True
        elif skill_name == "move":
            self.skills.move = True

        # tắt pending puzzle sau khi mở
        self.pending_puzzle = None
