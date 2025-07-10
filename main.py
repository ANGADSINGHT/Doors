import sys
import os

try:
    from pygrender import Game, pygame
    from tkinter import messagebox
    from scipy.ndimage import gaussian_filter
    import numpy as np
except ImportError as e:
    print(f"[PYGRender] [Error] Import failed: {e}")
    print("[PYGRender] [Info] Attempting to install required packages...")

    os.system("pip install pygame tkinter numpy noise")

    from pygrender import Game, pygame
    from tkinter import messagebox


class FNAV(Game):
    def __init__(self) -> None:
        super().__init__(1920, 1080, fullscreen=True, player=True)
        pygame.display.set_caption("Five Nights at Vinny's")
        pygame.mouse.set_visible(0)

        PSF: int = 1.3  # Scale factor for assets

        self.load_assets({
            "lobby": "assets/backgrounds/new_lobby.png",
            "walk1": "assets/character/walk1.png",
            "walk2": "assets/character/walk2.png",
            "walk3": "assets/character/walk3.png",
            "down1": "assets/character/back1.png",
            "down2": "assets/character/back2.png",
            "left1": "assets/character/left1.png",
            "left2": "assets/character/left2.png",
            "right1": "assets/character/right1.png",
            "right2": "assets/character/right2.png",
        })

        self.asset_scales = {
            "walk1": PSF,
            "walk2": PSF,
            "walk3": PSF,
            "down1": PSF,
            "down2": PSF,
            "left1": PSF,
            "left2": PSF,
            "right1": PSF,
            "right2": PSF
        }

        self.stage: int = 0
        self.keyevent_functions: dict[int, callable] = {
            pygame.K_ESCAPE: self.pause
        }

        self.player.animation_time_range = 100
        self.player.styles = ["walk1", "walk2", "walk3"]
        self.player.backward_style = ["down1", "down2"]
        self.player.left_style = ["left1", "left2"]
        self.player.right_style = ["right1", "right2"]
        self.player.x = 960
        self.player.y = 540

    def update(self) -> None:
        super().update()

        if not self.loading and self.stage == 0:
            self.stage = 1

    def draw(self) -> None:
        width, height = 540, 960

        # Generate base random noise
        base_noise = np.random.randint(0, 256, (height, width)).astype(np.float32)  # noqa: E501

        # Apply Gaussian blur for smoothness
        smooth_noise = gaussian_filter(base_noise, sigma=3)

        # Normalize and scale to 0-180 for darker tone
        smooth_noise = (smooth_noise - smooth_noise.min()) / (smooth_noise.max() - smooth_noise.min())  # noqa: E501
        smooth_noise = (smooth_noise * 180).astype(np.uint8)

        # Add vertical scanlines (every 4th column darker)
        smooth_noise[:, ::4] = np.clip(smooth_noise[:, ::4] - 30, 0, 180)

        # Add flicker: add small random values per pixel
        flicker = np.random.randint(-10, 10, (height, width))
        smooth_noise = np.clip(smooth_noise + flicker, 0, 180).astype(np.uint8)

        # Convert to RGB
        arr_rgb = np.repeat(smooth_noise[:, :, np.newaxis], 3, axis=2)

        # Upscale by 2 for 1080x1920
        arr_upscaled = np.repeat(np.repeat(arr_rgb, 2, axis=0), 2, axis=1)

        surface = pygame.surfarray.make_surface(arr_upscaled)
        self.screen.blit(surface, (0, 0))

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
    game = FNAV()

    try:
        game.run()
    except Exception as e:
        print(f"[PYGRender] [Error] An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")
        game.quit()
    except KeyboardInterrupt:
        print("[PYGRender] [Info] Game interrupted by user.")
        game.quit()
    except SystemExit:
        print("[PYGRender] [Info] Game exited.")
        game.quit()
    finally:
        sys.exit()
