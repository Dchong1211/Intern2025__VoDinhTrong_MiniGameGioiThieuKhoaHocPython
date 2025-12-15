        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                screen = pygame.display.set_mode(
                    (0, 0), pygame.FULLSCREEN
                ) if fullscreen else pygame.display.set_mode(
                    (BASE_W, BASE_H), pygame.RESIZABLE
                )

            elif event.key == pygame.K_j:
                hud.show_objectives = not hud.show_objectives
