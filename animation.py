from PyQt5.QtGui import QTransform
from PyQt5.QtCore import Qt
from config import Config
from assets import Assets

class AnimationManager:
    def __init__(self):
        self.current_state = "IDLE"
        self.current_frame = 0
        self.state_frames = {}
        self.facing_right = True
        self.timer = 0.0
        
        # Load all sprites at startup
        Assets.generate_all()
        for state in ["IDLE", "WALK", "RUN", "JUMP", "CRAWL", "SWING"]:
            self.state_frames[state] = Assets.get_sprites(state)
        
        self.state_frames["INTERACT"] = self.state_frames.get("IDLE", [])

    def set_state(self, state):
        if self.current_state != state:
            self.current_state = state
            self.current_frame = 0
            self.timer = 0.0

    def update(self, dt, vx):
        # Update facing direction
        if abs(vx) > 0.1:
            self.facing_right = vx > 0

        # Advance frames
        self.timer += dt
        frame_time = 1.0 / max(1, Config.ANIMATION_FPS)
        frames = self.state_frames.get(self.current_state, [])
        while frames and self.timer >= frame_time:
            self.timer -= frame_time
            self.current_frame = (self.current_frame + 1) % len(frames)

    def get_current_sprite(self):
        frames = self.state_frames.get(self.current_state, [])
        if not frames: return None
        
        sprite = frames[self.current_frame % len(frames)]
        if not self.facing_right:
            sprite = sprite.transformed(QTransform().scale(-1, 1))
        return sprite

    def get_oriented_sprite(self, surface):
        sprite = self.get_current_sprite()
        if sprite is None: return None

        if self.current_state != "CRAWL":
            return sprite

        # Handle crawl orientations based on contact surface.
        if surface == "left_wall":
            return sprite.transformed(QTransform().rotate(-90), Qt.SmoothTransformation)
        if surface == "right_wall":
            return sprite.transformed(QTransform().rotate(90), Qt.SmoothTransformation)
        if surface == "ceiling":
            return sprite.transformed(QTransform().rotate(180), Qt.SmoothTransformation)
        return sprite
