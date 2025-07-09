import pygame
import threading
import sys
import os
from dataclasses import dataclass

# Globals
running: bool = None


# Main
class Player:
    def __init__(self) -> None:
        self.x: int = 0
        self.y: int = 0
        self.animation_time_range: int = 0

        self.styles: list | None = None
        self.current_style_index: int = 0
        self.current_style: str = ""

        self.lock = threading.Lock()
        return

    def update(self) -> None:
        print("[PYGRender] [Info] Player update thread started.")
        while running:
            if len(self.styles) > 0:
                if self.current_style_index >= len(self.styles):
                    self.current_style_index = 0

                self.current_style = self.styles[self.current_style_index]  # noqa: E501
                self.current_style_index += 1

            pygame.time.delay(self.animation_time_range)
        return


@dataclass
class Game:
    SCREEN_WIDTH: int
    SCREEN_HEIGHT: int
    fullscreen: bool
    player: bool = False

    def __post_init__(self):
        pygame.init()

        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), flags)  # noqa: E501
        self.clock = pygame.time.Clock()
        self.FPS = 60

        self.running = True
        self.show_fps = True
        self.loading = True
        self.style = None

        self.assets_to_load = 0
        self.assets_loaded = 0

        self.lock = threading.Lock()
        self.keyevent_functions = {}
        self.player = Player() if self.player else None

        self.font = pygame.font.Font(None, 36)
        self.player_update_thread: threading.Thread | None = None

        self.style = True if hasattr(self, "player") and hasattr(self.player, "styles") else False  # noqa: E501
        if self.style:
            print(
                "[PYGRender] [Warning] "
                "Renderer will blit player automatically."
            )

    def run(self) -> None:
        global running
        running = True

        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)

        running = False
        print("[PYGRender] [Fatal Error] Quitting game...")
        pygame.quit()
        sys.exit()

    def quit(self) -> None:
        global running

        print("[PYGRender] [Info] Safely shutting down game...")
        self.running = False
        self.run()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key in self.keyevent_functions:
                    self.keyevent_functions[event.key]()

    def update(self) -> None:
        with self.lock:
            if self.loading and self.assets_loaded == self.assets_to_load:
                self.loading = False
                print("[PYGRender] [Info] Finished loading assets!")

            if not self.loading and hasattr(self, "player") and not self.player_update_thread:  # noqa: E501
                self.player_update_thread = True
                return threading.Thread(
                    target=self.player.update
                ).start()

    def draw(self) -> None:
        with self.lock:
            if self.loading:
                self.screen.fill((0, 0, 0))
                loading_text = self.font.render(
                    f"Loading... ({self.assets_loaded}/{self.assets_to_load})",
                    True,
                    (255, 255, 255)
                )
                self.screen.blit(
                    loading_text,
                    (self.SCREEN_WIDTH // 2 - loading_text.get_width() // 2,
                     self.SCREEN_HEIGHT // 2 - loading_text.get_height() // 2)
                )
                pygame.display.flip()
                return

        if self.show_fps:
            fps_text = self.font.render(
                f"FPS: {self.clock.get_fps():.2f}",
                True, (255, 255, 255)
            )
            self.screen.blit(fps_text, (10, 10))

        if self.style:
            with self.player.lock:
                style_image = getattr(self, self.player.current_style, None)
                if style_image:
                    self.screen.blit(style_image, (self.player.x, self.player.y))  # noqa: E501

        return pygame.display.flip()

    def _load_assets(self, asset_paths: dict) -> None:
        pygame.time.wait(1000)  # Let pygame.display initialise

        with self.lock:
            self.assets_to_load = len(asset_paths)
            self.assets_loaded = 0

        base_dir = os.path.dirname(os.path.abspath(__file__))

        for asset_name, relative_path in asset_paths.items():
            full_path = os.path.join(base_dir, relative_path)

            try:
                if not os.path.exists(full_path):
                    raise FileNotFoundError(f"Asset not found: {full_path}")

                if relative_path.lower().endswith('.png'):
                    print(f"[PYGRender] [Info] Loading asset: {asset_name} from {full_path}")  # noqa: E501
                    asset = pygame.image.load(full_path).convert_alpha()
                    setattr(self, asset_name, asset)

            except Exception as e:
                print(f"Error loading asset '{asset_name}': {e}")

            with self.lock:
                self.assets_loaded += 1

    def load_assets(self, asset_paths: dict) -> None:
        self.assets_to_load = len(asset_paths)
        threading.Thread(
            target=self._load_assets,
            args=(asset_paths,),
            daemon=True).start()


if __name__ == "__main__":
    print("[PYGRender] [Error] Invalid use!"
          " Import as a module using `import pygrender`")
