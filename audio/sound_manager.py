import pygame
import os


class SoundManager:
    def __init__(self):
        # ===== STATE =====
        self.enabled = True
        self.current_music = None

        # ===== VOLUME =====
        self.music_volume = 0.4
        self.sfx_volume = 0.6

        # ===== SFX STORAGE =====
        self.sfx = {}

        # preload sfx
        self._load_sfx("click", "assets/sounds/button_click.wav")

    # ================= LOAD SFX =================
    def _load_sfx(self, name, path):
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.sfx_volume)
            self.sfx[name] = sound
        else:
            print(f"[SoundManager] SFX not found: {path}")

    # ================= MUSIC =================
    def play_music(self, path, loop=True, fade_ms=1500):
        if not self.enabled:
            return

        if self.current_music == path:
            return

        if not os.path.exists(path):
            print(f"[SoundManager] Music not found: {path}")
            return

        self.current_music = path
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms)

    def stop_music(self, fade_ms=1000):
        pygame.mixer.music.fadeout(fade_ms)
        self.current_music = None

    def pause_music(self):
        pygame.mixer.music.pause()

    def resume_music(self):
        pygame.mixer.music.unpause()

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    # ================= SFX =================
    def play_sfx(self, name):
        if not self.enabled:
            return

        sfx = self.sfx.get(name)
        if sfx:
            sfx.play()

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for s in self.sfx.values():
            s.set_volume(self.sfx_volume)

    # ================= GLOBAL =================
    def mute(self):
        self.enabled = False
        pygame.mixer.music.set_volume(0)

    def unmute(self):
        self.enabled = True
        pygame.mixer.music.set_volume(self.music_volume)

        if not pygame.mixer.music.get_busy() and self.current_music:
            pygame.mixer.music.load(self.current_music)
            pygame.mixer.music.play(-1)

    def is_enabled(self):
        return self.enabled
