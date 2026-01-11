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

# ================= WINDOW =================
BASE_W, BASE_H = 1280, 720
screen = pygame.display.set_mode((BASE_W, BASE_H), pygame.RESIZABLE)
pygame.display.set_caption("Code Fruit")

icon = pygame.image.load("assets/Background/Menu/Logo.png").convert_alpha()
pygame.display.set_icon(icon)

clock = pygame.time.Clock()
FPS = 60

fullscreen = False
windowed_size = (BASE_W, BASE_H)

# ================= INPUT MODE =================
INPUT_CONTROL = "control"
INPUT_CODE = "code"
input_mode = INPUT_CONTROL

# ================= SAVE =================
save = SaveManager()

# ================= LEVEL MANAGER =================
level_manager = LevelManager(save)

saved_fruits = save.get_fruits()
level_manager.item_manager.import_data(saved_fruits)

# ================= CHARACTER =================
char_manager = CharacterManager(save, level_manager.item_manager)
char_select = CharacterSelect(char_manager, level_manager.item_manager)

# ================= STATE =================
state = GameState.MENU
next_state = None
next_level = None
last_codepanel_level = level_manager.current_level

# ================= UI =================
menu = MainMenu()
level_select = LevelSelect(save)

sound.play_music("assets/sounds/bgm.ogg")

# ================= WORLD =================
WORLD_W, WORLD_H = level_manager.map_w, level_manager.map_h
world = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)

# ================= HUD & PANELS =================
hud = HUD(level_manager.item_manager)

mission_panel = MissionPanel(
    screen.get_width(),
    level_manager.objective,
    hud.icons
)

code_panel = CodePanel(BASE_W, BASE_H)

transition = SquareTransition(screen.get_size())


# ================= DRAW WORLD =================
def draw_scaled_world():
    sw, sh = screen.get_size()
    scale = min(sw / WORLD_W, sh / WORLD_H)

    draw_w = int(WORLD_W * scale)
    draw_h = int(WORLD_H * scale)

    scaled = pygame.transform.scale(world, (draw_w, draw_h))
    x = (sw - draw_w) // 2
    y = (sh - draw_h) // 2

    screen.fill((0, 0, 0))
    screen.blit(scaled, (x, y))


# ================= MAIN LOOP =================
running = True
while running:
    dt = clock.tick(FPS) / 1000

    # ================= EVENTS =================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ===== RESIZE =====
        elif event.type == pygame.VIDEORESIZE and not fullscreen:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            transition.resize(event.size)
            level_select.on_resize(screen)
            code_panel.on_resize(*event.size)

        # ===== KEY =====
        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    windowed_size = screen.get_size()
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)

                transition.resize(screen.get_size())
                level_select.on_resize(screen)
                code_panel.on_resize(*screen.get_size())

            elif event.key == pygame.K_ESCAPE:
                # Đóng các bảng nếu đang mở
                if code_panel.opened:
                    code_panel.close()
                    input_mode = INPUT_CONTROL
                elif mission_panel.opened:
                    mission_panel.close()
                elif state == GameState.LEVEL_PLAY:
                    next_state = GameState.LEVEL_SELECT
                    transition.start_close()

        # ===== STATE EVENTS =====
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
                next_state = GameState.LEVEL_PLAY
                next_level = result
                transition.start_close()

        elif state == GameState.LEVEL_PLAY:
            hud.update(dt)
            action = hud.handle_event(event)

            mission_panel.handle_event(event)
            result = code_panel.handle_event(event)
            
            # Cập nhật chế độ nhập liệu nếu code panel mở
            if code_panel.opened:
                input_mode = INPUT_CODE

            # ===== RUN CODE =====
            if isinstance(result, list):
                level_manager.run_code(result)
                input_mode = INPUT_CONTROL # Trả quyền sau khi chạy

            if action == "HOME":
                next_state = GameState.MENU
                transition.start_close()

            elif action == "LEVEL":
                next_state = GameState.LEVEL_SELECT
                transition.start_close()

            elif action == "RESTART":
                next_state = GameState.LEVEL_PLAY
                next_level = level_manager.current_level
                transition.start_close()

            elif action == "TOGGLE_SOUND":
                if sound.enabled:
                    sound.mute()
                    hud.sound_on = False
                else:
                    sound.unmute()
                    hud.sound_on = True

    # ================= UPDATE =================
    if state == GameState.LEVEL_PLAY:

        if level_manager.current_level != last_codepanel_level:
            quest_path = f"data/quests/level_{level_manager.current_level}.json"
            code_panel.load_from_json(quest_path)
            code_panel.close()
            last_codepanel_level = level_manager.current_level

        # --- LOGIC FIX LỖI WIN+SPACE (QUAN TRỌNG) ---
        player_keys = None
        
        # Chỉ nhận phím khi:
        # 1. Đang ở chế độ điều khiển (CONTROL)
        # 2. Không mở Code Panel
        # 3. Không mở Mission Panel
        # 4. Cửa sổ game đang được active (get_focused)
        is_input_allowed = (input_mode == INPUT_CONTROL) and \
                           (not code_panel.opened) and \
                           (not mission_panel.opened) and \
                           pygame.key.get_focused()

        if is_input_allowed:
            player_keys = pygame.key.get_pressed()
        
        # Gửi phím (hoặc None) vào level manager
        level_manager.update(dt, player_keys)
        # --------------------------------------------

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

    # ================= STATE SWITCH =================
    if transition.is_closed() and next_state:
        state = next_state

        if state == GameState.LEVEL_PLAY and next_level:
            level_manager.load_level(next_level)

            WORLD_W, WORLD_H = level_manager.map_w, level_manager.map_h
            world = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)

            hud = HUD(level_manager.item_manager)
            mission_panel = MissionPanel(
                screen.get_width(),
                level_manager.objective,
                hud.icons
            )
            mission_panel.open()

            quest_path = f"data/quests/level_{next_level}.json"
            code_panel.load_from_json(quest_path)
            code_panel.close()

            next_level = None

        next_state = None
        transition.start_open()

    # ================= DRAW =================
    if state == GameState.MENU:
        menu.draw(screen, dt)

    elif state == GameState.CHARACTER_SELECT:
        screen.fill((20, 20, 25))
        char_select.draw(screen)

    elif state == GameState.LEVEL_SELECT:
        level_select.update(dt)
        level_select.draw(screen, dt)

    elif state == GameState.LEVEL_PLAY:
        world.fill((20, 20, 25))
        level_manager.draw(world)
        draw_scaled_world()

        hud.draw(screen, dt)
        mission_panel.draw(screen)
        code_panel.draw(screen)
        code_panel.draw_hint_popup(screen)

    transition.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()