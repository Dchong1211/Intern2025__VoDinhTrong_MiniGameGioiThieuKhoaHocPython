import sys
import pygame

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
# Kích thước mặc định lúc mở game
DEFAULT_GAME_W, DEFAULT_GAME_H = 960, 540
PANEL_W = 400 
BASE_W = DEFAULT_GAME_W + PANEL_W 
BASE_H = DEFAULT_GAME_H

screen = pygame.display.set_mode((BASE_W, BASE_H), pygame.RESIZABLE)
pygame.display.set_caption("Code Fruit")

icon = pygame.image.load("assets/Background/Menu/Logo.png").convert_alpha()
pygame.display.set_icon(icon)

clock = pygame.time.Clock()
FPS = 60

fullscreen = False
windowed_size = (BASE_W, BASE_H)

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
last_codepanel_level = level_manager.current_level

# ================= UI ELEMENTS =================
menu = MainMenu()
level_select = LevelSelect(save)

sound.play_music("assets/sounds/bgm.ogg")

# World Surface (Vẽ map game)
WORLD_W, WORLD_H = level_manager.map_w, level_manager.map_h
world = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)

# HUD & Panels
hud = HUD(level_manager.item_manager)

# Mission Panel
mission_panel = MissionPanel(
    DEFAULT_GAME_W, # Chiều rộng vùng game ban đầu
    level_manager.objective,
    hud.icons
)

# Code Panel (Khởi tạo nằm bên phải)
code_panel = CodePanel(x_pos=BASE_W - PANEL_W, width=PANEL_W, height=BASE_H)

transition = SquareTransition(screen.get_size())

# ================= HELPER FUNCTIONS =================

def handle_resize(w, h):
    """Hàm xử lý logic khi thay đổi kích thước màn hình (gọi chung cho Resize và F11)"""
    global screen
    
    # 1. Cập nhật Screen
    if fullscreen:
        screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)

    # 2. Cập nhật các thành phần UI
    transition.resize((w, h))
    level_select.on_resize(screen)
    
    # 3. Cập nhật Code Panel (QUAN TRỌNG: Phải truyền đúng kích thước màn hình mới)
    # CodePanel tự tính toán lại vị trí dựa trên width mới truyền vào
    code_panel.on_resize(w, h)
    
    # 4. Cập nhật Mission Panel 
    # (Để nút bấm nhận diện đúng toạ độ mới sau khi scale)
    if hasattr(mission_panel, 'on_resize'):
        # Tính toán chiều rộng khả dụng cho game view (trừ đi phần panel)
        available_game_w = w - PANEL_W
        mission_panel.on_resize(available_game_w, h)

def draw_game_view():
    """Vẽ vùng game vào phần bên trái màn hình, tự động căn giữa"""
    sw, sh = screen.get_size()
    
    # Tính toán vùng trống bên trái (trừ đi Code Panel)
    available_w = sw - PANEL_W
    
    # Logic giữ tỷ lệ khung hình (Aspect Ratio) cho map
    target_h = sh
    target_w = int(target_h * (WORLD_W / WORLD_H))
    
    # Nếu map quá rộng so với vùng trống, scale theo chiều ngang
    if target_w > available_w:
        target_w = int(available_w)
        target_h = int(target_w * (WORLD_H / WORLD_W))

    # Scale map từ world surface
    scaled = pygame.transform.scale(world, (target_w, target_h))
    
    # Vẽ Background đệm (màu tối) cho vùng Game View
    # Dùng rect để fill đúng vùng bên trái, tránh bị lem màu khi resize
    game_view_rect = pygame.Rect(0, 0, available_w, sh)
    pygame.draw.rect(screen, (20, 20, 25), game_view_rect)
    
    # Tính toạ độ để vẽ Map căn giữa trong vùng Game View
    draw_x = (available_w - target_w) // 2
    draw_y = (sh - target_h) // 2
    
    screen.blit(scaled, (draw_x, draw_y))

# ================= MAIN LOOP =================
running = True
while running:
    dt = clock.tick(FPS) / 1000

    # ================= EVENTS =================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ----- Xử lý Resize -----
        elif event.type == pygame.VIDEORESIZE and not fullscreen:
            windowed_size = event.size
            handle_resize(*event.size)

        # ----- Xử lý Fullscreen (F11) -----
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    # Lấy độ phân giải màn hình hiện tại
                    info = pygame.display.Info()
                    handle_resize(info.current_w, info.current_h)
                else:
                    # Trở về kích thước cửa sổ cũ
                    handle_resize(*windowed_size)

        # ----- Xử lý Input theo State -----
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

        elif state == GameState.LEVEL_CODE:
            result = code_panel.handle_event(event)
            
            if isinstance(result, list):
                level_manager.run_code(result)
                state = GameState.LEVEL_PLAY 
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    next_state = GameState.LEVEL_SELECT
                    transition.start_close()

        # ----- PHASE 2: LEVEL PLAY (SỬA LỖI NHẬP CODE) -----
        elif state == GameState.LEVEL_PLAY:
            # 1. Kiểm tra vị trí chuột xem có đang nằm bên Code Panel không
            mouse_pos = pygame.mouse.get_pos()
            # PANEL_W là chiều rộng panel bên phải. 
            # Nếu x > (Tổng chiều rộng - Chiều rộng panel) => Chuột đang ở bên phải
            is_hovering_panel = mouse_pos[0] > (screen.get_width() - PANEL_W)
            
            # --- LOGIC ƯU TIÊN CODE PANEL ---
            if is_hovering_panel:
                # Nếu chuột đang ở bên Panel, truyền event thẳng cho Panel xử lý
                # Điều này giúp Textbox nhận được sự kiện click và focus
                panel_res = code_panel.handle_event(event)
                
                # Nếu người dùng nhấn chuột xuống vùng này
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Chuyển ngay sang trạng thái CODE
                    state = GameState.LEVEL_CODE
                    
                    # (Tùy chọn) Xóa phím di chuyển đang giữ để nhân vật đứng lại
                    level_manager.update(dt, None) 
            
            # --- LOGIC GAMEPLAY (Nếu không đụng vào Panel) ---
            else:
                # Chỉ xử lý HUD và Mission khi chuột KHÔNG ở bên Panel
                action = hud.handle_event(event)
                mission_panel.handle_event(event)

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

            # Phím tắt chung
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = GameState.LEVEL_CODE

    # ================= UPDATE & LOGIC =================
    if state in (GameState.LEVEL_CODE, GameState.LEVEL_PLAY):
        # Load quest data nếu đổi level
        if level_manager.current_level != last_codepanel_level:
            quest_path = f"data/quests/level_{level_manager.current_level}.json"
            code_panel.load_from_json(quest_path)
            last_codepanel_level = level_manager.current_level

        player_keys = None
        if state == GameState.LEVEL_PLAY:
            if pygame.key.get_focused():
                player_keys = pygame.key.get_pressed()
        
        level_manager.update(dt, player_keys)
        mission_panel.update(dt)
        code_panel.update(dt)

        # Logic chuyển cảnh từ Level Manager
        if level_manager.request_go_home:
            next_state = GameState.MENU
            transition.start_close()
            level_manager.request_go_home = False

        if level_manager.request_go_level_select:
            next_state = GameState.LEVEL_SELECT
            transition.start_close()
            level_manager.request_go_level_select = False

    transition.update(dt)

    # ================= STATE SWITCHING =================
    if transition.is_closed() and next_state:
        state = next_state

        if (state == GameState.LEVEL_CODE or state == GameState.LEVEL_PLAY) and next_level:
            level_manager.load_level(next_level)
            
            # Cập nhật kích thước World theo level mới
            WORLD_W, WORLD_H = level_manager.map_w, level_manager.map_h
            world = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)

            # Reset HUD và Mission
            hud = HUD(level_manager.item_manager)
            mission_panel = MissionPanel(
                screen.get_width() - PANEL_W, # Khởi tạo với width hiện tại
                level_manager.objective, 
                hud.icons
            )
            mission_panel.open()

            quest_path = f"data/quests/level_{next_level}.json"
            code_panel.load_from_json(quest_path)
            last_codepanel_level = next_level
            
            state = GameState.LEVEL_CODE 
            next_level = None

        next_state = None
        transition.start_open()

    # ================= DRAW =================
    # Xoá màn hình trước khi vẽ để tránh lỗi chồng hình khi resize
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
        
        # 1. Vẽ Game View (Map)
        draw_game_view() 
        
        # 2. Vẽ UI Game (Truyền width của Panel để HUD biết đường né)
        hud.draw(screen, dt, right_margin=PANEL_W)
        mission_panel.draw(screen)

        # 3. Vẽ Code Panel (Luôn nằm đè lên bên phải)
        code_panel.draw(screen)
        code_panel.draw_hint_popup(screen)

    transition.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()