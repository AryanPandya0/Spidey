import sys
from PyQt5.QtWidgets import QApplication

class Config:
    # Screen Dimensions (Auto-detect)
    _app = None
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    
    @classmethod
    def initialize(cls):
        if not cls._app:
            cls._app = QApplication.instance() or QApplication(sys.argv)
        screen = cls._app.primaryScreen().geometry()
        cls.SCREEN_WIDTH = screen.width()
        cls.SCREEN_HEIGHT = screen.height()

    # Sprite Rendering
    SPRITE_BASE_SIZE = 128
    SCALE_FACTOR = 1.5
    RENDER_SIZE = int(SPRITE_BASE_SIZE * SCALE_FACTOR)  # 192x192

    # Timing
    FPS = 60
    ANIMATION_FPS = 10
    
    # Physics Constants
    GRAVITY = 0.5
    TERMINAL_VELOCITY = 15.0
    JUMP_FORCE = -12.0
    WALK_SPEED = 2.0
    RUN_SPEED = 4.5
    
    # Behavior Constants
    MIN_IDLE_TIME = 2000  # ms
    MAX_IDLE_TIME = 8000  # ms
    ACTION_COOLDOWN = 1000 # ms
    
    # Swing Constants
    ROPE_LENGTH_MIN = 300
    ROPE_LENGTH_MAX = 600
    GRAVITY_ACCEL = 9.8
    DAMPING = 0.99
    
    # Colors
    COLOR_PRIMARY = "#FF0000"  # Red
    COLOR_SECONDARY = "#0000FF" # Blue
    COLOR_ACCENT = "#FFFFFF"    # White
    COLOR_OUTLINE = "#000000"   # Black
    
    # Debug
    DEBUG_MODE = False
