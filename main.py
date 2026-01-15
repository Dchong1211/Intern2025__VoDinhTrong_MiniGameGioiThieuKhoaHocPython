import sys
import pygame
import traceback

from data.save_manager import SaveManager
from level.level_manager import LevelManager

from characters.character_manager import CharacterManager
from characters.character_select import CharacterSelect

from ui.game_state import GameState
from ui.main_menu import MainMenu
from ui.level_select import LevelSelect
from ui.hud import HUD
from ui.mission_panel import MissionPanel
from ui.square_transition import SquareTransition
from ui.code_panel import CodePanel

from audio.sound_manager import SoundManager

# ================= INIT =================
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

sound = SoundManager()

# ================= CONFIG =================
BASE_W = 1280
BASE_H = 720
PANEL_W = 320 # Chiều rộng của bảng code

screen = pygame.display.set_mode((BASE_W, BASE_H), pygame.RESIZABLE)
pygame.display.set_caption("Code Fruit")

icon = pygame.image.load("assets/Background/Menu/Logo.png").convert_alpha()
pygame.display.set_icon(icon)

clock = pygame.time.Clock()
FPS = 60

fullscreen = False
windowed_size = (BASE_W, BASE_H)

# ================= COMMAND CLASSES =================
class CmdMove:
    def __init__(self, direction):
        self.direction = direction
        self.target_x = 0

    def start(self, player):
        player.facing_right = (self.direction == 1)
        player.vel_x = player.speed * self.direction
        current_grid = round(player.rect.x / 32)
        self.target_x = (current_grid + self.direction) * 32

    def update(self, player):
        if (self.direction == 1 and player.rect.x >= self.target_x) or \
           (self.direction == -1 and player.rect.x <= self.target_x):
            player.rect.x = self.target_x
            player.vel_x = 0
            return True
        return False

class CmdJump:
    def start(self, player):
        if player.on_ground or (player.skills.has("double_jump") and player.jump_count < 2):
            player.vel_y = player.jump_force
            player.jump_count += 1
            player.on_ground = False

    def update(self, player):
        return True

# ================= DATA =================
save = SaveManager()

# ================= MANAGERS =================
level_manager = LevelManager(save)
saved_fruits = save.get_fruits()
level_manager.item_manager.import_data(saved_fruits)

char_manager = CharacterManager(save, level_manager.item_manager)
char_select = CharacterSelect(char_manager, level_manager.item_manager)

# ================= STATE =================
state = GameState.MENU
next_state = None
next_level = None
last_codepanel_level = -1 # Biến để kiểm tra xem đã load code cho level chưa

# ================= UI ELEMENTS =================
menu = MainMenu()
level_select = LevelSelect(save)

sound.play_music("assets/sounds/bgm.ogg")

# World Surface
WORLD_W, WORLD_H = level_manager.map_w, level_manager.map_h
world = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)

# HUD & Panels
hud = HUD(level_manager.item_manager)

# --- FIX VỊ TRÍ PANEL (Game Trái - Code Phải) ---
mission_panel = MissionPanel(0, level_manager.objective, hud.icons)
code_panel = CodePanel(x_pos=BASE_W - PANEL_W, width=PANEL_W, height=BASE_H)

transition = SquareTransition(screen.get_size())

# ================= HELPER FUNCTIONS =================

def handle_resize(w, h):
    global screen
    if fullscreen:
        screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)

    transition.resize((w, h))
    level_select.on_resize(screen)
    
    # Cập nhật vị trí Code Panel luôn nằm bên phải
    code_panel.on_resize(w, h)
    
    # Mission Panel giữ nguyên vị trí, chỉ cập nhật kích thước game nếu cần
    if hasattr(mission_panel, 'on_resize'):
        available_game_w = w - PANEL_W
        mission_panel.on_resize(available_game_w, h)

def draw_game_view():
    sw, sh = screen.get_size()
    
    # Khu vực hiển thị game: Từ 0 đến (Screen Width - Panel Width)
    available_w = sw - PANEL_W
    
    target_h = sh
    target_w = int(target_h * (WORLD_W / WORLD_H))
    
    if target_w > available_w:
        target_w = int(available_w)
        target_h = int(target_w * (WORLD_H / WORLD_W))

    scaled = pygame.transform.scale(world, (target_w, target_h))
    
    # Vẽ nền đen cho khu vực game (Bên TRÁI)
    game_view_rect = pygame.Rect(0, 0, available_w, sh)
    pygame.draw.rect(screen, (20, 20, 25), game_view_rect)
    
    # Căn giữa game trong khu vực bên trái
    draw_x = (available_w - target_w) // 2
    draw_y = (sh - target_h) // 2
    
    screen.blit(scaled, (draw_x, draw_y))

# ================= MAIN LOOP =================
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE and not fullscreen:
            windowed_size = event.size
            handle_resize(*event.size)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    info = pygame.display.Info()
                    handle_resize(info.current_w, info.current_h)
                else:
                    handle_resize(*windowed_size)

        # ----- STATE HANDLING -----
        if state == GameState.MENU:
            result = menu.handle_event(event, screen)
            if result == "PLAY" and not transition.is_active():
                sound.play_sfx("click")
                next_state = GameState.LEVEL_SELECT
                transition.start_close()

        elif state == GameState.CHARACTER_SELECT:
            char_select.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                next_state = GameState.LEVEL_SELECT
                transition.start_close()

        elif state == GameState.LEVEL_SELECT:
            result = level_select.handle_event(event, screen)
            if result == "BACK" and not transition.is_active():
                next_state = GameState.MENU
                transition.start_close()
            elif result == "CHARACTER" and not transition.is_active():
                next_state = GameState.CHARACTER_SELECT
                transition.start_close()
            elif isinstance(result, int) and not transition.is_active():
                next_state = GameState.LEVEL_CODE
                next_level = result
                transition.start_close()
        # ----- LEVEL CODE -----
        elif state == GameState.LEVEL_CODE:
            # 1. Check Mission Panel (nút đóng mở nhiệm vụ)
            if mission_panel.handle_event(event):
                pass 
            else:
                # 2. Check Code Panel
                result = code_panel.handle_event(event)
                
                # Nếu Code Panel trả về danh sách lệnh -> Chạy Code
                if isinstance(result, list): 
                    print("--- START CODE ---")
                    player = level_manager.player
                    player.reset_code_state()
                    
                    def api_move_right(steps=1):
                        for _ in range(steps): player.enqueue_command(CmdMove(1))
                    def api_move_left(steps=1):
                        for _ in range(steps): player.enqueue_command(CmdMove(-1))
                    def api_jump():
                        player.enqueue_command(CmdJump())

                    execution_env = {
                        "move_right": api_move_right,
                        "move_left": api_move_left,
                        "jump": api_jump,
                        "range": range,
                        "print": print
                    }
                    
                    code_str = "\n".join(result)
                    try:
                        exec(code_str, {}, execution_env)
                        state = GameState.LEVEL_PLAY 
                    except Exception as e:
                        print(f"Error executing code: {e}")
                        traceback.print_exc()
                
                # 3. QUAN TRỌNG: Nếu không click vào Code Panel, kiểm tra HUD (Nút Setting)
                elif result is None:
                    action = hud.handle_event(event)
                    if action == "HOME":
                        next_state = GameState.MENU
                        transition.start_close()
                    elif action == "LEVEL":
                        next_state = GameState.LEVEL_SELECT
                        transition.start_close()
                    elif action == "RESTART":
                        next_level = level_manager.current_level
                        transition.start_close()
                    elif action == "TOGGLE_SOUND":
                        if sound.enabled: sound.mute(); hud.sound_on = False
                        else: sound.unmute(); hud.sound_on = True

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                next_state = GameState.LEVEL_SELECT
                transition.start_close()
        # ----- LEVEL PLAY -----
        elif state == GameState.LEVEL_PLAY:
            mission_panel.handle_event(event)
            mouse_pos = pygame.mouse.get_pos()
            
            # Kiểm tra chuột có nằm bên Phải (Code Panel) hay không
            is_hovering_panel = mouse_pos[0] > (screen.get_width() - PANEL_W)
            
            if is_hovering_panel:
                panel_res = code_panel.handle_event(event)
                # Chỉ chuyển về chế độ soạn thảo (Code) khi click chuột VÀ
                # Level hiện tại KHÔNG phải là chế độ Keyboard
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if code_panel.control_mode != "keyboard":
                        state = GameState.LEVEL_CODE
                        level_manager.player.reset_code_state()
            else:
                action = hud.handle_event(event)
                if action == "HOME":
                    next_state = GameState.MENU
                    transition.start_close()
                elif action == "LEVEL":
                    next_state = GameState.LEVEL_SELECT
                    transition.start_close()
                elif action == "RESTART":
                    next_state = GameState.LEVEL_CODE
                    next_level = level_manager.current_level
                    transition.start_close()
                elif action == "TOGGLE_SOUND":
                    if sound.enabled: sound.mute(); hud.sound_on = False
                    else: sound.unmute(); hud.sound_on = True

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Nếu là level keyboard, ESC sẽ về menu chọn level, nếu là level code thì về soạn code
                if code_panel.control_mode == "keyboard":
                    next_state = GameState.LEVEL_SELECT
                    transition.start_close()
                else:
                    state = GameState.LEVEL_CODE
                    level_manager.player.reset_code_state()

    # ================= UPDATE =================
    if state in (GameState.LEVEL_CODE, GameState.LEVEL_PLAY):
        # [FIX] Tự động load code khi vào level mới nếu chưa load
        if level_manager.current_level != last_codepanel_level:
            code_panel.load_level(level_manager.current_level) 
            last_codepanel_level = level_manager.current_level

        player_keys = None
        # Chỉ nhận phím điều khiển nếu đang chơi (Play) và Code không đang chạy (code_active = False)
        if state == GameState.LEVEL_PLAY and not level_manager.player.code_active:
            # === [FIX] QUAN TRỌNG: Chỉ nhận phím nếu control_mode là "keyboard" ===
            if code_panel.control_mode == "keyboard":
                if pygame.key.get_focused():
                    player_keys = pygame.key.get_pressed()
        
        level_manager.update(dt, player_keys)
        mission_panel.update(dt)
        code_panel.update(dt)

        if level_manager.request_go_home:
            next_state = GameState.MENU
            transition.start_close()
            level_manager.request_go_home = False
        if level_manager.request_go_level_select:
            next_state = GameState.LEVEL_SELECT
            transition.start_close()
            level_manager.request_go_level_select = False

    transition.update(dt)

    if transition.is_closed() and next_state:
        state = next_state
        if (state == GameState.LEVEL_CODE or state == GameState.LEVEL_PLAY) and next_level:
            level_manager.load_level(next_level)
            WORLD_W, WORLD_H = level_manager.map_w, level_manager.map_h
            world = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)

            hud = HUD(level_manager.item_manager)
            
            # Reset Mission Panel
            mission_panel = MissionPanel(0, level_manager.objective, hud.icons)
            mission_panel.open()

            # [FIX] Load level code khi chuyển màn bằng Transition
            code_panel.load_level(next_level)
            last_codepanel_level = next_level
            
            # --- [FIX QUAN TRỌNG] Tự động set trạng thái PLAY nếu là Keyboard level ---
            if code_panel.control_mode == "keyboard":
                state = GameState.LEVEL_PLAY
            else:
                state = GameState.LEVEL_CODE
            # --------------------------------------------------------------------------
            
            next_level = None
        next_state = None
        transition.start_open()

    # ================= DRAW =================
    screen.fill((0, 0, 0))

    if state == GameState.MENU:
        menu.draw(screen, dt)
    elif state == GameState.CHARACTER_SELECT:
        screen.fill((20, 20, 25))
        char_select.draw(screen)
    elif state == GameState.LEVEL_SELECT:
        level_select.update(dt)
        level_select.draw(screen, dt)
    elif state in (GameState.LEVEL_CODE, GameState.LEVEL_PLAY):
        world.fill((20, 20, 25))
        level_manager.draw(world)
        
        draw_game_view() # Vẽ Game bên TRÁI
        
        # Vẽ HUD và Mission
        hud.draw(screen, dt, right_margin=PANEL_W)
        mission_panel.draw(screen)
        
        code_panel.draw(screen) # Vẽ Code Panel bên PHẢI
        code_panel.draw_hint_popup(screen)

    transition.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()