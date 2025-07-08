import pygame
import threading
import sys
import os


class Game:
    def __init__(self, SCREEN_WIDTH: int, SCREEN_HEIGHT: int, fullscreen: bool) -> None:  # noqa: E501
        pygame.init()

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.FPS = 75

        flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), flags)  # noqa: E501
        self.clock = pygame.time.Clock()

        self.running: bool = True
        self.show_fps: bool = True
        self.loading: bool = True

        self.assets_to_load: int = 0
        self.assets_loaded: int = 0

        self.lock = threading.Lock()
        self.keyevent_functions: dict[int, callable] = {}

        self.font = pygame.font.Font(None, 36)

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)

        pygame.quit()
        sys.exit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key in self.keyevent_functions:
                    self.keyevent_functions[event.key]()

    def update(self) -> None:
        with self.lock:
            if self.assets_loaded >= self.assets_to_load:
                self.loading = False

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

        return pygame.display.flip()

    def _load_assets(self, asset_paths: dict) -> None:
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
                    print(f"Loading asset: {asset_name} from {full_path}")
                    asset = pygame.image.load(full_path).convert_alpha()
                    setattr(self, asset_name, asset)

            except Exception as e:
                print(f"Error loading asset '{asset_name}': {e}")

            with self.lock:
                self.assets_loaded += 1

    def load_assets(self, asset_paths: dict) -> None:
        threading.Thread(
            target=self._load_assets,
            args=(asset_paths,),
            daemon=True).start()


if __name__ == "__main__":
    game = Game()
    game.run()
