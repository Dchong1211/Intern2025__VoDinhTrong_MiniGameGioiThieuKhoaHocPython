import pygame
import os

class SoundManager:
    def __init__(self):
        self.music_volume = 0.4
        self.sfx_volume = 0.5
        self.current_music = None
        self.enabled = True

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
