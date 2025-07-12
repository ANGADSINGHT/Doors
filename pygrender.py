import pygame
import threading
import sys
import os
from dataclasses import dataclass
from enum import Enum, auto

# Globals
running: bool = None


# Enums
class WalkingStyle(Enum):
    FORWARD = auto()
    BACKWARD = auto()
    LEFT = auto()
    RIGHT = auto()

    def __str__(self):
        return f'{self.name(self.value)}'


# Main
class Player:
    x: int = 0
    y: int = 0
    walking_speed: int = 3
    animation_time_range: int = 0
    current_style_index: int = 0

    walking: bool = False
    walking_style: WalkingStyle = None

    current_style: str = ""

    lock = threading.Lock()

    def __init__(self) -> None:
        self.styles: list | None = None
        return

    def update(self) -> None:
        print("[PYGRender] [Info] Player update thread started.")

        styleDict: dict[WalkingStyle, list[str]] = {
            WalkingStyle.FORWARD: self.styles,
            WalkingStyle.BACKWARD: self.backward_style,
            WalkingStyle.LEFT: self.left_style,
            WalkingStyle.RIGHT: self.right_style
        }

        while running:
            with self.lock:
                if len(self.styles) > 0 and self.walking:
                    self.current_styles = styleDict[self.walking_style]
                    if self.current_style_index >= len(self.current_styles):
                        self.current_style_index = 0

                    if self.walking_style == WalkingStyle.FORWARD:
                        self.current_style = self.styles[self.current_style_index]  # noqa: E501
                    if self.walking_style == WalkingStyle.BACKWARD:
                        self.current_style = self.backward_style[self.current_style_index]  # noqa: E501
                    if self.walking_style == WalkingStyle.LEFT:
                        self.current_style = self.left_style[self.current_style_index]  # noqa: E501
                    if self.walking_style == WalkingStyle.RIGHT:
                        self.current_style = self.right_style[self.current_style_index]  # noqa: E501

                    self.current_style_index += 1

            pygame.time.delay(self.animation_time_range)
        return


@dataclass
class Game:
    SCREEN_WIDTH: int
    SCREEN_HEIGHT: int
    fullscreen: bool
    player: bool = False
    show_fps: bool = False

    def __post_init__(self):
        pygame.init()

        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), flags)  # noqa: E501
        self.clock = pygame.time.Clock()
        self.FPS = 30

        self.running = True
        self.loading = True
        self.style = None

        self.assets_to_load = 0
        self.assets_loaded = 0

        self.lock = threading.Lock()
        self.keyevent_functions = {}
        self.player = Player() if self.player else None

        self.font = pygame.font.Font(None, 36)

        self.player_update_thread: threading.Thread | None = None
        self.asset_scales: dict | None = None

        self.style = True if hasattr(self, "player") and hasattr(self.player, "styles") else False  # noqa: E501
        self.has_player = True if hasattr(self, "player") else False
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

        print("[PYGRender] [Error] Quitting game... (please allow a few seconds)")  # noqa: E501
        if running:
            running = False

        pygame.quit()
        sys.exit()

    def quit(self) -> None:
        global running

        print("[PYGRender] [Info] Safely shutting down game...")
        self.running = False
        running = False
        pygame.quit()
        sys.exit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.has_player:
                    if event.key == pygame.K_w:
                        self.player.walking = True

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

            if self.has_player:
                self.playerLogic()

        return

    def playerLogic(self):
        keys = pygame.key.get_pressed()

        self.player.walking = any(
            (keys[pygame.K_w],
             keys[pygame.K_a],
             keys[pygame.K_s],
             keys[pygame.K_d])
        )

        if keys[pygame.K_w]:
            self.player.y -= self.player.walking_speed
            self.player.walking_style = WalkingStyle.FORWARD
        if keys[pygame.K_s]:
            self.player.y += self.player.walking_speed
            self.player.walking_style = WalkingStyle.BACKWARD
        if keys[pygame.K_a]:
            self.player.x -= self.player.walking_speed
            self.player.walking_style = WalkingStyle.LEFT
        if keys[pygame.K_d]:
            self.player.x += self.player.walking_speed
            self.player.walking_style = WalkingStyle.RIGHT

        if keys[pygame.K_LSHIFT]:
            self.player.walking_speed = 6
        else:
            self.player.walking_speed = 3

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
                    print(f"[PYGRender] [Info] Loading asset: {asset_name}"
                          f" from {full_path}")
                    asset = pygame.image.load(full_path).convert_alpha()

                    # Check if scaling is defined for this asset
                    if hasattr(self, 'asset_scales') and asset_name in self.asset_scales:  # noqa: E501
                        scale_value = self.asset_scales[asset_name]

                        if isinstance(scale_value, (int, float)):  # Multiplier factor  # noqa: E501
                            original_size = asset.get_size()
                            new_size = (int(original_size[0] * scale_value), int(original_size[1] * scale_value))  # noqa: E501
                            asset = pygame.transform.smoothscale(asset, new_size)  # noqa: E501
                        elif isinstance(scale_value, (tuple, list)) and len(scale_value) == 2:  # Fixed size  # noqa: E501
                            asset = pygame.transform.smoothscale(asset, scale_value)  # noqa: E501
                        else:
                            print(f"[PYGRender] [Warning] Invalid scale value for '{asset_name}': {scale_value}")  # noqa: E501

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
