import pygame
import os

class Checkpoint:
    SIZE = 64

    # Các trạng thái của Checkpoint
    STATE_IDLE = "IDLE"           # Chưa làm gì (Cờ chưa lên)
    STATE_WAIT = "WAIT"           # Đang mở bảng nhiệm vụ (người chơi chạm vào nhưng chưa đủ quả)
    STATE_ACTIVATING = "ACTIVATING" # Đang kéo cờ lên (Animation)
    STATE_ACTIVE = "ACTIVE"       # Cờ đã bay phấp phới (Đã qua màn)

    def __init__(self, x, y):
        # Tạo khung va chạm
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)

        base = "assets/Checkpoints/Checkpoint"

        # Load hình ảnh
        # 1. Hình cột cờ trống
        self.no_flag = pygame.image.load(
            os.path.join(base, "Checkpoint (No Flag).png")
        ).convert_alpha()

        # 2. Animation cờ bay (Idle)
        self.idle_frames = self._load_sheet(
            os.path.join(base, "Checkpoint (Flag Idle)(64x64).png")
        )

        # 3. Animation kéo cờ lên (Activate)
        self.activate_frames = self._load_sheet(
            os.path.join(base, "Checkpoint (Flag Out)(64x64).png")
        )

        # ===== STATE & VARS =====
        self.state = self.STATE_IDLE

        self.frames = self.idle_frames
        self.frame_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.08

        self.ready = False          # True nếu đã đủ điều kiện qua màn
        self.active = False         # True nếu cờ đã được kích hoạt hoàn toàn
        self.waiting_quest = False  # True nếu đang hiển thị bảng nhiệm vụ
        self._finished = False      # True nếu animation kết thúc
        self.player_inside = False  # Trạng thái người chơi đang đứng trong vùng cờ
        self.pending_next_level = False # Cờ hiệu báo chuyển màn

    # ==================================================
    # HELPER: CẮT ẢNH TỪ SPRITESHEET
    # ==================================================
    def _load_sheet(self, path):
        if not os.path.exists(path):
            print(f"[ERROR] Checkpoint image not found: {path}")
            # Trả về mảng chứa 1 surface rỗng để tránh crash
            return [pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)]

        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        sheet_w = sheet.get_width()
        
        # Cắt theo chiều ngang, mỗi khung hình kích thước SIZE x SIZE
        for x in range(0, sheet_w, self.SIZE):
            frame = sheet.subsurface((x, 0, self.SIZE, self.SIZE))
            frames.append(frame)

        return frames

    # ==================================================
    # PUBLIC API (GỌI TỪ LEVEL MANAGER)
    # ==================================================
    
    def on_player_touch(self, quest_panel):
        """
        Được gọi khi người chơi chạm vào Checkpoint nhưng chưa đủ điều kiện qua màn.
        Mục đích: Mở bảng nhiệm vụ để nhắc nhở.
        """
        # Nếu đã qua màn (active) hoặc đang hiện bảng (waiting_quest) thì không làm gì thêm
        if self.active or self.waiting_quest:
            return

        # --- ĐÃ SỬA Ở ĐÂY ---
        # Bỏ điều kiện "if not self.ready return" để cho phép mở bảng kể cả khi chưa ready
        
        self.waiting_quest = True
        self.state = self.STATE_WAIT
        quest_panel.open()

    def activate(self):
        """Kích hoạt animation kéo cờ lên (Chiến thắng)"""
        if self.active:
            return

        self.active = True
        self.ready = True
        self.waiting_quest = False # Đóng chế độ chờ nhiệm vụ nếu lỡ đang mở

        self.state = self.STATE_ACTIVATING
        self.frames = self.activate_frames
        self.frame_index = 0
        self.anim_timer = 0.0
        self._finished = False
        self.pending_next_level = True

    def force_active(self):
        """Kích hoạt ngay lập tức (Dùng khi load lại màn đã chơi rồi)"""
        self.active = True
        self.ready = True
        self.waiting_quest = False

        self.state = self.STATE_ACTIVE
        self.frames = self.idle_frames
        self.frame_index = 0
        self.anim_timer = 0.0
        self._finished = True

    def animation_finished(self):
        return self._finished

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self, dt):
        # 1. Trạng thái đang kéo cờ lên
        if self.state == self.STATE_ACTIVATING:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index += 1

                # Nếu chạy hết frame animation kéo cờ
                if self.frame_index >= len(self.frames):
                    # Chuyển sang trạng thái cờ bay (Idle)
                    self.state = self.STATE_ACTIVE
                    self.frames = self.idle_frames
                    self.frame_index = 0
                    self._finished = True

                    # Gửi sự kiện chuyển màn (nếu cần dùng event system)
                    if self.pending_next_level:
                        self.pending_next_level = False
                        pygame.event.post(
                            pygame.event.Event(
                                pygame.USEREVENT, 
                                {"action": "NEXT_LEVEL"}
                            )
                        )

        # 2. Trạng thái cờ đang bay (Active)
        elif self.state == self.STATE_ACTIVE:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self, surf):
        # Nếu chưa kích hoạt hoặc đang chờ xem nhiệm vụ -> Vẽ cột cờ không cờ
        if self.state in (self.STATE_IDLE, self.STATE_WAIT):
            surf.blit(self.no_flag, self.rect.topleft)
        
        # Nếu đang kích hoạt hoặc đã xong -> Vẽ animation
        else:
            # Kiểm tra an toàn để không bị lỗi index out of range
            if self.frame_index < len(self.frames):
                surf.blit(self.frames[self.frame_index], self.rect.topleft)