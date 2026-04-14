from PyQt5.QtCore import Qt
from config import Config

class AnimationManager:
    def __init__(self):
        self.current_state = "IDLE"
        self.current_frame = 0
        self.facing_right = True
        self.timer = 0.0
        
        # We'll use 8 virtual frames for all animations to drive procedural logic
        self.VIRTUAL_FPS = Config.ANIMATION_FPS

    def set_state(self, state):
        if self.current_state != state:
            self.current_state = state
            self.current_frame = 0
            self.timer = 0.0

    def update(self, dt, vx):
        # Update facing direction
        if abs(vx) > 0.1:
            self.facing_right = vx > 0

        # Advance frames (8 frame cycle for procedural math)
        self.timer += dt
        frame_time = 1.0 / self.VIRTUAL_FPS
        
        if self.timer >= frame_time:
            self.timer -= frame_time
            self.current_frame = (self.current_frame + 1) % 8

