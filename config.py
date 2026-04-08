import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect

class Config:
    # Screen Dimensions (Auto-detect)
    _app = None
    VIRTUAL_LEFT = 0
    VIRTUAL_TOP = 0
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    VIRTUAL_RIGHT = SCREEN_WIDTH
    VIRTUAL_BOTTOM = SCREEN_HEIGHT
    OVERLAY_MARGIN = 32
    TARGET_DT = 1.0 / 60.0
    
    @classmethod
    def initialize(cls, app=None):
        if app is not None:
            cls._app = app
        elif not cls._app:
            cls._app = QApplication.instance() or QApplication(sys.argv)
        primary_screen = cls._app.primaryScreen().availableGeometry()
        virtual_rect = primary_screen

        for screen in cls._app.screens():
            virtual_rect = virtual_rect.united(screen.geometry())

        cls.VIRTUAL_LEFT = virtual_rect.left()
        cls.VIRTUAL_TOP = virtual_rect.top()
        cls.VIRTUAL_RIGHT = virtual_rect.right()
        cls.VIRTUAL_BOTTOM = virtual_rect.bottom()
        cls.SCREEN_WIDTH = virtual_rect.width()
        cls.SCREEN_HEIGHT = virtual_rect.height()

    @classmethod
    def get_screen_available_rect(cls, x, y):
        if cls._app is None:
            cls.initialize()

        point_x = int(x)
        point_y = int(y)
        for screen in cls._app.screens():
            geometry = screen.geometry()
            if geometry.contains(point_x, point_y):
                return screen.availableGeometry()

        return cls._app.primaryScreen().availableGeometry()

    @classmethod
    def get_virtual_rect(cls):
        return QRect(
            cls.VIRTUAL_LEFT,
            cls.VIRTUAL_TOP,
            cls.SCREEN_WIDTH,
            cls.SCREEN_HEIGHT,
        )

    # Sprite Rendering (High-Res Separate Assets)
    SPRITE_BASE_SIZE = 400 # Default max height for new assets
    SCALE_FACTOR = 0.55    # Scale down high-res sprites to desktop size
    RENDER_SIZE = int(SPRITE_BASE_SIZE * SCALE_FACTOR)  # ~220px

    # Timing
    FPS = 60
    ANIMATION_FPS = 15 # Faster animation for high-res sprites
    
    # Physics Constants
    GRAVITY = 0.5
    TERMINAL_VELOCITY = 15.0
    JUMP_FORCE = -12.0
    WALK_SPEED = 2.5
    RUN_SPEED = 5.0
    
    # Behavior Constants
    MIN_IDLE_TIME = 2000
    MAX_IDLE_TIME = 8000
    ACTION_COOLDOWN = 1000
    WEBSHOOT_MAX_TIME = 2000 # 2 seconds for webshooting
    ROPE_LENGTH_MIN = 300
    ROPE_LENGTH_MAX = 600
    DAMPING = 0.99
    
    # Persistence
    PERSISTENCE_PATH = "spidey_settings.json"
    
    # Interaction
    DRAG_THRESHOLD = 5
    
    # Debug
    DEBUG_MODE = False
