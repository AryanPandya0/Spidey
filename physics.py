import math
import time
from config import Config
from utils.window_helper import WindowHelper

class PhysicsEngine:
    def __init__(self):
        self.x = Config.SCREEN_WIDTH // 2
        self.y = Config.SCREEN_HEIGHT - Config.RENDER_SIZE
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = True
        self.is_walled = False
        self.is_ceiling = False
        
        # Window awareness
        self.window_helper = WindowHelper()
        self.start_time = time.time()
        
        # Swing state
        self.swing_anchor = (0, 0)
        self.swing_length = 0
        self.swing_angle = 0
        self.swing_angular_vel = 0

    def update(self, dt, current_state):
        frame_scale = dt / Config.TARGET_DT if Config.TARGET_DT else 1.0

        # Update window data
        self.window_helper.update(int((time.time() - self.start_time) * 1000))
        
        if current_state == "SWING":
            self._update_swing(frame_scale)
        else:
            self._update_linear(frame_scale, current_state)
            
        self._check_collisions()

    def _update_linear(self, frame_scale, state):
        # Apply Gravity
        if not self.is_grounded and state not in ["CRAWL", "SWING"]:
            self.vy += Config.GRAVITY * frame_scale
            if self.vy > Config.TERMINAL_VELOCITY:
                self.vy = Config.TERMINAL_VELOCITY

        # Update Position
        self.x += self.vx * frame_scale
        self.y += self.vy * frame_scale

    def _update_swing(self, frame_scale):
        if self.swing_length <= 0:
            self.swing_length = 1.0  # Avoid zero division
            
        # Pendulum Physics: theta'' = -(g/L) * sin(theta)
        g = 0.5  # Local gravity scaling
        accel = -(g / self.swing_length) * math.sin(self.swing_angle)
        self.swing_angular_vel += accel * frame_scale
        self.swing_angular_vel *= 0.99 ** frame_scale  # Damping
        self.swing_angle += self.swing_angular_vel * frame_scale

        # Cartesion from Polar
        self.x = self.swing_anchor[0] + self.swing_length * math.sin(self.swing_angle) - Config.RENDER_SIZE // 2
        self.y = self.swing_anchor[1] + self.swing_length * math.cos(self.swing_angle) - Config.RENDER_SIZE // 2
        
        # Update linear velocities for when we release
        self.vx = self.swing_angular_vel * self.swing_length * math.cos(self.swing_angle)
        self.vy = -self.swing_angular_vel * self.swing_length * math.sin(self.swing_angle)

    def _check_collisions(self):
        # Floor
        floor_y = Config.SCREEN_HEIGHT - Config.RENDER_SIZE
        
        # Window check
        ground_y = self.window_helper.get_ground_y(self.x, self.y, Config.RENDER_SIZE)
        
        # Final ground check
        if self.y >= ground_y:
            self.y = ground_y
            self.vy = 0
            self.is_grounded = True
        else:
            self.is_grounded = False

        # Walls (Screen bounds only for simplicity, win32 sidebar detection is hard)
        self.is_walled = False
        if self.x <= 0:
            self.x = 0
            self.vx = 0
            self.is_walled = True
        elif self.x >= Config.SCREEN_WIDTH - Config.RENDER_SIZE:
            self.x = Config.SCREEN_WIDTH - Config.RENDER_SIZE
            self.vx = 0
            self.is_walled = True

        # Ceiling
        if self.y <= 0:
            self.y = 0
            self.vy = 0
            self.is_ceiling = True
        else:
            self.is_ceiling = False

    def jump(self):
        if self.is_grounded or self.is_walled:
            self.vy = Config.JUMP_FORCE
            self.is_grounded = False
            
    def start_swing(self):
        import random
        anchor_x = random.uniform(Config.SCREEN_WIDTH * 0.2, Config.SCREEN_WIDTH * 0.8)
        self.swing_anchor = (anchor_x, 0)
        
        # Calculate angle and length from current position
        dx = self.x + Config.RENDER_SIZE // 2 - anchor_x
        dy = self.y + Config.RENDER_SIZE // 2 - 0
        self.swing_length = max(1.0, math.sqrt(dx*dx + dy*dy))
        self.swing_angle = math.atan2(dx, dy)
        self.swing_angular_vel = self.vx / self.swing_length
