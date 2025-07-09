from pygrender import Game, pygame


class Doors(Game):
    def __init__(self) -> None:
        super().__init__(1920, 1080, fullscreen=True, player=True)
        pygame.display.set_caption("Doors")
        pygame.mouse.set_visible(0)

        self.load_assets({
            "lobby": "assets/backgrounds/new_lobby.png",
            "walk1": "assets/character/walk1.png",
            "walk2": "assets/character/walk2.png",
        })

        self.stage: int = 0
        self.keyevent_functions: dict[int, callable] = {
            pygame.K_ESCAPE: self.pause
        }

        self.player.animation_time_range = 100
        self.player.styles = ["walk1", "walk2"]
        self.player.x = 960
        self.player.y = 540

    def update(self) -> None:
        super().update()

        if not self.loading:
            self.stage = 1

    def draw(self) -> None:
        if self.stage == 1 and hasattr(self, "lobby"):
            self.screen.blit(self.lobby, (0, 0))
            self.stage = 2

        super().draw()

    def pause(self) -> None:
        """Pause the game."""
        self.running = False
        print("Game paused. Press ESC to resume, Q to quit.")

        font = pygame.font.SysFont(None, 72)
        text_surface = font.render("Game paused. Press ESC to resume, Q to quit.", True, (255, 255, 255))  # noqa: E501
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))  # noqa: E501
        self.screen.blit(text_surface, text_rect)

        pygame.display.flip()

        while not self.running:
            self.pauseScreen()

    def pauseScreen(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = True
                    print("Game resumed.")

                elif event.key == pygame.K_q:
                    self.quit()
                    break

        pygame.display.flip()


if __name__ == "__main__":
    game = Doors()
    game.run()
