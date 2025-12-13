import pygame
from ui.button import Button

class MainMenu:
    def __init__(self):
        self.play_img = pygame.image.load(
            "assets/Menu/Buttons/Play.png"
        ).convert_alpha()

        sw, sh = pygame.display.get_surface().get_size()
        self.play_btn = Button(sw // 2, sh // 2, self.play_img)

    def update(self, screen):
        screen.fill((15, 15, 20))

        if self.play_btn.draw(screen):
            return "PLAY"

        return "MENU"
